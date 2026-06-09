# AGENTS.md

Repository-local guidance for `trusted-ai-environment`.

## Purpose

This is a public-safe prototype repository for a local evidence-processing
pattern:

```text
text source -> item -> chunk -> arc finding -> synthesis report
```

Stage 1 proves the evidence bundle contract with fake data only.

## Public-Safety Boundary

- Commit only generic code, examples, schemas, fake data, and documentation.
- Do not commit employer data, internal URLs, real logs, real tickets, real
  incident data, real service names, proprietary documentation, or generated
  summaries derived from work data.
- Real overlays, configs, secrets, reports, and generated outputs from real data
  must live outside this public repository.

## Workflow

- Follow the workspace playbook at
  `ai-workflow-playbook/docs/start-here.md`.
- Keep changes small and reviewable.
- Use `make check` as the canonical local validation command.
- Open ready-for-review pull requests when implementation work is complete.

## Scope Guardrails

Do not add LKE provisioning, model serving, real adapters, embeddings, vector
storage, chatbot UI, persistent knowledge bases, autonomous actions, or
work-specific configuration in this repository unless the repository purpose is
explicitly changed.

