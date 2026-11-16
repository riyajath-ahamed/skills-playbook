// Package registry discovers portable skills and workflows from the Git tree.
package registry

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

// Skill is one portable procedure.
type Skill struct {
	Name        string
	Description string
	Domain      string
	Version     string
	Risk        string
	Path        string
	Body        string
}

// Workflow is one ordered procedure.
type Workflow struct {
	Name        string
	Description string
	Execution   string
	MultiAgent  string
	Skills      []string
	Path        string
	Body        string
}

// Library is the discovered portable definitions.
type Library struct {
	Skills    []Skill
	Workflows []Workflow
}

type skillFile struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description"`
	Metadata    struct {
		Version string `yaml:"version"`
		Domain  string `yaml:"domain"`
		Risk    string `yaml:"risk"`
	} `yaml:"metadata"`
}

type workflowFile struct {
	Name        string   `yaml:"name"`
	Description string   `yaml:"description"`
	Execution   string   `yaml:"execution"`
	MultiAgent  string   `yaml:"multi_agent"`
	Skills      []string `yaml:"skills"`
}

// Load reads every skill and workflow under root.
func Load(root string) (Library, error) {
	var lib Library
	var errs []error
	err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			name := entry.Name()
			if name == ".git" || name == ".eit" || name == "node_modules" {
				return fs.SkipDir
			}
			return nil
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		slash := filepath.ToSlash(rel)
		parts := strings.Split(slash, "/")
		switch {
		case len(parts) == 4 && parts[0] == "skills" && parts[3] == "SKILL.md":
			skill, err := readSkill(path, slash)
			if err != nil {
				errs = append(errs, err)
				return nil
			}
			lib.Skills = append(lib.Skills, skill)
		case len(parts) == 3 && parts[0] == "workflows" && parts[2] == "WORKFLOW.md":
			workflow, err := readWorkflow(path, slash)
			if err != nil {
				errs = append(errs, err)
				return nil
			}
			lib.Workflows = append(lib.Workflows, workflow)
		}
		return nil
	})
	if err != nil {
		return Library{}, err
	}
	sort.Slice(lib.Skills, func(i, j int) bool { return lib.Skills[i].Name < lib.Skills[j].Name })
	sort.Slice(lib.Workflows, func(i, j int) bool { return lib.Workflows[i].Name < lib.Workflows[j].Name })
	if len(errs) > 0 {
		return lib, errors.Join(errs...)
	}
	return lib, nil
}

// FindSkill returns the skill with the given name.
func (lib Library) FindSkill(name string) (Skill, error) {
	var found *Skill
	for i := range lib.Skills {
		if lib.Skills[i].Name == name {
			if found != nil {
				return Skill{}, fmt.Errorf("duplicate skill name %s", name)
			}
			found = &lib.Skills[i]
		}
	}
	if found == nil {
		return Skill{}, fmt.Errorf("skill not found: %s (run `ei skills list`)", name)
	}
	return *found, nil
}

// FindWorkflow returns the workflow with the given name.
func (lib Library) FindWorkflow(name string) (Workflow, error) {
	var found *Workflow
	for i := range lib.Workflows {
		if lib.Workflows[i].Name == name {
			if found != nil {
				return Workflow{}, fmt.Errorf("duplicate workflow name %s", name)
			}
			found = &lib.Workflows[i]
		}
	}
	if found == nil {
		return Workflow{}, fmt.Errorf("workflow not found: %s (run `ei workflows list`)", name)
	}
	return *found, nil
}

func readSkill(path, rel string) (Skill, error) {
	front, body, err := splitFrontmatter(path)
	if err != nil {
		return Skill{}, err
	}
	var file skillFile
	if err := yaml.Unmarshal(front, &file); err != nil {
		return Skill{}, fmt.Errorf("%s: malformed skill metadata: %w", rel, err)
	}
	if strings.TrimSpace(file.Name) == "" || strings.TrimSpace(file.Description) == "" {
		return Skill{}, fmt.Errorf("%s: skill name and description are required", rel)
	}
	if file.Metadata.Domain == "" || file.Metadata.Version == "" {
		return Skill{}, fmt.Errorf("%s: metadata.domain and metadata.version are required", rel)
	}
	return Skill{
		Name:        file.Name,
		Description: strings.TrimSpace(file.Description),
		Domain:      file.Metadata.Domain,
		Version:     file.Metadata.Version,
		Risk:        file.Metadata.Risk,
		Path:        rel,
		Body:        body,
	}, nil
}

func readWorkflow(path, rel string) (Workflow, error) {
	front, body, err := splitFrontmatter(path)
	if err != nil {
		return Workflow{}, err
	}
	var file workflowFile
	if err := yaml.Unmarshal(front, &file); err != nil {
		return Workflow{}, fmt.Errorf("%s: malformed workflow metadata: %w", rel, err)
	}
	if strings.TrimSpace(file.Name) == "" || strings.TrimSpace(file.Description) == "" {
		return Workflow{}, fmt.Errorf("%s: workflow name and description are required", rel)
	}
	if file.Execution == "" {
		return Workflow{}, fmt.Errorf("%s: execution is required", rel)
	}
	multi := file.MultiAgent
	if multi == "" {
		multi = "disabled"
	}
	return Workflow{
		Name:        file.Name,
		Description: strings.TrimSpace(file.Description),
		Execution:   file.Execution,
		MultiAgent:  multi,
		Skills:      file.Skills,
		Path:        rel,
		Body:        body,
	}, nil
}

func splitFrontmatter(path string) ([]byte, string, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return nil, "", err
	}
	text := string(content)
	if !strings.HasPrefix(text, "---\n") {
		return nil, "", fmt.Errorf("%s: missing YAML frontmatter", filepath.ToSlash(path))
	}
	end := strings.Index(text[4:], "\n---\n")
	if end == -1 {
		return nil, "", fmt.Errorf("%s: frontmatter is not closed", filepath.ToSlash(path))
	}
	front := text[4 : 4+end]
	body := text[4+end+5:]
	return []byte(front), body, nil
}
