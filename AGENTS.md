# AGENTS.md

Repository-local guidance for `trusted-ai-environment`.

Use `ai-workflow-playbook` as the shared workflow baseline. This file is the
repo-local execution layer for `trusted-ai-environment`. Repo-local rules take
precedence only for repository-specific behavior.

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

## Startup And Interaction Mode

- Start with `ai-workflow-playbook/docs/start-here.md` before repository or
  software work.
- Before acting, select the interaction mode from
  `ai-workflow-playbook/docs/repo-readiness.md`: implementation, review/audit,
  or orchestration/prompt-authoring.
- Implementation agents make explicit repo changes and carry them through
  validation, commit, push, and PR delivery.
- Review/audit agents inspect and report findings without mutating the repo.
- Orchestration/prompt-authoring agents produce complete, self-contained
  handoffs or prompts unless explicitly asked to implement.

## File Placement

- Put source code under `src/trusted_ai_environment/`.
- Put tests under `tests/`.
- Put repository documentation under `docs/`.
- Put JSON Schemas under `schemas/`.
- Put deterministic synthetic examples under `examples/fake-corpus/`.
- Do not commit real overlays, configs, inputs, reports, secrets, or generated
  outputs derived from real data.

## Local Execution

- Run commands from this repository working directory by default.
- Keep temporary workflow state repo-local, for example `.worktrees/` or
  gitignored build output.
- Use direct command execution for ordinary repo commands such as `git ...`,
  `gh ...`, `make ...`, `python ...`, and repo-local scripts or tools.
- Before using `zsh`, `bash`, `sh`, `zsh -lc`, `bash -lc`, `sh -c`, aliases, or
  equivalent wrapper shells, check whether the command has a direct form and
  use that direct form when it does.
- Use shell wrappers only when shell syntax is genuinely required, such as
  pipelines, redirection, glob expansion, command chaining, scoped environment
  assignment, compound commands, or shell builtins.

## Validation

- Use `make check` as the canonical local validation entrypoint.
- Run `make check` before opening or updating a pull request.
- `make check` creates or refreshes the synthetic evidence bundle, runs
  dependency-free syntax checks, runs unit tests, validates schemas, JSONL,
  references, checksums, and public-safety scans, and produces a deterministic
  synthesis stub without an LLM.
- Keep validation deterministic and fake-data-only. Do not require real
  provider access, credentials, real work data, or model access for normal PR
  validation.
- Do not substitute underlying tools for normal readiness reporting.

## Branches And Pull Requests

- Branch from current `origin/main`.
- Use focused, purpose-based names such as `docs/<short-name>`,
  `chore/<short-name>`, or `fix/<short-name>`.
- Keep changes small, scoped, and limited to this repository.
- Open pull requests against `main`.
- Open PRs ready for review when validation passes and no known blocking work
  remains.
- Include a clear summary and validation notes.

## Scope Guardrails

Do not add LKE provisioning, model serving, real adapters, embeddings, vector
storage, chatbot UI, persistent knowledge bases, autonomous actions, or
work-specific configuration in this repository unless the repository purpose is
explicitly changed.
