"""Compile imported raw papers into structured wiki notes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from brain_graph.compiler_schema import validate_compiled_payload
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.models import COMPILE_STATUS_COMPILED
from brain_graph.normalize_graph import (
    build_author_payloads,
    detect_concepts,
    detect_gaps,
    detect_methods,
)
from brain_graph.openrouter_client import compile_with_openrouter
from brain_graph.paths import note_path_for_type, raw_metadata_path_for_paper
from brain_graph.slugify import slugify_title

PAPER_AUTO_START = "<!-- brain-graph:auto-summary:start -->"
PAPER_AUTO_END = "<!-- brain-graph:auto-summary:end -->"
CONCEPT_AUTO_START = "<!-- brain-graph:auto-related-papers:start -->"
CONCEPT_AUTO_END = "<!-- brain-graph:auto-related-papers:end -->"
METHOD_AUTO_START = "<!-- brain-graph:auto-method:start -->"
METHOD_AUTO_END = "<!-- brain-graph:auto-method:end -->"
GAP_AUTO_START = "<!-- brain-graph:auto-gap:start -->"
GAP_AUTO_END = "<!-- brain-graph:auto-gap:end -->"
AUTHOR_AUTO_START = "<!-- brain-graph:auto-author:start -->"
AUTHOR_AUTO_END = "<!-- brain-graph:auto-author:end -->"


def compile_imported_paper(
    project_root: Path,
    slug: str,
    compiler: str = "heuristic",
    model: str | None = None,
) -> dict[str, object]:
    root = Path(project_root)
    metadata_path = raw_metadata_path_for_paper(root, slug)
    if not metadata_path.exists():
        raise FileNotFoundError(f"missing metadata for slug {slug}: {metadata_path}")

    raw_path = _find_raw_note(root, slug)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    paper_title = metadata.get("title") or slug
    summary = _resolve_summary(root, metadata)
    full_text = _load_full_text(root, metadata)
    research_notes: list[str] = []
    if compiler == "openrouter":
        llm_payload = compile_with_openrouter(metadata, full_text, model)
        summary = str(llm_payload.get("summary") or summary)
        concept_payloads = _normalize_openrouter_concepts(llm_payload.get("concepts"), paper_title)
        method_payloads = _normalize_openrouter_methods(llm_payload.get("methods"), paper_title)
        gap_payloads = _normalize_openrouter_gaps(llm_payload.get("gaps"), paper_title)
        research_notes = _coerce_string_list(llm_payload.get("research_notes"))
    else:
        haystack = _compile_haystack(root, metadata)
        concept_payloads = detect_concepts(haystack, paper_title)
        method_payloads = detect_methods(haystack, paper_title)
        gap_payloads = detect_gaps(haystack, paper_title)
    author_payloads = build_author_payloads(_coerce_string_list(metadata.get("authors")), paper_title)
    concept_titles = [payload["title"] for payload in concept_payloads]
    method_titles = [payload["title"] for payload in method_payloads]
    gap_titles = [payload["title"] for payload in gap_payloads]
    raw_ref = raw_path.stem

    payload = {
        "paper": {
            "id": f"paper-{slug}",
            "title": paper_title,
            "summary": summary,
            "authors": _coerce_string_list(metadata.get("authors")),
            "raw_refs": [raw_ref],
            "concept_refs": concept_titles,
            "method_refs": method_titles,
            "gap_refs": gap_titles,
            "related": [],
        },
        "concepts": concept_payloads,
        "methods": method_payloads,
        "gaps": gap_payloads,
        "authors": author_payloads,
        "maps": [],
        "research_notes": research_notes,
    }
    validate_compiled_payload(payload)

    _upsert_paper_note(root, payload["paper"])
    for concept_payload in payload["concepts"]:
        _upsert_concept_note(root, concept_payload)
    for method_payload in payload["methods"]:
        _upsert_method_note(root, method_payload)
    for gap_payload in payload["gaps"]:
        _upsert_gap_note(root, gap_payload)
    for author_payload in payload["authors"]:
        _upsert_author_note(root, author_payload)
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


def _compile_haystack(root: Path, metadata: dict[str, object]) -> str:
    parts: list[str] = []
    for key in ("title", "abstract"):
        value = metadata.get(key)
        if isinstance(value, str):
            parts.append(value)

    text = _load_full_text(root, metadata)
    return " ".join(parts + [text])


def _load_full_text(root: Path, metadata: dict[str, object]) -> str:
    full_text_path = metadata.get("full_text_path")
    if isinstance(full_text_path, str) and full_text_path:
        path = root / full_text_path
        if path.exists():
            return path.read_text(encoding="utf-8")
    return ""


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
        "authors": _coerce_string_list(payload["authors"]),
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

    paper_refs = _unique_strings(
        _coerce_string_list(existing_frontmatter.get("paper_refs")) + _coerce_string_list(payload["paper_refs"])
    )
    aliases = _unique_strings(
        _coerce_string_list(existing_frontmatter.get("aliases")) + _coerce_string_list(payload.get("aliases"))
    )
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
        "aliases": aliases,
        "parent_concepts": existing_frontmatter.get("parent_concepts", []),
        "paper_refs": paper_refs,
        "method_refs": existing_frontmatter.get("method_refs", []),
    }

    auto_block = _concept_auto_block(paper_refs)
    body = _replace_or_append_block(existing_body, title, auto_block, CONCEPT_AUTO_START, CONCEPT_AUTO_END)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _upsert_method_note(root: Path, payload: dict[str, object]) -> None:
    title = payload["title"]
    path = note_path_for_type(root, "method", title)
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    introduced_by = _unique_strings(
        _coerce_string_list(existing_frontmatter.get("introduced_by"))
        + _coerce_string_list(payload.get("introduced_by"))
    )
    frontmatter = {
        "id": existing_frontmatter.get("id", f"method-{slugify_title(title)}"),
        "title": title,
        "node_type": "method",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", payload.get("related", [])),
        "introduced_by": introduced_by,
        "applies_to": existing_frontmatter.get("applies_to", payload.get("applies_to", [])),
        "limitations": existing_frontmatter.get("limitations", payload.get("limitations", [])),
    }

    body = _replace_or_append_block(
        existing_body,
        title,
        _method_auto_block(introduced_by),
        METHOD_AUTO_START,
        METHOD_AUTO_END,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _upsert_gap_note(root: Path, payload: dict[str, object]) -> None:
    title = payload["title"]
    path = note_path_for_type(root, "gap", title)
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    raised_by = _unique_strings(
        _coerce_string_list(existing_frontmatter.get("raised_by"))
        + _coerce_string_list(payload.get("raised_by"))
    )
    frontmatter = {
        "id": existing_frontmatter.get("id", f"gap-{slugify_title(title)}"),
        "title": title,
        "node_type": "gap",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", payload.get("related", [])),
        "gap_kind": existing_frontmatter.get("gap_kind", payload.get("gap_kind", "open")),
        "raised_by": raised_by,
        "potential_directions": existing_frontmatter.get(
            "potential_directions",
            payload.get("potential_directions", []),
        ),
    }

    body = _replace_or_append_block(
        existing_body,
        title,
        _gap_auto_block(raised_by),
        GAP_AUTO_START,
        GAP_AUTO_END,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _upsert_author_note(root: Path, payload: dict[str, object]) -> None:
    title = payload["title"]
    path = note_path_for_type(root, "author", title)
    today = date.today().isoformat()
    existing_frontmatter: dict[str, object] = {}
    existing_body = ""
    if path.exists():
        existing_frontmatter, existing_body = load_frontmatter(path.read_text(encoding="utf-8"))

    paper_refs = _unique_strings(
        _coerce_string_list(existing_frontmatter.get("paper_refs")) + _coerce_string_list(payload.get("paper_refs"))
    )
    frontmatter = {
        "id": existing_frontmatter.get("id", f"author-{slugify_title(title)}"),
        "title": title,
        "node_type": "author",
        "status": existing_frontmatter.get("status", "seed"),
        "tags": existing_frontmatter.get("tags", ["compiled"]),
        "created": existing_frontmatter.get("created", today),
        "updated": today,
        "source_refs": existing_frontmatter.get("source_refs", []),
        "related": existing_frontmatter.get("related", payload.get("related", [])),
        "affiliation": existing_frontmatter.get("affiliation", None),
        "paper_refs": paper_refs,
    }

    body = _replace_or_append_block(
        existing_body,
        title,
        _author_auto_block(paper_refs),
        AUTHOR_AUTO_START,
        AUTHOR_AUTO_END,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.rstrip()}\n", encoding="utf-8")


def _mark_raw_note_compiled(raw_path: Path, paper_title: str) -> None:
    frontmatter, body = load_frontmatter(raw_path.read_text(encoding="utf-8"))
    frontmatter["compile_status"] = COMPILE_STATUS_COMPILED
    frontmatter["compiled_note"] = f"wiki/papers/{paper_title}.md"
    raw_path.write_text(f"{dump_frontmatter(frontmatter)}\n\n{body.lstrip()}", encoding="utf-8")


def _paper_auto_block(payload: dict[str, object]) -> str:
    concept_lines = "\n".join(f"- [[{title}]]" for title in payload["concept_refs"]) or "- None yet"
    method_lines = "\n".join(f"- [[{title}]]" for title in payload["method_refs"]) or "- None yet"
    gap_lines = "\n".join(f"- [[{title}]]" for title in payload["gap_refs"]) or "- None yet"
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
        f"{method_lines}\n\n"
        "### Gaps\n"
        f"{gap_lines}\n"
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


def _method_auto_block(introduced_by: list[str]) -> str:
    paper_lines = "\n".join(f"- [[{title}]]" for title in introduced_by) or "- None yet"
    return (
        f"{METHOD_AUTO_START}\n"
        "## Introduced By\n"
        f"{paper_lines}\n"
        f"{METHOD_AUTO_END}"
    )


def _gap_auto_block(raised_by: list[str]) -> str:
    paper_lines = "\n".join(f"- [[{title}]]" for title in raised_by) or "- None yet"
    return (
        f"{GAP_AUTO_START}\n"
        "## Raised By\n"
        f"{paper_lines}\n"
        f"{GAP_AUTO_END}"
    )


def _author_auto_block(paper_refs: list[str]) -> str:
    paper_lines = "\n".join(f"- [[{title}]]" for title in paper_refs) or "- None yet"
    return (
        f"{AUTHOR_AUTO_START}\n"
        "## Papers\n"
        f"{paper_lines}\n"
        f"{AUTHOR_AUTO_END}"
    )


def _normalize_openrouter_concepts(payloads: object, paper_title: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    if not isinstance(payloads, list):
        return result
    for payload in payloads:
        if not isinstance(payload, dict) or not isinstance(payload.get("title"), str):
            continue
        result.append(
            {
                "title": payload["title"],
                "aliases": _coerce_string_list(payload.get("aliases")),
                "paper_refs": [paper_title],
                "related": _coerce_string_list(payload.get("related")),
            }
        )
    return result


def _normalize_openrouter_methods(payloads: object, paper_title: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    if not isinstance(payloads, list):
        return result
    for payload in payloads:
        if not isinstance(payload, dict) or not isinstance(payload.get("title"), str):
            continue
        result.append(
            {
                "title": payload["title"],
                "introduced_by": [paper_title],
                "applies_to": _coerce_string_list(payload.get("applies_to")),
                "limitations": _coerce_string_list(payload.get("limitations")),
                "related": _coerce_string_list(payload.get("related")),
            }
        )
    return result


def _normalize_openrouter_gaps(payloads: object, paper_title: str) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    if not isinstance(payloads, list):
        return result
    for payload in payloads:
        if not isinstance(payload, dict) or not isinstance(payload.get("title"), str):
            continue
        gap_kind = payload.get("gap_kind")
        result.append(
            {
                "title": payload["title"],
                "gap_kind": gap_kind if isinstance(gap_kind, str) else "open",
                "raised_by": [paper_title],
                "potential_directions": _coerce_string_list(payload.get("potential_directions")),
                "related": _coerce_string_list(payload.get("related")),
            }
        )
    return result


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


def _coerce_string_list(values: object) -> list[str]:
    if values is None or values == "[]":
        return []
    if isinstance(values, list):
        return [value for value in values if isinstance(value, str) and value]
    if isinstance(values, str) and values:
        return [values]
    return []
