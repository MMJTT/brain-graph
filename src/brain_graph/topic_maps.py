"""Generated topical map helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter, load_frontmatter

TOPIC_RULES = (
    ("Attack Paper Map", "attack", {"Prompt Injection", "Environmental Injection"}),
    ("Defense Paper Map", "defense", {"Agent Defenses"}),
    ("Benchmark Paper Map", "benchmark", {"Agent Benchmarks"}),
    ("System Paper Map", "system", {"Multimodal Agents"}),
)


def refresh_topic_maps(project_root: Path) -> list[Path]:
    root = Path(project_root)
    papers = _load_paper_frontmatters(root)
    generated: list[Path] = []
    for map_title, topic_slug, concept_titles in TOPIC_RULES:
        included_titles = [
            paper["title"]
            for paper in papers
            if concept_titles.intersection(set(_coerce_string_list(paper.get("concept_refs"))))
        ]
        if not included_titles:
            continue
        path = _write_topic_map(root, map_title, topic_slug, included_titles)
        generated.append(path)
    return generated


def _load_paper_frontmatters(root: Path) -> list[dict[str, object]]:
    papers: list[dict[str, object]] = []
    for path in sorted((root / "wiki" / "papers").glob("*.md")):
        frontmatter, _ = load_frontmatter(path.read_text(encoding="utf-8"))
        papers.append(frontmatter)
    return papers


def _write_topic_map(
    root: Path,
    map_title: str,
    topic_slug: str,
    included_titles: list[str],
) -> Path:
    path = root / "wiki" / "maps" / f"{map_title}.md"
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    if path.exists():
        existing_frontmatter, _ = load_frontmatter(path.read_text(encoding="utf-8"))
    frontmatter = {
        "id": existing_frontmatter.get("id", f"map-{topic_slug}-paper-map"),
        "title": map_title,
        "node_type": "map",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", [topic_slug]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", included_titles),
        "focus": f"Generated {topic_slug} paper cluster.",
        "includes": included_titles,
        "questions": existing_frontmatter.get(
            "questions",
            [f"Which {topic_slug} papers need manual curation next?"],
        ),
    }
    paper_lines = "\n".join(f"- [[{title}]]" for title in included_titles) or "- None yet"
    body = (
        f"# {map_title}\n\n"
        "## Included Papers\n"
        f"{paper_lines}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body}", encoding="utf-8")
    return path


def _coerce_string_list(value: object) -> list[str]:
    if value is None or value == "[]":
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    if isinstance(value, str) and value:
        return [value]
    return []
