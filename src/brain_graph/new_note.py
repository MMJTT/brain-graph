"""Create new wiki notes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from brain_graph.paths import note_path_for_type
from brain_graph.templates import render_template


@dataclass(slots=True)
class NewNoteCommand:
    note_type: str
    title: str
    note_id: str
    force: bool = False


def create_note(project_root: Path, command: NewNoteCommand) -> Path:
    target = note_path_for_type(project_root, command.note_type, command.title)

    if target.exists() and not command.force:
        raise FileExistsError(f"{target} already exists")

    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_template(
        project_root,
        command.note_type,
        command.title,
        command.note_id,
        date.today().isoformat(),
    )
    target.write_text(content, encoding="utf-8")
    return target
