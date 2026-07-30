"""Create a deterministic public-safe fake evidence bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .checksum import byte_len, sha256_text, write_checksums

BUNDLE_ID = "fake-corpus"
BUNDLE_VERSION = "0.1.0"
CREATED_AT = "2026-01-15T12:00:00Z"
GENERATOR_NAME = "trusted-ai-environment.fake_bundle"
SYSTEM_NAME = "synthetic-fake-corpus"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def synthetic_boundary() -> dict[str, object]:
    return {
        "level": "synthetic-public",
        "labels": ["synthetic", "public-safe"],
        "exportable": True,
        "retention": "keep-with-repository",
        "handling": "synthetic examples only; do not mix with real data",
    }


def synthetic_transform(name: str) -> dict[str, object]:
    return {
        "name": name,
        "version": BUNDLE_VERSION,
        "description": "Deterministic synthetic construction for local validation.",
    }


def fake_sources() -> list[dict[str, object]]:
    source_specs = [
        ("src-runbook-page", "document", "Synthetic Runbook Page", "docs/runbook-page"),
        ("src-recovery-guide", "document", "Synthetic Recovery Guide", "docs/recovery-guide"),
        ("src-operator-note", "document", "Synthetic Operator Note", "docs/operator-note"),
        ("src-event-feed", "event_stream", "Synthetic Event Feed", "events/feed"),
        ("src-work-queue", "issue_tracker", "Synthetic Work Queue", "issues/work-queue"),
        ("src-change-notes", "change_log", "Synthetic Change Notes", "changes/notes"),
    ]
    return [
        {
            "source_id": source_id,
            "source_type": source_type,
            "system": SYSTEM_NAME,
            "title": title,
            "origin_ref": f"synthetic://fake-corpus/{origin}",
            "retrieved_at": CREATED_AT,
            "retrieval_method": "deterministic synthetic generator",
            "retrieval_scope": "stage-1 fake corpus only",
            "adapter": {"name": "fake-corpus-adapter", "version": BUNDLE_VERSION},
            "trust_boundary": synthetic_boundary(),
            "metadata": {"public_safety": "synthetic-only", "fixture": True},
        }
        for source_id, source_type, title, origin in source_specs
    ]


def make_item(
    item_id: str,
    source_id: str,
    kind: str,
    title: str,
    body: str,
    locator: str,
    observed_at: str = CREATED_AT,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "item_id": item_id,
        "source_id": source_id,
        "kind": kind,
        "title": title,
        "body": body,
        "source_ref": {"system": SYSTEM_NAME, "locator": locator},
        "time": {
            "created_at": observed_at,
            "updated_at": observed_at,
            "observed_at": observed_at,
            "time_range": None,
        },
        "actors": {},
        "content_ref": {
            "path": locator,
            "mime_type": "text/plain",
            "sha256": sha256_text(body),
            "size_bytes": byte_len(body),
        },
        "transforms": [synthetic_transform("fake-item-construction")],
        "sensitivity": synthetic_boundary(),
        "metadata": metadata or {},
    }


def fake_items() -> list[dict[str, object]]:
    return [
        make_item(
            "item-stale-runbook",
            "src-runbook-page",
            "document",
            "Runbook: Acorn Queue Restart",
            (
                "The Acorn Queue runbook says to restart the blue worker first, "
                "then clear the backlog counter. The page still mentions the old "
                "three-minute timer and has not been reviewed since the fictional "
                "Falcon Release rehearsal."
            ),
            "synthetic/docs/runbook-page.md",
            metadata={"scenario": "stale-runbook"},
        ),
        make_item(
            "item-overlap-guide",
            "src-recovery-guide",
            "document",
            "Guide: Acorn Queue Recovery",
            (
                "The Acorn Queue recovery guide also tells operators to restart "
                "the blue worker before clearing the backlog counter. It adds a "
                "new five-minute timer, creating overlap with the older runbook."
            ),
            "synthetic/docs/recovery-guide.md",
            metadata={"scenario": "duplicate-overlap"},
        ),
        make_item(
            "item-contradictory-note",
            "src-operator-note",
            "document",
            "Note: Acorn Queue Safe Mode",
            (
                "The safe-mode note says never restart the blue worker while the "
                "backlog counter is above ten. It instructs operators to pause "
                "new intake first, contradicting the restart-first guidance."
            ),
            "synthetic/docs/operator-note.md",
            metadata={"scenario": "contradiction"},
        ),
        make_item(
            "item-log-like-event",
            "src-event-feed",
            "event",
            "Event: Synthetic Backlog Spike",
            (
                "2026-01-15T11:44:02Z component=acorn-worker level=warning "
                "message='backlog counter reached 12 during rehearsal data run'"
            ),
            "synthetic/events/feed#evt-acorn-0001",
            observed_at="2026-01-15T11:44:02Z",
            metadata={"scenario": "log-like-event", "synthetic": True},
        ),
        make_item(
            "item-issue-1001",
            "src-work-queue",
            "issue",
            "Issue 1001: Clarify Acorn Queue restart sequence",
            (
                "A fictional operator noticed the restart sequence differs between "
                "the runbook and the safe-mode note. The issue asks for one "
                "reviewed sequence and updated examples."
            ),
            "synthetic/issues/issue-1001",
            metadata={"scenario": "issue-change-relationship"},
        ),
        make_item(
            "item-change-2001",
            "src-change-notes",
            "change",
            "Change 2001: Draft unified Acorn Queue guidance",
            (
                "A fictional change note proposes replacing restart-first wording "
                "with pause-intake-first wording and linking both synthetic docs "
                "to a single reviewed procedure."
            ),
            "synthetic/changes/change-2001",
            metadata={"scenario": "issue-change-relationship"},
        ),
    ]


def make_chunk(item: dict[str, Any], ordinal: int = 0) -> dict[str, object]:
    text = str(item["body"])
    return {
        "chunk_id": f"chunk-{str(item['item_id']).removeprefix('item-')}-{ordinal}",
        "bundle_id": BUNDLE_ID,
        "source_id": item["source_id"],
        "item_id": item["item_id"],
        "ordinal": ordinal,
        "chunk_type": "item-body",
        "title": item["title"],
        "text": text,
        "location": {
            "type": "item-body-span",
            "source_ref": item["source_ref"],
            "char_start": 0,
            "char_end": len(text),
        },
        "time": {
            "observed_at": item["time"]["observed_at"],
            "time_range": item["time"]["time_range"],
        },
        "chunker": {
            "name": "single-item-span",
            "version": BUNDLE_VERSION,
            "config": {"max_items_per_chunk": 1},
        },
        "token_estimate": len(text.split()),
        "chunk_sha256": sha256_text(text),
        "sensitivity": item["sensitivity"],
        "metadata": {"strategy": "single-item-span", **dict(item["metadata"])},
    }


def endpoint(endpoint_type: str, endpoint_id: str) -> dict[str, str]:
    return {"type": endpoint_type, "id": endpoint_id}


def fake_relations() -> list[dict[str, object]]:
    return [
        {
            "relation_id": "rel-runbook-overlaps-guide",
            "from": endpoint("item", "item-stale-runbook"),
            "to": endpoint("item", "item-overlap-guide"),
            "relation_type": "overlaps",
            "observed_in": endpoint("item", "item-overlap-guide"),
            "source_observed": True,
            "confidence": "synthetic",
            "metadata": {"reason": "both describe restart-before-clear sequence"},
        },
        {
            "relation_id": "rel-note-contradicts-runbook",
            "from": endpoint("item", "item-contradictory-note"),
            "to": endpoint("item", "item-stale-runbook"),
            "relation_type": "contradicts",
            "observed_in": endpoint("item", "item-contradictory-note"),
            "source_observed": True,
            "confidence": "synthetic",
            "metadata": {"reason": "restart prohibition conflicts with restart-first guidance"},
        },
        {
            "relation_id": "rel-change-resolves-issue",
            "from": endpoint("item", "item-change-2001"),
            "to": endpoint("item", "item-issue-1001"),
            "relation_type": "resolves",
            "observed_in": endpoint("item", "item-change-2001"),
            "source_observed": True,
            "confidence": "synthetic",
            "metadata": {"reason": "change proposes unified wording requested by issue"},
        },
    ]


def make_bundle_metadata(
    sources: list[dict[str, object]],
    items: list[dict[str, object]],
    chunks: list[dict[str, object]],
    relations: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "schema_version": BUNDLE_VERSION,
        "bundle_id": BUNDLE_ID,
        "created_at": CREATED_AT,
        "created_by": {"name": GENERATOR_NAME, "version": BUNDLE_VERSION},
        "title": "Synthetic Fake Corpus Evidence Bundle",
        "description": "Public-safe bundle for local contract validation.",
        "purpose": "Exercise the Stage 1 source-to-item-to-chunk evidence contract.",
        "trust_profile": {
            "default_level": "synthetic-public",
            "allowed_processing": ["local validation", "deterministic synthesis stub"],
            "external_export_allowed": True,
            "retention": "keep-with-repository",
        },
        "contents": {
            "source_count": len(sources),
            "item_count": len(items),
            "chunk_count": len(chunks),
            "relation_count": len(relations),
        },
        "files": {
            "sources": "sources.jsonl",
            "items": "items.jsonl",
            "chunks": "chunks.jsonl",
            "relations": "relations.jsonl",
            "checksums": "checksums.sha256",
        },
    }


def create_fake_bundle(bundle_dir: Path) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)

    readme = """# Fake Evidence Bundle

This bundle contains synthetic public-safe data only. It exercises the Stage 1
evidence model:

```text
source -> item -> chunk
```

The examples include a stale runbook, overlapping documentation, contradictory
guidance, a log-like event, and a fake issue/change relationship.
"""
    (bundle_dir / "README.md").write_text(readme, encoding="utf-8")

    sources = fake_sources()
    items = fake_items()
    chunks = [make_chunk(item) for item in items]
    relations = fake_relations()

    write_json(bundle_dir / "bundle.json", make_bundle_metadata(sources, items, chunks, relations))
    write_jsonl(bundle_dir / "sources.jsonl", sources)
    write_jsonl(bundle_dir / "items.jsonl", items)
    write_jsonl(bundle_dir / "chunks.jsonl", chunks)
    write_jsonl(bundle_dir / "relations.jsonl", relations)
    write_checksums(bundle_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create the fake evidence bundle.")
    parser.add_argument("--bundle-dir", type=Path, default=Path("examples/fake-corpus/bundle"))
    args = parser.parse_args(argv)
    create_fake_bundle(args.bundle_dir)
    print(f"wrote fake evidence bundle: {args.bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
