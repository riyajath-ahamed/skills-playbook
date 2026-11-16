// Package evidence records paths and notes for a run.
// Notes are redacted before they are stored. The store is in memory.
package evidence

import "engineering-intelligence/platform/internal/telemetry"

// Item is one piece of evidence.
type Item struct {
	Path string
	Kind string
	Note string
}

// Store collects items for the lifetime of a process.
type Store struct {
	Items []Item
}

// Add redacts the note and keeps the item.
func (s *Store) Add(item Item) {
	item.Note = telemetry.Redact(item.Note)
	s.Items = append(s.Items, item)
}
