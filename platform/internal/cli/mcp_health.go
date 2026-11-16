package cli

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"
)

const mcpHealthTimeout = 8 * time.Second

type mcpHealthResult struct {
	ID     string
	Result string
	Detail string
}

func mcpHealthClient() *http.Client {
	return &http.Client{
		Timeout: mcpHealthTimeout,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 3 {
				return errors.New("stopped after 3 redirects")
			}
			if req.URL != nil && req.URL.User != nil {
				return errors.New("redirect included credentials")
			}
			return nil
		},
	}
}

func checkMCPHealth(ctx context.Context, items []mcpIntegration, client *http.Client) []mcpHealthResult {
	results := make([]mcpHealthResult, len(items))
	var wg sync.WaitGroup
	sem := make(chan struct{}, 6)
	for i, item := range items {
		wg.Add(1)
		go func(i int, item mcpIntegration) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()
			results[i] = probeMCP(ctx, client, item)
		}(i, item)
	}
	wg.Wait()
	return results
}

func probeMCP(ctx context.Context, client *http.Client, item mcpIntegration) mcpHealthResult {
	endpoint := strings.TrimSpace(item.Endpoint)
	if endpoint == "" || item.Transport == "none" || item.Status == "planned" {
		detail := "no remote endpoint"
		if item.Transport == "stdio" {
			detail = "local server is started by the host"
		}
		if item.Status == "planned" || item.Transport == "none" {
			detail = "no server is published"
		}
		return mcpHealthResult{ID: item.ID, Result: "skipped", Detail: detail}
	}
	parsed, err := url.Parse(endpoint)
	if err != nil || parsed.Host == "" || (parsed.Scheme != "http" && parsed.Scheme != "https") {
		return mcpHealthResult{ID: item.ID, Result: "skipped", Detail: "endpoint is not an http URL"}
	}
	if parsed.User != nil {
		return mcpHealthResult{ID: item.ID, Result: "skipped", Detail: "endpoint must not include credentials"}
	}
	if err := rejectPrivateHost(parsed.Hostname()); err != nil {
		return mcpHealthResult{ID: item.ID, Result: "skipped", Detail: err.Error()}
	}
	if client == nil {
		client = mcpHealthClient()
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return mcpHealthResult{ID: item.ID, Result: "unreachable", Detail: "request was not sent"}
	}
	req.Header.Set("Accept", "application/json, text/event-stream")
	resp, err := client.Do(req)
	if err != nil {
		return mcpHealthResult{ID: item.ID, Result: "unreachable", Detail: probeFailure(err)}
	}
	defer resp.Body.Close()
	_, _ = io.Copy(io.Discard, io.LimitReader(resp.Body, 1024))
	switch resp.StatusCode {
	case http.StatusUnauthorized, http.StatusForbidden:
		return mcpHealthResult{
			ID:     item.ID,
			Result: "auth-required",
			Detail: fmt.Sprintf("HTTP %d; server answered and sign-in is required", resp.StatusCode),
		}
	default:
		return mcpHealthResult{
			ID:     item.ID,
			Result: "reachable",
			Detail: fmt.Sprintf("HTTP %d", resp.StatusCode),
		}
	}
}

func rejectPrivateHost(host string) error {
	ip := net.ParseIP(host)
	if ip == nil {
		return nil
	}
	if ip.IsLoopback() {
		return nil
	}
	if !ip.IsGlobalUnicast() || ip.IsPrivate() {
		return errors.New("private addresses are not probed")
	}
	return nil
}

func probeFailure(err error) string {
	if errors.Is(err, context.DeadlineExceeded) {
		return "timed out"
	}
	var dnsErr *net.DNSError
	if errors.As(err, &dnsErr) {
		return "name not resolved"
	}
	return "connection failed"
}

func writeMCPHealth(w io.Writer, results []mcpHealthResult) {
	const detailWidth = 56
	idWidth := len("Integration")
	resultWidth := len("Result")
	for _, result := range results {
		if len(result.ID) > idWidth {
			idWidth = len(result.ID)
		}
		if len(result.Result) > resultWidth {
			resultWidth = len(result.Result)
		}
	}
	counts := map[string]int{}
	for _, result := range results {
		counts[result.Result]++
	}
	fmt.Fprintf(w, "%d integrations\n", len(results))
	fmt.Fprintln(w, "Unauthenticated reachability check. No credentials are sent, and catalog installed stays false.")
	fmt.Fprintf(w, "reachable %d, auth-required %d, unreachable %d, skipped %d\n\n",
		counts["reachable"], counts["auth-required"], counts["unreachable"], counts["skipped"])
	rule := func(left, mid, right string) {
		fmt.Fprintf(w, "%s%s%s%s%s%s%s\n",
			left,
			strings.Repeat("─", idWidth+2),
			mid,
			strings.Repeat("─", resultWidth+2),
			mid,
			strings.Repeat("─", detailWidth+2),
			right,
		)
	}
	rule("┌", "┬", "┐")
	fmt.Fprintf(w, "│ %-*s │ %-*s │ %-*s │\n", idWidth, "Integration", resultWidth, "Result", detailWidth, "Detail")
	rule("├", "┼", "┤")
	for i, result := range results {
		detail := wrapText(oneLine(result.Detail), detailWidth)
		if len(detail) == 0 {
			detail = []string{""}
		}
		for line, text := range detail {
			id, status := "", ""
			if line == 0 {
				id = result.ID
				status = result.Result
			}
			fmt.Fprintf(w, "│ %-*s │ %-*s │ %-*s │\n", idWidth, id, resultWidth, status, detailWidth, text)
		}
		if i < len(results)-1 {
			rule("├", "┼", "┤")
		}
	}
	rule("└", "┴", "┘")
}
