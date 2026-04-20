"""Lint wiki notes for Brain Graph."""

from __future__ import annotations

import re
from pathlib import Path

from brain_graph.frontmatter import load_frontmatter
from brain_graph.models import (
    NOTE_TYPES,
    NOTE_TYPE_BY_WIKI_DIRECTORY,
    WIKI_DIRECTORY_BY_NOTE_TYPE,
)

REQUIRED_FIELDS = (
    "id",
    "title",
    "node_type",
    "status",
    "tags",
    "created",
    "updated",
    "source_refs",
    "related",
)

NON_REFERENCE_LIST_FIELDS = {
    "aliases",
    "authors",
    "raw_refs",
    "limitations",
    "potential_directions",
    "questions",
    "tags",
}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def collect_issues(project_root: Path) -> list[str]:
    root = Path(project_root)
    note_paths = sorted(root.glob("wiki/*/*.md"))

    notes: list[tuple[Path, dict[str, object], str]] = []
    titles: set[str] = set()
    ids: set[str] = set()
    duplicate_titles: set[str] = set()
    duplicate_ids: set[str] = set()

    for path in note_paths:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            continue
        data, body = load_frontmatter(text)
        notes.append((path, data, body))

        title = data.get("title")
        if isinstance(title, str):
            if title in titles:
                duplicate_titles.add(title)
            titles.add(title)

        note_id = data.get("id")
        if isinstance(note_id, str):
            if note_id in ids:
                duplicate_ids.add(note_id)
            ids.add(note_id)

    issues: list[str] = []
    for path, data, body in notes:
        issues.extend(
            _collect_note_issues(path, data, body, titles, ids, duplicate_titles, duplicate_ids)
        )

    return issues


def _collect_note_issues(
    path: Path,
    data: dict[str, object],
    body: str,
    titles: set[str],
    ids: set[str],
    duplicate_titles: set[str],
    duplicate_ids: set[str],
) -> list[str]:
    issues: list[str] = []
    location = path.as_posix()

    for field in REQUIRED_FIELDS:
        if field not in data:
            issues.append(f"{location}: missing required field: {field}")

    node_type = data.get("node_type")
    if node_type is not None and node_type not in NOTE_TYPES:
        issues.append(f"{location}: invalid node_type: {node_type}")
    elif isinstance(node_type, str):
        expected_directory = WIKI_DIRECTORY_BY_NOTE_TYPE[node_type]
        actual_directory = path.parent.name
        if actual_directory != expected_directory:
            issues.append(
                f"{location}: folder mismatch for node_type {node_type}: "
                f"expected wiki/{expected_directory}, found wiki/{actual_directory}"
            )

    expected_node_type = NOTE_TYPE_BY_WIKI_DIRECTORY.get(path.parent.name)
    if expected_node_type is not None and node_type not in (None, expected_node_type):
        issues.append(
            f"{location}: node_type {node_type} does not match folder wiki/{path.parent.name}"
        )

    note_id = data.get("id")
    if isinstance(note_id, str) and note_id in duplicate_ids:
        issues.append(f"{location}: duplicate id: {note_id}")

    title = data.get("title")
    if isinstance(title, str) and title in duplicate_titles:
        issues.append(f"{location}: duplicate title: {title}")

    for match in WIKILINK_RE.finditer(body):
        target = _normalize_reference(match.group(1))
        if target and target not in titles:
            issues.append(f"{location}: unresolved wikilink: {target}")

    for field, value in _reference_fields(data):
        for item in _as_list(value):
            reference = _normalize_reference(_stringify(item))
            if not reference:
                continue
            if reference not in titles and reference not in ids:
                issues.append(f"{location}: unresolved relation reference in {field}: {reference}")

    return issues


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if value == "[]":
        return []
    return [value]


def _reference_fields(data: dict[str, object]) -> list[tuple[str, object]]:
    fields: list[tuple[str, object]] = []
    for field, value in data.items():
        if field in NON_REFERENCE_LIST_FIELDS:
            continue
        if (
            field == "related"
            or field == "source_refs"
            or field.endswith("_refs")
            or field.endswith("_by")
            or isinstance(value, list)
        ):
            fields.append((field, value))
    return fields


def _stringify(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(value)


def _normalize_reference(value: str) -> str:
    reference = value.strip()
    if "|" in reference:
        reference = reference.split("|", 1)[0].strip()
    if "#" in reference:
        reference = reference.split("#", 1)[0].strip()
    return reference
