.PHONY: validate test build index doctor mcp-config evals

validate:
	bash scripts/validate-skills.sh
	bash scripts/validate-catalog.sh
	bash scripts/check-links.sh
	bash scripts/validate-evals.sh

test:
	bash scripts/test-all.sh

build:
	cd platform && go build -o bin/ei ./cmd/ei

index:
	bash scripts/build-index.sh

doctor:
	bash scripts/setup.sh

mcp-config:
	.venv/bin/python scripts/generate_cursor_mcp.py

evals:
	bash scripts/run-skill-evals.sh self-test
