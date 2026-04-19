"""Export Brain Graph notes to JSON and Mermaid files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from brain_graph.frontmatter import load_frontmatter

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

FIELD_EDGE_LABELS = {
    "concept_refs": "mentions",
    "method_refs": "uses",
    "gap_refs": "raises_gap",
    "paper_refs": "supports",
    "introduced_by": "introduces",
    "raised_by": "raises_gap",
    "related": "related_to",
    "source_refs": "supports_reference",
}


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    node_type: str
    status: str
    path: Path
    body: str
    data: dict[str, object]


def export_graph_files(project_root: Path) -> tuple[Path, Path]:
    root = Path(project_root)
    notes = _load_notes(root)
    _validate_unique_titles(notes)
    nodes = [
        {
            "id": note.id,
            "title": note.title,
            "node_type": note.node_type,
            "status": note.status,
        }
        for note in notes
    ]
    edges = _build_edges(notes)

    exports_dir = root / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    json_path = exports_dir / "brain_graph.json"
    mermaid_path = exports_dir / "brain_graph.mmd"

    json_path.write_text(
        json.dumps({"nodes": nodes, "edges": edges}, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    mermaid_path.write_text(_render_mermaid(notes, edges), encoding="utf-8")

    return json_path, mermaid_path


def _load_notes(root: Path) -> list[Note]:
    notes: list[Note] = []
    for path in sorted(root.glob("wiki/*/*.md")):
        data, body = load_frontmatter(path.read_text(encoding="utf-8"))
        note_id = data.get("id")
        title = data.get("title")
        node_type = data.get("node_type")
        status = data.get("status")
        missing_fields = [
            field
            for field, value in (
                ("id", note_id),
                ("title", title),
                ("node_type", node_type),
                ("status", status),
            )
            if not isinstance(value, str)
        ]
        if missing_fields:
            raise ValueError(
                f"{path}: invalid or missing required string fields: "
                f"{', '.join(missing_fields)}"
            )
        notes.append(
            Note(
                id=note_id,
                title=title,
                node_type=node_type,
                status=status,
                path=path,
                body=body,
                data=data,
            )
        )
    return notes


def _validate_unique_titles(notes: list[Note]) -> None:
    title_to_path: dict[str, Path] = {}
    for note in notes:
        existing_path = title_to_path.get(note.title)
        if existing_path is not None:
            raise ValueError(
                f"duplicate note title: {note.title} ({existing_path} and {note.path})"
            )
        title_to_path[note.title] = note.path


def _build_edges(notes: list[Note]) -> list[dict[str, str]]:
    notes_by_id = {note.id: note for note in notes}
    notes_by_title = {note.title: note for note in notes}
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for note in notes:
        for field, label in FIELD_EDGE_LABELS.items():
            for reference in _as_list(note.data.get(field)):
                target = _resolve_reference(reference, notes_by_id, notes_by_title)
                if target is None:
                    continue
                _append_edge(edges, seen, note.id, target.id, label)

        for match in WIKILINK_RE.finditer(note.body):
            reference = _normalize_reference(match.group(1))
            target = _resolve_reference(reference, notes_by_id, notes_by_title)
            if target is None:
                continue
            _append_edge(edges, seen, note.id, target.id, "body_link")

    return edges


def _render_mermaid(notes: list[Note], edges: list[dict[str, str]]) -> str:
    aliases = {note.id: f"n{index}" for index, note in enumerate(notes)}
    lines = ["graph LR"]
    for note in notes:
        alias = aliases[note.id]
        lines.append(f'    {alias}["{_escape_mermaid_label(note.title)}"]')
    for edge in edges:
        source = aliases.get(edge["source"])
        target = aliases.get(edge["target"])
        if source is None or target is None:
            continue
        lines.append(f"    {source} -->|{edge['type']}| {target}")
    return "\n".join(lines) + "\n"


def _append_edge(
    edges: list[dict[str, str]],
    seen: set[tuple[str, str, str]],
    source: str,
    target: str,
    edge_type: str,
) -> None:
    key = (source, target, edge_type)
    if key in seen:
        return
    seen.add(key)
    edges.append({"source": source, "target": target, "type": edge_type})


def _resolve_reference(
    value: object,
    notes_by_id: dict[str, Note],
    notes_by_title: dict[str, Note],
) -> Note | None:
    if value is None:
        return None
    reference = _normalize_reference(_stringify(value))
    if not reference:
        return None
    return notes_by_id.get(reference) or notes_by_title.get(reference)


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    if value == "[]":
        return []
    return [value]


def _normalize_reference(value: str) -> str:
    reference = value.strip()
    if "|" in reference:
        reference = reference.split("|", 1)[0].strip()
    if "#" in reference:
        reference = reference.split("#", 1)[0].strip()
    return reference


def _stringify(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(value)


def _escape_mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
