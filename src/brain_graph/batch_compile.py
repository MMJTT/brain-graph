"""Batch compilation helpers for imported papers."""

from __future__ import annotations

from pathlib import Path

from brain_graph.compile_paper import compile_imported_paper
from brain_graph.export_graph import export_graph_files
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.lint import collect_issues
from brain_graph.topic_maps import refresh_topic_maps


def compile_batch(
    project_root: Path,
    source: str,
    limit: int | None,
    compiler: str = "heuristic",
    model: str | None = None,
) -> list[Path]:
    root = Path(project_root)
    source_dir = root / source
    compiled_paths: list[Path] = []
    compiled_titles: list[str] = []

    for raw_path in sorted(source_dir.glob("*.md")):
        frontmatter, _ = load_frontmatter(raw_path.read_text(encoding="utf-8"))
        if frontmatter.get("compile_status") == "compiled":
            continue
        slug = frontmatter.get("slug")
        if not isinstance(slug, str):
            continue
        payload = compile_imported_paper(root, slug, compiler=compiler, model=model)
        paper_title = payload["paper"]["title"]
        compiled_paths.append(root / "wiki" / "papers" / f"{paper_title}.md")
        compiled_titles.append(paper_title)
        if limit is not None and len(compiled_paths) >= limit:
            break

    refresh_topic_maps(root)
    _ensure_queue_map(root, compiled_titles)
    _ensure_compilation_queue_view(root)

    issues = collect_issues(root)
    if issues:
        raise ValueError("\n".join(issues))
    export_graph_files(root)
    return compiled_paths


def _ensure_queue_map(root: Path, compiled_titles: list[str]) -> None:
    path = root / "wiki" / "maps" / "Imported Paper Queue.md"
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    topical_maps = [
        name
        for name in [
            "Attack Paper Map",
            "Defense Paper Map",
            "Benchmark Paper Map",
            "System Paper Map",
        ]
        if (root / "wiki" / "maps" / f"{name}.md").exists()
    ]
    includes = _unique_strings(list(existing_frontmatter.get("includes", [])) + compiled_titles + topical_maps)
    frontmatter = {
        "id": existing_frontmatter.get("id", "map-imported-paper-queue"),
        "title": "Imported Paper Queue",
        "node_type": "map",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", "2026-04-20"),
        "updated": "2026-04-20",
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": _unique_strings(list(existing_frontmatter.get("related", [])) + topical_maps),
        "focus": "Recently compiled papers and their linked topical maps.",
        "includes": includes,
        "questions": existing_frontmatter.get(
            "questions",
            [
                "Which imported papers still need manual curation?",
                "Which topical map should absorb the next compiled paper?",
            ],
        ),
    }
    compiled_lines = "\n".join(f"- [[{title}]]" for title in compiled_titles) or "- None in this run"
    map_lines = "\n".join(f"- [[{title}]]" for title in topical_maps) or "- None yet"
    body = (
        "# Imported Paper Queue\n\n"
        "## Focus\n"
        "This map tracks papers compiled by the batch pipeline and points to topical entry maps.\n\n"
        "## Recently Compiled Papers\n"
        f"{compiled_lines}\n\n"
        "## Topic Maps\n"
        f"{map_lines}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body}", encoding="utf-8")


def _ensure_compilation_queue_view(root: Path) -> None:
    path = root / "views" / "dataview" / "compilation-queue.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '# Compilation Queue\n\n```dataview\nTABLE compile_status, imported_at\nFROM "raw/papers"\nSORT file.name ASC\n```\n',
        encoding="utf-8",
    )


def _unique_strings(values: list[object]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
