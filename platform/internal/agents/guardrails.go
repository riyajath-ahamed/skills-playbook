package agents

import (
	"fmt"
	"path"
	"regexp"
	"sort"
	"strings"
	"time"
)

const (
	// MaxConcurrency is the upper bound for specialists running at once.
	MaxConcurrency = 4
	// MaxRetries is the upper bound for contract-level retries.
	MaxRetries = 2
	minTimeout = time.Second
	maxTimeout = 15 * time.Minute
)

// Contract is an orchestration request. Guard checks it and does not run it.
type Contract struct {
	Coordinator       string
	Concurrency       int
	Retries           int
	CancelOnFailure   bool
	FinalVerification bool
	Specialists       []Specialist
}

// Specialist is one bounded worker in a contract.
type Specialist struct {
	ID          string
	Skill       string
	Environment string
	Tools       []string
	WriteScope  []string
	Timeout     time.Duration
	Approval    bool
}

var (
	skillNamePattern = regexp.MustCompile(`^[a-z0-9]+(?:-[a-z0-9]+)*$`)
	blockedTools     = map[string]struct{}{
		"*":                {},
		"all":              {},
		"shell":            {},
		"deploy":           {},
		"delete":           {},
		"credential_admin": {},
	}
	overridePhrases = []string{
		"ignore previous instructions",
		"ignore prior instructions",
		"ignore policy",
		"bypass approval",
		"bypass the guardrail",
	}
)

// Guard rejects a contract that violates the orchestration guardrails.
// skills contains the known skill names. A missing or unknown skill is denied.
func Guard(contract Contract, skills map[string]struct{}) error {
	var errs []error
	if strings.TrimSpace(contract.Coordinator) == "" {
		errs = append(errs, fmt.Errorf("coordinator is required"))
	}
	if contract.Retries < 0 || contract.Retries > MaxRetries {
		errs = append(errs, fmt.Errorf("retries must be from 0 to %d", MaxRetries))
	}
	if len(contract.Specialists) == 0 {
		errs = append(errs, fmt.Errorf("at least one specialist is required"))
	}
	if contract.Concurrency < 1 || contract.Concurrency > MaxConcurrency {
		errs = append(errs, fmt.Errorf("concurrency must be from 1 to %d", MaxConcurrency))
	} else if contract.Concurrency > len(contract.Specialists) && len(contract.Specialists) > 0 {
		errs = append(errs, fmt.Errorf("concurrency %d exceeds specialist count %d", contract.Concurrency, len(contract.Specialists)))
	}
	if contract.Concurrency > 1 && !contract.CancelOnFailure {
		errs = append(errs, fmt.Errorf("cancellation is required when concurrency is greater than 1"))
	}
	if len(contract.Specialists) > 1 && !contract.FinalVerification {
		errs = append(errs, fmt.Errorf("final verification is required when more than one specialist is assigned"))
	}

	seenIDs := map[string]struct{}{}
	var writes []scopedWrite
	for _, specialist := range contract.Specialists {
		errs = append(errs, checkSpecialist(specialist, skills, seenIDs)...)
		for _, scope := range specialist.WriteScope {
			writes = append(writes, scopedWrite{owner: specialist.ID, path: scope})
		}
	}
	errs = append(errs, overlappingWrites(writes)...)
	return joinErrors(errs)
}

// ScreenResult rejects specialist text that tries to override policy.
func ScreenResult(output string) error {
	lower := strings.ToLower(output)
	for _, phrase := range overridePhrases {
		if strings.Contains(lower, phrase) {
			return fmt.Errorf("specialist result contains a policy override")
		}
	}
	return nil
}

func checkSpecialist(specialist Specialist, skills map[string]struct{}, seenIDs map[string]struct{}) []error {
	var errs []error
	id := strings.TrimSpace(specialist.ID)
	if id == "" {
		errs = append(errs, fmt.Errorf("specialist id is required"))
		id = "<missing>"
	} else if _, ok := seenIDs[id]; ok {
		errs = append(errs, fmt.Errorf("specialist %s: duplicate id", id))
	} else {
		seenIDs[id] = struct{}{}
	}
	if !skillNamePattern.MatchString(specialist.Skill) {
		errs = append(errs, fmt.Errorf("specialist %s: skill must be a lowercase hyphenated name", id))
	} else if _, ok := skills[specialist.Skill]; !ok {
		errs = append(errs, fmt.Errorf("specialist %s: unknown skill %s", id, specialist.Skill))
	}
	if specialist.Timeout < minTimeout || specialist.Timeout > maxTimeout {
		errs = append(errs, fmt.Errorf("specialist %s: timeout must be from 1s to 15m", id))
	}
	needsEnvironment := len(specialist.Tools) > 0 || len(specialist.WriteScope) > 0
	switch specialist.Environment {
	case "":
		if needsEnvironment {
			errs = append(errs, fmt.Errorf("specialist %s: environment is required", id))
		}
	case "development", "test":
	case "production":
		errs = append(errs, fmt.Errorf("specialist %s: production access is denied", id))
	default:
		errs = append(errs, fmt.Errorf("specialist %s: unknown environment %s", id, specialist.Environment))
	}
	for _, tool := range specialist.Tools {
		name := strings.ToLower(strings.TrimSpace(tool))
		if _, blocked := blockedTools[name]; blocked {
			errs = append(errs, fmt.Errorf("specialist %s: tool %s is denied", id, tool))
		}
	}
	for _, scope := range specialist.WriteScope {
		if _, err := cleanWriteScope(scope); err != nil {
			errs = append(errs, fmt.Errorf("specialist %s: %w", id, err))
		}
	}
	return errs
}

type scopedWrite struct {
	owner string
	path  string
}

func overlappingWrites(writes []scopedWrite) []error {
	cleaned := make([]scopedWrite, 0, len(writes))
	for _, write := range writes {
		cleanedPath, err := cleanWriteScope(write.path)
		if err != nil {
			continue
		}
		cleaned = append(cleaned, scopedWrite{owner: write.owner, path: cleanedPath})
	}
	sort.Slice(cleaned, func(i, j int) bool {
		if cleaned[i].path == cleaned[j].path {
			return cleaned[i].owner < cleaned[j].owner
		}
		return cleaned[i].path < cleaned[j].path
	})
	var errs []error
	reported := map[string]struct{}{}
	for i := 0; i < len(cleaned); i++ {
		for j := i + 1; j < len(cleaned); j++ {
			if cleaned[i].owner == cleaned[j].owner {
				continue
			}
			if !pathsOverlap(cleaned[i].path, cleaned[j].path) {
				continue
			}
			key := cleaned[i].owner + "\x00" + cleaned[j].owner + "\x00" + cleaned[i].path + "\x00" + cleaned[j].path
			if _, ok := reported[key]; ok {
				continue
			}
			reported[key] = struct{}{}
			errs = append(errs, fmt.Errorf("write scopes overlap: %s (%s) and %s (%s)", cleaned[i].owner, cleaned[i].path, cleaned[j].owner, cleaned[j].path))
		}
	}
	return errs
}

func cleanWriteScope(scope string) (string, error) {
	trimmed := strings.TrimSpace(scope)
	if trimmed == "" {
		return "", fmt.Errorf("write scope is empty")
	}
	slash := strings.ReplaceAll(trimmed, "\\", "/")
	if strings.HasPrefix(slash, "/") || strings.Contains(slash, "..") {
		return "", fmt.Errorf("write scope %s is unbounded", scope)
	}
	cleaned := path.Clean(slash)
	if cleaned == "." || cleaned == "/" || strings.HasPrefix(cleaned, "../") || cleaned == ".." {
		return "", fmt.Errorf("write scope %s is unbounded", scope)
	}
	return cleaned, nil
}

func pathsOverlap(left, right string) bool {
	return left == right || strings.HasPrefix(left, right+"/") || strings.HasPrefix(right, left+"/")
}

func joinErrors(errs []error) error {
	var kept []error
	for _, err := range errs {
		if err != nil {
			kept = append(kept, err)
		}
	}
	switch len(kept) {
	case 0:
		return nil
	case 1:
		return kept[0]
	default:
		parts := make([]string, len(kept))
		for i, err := range kept {
			parts[i] = err.Error()
		}
		return fmt.Errorf("%s", strings.Join(parts, "; "))
	}
}
