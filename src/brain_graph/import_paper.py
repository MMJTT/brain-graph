"""Import paper sources into the raw Brain Graph workspace."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.models import COMPILE_STATUS_IMPORTED
from brain_graph.paths import (
    raw_asset_path_for_paper,
    raw_metadata_path_for_paper,
    raw_path_for_kind,
)
from brain_graph.slugify import slugify_title


@dataclass(slots=True)
class ImportPaperCommand:
    pdf_path: str | None
    url: str | None
    title: str | None
    slug: str | None


def import_paper_source(
    project_root: Path,
    command: ImportPaperCommand,
    imported_at: str,
) -> tuple[Path, Path]:
    source_kind = "pdf" if command.pdf_path else "url"
    title = _resolve_title(command)
    slug = command.slug or slugify_title(title)
    raw_path = raw_path_for_kind(project_root, "paper", slug, imported_at)
    metadata_path = raw_metadata_path_for_paper(project_root, slug)

    asset_path: Path | None = None
    source_path: str | None = None
    source_url: str | None = None

    if command.pdf_path:
        source = Path(command.pdf_path)
        asset_path = raw_asset_path_for_paper(project_root, slug, source.suffix or ".pdf")
        source_path = str(source)
    elif command.url:
        source_url = command.url

    for target in [raw_path, metadata_path, asset_path]:
        if target is not None and target.exists():
            raise FileExistsError(f"paper import already exists for slug {slug}: {target}")

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    asset_value: str | None = None
    if command.pdf_path and asset_path is not None:
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(command.pdf_path, asset_path)
        asset_value = asset_path.relative_to(project_root).as_posix()

    metadata_value = metadata_path.relative_to(project_root).as_posix()
    frontmatter = {
        "kind": "paper",
        "slug": slug,
        "title": title,
        "import_source": source_kind,
        "asset_path": asset_value,
        "metadata_path": metadata_value,
        "imported_at": imported_at,
        "compile_status": COMPILE_STATUS_IMPORTED,
        "compiled_note": None,
    }
    body_lines = [
        dump_frontmatter(frontmatter),
        "",
        f"# {title}",
        "",
        f"Imported from {source_kind} source.",
        "",
    ]
    raw_path.write_text("\n".join(body_lines), encoding="utf-8")

    metadata = {
        "slug": slug,
        "title": title,
        "source_kind": source_kind,
        "source_path": source_path,
        "source_url": source_url,
        "authors": [],
        "abstract": "",
        "full_text_path": None,
        "imported_at": imported_at,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return raw_path, metadata_path


def _resolve_title(command: ImportPaperCommand) -> str:
    if command.title:
        return command.title
    if command.pdf_path:
        return Path(command.pdf_path).stem
    raise ValueError("title is required when importing from URL")
