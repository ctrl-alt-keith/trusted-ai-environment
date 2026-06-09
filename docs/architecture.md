# Architecture

Stage 1 implements the smallest useful local proof of an evidence-processing
pattern:

```text
text source -> item -> chunk -> arc finding -> synthesis report
```

Only the evidence bundle is part of the durable contract. Arc findings and
synthesis reports are outputs produced from evidence. They are intentionally not
stored in the bundle in this MVP.

## Components

- `fake_bundle.py` creates deterministic synthetic evidence.
- `bundle_validate.py` validates required files, schemas, JSONL parsing,
  references, checksums, and public-safety guardrails.
- `checksum.py` computes and verifies bundle file hashes.
- `synthesize_stub.py` produces a deterministic fake report without calling an
  LLM or external service.

## Data Flow

1. Synthetic text sources are represented in `sources.jsonl`.
2. Source-derived records are represented in `items.jsonl`.
3. Item text spans are represented in `chunks.jsonl`.
4. Optional evidence relationships are represented in `relations.jsonl`.
5. A local synthesis stub reads the bundle and emits a generated report outside
   the bundle.

## Non-Goals

This repository does not implement LKE provisioning, model serving, real
adapters, enterprise wiki access, log store access, issue tracker access,
version-control access, embeddings, vector databases, chatbot UI, persistent
knowledge bases, autonomous actions, work-specific config, or secret handling
beyond documentation placeholders.
