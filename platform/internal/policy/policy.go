// Package policy decides whether a tool capability is allowed.
// It does not contact an MCP server.
package policy

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

// Request is one capability check.
type Request struct {
	Integration string
	Environment string
	Capability  string
	Profile     string
	Approval    bool
}

// Decision is the allow or deny result.
type Decision struct {
	Allow  bool
	Reason string
}

// Integration is the catalog data the decision needs.
type Integration struct {
	ID                string
	PermissionProfile string
	Production        string
}

// Policy is one permission profile.
type Policy struct {
	ID               string
	ProductionAccess string
	Allow            map[string][]string
	Deny             []string
	ApprovalRequired []string
	FailClosed       bool
}

// Set is the catalog view used for decisions.
type Set struct {
	Integrations map[string]Integration
	Policies     map[string]Policy
}

type catalogFile struct {
	Integrations []struct {
		ID                string `yaml:"id"`
		PermissionProfile string `yaml:"permission_profile"`
		Environments      struct {
			Production string `yaml:"production"`
		} `yaml:"environments"`
	} `yaml:"integrations"`
}

type policyFile struct {
	ID               string              `yaml:"id"`
	ProductionAccess string              `yaml:"production_access"`
	Allow            map[string][]string `yaml:"allow"`
	Deny             []string            `yaml:"deny"`
	ApprovalRequired []string            `yaml:"approval_required"`
	FailClosed       bool                `yaml:"fail_closed"`
}

// Load reads mcp/catalog.yaml and mcp/policies.
func Load(root string) (Set, error) {
	raw, err := os.ReadFile(filepath.Join(root, "mcp", "catalog.yaml"))
	if err != nil {
		return Set{}, fmt.Errorf("read catalog: %w", err)
	}
	var catalog catalogFile
	if err := yaml.Unmarshal(raw, &catalog); err != nil {
		return Set{}, fmt.Errorf("parse catalog: %w", err)
	}
	set := Set{
		Integrations: map[string]Integration{},
		Policies:     map[string]Policy{},
	}
	for _, item := range catalog.Integrations {
		set.Integrations[item.ID] = Integration{
			ID:                item.ID,
			PermissionProfile: item.PermissionProfile,
			Production:        item.Environments.Production,
		}
	}
	entries, err := os.ReadDir(filepath.Join(root, "mcp", "policies"))
	if err != nil {
		return Set{}, fmt.Errorf("read policies: %w", err)
	}
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".yaml") {
			continue
		}
		path := filepath.Join(root, "mcp", "policies", entry.Name())
		body, err := os.ReadFile(path)
		if err != nil {
			return Set{}, err
		}
		var file policyFile
		if err := yaml.Unmarshal(body, &file); err != nil {
			return Set{}, fmt.Errorf("parse %s: %w", entry.Name(), err)
		}
		set.Policies[file.ID] = Policy{
			ID:               file.ID,
			ProductionAccess: file.ProductionAccess,
			Allow:            file.Allow,
			Deny:             file.Deny,
			ApprovalRequired: file.ApprovalRequired,
			FailClosed:       file.FailClosed,
		}
	}
	return set, nil
}

// Evaluate denies unknown integrations, environments, and capabilities.
func Evaluate(set Set, req Request) Decision {
	deny := func(reason string) Decision {
		return Decision{Allow: false, Reason: reason}
	}
	integration, ok := set.Integrations[req.Integration]
	if !ok || req.Integration == "" {
		return deny("unknown integration")
	}
	switch req.Environment {
	case "development", "test", "production":
	default:
		return deny("unknown or ambiguous environment")
	}
	switch req.Capability {
	case "read", "write", "delete", "deploy", "shell", "credential_admin":
	default:
		return deny("unknown capability")
	}
	profileName := integration.PermissionProfile
	if req.Profile != "" && req.Profile != profileName {
		if !req.Approval {
			return deny("profile escalation requires approval")
		}
		profileName = req.Profile
	}
	profile, ok := set.Policies[profileName]
	if !ok {
		return deny("unknown permission profile")
	}
	if contains(profile.Deny, req.Capability) {
		return deny("capability is denied by profile " + profile.ID)
	}
	if req.Environment == "production" {
		if integration.Production != "approval" {
			return deny("integration denies production access")
		}
		if profile.ProductionAccess == "deny" || profile.ProductionAccess == "" {
			return deny("profile denies production access")
		}
		if profile.ProductionAccess != "approval" {
			return deny("unknown production access rule")
		}
		if !req.Approval || !contains(profile.ApprovalRequired, "production") {
			return deny("production access requires approval")
		}
	}
	allowed := profile.Allow[req.Environment]
	if !contains(allowed, req.Capability) {
		return deny("capability is not granted in " + req.Environment)
	}
	if contains(profile.ApprovalRequired, req.Capability) && !req.Approval {
		return deny("capability requires approval")
	}
	return Decision{Allow: true, Reason: "allowed by profile " + profile.ID}
}

func contains(values []string, want string) bool {
	for _, value := range values {
		if value == want {
			return true
		}
	}
	return false
}
