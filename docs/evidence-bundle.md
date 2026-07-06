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
- An item is source-native evidence derived from one source.
- A chunk is a self-contained evidence span derived from one item.
- A relation connects existing sources, items, or chunks when the relationship
  is source-observed or synthetic-observed.

Findings, arc findings, and synthesis reports are outputs. They are not
evidence bundle records in this MVP.

## Hardened Stage 1 Records

`bundle.json` is a point-in-time package manifest. It includes schema version,
bundle ID, creation time, generator identity, purpose, trust profile, expected
file names, and row counts.

`sources.jsonl` records source provenance and boundary metadata, including
system, origin reference, retrieval method and scope, adapter identity, trust
boundary, and metadata.

`items.jsonl` records source-native evidence. Each item includes kind, title,
body, source reference, time metadata, actors, content reference, transforms,
sensitivity, and metadata.

`chunks.jsonl` records the primary arc input. Each chunk includes the bundle ID,
source and item IDs, title, text, location, time, chunker identity, token
estimate, chunk hash, sensitivity, and metadata so arc workers can consume
chunks with minimal joins.

`relations.jsonl` uses nested endpoints:

```json
{
  "from": {"type": "item", "id": "item-example"},
  "to": {"type": "chunk", "id": "chunk-example-0"},
  "observed_in": {"type": "item", "id": "item-example"}
}
```

Allowed endpoint types are `source`, `item`, and `chunk`. Allowed confidence
values are `source`, `extracted`, and `synthetic`.

## Required Integrity Rules

- Every bundle file must exist.
- `bundle.json` must be valid JSON and match `schemas/bundle.schema.json`.
- Every JSONL row must parse as a JSON object and match its schema.
- `bundle.contents.*_count` must match actual JSONL row counts.
- `bundle.files.*` must point to the expected bundle files.
- Every `item.source_id` must exist in `sources.jsonl`.
- Every `chunk.item_id` must exist in `items.jsonl`.
- Every `chunk.source_id` must exist in `sources.jsonl`.
- Every `chunk.bundle_id` must match `bundle.bundle_id`.
- Every chunk's `source_id` must match its parent item's `source_id`.
- Every item content hash and byte length must match the item body.
- Every chunk hash and item-body character span must match the chunk text.
- Every item and chunk must include sensitivity metadata.
- Every nested relation endpoint must resolve.
- `checksums.sha256` must match the current bytes of every bundle file except
  itself.
- Bundle files must not contain internal-looking URLs or suspicious
  public-safety markers.

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
