.PHONY: help check fake-bundle validate-bundle synthesize-stub test lint

PYTHON ?= python3
BUNDLE_DIR ?= examples/fake-corpus/bundle
REPORT ?= build/synthesis-stub.md

help: ## List available targets.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

fake-bundle: ## Create or refresh the synthetic evidence bundle.
	PYTHONPATH=src $(PYTHON) -m trusted_ai_environment.fake_bundle --bundle-dir $(BUNDLE_DIR)

validate-bundle: ## Validate schemas, JSONL, references, checksums, and public-safety scans.
	PYTHONPATH=src $(PYTHON) -m trusted_ai_environment.bundle_validate $(BUNDLE_DIR)

synthesize-stub: ## Produce a deterministic fake synthesis report without an LLM.
	PYTHONPATH=src $(PYTHON) -m trusted_ai_environment.synthesize_stub $(BUNDLE_DIR) --output $(REPORT)

lint: ## Run dependency-free syntax checks.
	$(PYTHON) -m compileall -q src tests

test: ## Run unit tests.
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

check: fake-bundle lint test validate-bundle synthesize-stub ## Run canonical local validation.
