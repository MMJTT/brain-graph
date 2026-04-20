"""Orchestrate discovery, compilation, and summary updates."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from brain_graph.batch_compile import compile_batch
from brain_graph.discover_papers import discover_papers, import_discovered_papers


def run_research_loop(
    project_root: Path,
    query: str,
    provider: str,
    limit: int,
    compiler: str = "heuristic",
    model: str | None = None,
) -> dict[str, object]:
    root = Path(project_root)
    today = date.today().isoformat()
    discovered = discover_papers(query, provider, limit)
    imported_paths = import_discovered_papers(root, discovered, today)
    compiled_paths: list[Path] = []
    if imported_paths:
        compiled_paths = compile_batch(
            root,
            "raw/papers",
            len(imported_paths),
            compiler=compiler,
            model=model,
        )
    research_path = _append_research_summary(root, query, provider, discovered, imported_paths, compiled_paths)
    return {
        "discovered": discovered,
        "imported_paths": imported_paths,
        "compiled_paths": compiled_paths,
        "research_path": research_path,
    }


def _append_research_summary(
    root: Path,
    query: str,
    provider: str,
    discovered: list[object],
    imported_paths: list[Path],
    compiled_paths: list[Path],
) -> Path:
    research_path = root / "shared" / "research.md"
    research_path.parent.mkdir(parents=True, exist_ok=True)
    if research_path.exists():
        existing_text = research_path.read_text(encoding="utf-8").rstrip()
    else:
        existing_text = "# Research Scratchpad"
    imported_titles = [path.stem.split("-", 3)[-1] for path in imported_paths]
    compiled_titles = [path.stem for path in compiled_paths]
    lines = [
        existing_text,
        "",
        f"## {date.today().isoformat()} Research Loop",
        f"- Query: {query}",
        f"- Provider: {provider}",
        f"- Discovered: {len(discovered)}",
        f"- Imported: {', '.join(imported_titles) if imported_titles else 'none'}",
        f"- Compiled: {', '.join(compiled_titles) if compiled_titles else 'none'}",
    ]
    research_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return research_path
