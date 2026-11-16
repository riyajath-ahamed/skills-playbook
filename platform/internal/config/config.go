// Package config locates the toolkit repository and records process settings.
package config

import (
	"errors"
	"os"
	"path/filepath"
)

const (
	EnvRoot = "EI_ROOT"
	Version = "0.1.0"
)

// Settings is the process configuration for one CLI invocation.
type Settings struct {
	Root        string
	Environment string
	Version     string
}

// FindRoot walks from start and then from parents until it finds the toolkit markers.
// An explicit root, when non-empty, is used instead of walking.
func FindRoot(explicit, envRoot, start string) (string, error) {
	if explicit != "" {
		return checkRoot(explicit)
	}
	if envRoot != "" {
		return checkRoot(envRoot)
	}
	if start == "" {
		wd, err := os.Getwd()
		if err != nil {
			return "", err
		}
		start = wd
	}
	current, err := filepath.Abs(start)
	if err != nil {
		return "", err
	}
	for {
		if _, err := checkRoot(current); err == nil {
			return current, nil
		}
		parent := filepath.Dir(current)
		if parent == current {
			break
		}
		current = parent
	}
	return "", errors.New("repository root not found; set --root or EI_ROOT")
}

func checkRoot(path string) (string, error) {
	abs, err := filepath.Abs(path)
	if err != nil {
		return "", err
	}
	if _, err := os.Stat(filepath.Join(abs, "AGENTS.md")); err != nil {
		return "", errors.New("AGENTS.md not found in " + abs)
	}
	if _, err := os.Stat(filepath.Join(abs, "mcp", "catalog.yaml")); err != nil {
		return "", errors.New("mcp/catalog.yaml not found in " + abs)
	}
	return abs, nil
}

// Load resolves the repository root. Environment defaults to development.
func Load(explicit, envRoot, start string) (Settings, error) {
	root, err := FindRoot(explicit, envRoot, start)
	if err != nil {
		return Settings{}, err
	}
	return Settings{Root: root, Environment: "development", Version: Version}, nil
}
