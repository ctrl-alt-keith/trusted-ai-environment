"""Deterministic synthesis stub for the fake evidence bundle."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

from .bundle_validate import load_json, load_jsonl, validate_bundle


def rows_by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def build_report(bundle_dir: Path) -> str:
    errors = validate_bundle(bundle_dir)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"bundle is not valid:\n{joined}")

    bundle = load_json(bundle_dir / "bundle.json")
    sources = load_jsonl(bundle_dir / "sources.jsonl")
    items = load_jsonl(bundle_dir / "items.jsonl")
    chunks = load_jsonl(bundle_dir / "chunks.jsonl")
    relations = load_jsonl(bundle_dir / "relations.jsonl")
    items_index = rows_by_id(items, "item_id")

    kind_counts = Counter(item["kind"] for item in items)
    relation_counts = Counter(relation["relation_type"] for relation in relations)

    lines = [
        "# Synthetic Synthesis Report",
        "",
        "This deterministic report is generated from fake evidence only. It does",
        "not call an LLM or external service.",
        "",
        f"Bundle: {bundle['title']} (`{bundle['bundle_id']}`)",
        f"Sources: {len(sources)}",
        f"Items: {len(items)}",
        f"Chunks: {len(chunks)}",
        f"Relations: {len(relations)}",
        "",
        "## Item Mix",
        "",
    ]

    for kind, count in sorted(kind_counts.items()):
        lines.append(f"- {kind}: {count}")

    lines.extend(["", "## Stub Arc Findings", ""])
    if relation_counts:
        for relation_type, count in sorted(relation_counts.items()):
            lines.append(f"- {relation_type}: {count} synthetic relation(s)")
    else:
        lines.append("- No relations were present.")

    lines.extend(["", "## Evidence Highlights", ""])
    for relation in relations:
        from_item = items_index.get(relation["from_id"])
        to_item = items_index.get(relation["to_id"])
        if from_item and to_item:
            lines.append(
                f"- `{relation['relation_type']}`: {from_item['title']} -> {to_item['title']}"
            )

    lines.extend(
        [
            "",
            "## Boundary Note",
            "",
            "This report is an output, not bundle evidence. A report produced from",
            "real data would be work-derived and must remain inside the approved",
            "boundary for that data.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a fake synthesis report.")
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("build/synthesis-stub.md"))
    args = parser.parse_args(argv)

    try:
        report = build_report(args.bundle_dir)
    except ValueError as exc:
        print(f"synthesis stub failed: {exc}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"wrote synthesis stub report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

