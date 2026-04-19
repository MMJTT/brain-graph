"""Ingest raw notes into the append-only raw vault."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.paths import raw_path_for_kind


@dataclass(slots=True)
class IngestRawCommand:
    kind: str
    slug: str
    title: str
    source_url: str
    summary: str | None = None


def ingest_raw_entry(
    project_root: Path, command: IngestRawCommand, date_text: str
) -> Path:
    target = raw_path_for_kind(project_root, command.kind, command.slug, date_text)

    if target.exists():
        raise FileExistsError(f"{target} already exists; raw ingestion is append-only")

    target.parent.mkdir(parents=True, exist_ok=True)

    frontmatter: dict[str, object] = {
        "kind": command.kind,
        "slug": command.slug,
        "title": command.title,
        "source_url": command.source_url,
    }
    if command.summary is not None:
        frontmatter["summary"] = command.summary

    body_lines = [
        dump_frontmatter(frontmatter),
        "",
        f"# {command.title}",
    ]
    if command.summary:
        body_lines.extend(["", command.summary])
    body_lines.extend(["", f"Source: {command.source_url}", ""])

    target.write_text("\n".join(body_lines), encoding="utf-8")
    return target
