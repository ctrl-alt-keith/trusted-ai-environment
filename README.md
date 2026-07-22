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

`bundle.json` describes the point-in-time package, including who created it,
why it exists, its trust profile, expected file names, and record counts.
Sources carry provenance and trust-boundary metadata. Items carry source-native
evidence metadata, time, actors, content references, transforms, and
sensitivity. Chunks are the primary arc input, so each chunk includes enough
title, time, location, chunker, hash, and sensitivity metadata for downstream
workers to consume it without constant joins.

All bundle `date-time` fields must include an explicit timezone offset. The
checked-in examples use RFC3339 UTC timestamps ending in `Z`, and naive values
such as `2026-01-15T12:00:00` fail validation.

Relations are source-observed or synthetic-observed links between existing
sources, items, or chunks. Findings and synthesis reports are outputs, not
evidence, and are not stored in the evidence bundle contract. Future findings
should cite chunks.

`checksums.sha256` is part of the contract, not a convenience artifact. It must
contain exactly one `<sha256>  <filename>` line for each bundle file except
itself, with no duplicate or unexpected filenames.

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
- `docs/product-boundary.md` defines the current Stage 1 product boundary.
- `schemas/` contains the hardened Stage 1 JSON Schemas.
- `examples/fake-corpus/bundle/` contains deterministic synthetic evidence.
- `src/trusted_ai_environment/` contains local generation, validation,
  checksum, and synthesis-stub commands.
- `tests/` contains dependency-free unit tests.
