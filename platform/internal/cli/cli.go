// Package cli implements the ei command.
package cli

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"

	"engineering-intelligence/platform/internal/config"
	"engineering-intelligence/platform/internal/knowledge"
	"engineering-intelligence/platform/internal/registry"

	"gopkg.in/yaml.v3"
)

// Main runs ei and returns a process exit code.
func Main(args []string, stdout, stderr io.Writer, getenv func(string) string) int {
	if getenv == nil {
		getenv = os.Getenv
	}
	rootFlag, rest, err := parseRoot(args)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	if len(rest) == 0 || rest[0] == "help" || rest[0] == "--help" || rest[0] == "-h" {
		fmt.Fprint(stdout, usageText)
		return 0
	}
	switch rest[0] {
	case "version":
		if len(rest) != 1 {
			fmt.Fprintln(stderr, "version takes no arguments")
			return 2
		}
		fmt.Fprintf(stdout, "ei %s\n", config.Version)
		return 0
	case "doctor":
		return doctor(rootFlag, getenv, stdout, stderr)
	case "skills":
		return skillsCommand(rest[1:], rootFlag, getenv, stdout, stderr)
	case "workflows":
		return workflowsCommand(rest[1:], rootFlag, getenv, stdout, stderr)
	case "mcp":
		return mcpCommand(rest[1:], rootFlag, getenv, stdout, stderr)
	case "knowledge":
		return knowledgeCommand(rest[1:], rootFlag, getenv, stdout, stderr)
	case "validate":
		if len(rest) != 1 {
			fmt.Fprintln(stderr, "validate takes no arguments")
			return 2
		}
		return validate(rootFlag, getenv, stdout, stderr)
	default:
		fmt.Fprintf(stderr, "unknown command %q\n%s", rest[0], usageText)
		return 2
	}
}

func parseRoot(args []string) (string, []string, error) {
	var root string
	var rest []string
	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch {
		case arg == "--root":
			if i+1 >= len(args) {
				return "", nil, errors.New("--root requires a path")
			}
			i++
			root = args[i]
		case strings.HasPrefix(arg, "--root="):
			root = strings.TrimPrefix(arg, "--root=")
		default:
			rest = append(rest, arg)
		}
	}
	return root, rest, nil
}

func resolve(rootFlag string, getenv func(string) string) (config.Settings, error) {
	return config.Load(rootFlag, getenv(config.EnvRoot), "")
}

func skillsCommand(args []string, rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	if len(args) == 0 {
		fmt.Fprintln(stderr, "usage: ei skills list | ei skills show <name>")
		return 2
	}
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	lib, err := registry.Load(settings.Root)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	switch args[0] {
	case "list":
		if len(args) != 1 {
			fmt.Fprintln(stderr, "usage: ei skills list")
			return 2
		}
		writeSkillList(stdout, lib.Skills)
		return 0
	case "show":
		if len(args) != 2 {
			fmt.Fprintln(stderr, "usage: ei skills show <name>")
			return 2
		}
		skill, err := lib.FindSkill(args[1])
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 1
		}
		fmt.Fprintf(stdout, "name: %s\npath: %s\ndomain: %s\nversion: %s\nrisk: %s\n\n%s\n%s",
			skill.Name, skill.Path, skill.Domain, skill.Version, skill.Risk, skill.Description, skill.Body)
		return 0
	default:
		fmt.Fprintf(stderr, "unknown skills command %q\n", args[0])
		return 2
	}
}

func workflowsCommand(args []string, rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	if len(args) == 0 {
		fmt.Fprintln(stderr, "usage: ei workflows list | ei workflows show <name>")
		return 2
	}
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	lib, err := registry.Load(settings.Root)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	switch args[0] {
	case "list":
		if len(args) != 1 {
			fmt.Fprintln(stderr, "usage: ei workflows list")
			return 2
		}
		for _, workflow := range lib.Workflows {
			fmt.Fprintf(stdout, "%s\t%s\t%s\n", workflow.Name, workflow.Execution, oneLine(workflow.Description))
		}
		return 0
	case "show":
		if len(args) != 2 {
			fmt.Fprintln(stderr, "usage: ei workflows show <name>")
			return 2
		}
		workflow, err := lib.FindWorkflow(args[1])
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 1
		}
		fmt.Fprintf(stdout, "name: %s\npath: %s\nexecution: %s\nmulti_agent: %s\n\n%s\n%s",
			workflow.Name, workflow.Path, workflow.Execution, workflow.MultiAgent, workflow.Description, workflow.Body)
		return 0
	default:
		fmt.Fprintf(stderr, "unknown workflows command %q\n", args[0])
		return 2
	}
}

func mcpCommand(args []string, rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	if len(args) != 1 || (args[0] != "list" && args[0] != "health") {
		if len(args) > 0 && args[0] != "list" && args[0] != "health" {
			fmt.Fprintf(stderr, "unknown mcp command %q\n", args[0])
			return 2
		}
		fmt.Fprintln(stderr, "usage: ei mcp list | ei mcp health")
		return 2
	}
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	items, err := loadMCPIntegrations(settings.Root)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if args[0] == "list" {
		writeMCPList(stdout, items)
		return 0
	}
	results := checkMCPHealth(context.Background(), items, mcpHealthClient())
	writeMCPHealth(stdout, results)
	for _, result := range results {
		if result.Result == "unreachable" {
			return 1
		}
	}
	return 0
}

func loadMCPIntegrations(root string) ([]mcpIntegration, error) {
	raw, err := os.ReadFile(filepath.Join(root, "mcp", "catalog.yaml"))
	if err != nil {
		return nil, fmt.Errorf("read catalog: %w", err)
	}
	var catalog mcpCatalog
	if err := yaml.Unmarshal(raw, &catalog); err != nil {
		return nil, fmt.Errorf("parse catalog: %w", err)
	}
	items := catalog.Integrations
	sort.Slice(items, func(i, j int) bool {
		return items[i].ID < items[j].ID
	})
	return items, nil
}

func writeMCPList(w io.Writer, items []mcpIntegration) {
	const purposeWidth = 48
	idWidth := len("Integration")
	vendorWidth := len("Vendor")
	profileWidth := len("Profile")
	installedWidth := len("Installed")
	for _, item := range items {
		if len(item.ID) > idWidth {
			idWidth = len(item.ID)
		}
		if len(item.Provider) > vendorWidth {
			vendorWidth = len(item.Provider)
		}
		if len(item.PermissionProfile) > profileWidth {
			profileWidth = len(item.PermissionProfile)
		}
	}
	type row struct {
		id        string
		vendor    string
		profile   string
		installed string
		purpose   []string
	}
	rows := make([]row, 0, len(items))
	for _, item := range items {
		purpose := wrapText(oneLine(item.Purpose), purposeWidth)
		if len(purpose) == 0 {
			purpose = []string{""}
		}
		installed := "false"
		if item.Installed {
			installed = "true"
		}
		rows = append(rows, row{
			id:        item.ID,
			vendor:    item.Provider,
			profile:   item.PermissionProfile,
			installed: installed,
			purpose:   purpose,
		})
	}
	rule := func(left, mid, right string) {
		fmt.Fprintf(w, "%s%s%s%s%s%s%s%s%s%s%s\n",
			left,
			strings.Repeat("─", idWidth+2),
			mid,
			strings.Repeat("─", vendorWidth+2),
			mid,
			strings.Repeat("─", profileWidth+2),
			mid,
			strings.Repeat("─", installedWidth+2),
			mid,
			strings.Repeat("─", purposeWidth+2),
			right,
		)
	}
	fmt.Fprintf(w, "%d integrations\n", len(items))
	fmt.Fprintln(w, "Source: mcp/catalog.yaml")
	fmt.Fprintln(w)
	rule("┌", "┬", "┐")
	fmt.Fprintf(w, "│ %-*s │ %-*s │ %-*s │ %-*s │ %-*s │\n",
		idWidth, "Integration",
		vendorWidth, "Vendor",
		profileWidth, "Profile",
		installedWidth, "Installed",
		purposeWidth, "Purpose",
	)
	rule("├", "┼", "┤")
	for i, item := range rows {
		for line, text := range item.purpose {
			id, vendor, profile, installed := "", "", "", ""
			if line == 0 {
				id = item.id
				vendor = item.vendor
				profile = item.profile
				installed = item.installed
			}
			fmt.Fprintf(w, "│ %-*s │ %-*s │ %-*s │ %-*s │ %-*s │\n",
				idWidth, id,
				vendorWidth, vendor,
				profileWidth, profile,
				installedWidth, installed,
				purposeWidth, text,
			)
		}
		if i < len(rows)-1 {
			rule("├", "┼", "┤")
		}
	}
	rule("└", "┴", "┘")
}

type mcpCatalog struct {
	Integrations []mcpIntegration `yaml:"integrations"`
}

type mcpIntegration struct {
	ID                string `yaml:"id"`
	Provider          string `yaml:"provider"`
	Purpose           string `yaml:"purpose"`
	PermissionProfile string `yaml:"permission_profile"`
	Installed         bool   `yaml:"installed"`
	Transport         string `yaml:"transport"`
	Endpoint          string `yaml:"endpoint"`
	Status            string `yaml:"status"`
}

func knowledgeCommand(args []string, rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	if len(args) == 0 || args[0] != "search" {
		fmt.Fprintln(stderr, "usage: ei knowledge search <query>")
		return 2
	}
	if len(args) < 2 {
		fmt.Fprintln(stderr, "search query is required")
		return 2
	}
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	hits, err := knowledge.Search(settings.Root, strings.Join(args[1:], " "), 20)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	if len(hits) == 0 {
		fmt.Fprintln(stdout, "no results")
		return 0
	}
	for _, hit := range hits {
		fmt.Fprintf(stdout, "%s\t%d\t%s\n", hit.Path, hit.Score, oneLine(hit.Snippet))
	}
	return 0
}

func validate(rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	scripts := []string{
		"validate-skills.sh",
		"validate-catalog.sh",
		"check-links.sh",
		"validate-evals.sh",
	}
	for _, name := range scripts {
		path := filepath.Join(settings.Root, "scripts", name)
		if _, err := os.Stat(path); err != nil {
			fmt.Fprintf(stderr, "validator not found: %s\n", path)
			return 1
		}
		cmd := exec.Command("bash", path)
		cmd.Dir = settings.Root
		cmd.Stdout = stdout
		cmd.Stderr = stderr
		cmd.Env = os.Environ()
		if err := cmd.Run(); err != nil {
			fmt.Fprintf(stderr, "%s failed: %v\n", name, err)
			return 1
		}
	}
	return 0
}

func doctor(rootFlag string, getenv func(string) string, stdout, stderr io.Writer) int {
	failed := false
	report := func(ok bool, optional bool, name, detail string) {
		state := "ok"
		suffix := ""
		if !ok {
			state = "missing"
			if optional {
				suffix = " (optional)"
			} else {
				suffix = " (required)"
				failed = true
			}
		}
		if detail != "" {
			fmt.Fprintf(stdout, "[%s] %s%s: %s\n", state, name, suffix, detail)
			return
		}
		fmt.Fprintf(stdout, "[%s] %s%s\n", state, name, suffix)
	}
	for _, probe := range []struct {
		name     string
		optional bool
		args     []string
	}{
		{name: "git", args: []string{"--version"}},
		{name: "go", args: []string{"version"}},
		{name: "python3", args: []string{"--version"}},
		{name: "PyYAML", args: []string{"-c", "import yaml"}},
		{name: "node", optional: true, args: []string{"--version"}},
		{name: "docker", optional: true, args: []string{"info"}},
		{name: "uv", optional: true, args: []string{"--version"}},
	} {
		command := probe.name
		if probe.name == "PyYAML" {
			command = "python3"
		}
		ok, detail := probeCommand(command, probe.args...)
		report(ok, probe.optional, probe.name, detail)
	}
	report(false, true, "opentelemetry-export", "not configured")
	settings, err := resolve(rootFlag, getenv)
	if err != nil {
		fmt.Fprintf(stdout, "[missing] repository root (required): %s\n", err)
		failed = true
	} else {
		lib, loadErr := registry.Load(settings.Root)
		if loadErr != nil {
			fmt.Fprintf(stdout, "[missing] skill registry (required): %s\n", loadErr)
			failed = true
		} else {
			fmt.Fprintf(stdout, "[ok] repository root: %s\n", settings.Root)
			fmt.Fprintf(stdout, "[ok] skills: %d\n", len(lib.Skills))
			fmt.Fprintf(stdout, "[ok] workflows: %d\n", len(lib.Workflows))
		}
	}
	if failed {
		fmt.Fprintln(stderr, "doctor found missing requirements")
		return 1
	}
	return 0
}

func oneLine(value string) string {
	return strings.Join(strings.Fields(value), " ")
}

var skillDomainOrder = []string{
	"architecture",
	"agentic-systems",
	"platform-engineering",
	"application-engineering",
	"software-engineering",
	"documentation",
	"research",
	"learning",
	"security",
}

func writeSkillList(w io.Writer, skills []registry.Skill) {
	grouped := map[string][]registry.Skill{}
	for _, skill := range skills {
		grouped[skill.Domain] = append(grouped[skill.Domain], skill)
	}
	for domain := range grouped {
		sort.Slice(grouped[domain], func(i, j int) bool {
			return grouped[domain][i].Name < grouped[domain][j].Name
		})
	}
	order := make([]string, 0, len(grouped))
	seen := map[string]bool{}
	for _, domain := range skillDomainOrder {
		if len(grouped[domain]) > 0 {
			order = append(order, domain)
			seen[domain] = true
		}
	}
	var extra []string
	for domain := range grouped {
		if !seen[domain] {
			extra = append(extra, domain)
		}
	}
	sort.Strings(extra)
	order = append(order, extra...)

	fmt.Fprintf(w, "%d skills\n", len(skills))
	for _, domain := range order {
		fmt.Fprintf(w, "\n%s (%d)\n", domainHeading(domain), len(grouped[domain]))
		writeSkillTable(w, grouped[domain])
	}
}

func writeSkillTable(w io.Writer, skills []registry.Skill) {
	const summaryWidth = 64
	nameWidth := len("Skill")
	for _, skill := range skills {
		if len(skill.Name) > nameWidth {
			nameWidth = len(skill.Name)
		}
	}
	type row struct {
		name    string
		summary []string
	}
	rows := make([]row, 0, len(skills))
	for _, skill := range skills {
		summary := wrapText(oneLine(skill.Description), summaryWidth)
		if len(summary) == 0 {
			summary = []string{""}
		}
		rows = append(rows, row{name: skill.Name, summary: summary})
	}
	rule := func(left, mid, right string) {
		fmt.Fprintf(w, "%s%s%s%s%s\n",
			left,
			strings.Repeat("─", nameWidth+2),
			mid,
			strings.Repeat("─", summaryWidth+2),
			right,
		)
	}
	rule("┌", "┬", "┐")
	fmt.Fprintf(w, "│ %-*s │ %-*s │\n", nameWidth, "Skill", summaryWidth, "Summary")
	rule("├", "┼", "┤")
	for i, item := range rows {
		for line, text := range item.summary {
			name := ""
			if line == 0 {
				name = item.name
			}
			fmt.Fprintf(w, "│ %-*s │ %-*s │\n", nameWidth, name, summaryWidth, text)
		}
		if i < len(rows)-1 {
			rule("├", "┼", "┤")
		}
	}
	rule("└", "┴", "┘")
}

func domainHeading(domain string) string {
	if domain == "" {
		return "Unspecified"
	}
	parts := strings.Split(domain, "-")
	for i, part := range parts {
		if part == "" {
			continue
		}
		parts[i] = strings.ToUpper(part[:1]) + part[1:]
	}
	return strings.Join(parts, " ")
}

func wrapText(text string, width int) []string {
	words := strings.Fields(text)
	if len(words) == 0 || width < 1 {
		return nil
	}
	var lines []string
	current := words[0]
	for _, word := range words[1:] {
		if len(current)+1+len(word) > width {
			lines = append(lines, current)
			current = word
			continue
		}
		current += " " + word
	}
	return append(lines, current)
}

func probeCommand(name string, args ...string) (bool, string) {
	if _, err := exec.LookPath(name); err != nil {
		return false, "not on PATH"
	}
	cmd := exec.Command(name, args...)
	cmd.Env = os.Environ()
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	text := strings.TrimSpace(stdout.String())
	if err != nil {
		if name == "docker" {
			return false, "docker info failed; daemon is not reachable"
		}
		text = strings.TrimSpace(stderr.String())
		if text == "" {
			text = err.Error()
		}
	}
	if index := strings.IndexByte(text, '\n'); index >= 0 {
		text = text[:index]
	}
	if len(text) > 180 {
		text = text[:180]
	}
	return err == nil, text
}

const usageText = `ei is the Engineering Intelligence Toolkit CLI.

Usage:
  ei version
  ei doctor
  ei skills list
  ei skills show <name>
  ei workflows list
  ei workflows show <name>
  ei mcp list
  ei mcp health
  ei knowledge search <query>
  ei validate

Options:
  --root <path>   Repository root. Defaults to EI_ROOT, then the current directory's parents.

ei discovers files in the repository. ei mcp health sends an unauthenticated GET to remote catalog endpoints. It does not call models, open a tool session, or send credentials.
`
