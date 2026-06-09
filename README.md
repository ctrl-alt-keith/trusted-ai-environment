# trusted-ai-environment

Public-safe local prototype for a trusted AI evidence-processing pattern:

```text
text source -> item -> chunk -> arc finding -> synthesis report
```

This repository is intentionally small. Stage 1 proves a local evidence bundle
contract with synthetic data and deterministic validation. It is not a chatbot,
platform, knowledge graph, LKE deployment, adapter suite, vector store, or model
serving project.

## Public-Safe Scope

The repository contains only generic code, schemas, fake data, and
documentation. Do not commit employer data, internal URLs, real logs, real
tickets, real incident data, real service names, proprietary documentation, or
generated summaries derived from real work data.

Real overlays, configs, secrets, inputs, and generated reports from real data
belong outside this public repository and inside the approved boundary for that
data.

## Evidence Bundle

The MVP bundle layout is:

```text
bundle/
  README.md
  bundle.json
  sources.jsonl
  items.jsonl
  chunks.jsonl
  relations.jsonl
  checksums.sha256
```

The conceptual evidence model is:

```text
source -> item -> chunk
```

Findings and synthesis reports are outputs, not evidence, and are not stored in
the evidence bundle contract.

## Local Commands

```sh
make help
make fake-bundle
make validate-bundle
make synthesize-stub
make check
```

`make check` is the canonical local validation command.

## Repository Contents

- `docs/` describes the architecture, bundle contract, and trust boundary.
- `schemas/` contains the MVP JSON Schemas.
- `examples/fake-corpus/bundle/` contains deterministic synthetic evidence.
- `src/trusted_ai_environment/` contains local generation, validation,
  checksum, and synthesis-stub commands.
- `tests/` contains dependency-free unit tests.

