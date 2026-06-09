# Evidence Bundle Contract

The Stage 1 evidence bundle is a local directory with required files:

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

## Conceptual Model

```text
source -> item -> chunk
```

- A source is an origin record for synthetic text.
- An item is a normalized evidence record derived from one source.
- A chunk is a smaller text span derived from one item.
- A relation connects existing sources, items, or chunks.

Findings, arc findings, and synthesis reports are outputs. They are not
evidence bundle records in this MVP.

## Required Integrity Rules

- Every bundle file must exist.
- `bundle.json` must be valid JSON and match `schemas/bundle.schema.json`.
- Every JSONL row must parse as a JSON object and match its schema.
- Every `item.source_id` must exist in `sources.jsonl`.
- Every `chunk.item_id` must exist in `items.jsonl`.
- Every `chunk.source_id` must exist in `sources.jsonl`.
- Every relation endpoint must exist when its endpoint type is `source`,
  `item`, or `chunk`.
- `checksums.sha256` must match the current bytes of every bundle file except
  itself.

## Supported Item Kinds

- `document`
- `event`
- `issue`
- `change`
- `incident`
- `postmortem`
- `aggregate`
- `other`

## Format Notes

`relations.jsonl` may be empty, but the file and schema must exist. The fake
bundle includes safe synthetic relations so reference checks are exercised.

