package main

import (
	"os"

	"engineering-intelligence/platform/internal/cli"
)

func main() {
	os.Exit(cli.Main(os.Args[1:], os.Stdout, os.Stderr, os.Getenv))
}
