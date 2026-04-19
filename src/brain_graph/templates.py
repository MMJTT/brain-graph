"""Template rendering for Brain Graph notes."""

from __future__ import annotations

from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.models import TEMPLATE_FIELDS_BY_NOTE_TYPE


def _template_path(project_root: Path, note_type: str) -> Path:
    return Path(project_root) / "templates" / f"{note_type}.md"


def _base_payload(note_type: str, title: str, note_id: str, created: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": note_id,
        "title": title,
        "node_type": note_type,
        "status": "seed",
        "tags": [],
        "created": created,
        "updated": created,
        "source_refs": [],
        "related": [],
    }

    for field in TEMPLATE_FIELDS_BY_NOTE_TYPE[note_type]:
        payload.setdefault(field, [])

    return payload


def render_template(project_root: Path, note_type: str, title: str, note_id: str, created: str) -> str:
    payload = _base_payload(note_type, title, note_id, created)
    body = _template_path(project_root, note_type).read_text(encoding="utf-8")
    return f"{dump_frontmatter(payload)}\n\n{body.rstrip()}\n"
