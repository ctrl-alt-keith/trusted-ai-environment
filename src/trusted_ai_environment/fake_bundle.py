"""Create a deterministic public-safe fake evidence bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .checksum import write_checksums

BUNDLE_VERSION = "0.1.0"
CREATED_AT = "2026-01-15T12:00:00Z"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    text = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def make_chunk(item: dict[str, object], ordinal: int = 0) -> dict[str, object]:
    text = str(item["body"])
    return {
        "chunk_id": f"chunk-{str(item['item_id']).removeprefix('item-')}-{ordinal}",
        "source_id": item["source_id"],
        "item_id": item["item_id"],
        "ordinal": ordinal,
        "text": text,
        "char_start": 0,
        "char_end": len(text),
        "metadata": {"strategy": "single-item-span"},
    }


def fake_sources() -> list[dict[str, object]]:
    return [
        {
            "source_id": "src-runbook-page",
            "source_type": "document",
            "title": "Synthetic Runbook Page",
            "origin_ref": "synthetic://fake-corpus/docs/runbook-page",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
        {
            "source_id": "src-recovery-guide",
            "source_type": "document",
            "title": "Synthetic Recovery Guide",
            "origin_ref": "synthetic://fake-corpus/docs/recovery-guide",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
        {
            "source_id": "src-operator-note",
            "source_type": "document",
            "title": "Synthetic Operator Note",
            "origin_ref": "synthetic://fake-corpus/docs/operator-note",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
        {
            "source_id": "src-event-feed",
            "source_type": "event_stream",
            "title": "Synthetic Event Feed",
            "origin_ref": "synthetic://fake-corpus/events/feed",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
        {
            "source_id": "src-work-queue",
            "source_type": "issue_tracker",
            "title": "Synthetic Work Queue",
            "origin_ref": "synthetic://fake-corpus/issues/work-queue",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
        {
            "source_id": "src-change-notes",
            "source_type": "change_log",
            "title": "Synthetic Change Notes",
            "origin_ref": "synthetic://fake-corpus/changes/notes",
            "created_at": CREATED_AT,
            "metadata": {"public_safety": "synthetic-only"},
        },
    ]


def fake_items() -> list[dict[str, object]]:
    return [
        {
            "item_id": "item-stale-runbook",
            "source_id": "src-runbook-page",
            "kind": "document",
            "title": "Runbook: Acorn Queue Restart",
            "body": (
                "The Acorn Queue runbook says to restart the blue worker first, "
                "then clear the backlog counter. The page still mentions the old "
                "three-minute timer and has not been reviewed since the fictional "
                "Falcon Release rehearsal."
            ),
            "created_at": CREATED_AT,
            "metadata": {"scenario": "stale-runbook"},
        },
        {
            "item_id": "item-overlap-guide",
            "source_id": "src-recovery-guide",
            "kind": "document",
            "title": "Guide: Acorn Queue Recovery",
            "body": (
                "The Acorn Queue recovery guide also tells operators to restart "
                "the blue worker before clearing the backlog counter. It adds a "
                "new five-minute timer, creating overlap with the older runbook."
            ),
            "created_at": CREATED_AT,
            "metadata": {"scenario": "duplicate-overlap"},
        },
        {
            "item_id": "item-contradictory-note",
            "source_id": "src-operator-note",
            "kind": "document",
            "title": "Note: Acorn Queue Safe Mode",
            "body": (
                "The safe-mode note says never restart the blue worker while the "
                "backlog counter is above ten. It instructs operators to pause "
                "new intake first, contradicting the restart-first guidance."
            ),
            "created_at": CREATED_AT,
            "metadata": {"scenario": "contradiction"},
        },
        {
            "item_id": "item-log-like-event",
            "source_id": "src-event-feed",
            "kind": "event",
            "title": "Event: Synthetic Backlog Spike",
            "body": (
                "2026-01-15T11:44:02Z component=acorn-worker level=warning "
                "message='backlog counter reached 12 during rehearsal data run'"
            ),
            "created_at": "2026-01-15T11:44:02Z",
            "metadata": {"scenario": "log-like-event", "synthetic": True},
        },
        {
            "item_id": "item-issue-1001",
            "source_id": "src-work-queue",
            "kind": "issue",
            "title": "Issue 1001: Clarify Acorn Queue restart sequence",
            "body": (
                "A fictional operator noticed the restart sequence differs between "
                "the runbook and the safe-mode note. The issue asks for one "
                "reviewed sequence and updated examples."
            ),
            "created_at": CREATED_AT,
            "metadata": {"scenario": "issue-change-relationship"},
        },
        {
            "item_id": "item-change-2001",
            "source_id": "src-change-notes",
            "kind": "change",
            "title": "Change 2001: Draft unified Acorn Queue guidance",
            "body": (
                "A fictional change note proposes replacing restart-first wording "
                "with pause-intake-first wording and linking both synthetic docs "
                "to a single reviewed procedure."
            ),
            "created_at": CREATED_AT,
            "metadata": {"scenario": "issue-change-relationship"},
        },
    ]


def fake_relations() -> list[dict[str, object]]:
    return [
        {
            "relation_id": "rel-runbook-overlaps-guide",
            "relation_type": "overlaps",
            "from_type": "item",
            "from_id": "item-stale-runbook",
            "to_type": "item",
            "to_id": "item-overlap-guide",
            "metadata": {"reason": "both describe restart-before-clear sequence"},
        },
        {
            "relation_id": "rel-note-contradicts-runbook",
            "relation_type": "contradicts",
            "from_type": "item",
            "from_id": "item-contradictory-note",
            "to_type": "item",
            "to_id": "item-stale-runbook",
            "metadata": {"reason": "restart prohibition conflicts with restart-first guidance"},
        },
        {
            "relation_id": "rel-change-resolves-issue",
            "relation_type": "resolves",
            "from_type": "item",
            "from_id": "item-change-2001",
            "to_type": "item",
            "to_id": "item-issue-1001",
            "metadata": {"reason": "change proposes unified wording requested by issue"},
        },
    ]


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

    write_json(
        bundle_dir / "bundle.json",
        {
            "bundle_id": "fake-corpus",
            "schema_version": BUNDLE_VERSION,
            "title": "Synthetic Fake Corpus Evidence Bundle",
            "description": "Public-safe bundle for local contract validation.",
            "created_at": CREATED_AT,
        },
    )
    sources = fake_sources()
    items = fake_items()
    chunks = [make_chunk(item) for item in items]
    relations = fake_relations()
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

