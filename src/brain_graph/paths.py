"""Path helpers for wiki and raw notes."""

from pathlib import Path

from brain_graph.models import RAW_DIRECTORY_BY_KIND, WIKI_DIRECTORY_BY_NOTE_TYPE


def note_path_for_type(project_root, note_type: str, title: str) -> Path:
    directory = WIKI_DIRECTORY_BY_NOTE_TYPE[note_type]
    return Path(project_root) / "wiki" / directory / f"{title}.md"


def raw_path_for_kind(project_root, kind: str, slug: str, date_text: str) -> Path:
    directory = RAW_DIRECTORY_BY_KIND[kind]
    return Path(project_root) / "raw" / directory / f"{date_text}-{slug}.md"


def raw_asset_path_for_paper(project_root, slug: str, suffix: str) -> Path:
    return Path(project_root) / "raw" / "assets" / "papers" / f"{slug}{suffix}"


def raw_metadata_path_for_paper(project_root, slug: str) -> Path:
    return Path(project_root) / "raw" / "metadata" / "papers" / f"{slug}.json"


def raw_text_path_for_paper(project_root, slug: str) -> Path:
    return Path(project_root) / "raw" / "metadata" / "papers" / f"{slug}.txt"
