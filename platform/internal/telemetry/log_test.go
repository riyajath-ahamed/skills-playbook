package telemetry

import (
	"bytes"
	"strings"
	"testing"
)

func TestRedactAndLog(t *testing.T) {
	token := "ghp_" + strings.Repeat("b", 36)
	var buf bytes.Buffer
	logger := Logger{Out: &buf}
	if err := logger.Info("failed with "+token, map[string]string{"header": "Bearer " + token}); err != nil {
		t.Fatal(err)
	}
	output := buf.String()
	if strings.Contains(output, token) || !strings.Contains(output, "[REDACTED]") {
		t.Fatalf("log = %s", output)
	}
}
