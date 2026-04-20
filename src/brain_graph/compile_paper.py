"""Compile imported raw papers into structured wiki notes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from brain_graph.compiler_schema import validate_compiled_payload
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.models import COMPILE_STATUS_COMPILED
from brain_graph.paths import note_path_for_type, raw_metadata_path_for_paper
from brain_graph.slugify import slugify_title

PAPER_AUTO_START = "<!-- brain-graph:auto-summary:start -->"
PAPER_AUTO_END = "<!-- brain-graph:auto-summary:end -->"
CONCEPT_AUTO_START = "<!-- brain-graph:auto-related-papers:start -->"
CONCEPT_AUTO_END = "<!-- brain-graph:auto-related-papers:end -->"

KEYWORD_CONCEPTS = (
    ("prompt injection", "Prompt Injection"),
    ("environmental injection", "Environmental Injection"),
    ("multimodal agent", "Multimodal Agents"),
    ("benchmark", "Agent Benchmarks"),
    ("defense", "Agent Defenses"),
)


def compile_imported_paper(project_root: Path, slug: str) -> dict[str, object]:
    root = Path(project_root)
    metadata_path = raw_metadata_path_for_paper(root, slug)
    if not metadata_path.exists():
        raise FileNotFoundError(f"missing metadata for slug {slug}: {metadata_path}")

    raw_path = _find_raw_note(root, slug)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    summary = _resolve_summary(root, metadata)
    paper_title = metadata.get("title") or slug
    concept_titles = _detect_concepts(root, metadata)
    raw_ref = raw_path.stem

    payload = {
        "paper": {
            "id": f"paper-{slug}",
            "title": paper_title,
            "summary": summary,
            "authors": metadata.get("authors") or [],
            "raw_refs": [raw_ref],
            "concept_refs": concept_titles,
            "method_refs": [],
            "gap_refs": [],
            "related": [],
        },
        "concepts": [
            {
                "title": concept_title,
                "paper_refs": [paper_title],
                "related": [],
            }
            for concept_title in concept_titles
        ],
        "maps": [],
    }
    validate_compiled_payload(payload)

    _upsert_paper_note(root, payload["paper"])
    for concept_payload in payload["concepts"]:
        _upsert_concept_note(root, concept_payload)
    _mark_raw_note_compiled(raw_path, paper_title)
    return payload


def _find_raw_note(root: Path, slug: str) -> Path:
    matches = sorted((root / "raw" / "papers").glob(f"*-{slug}.md"))
    if not matches:
        raise FileNotFoundError(f"missing raw note for slug {slug}")
    return matches[-1]


def _resolve_summary(root: Path, metadata: dict[str, object]) -> str:
    abstract = metadata.get("abstract")
    if isinstance(abstract, str) and abstract.strip():
        return abstract.strip()

    full_text_path = metadata.get("full_text_path")
    if isinstance(full_text_path, str) and full_text_path:
        text_path = root / full_text_path
        if text_path.exists():
            text = text_path.read_text(encoding="utf-8").strip()
            if text:
                paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
                if paragraphs:
                    return paragraphs[0]
    return "Compiler seed summary pending manual review."


def _detect_concepts(root: Path, metadata: dict[str, object]) -> list[str]:
    parts: list[str] = []
    for key in ("title", "abstract"):
        value = metadata.get(key)
        if isinstance(value, str):
            parts.append(value)

    text = ""
    full_text_path = metadata.get("full_text_path")
    if isinstance(full_text_path, str) and full_text_path:
        path = root / full_text_path
        if path.exists():
            text = path.read_text(encoding="utf-8")
    haystack = " ".join(parts + [text]).lower()

    concepts: list[str] = []
    for needle, concept in KEYWORD_CONCEPTS:
        if needle in haystack and concept not in concepts:
            concepts.append(concept)
    return concepts


def _upsert_paper_note(root: Path, payload: dict[str, object]) -> None:
    title = payload["title"]
    path = note_path_for_type(root, "paper", title)
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    frontmatter = {
        "id": payload["id"],
        "title": title,
        "node_type": "paper",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", payload["related"]),
        "year": existing_frontmatter.get("year", None),
        "venue": existing_frontmatter.get("venue", None),
        "authors": payload["authors"],
        "paper_url": existing_frontmatter.get("paper_url", None),
        "raw_refs": payload["raw_refs"],
        "concept_refs": payload["concept_refs"],
        "method_refs": payload["method_refs"],
        "gap_refs": payload["gap_refs"],
    }

    auto_block = _paper_auto_block(payload)
    body = _replace_or_append_block(existing_body, title, auto_block, PAPER_AUTO_START, PAPER_AUTO_END)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _upsert_concept_note(root: Path, payload: dict[str, object]) -> None:
    title = payload["title"]
    path = note_path_for_type(root, "concept", title)
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    paper_refs = _unique_strings(existing_frontmatter.get("paper_refs", []) + payload["paper_refs"])
    frontmatter = {
        "id": existing_frontmatter.get("id", f"concept-{slugify_title(title)}"),
        "title": title,
        "node_type": "concept",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", payload["related"]),
        "aliases": existing_frontmatter.get("aliases", []),
        "parent_concepts": existing_frontmatter.get("parent_concepts", []),
        "paper_refs": paper_refs,
        "method_refs": existing_frontmatter.get("method_refs", []),
    }

    auto_block = _concept_auto_block(paper_refs)
    body = _replace_or_append_block(existing_body, title, auto_block, CONCEPT_AUTO_START, CONCEPT_AUTO_END)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _mark_raw_note_compiled(raw_path: Path, paper_title: str) -> None:
    frontmatter, body = load_frontmatter(raw_path.read_text(encoding="utf-8"))
    frontmatter["compile_status"] = COMPILE_STATUS_COMPILED
    frontmatter["compiled_note"] = f"wiki/papers/{paper_title}.md"
    raw_path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.lstrip()}", encoding="utf-8")


def _paper_auto_block(payload: dict[str, object]) -> str:
    concept_lines = "\n".join(f"- [[{title}]]" for title in payload["concept_refs"]) or "- None yet"
    return (
        f"{PAPER_AUTO_START}\n"
        "## Summary\n"
        f"{payload['summary']}\n\n"
        "## Claims\n"
        "- Compiler seed only. Manual review still needed.\n\n"
        "## Evidence\n"
        f"- Raw import: `{payload['raw_refs'][0]}`\n\n"
        "## Links\n"
        "### Concepts\n"
        f"{concept_lines}\n\n"
        "### Methods\n"
        "- None yet\n\n"
        "### Gaps\n"
        "- None yet\n"
        f"{PAPER_AUTO_END}"
    )


def _concept_auto_block(paper_refs: list[str]) -> str:
    paper_lines = "\n".join(f"- [[{title}]]" for title in paper_refs) or "- None yet"
    return (
        f"{CONCEPT_AUTO_START}\n"
        "## Related Papers\n"
        f"{paper_lines}\n"
        f"{CONCEPT_AUTO_END}"
    )


def _replace_or_append_block(
    existing_body: str,
    title: str,
    block: str,
    start_marker: str,
    end_marker: str,
) -> str:
    if not existing_body.strip():
        return f"# {title}\n\n{block}\n"
    if start_marker in existing_body and end_marker in existing_body:
        before, _, remainder = existing_body.partition(start_marker)
        _, _, after = remainder.partition(end_marker)
        return f"{before.rstrip()}\n\n{block}\n{after.lstrip()}"
    return f"{existing_body.rstrip()}\n\n{block}\n"


def _unique_strings(values: object) -> list[str]:
    if not isinstance(values, list):
        values = [values]
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
