// Package telemetry writes structured logs and redacts credential material.
// It does not export OpenTelemetry.
package telemetry

import (
	"encoding/json"
	"io"
	"regexp"
	"sort"
	"time"
)

var secretPatterns = []*regexp.Regexp{
	regexp.MustCompile(`-----BEGIN [A-Z ]*PRIVATE KEY-----`),
	regexp.MustCompile(`\bAKIA[0-9A-Z]{16}\b`),
	regexp.MustCompile(`\bghp_[A-Za-z0-9]{20,}\b`),
	regexp.MustCompile(`\bgithub_pat_[A-Za-z0-9_]{20,}\b`),
	regexp.MustCompile(`(?i)\bbearer\s+[A-Za-z0-9\-._~+/]+=*`),
	regexp.MustCompile(`\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}`),
}

// Redact replaces detected credential material with [REDACTED].
func Redact(value string) string {
	for _, pattern := range secretPatterns {
		value = pattern.ReplaceAllString(value, "[REDACTED]")
	}
	return value
}

// Logger writes one JSON object per event.
type Logger struct {
	Out io.Writer
}

// Info writes a redacted event. Export to a collector is not configured.
func (l Logger) Info(message string, fields map[string]string) error {
	payload := map[string]string{
		"time":    time.Now().UTC().Format(time.RFC3339),
		"message": Redact(message),
	}
	keys := make([]string, 0, len(fields))
	for key := range fields {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		payload[key] = Redact(fields[key])
	}
	encoded, err := json.Marshal(payload)
	if err != nil {
		return err
	}
	_, err = l.Out.Write(append(encoded, '\n'))
	return err
}
