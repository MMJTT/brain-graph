"""Discovery adapters for scholarly paper sources."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.models import (
    COMPILE_STATUS_IMPORTED,
    DISCOVERY_PROVIDER_ARXIV,
    DISCOVERY_PROVIDER_BOTH,
    DISCOVERY_PROVIDER_SEMANTIC_SCHOLAR,
)
from brain_graph.paths import raw_metadata_path_for_paper, raw_path_for_kind
from brain_graph.slugify import slugify_title


@dataclass(frozen=True, slots=True)
class DiscoveredPaper:
    title: str
    abstract: str
    authors: list[str]
    year: int | None
    paper_url: str
    pdf_url: str | None
    external_ids: dict[str, str]
    source_provider: str
    source_query: str


def discover_papers(query: str, provider: str, limit: int) -> list[DiscoveredPaper]:
    if provider == DISCOVERY_PROVIDER_ARXIV:
        return _discover_arxiv(query, limit)
    if provider == DISCOVERY_PROVIDER_SEMANTIC_SCHOLAR:
        return _discover_semantic_scholar(query, limit)
    if provider == DISCOVERY_PROVIDER_BOTH:
        discovered = _discover_arxiv(query, limit) + _discover_semantic_scholar(query, limit)
        unique: list[DiscoveredPaper] = []
        seen_titles: set[str] = set()
        for paper in discovered:
            normalized_title = paper.title.strip().lower()
            if normalized_title in seen_titles:
                continue
            seen_titles.add(normalized_title)
            unique.append(paper)
            if len(unique) >= limit:
                break
        return unique
    raise ValueError(f"unsupported discovery provider: {provider}")


def import_discovered_papers(
    project_root: Path,
    discovered_papers: list[DiscoveredPaper],
    imported_at: str,
) -> list[Path]:
    root = Path(project_root)
    imported_paths: list[Path] = []
    for paper in discovered_papers:
        slug = slugify_title(paper.title)
        raw_path = raw_path_for_kind(root, "paper", slug, imported_at)
        metadata_path = raw_metadata_path_for_paper(root, slug)
        if raw_path.exists() or metadata_path.exists():
            continue

        raw_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        frontmatter = {
            "kind": "paper",
            "slug": slug,
            "title": paper.title,
            "import_source": "url",
            "asset_path": None,
            "metadata_path": metadata_path.relative_to(root).as_posix(),
            "imported_at": imported_at,
            "compile_status": COMPILE_STATUS_IMPORTED,
            "compiled_note": None,
        }
        raw_path.write_text(
            "\n".join(
                [
                    dump_frontmatter(frontmatter),
                    "",
                    f"# {paper.title}",
                    "",
                    f"Imported from discovery provider `{paper.source_provider}`.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        metadata = {
            "slug": slug,
            "title": paper.title,
            "source_kind": "url",
            "source_path": None,
            "source_url": paper.paper_url,
            "authors": paper.authors,
            "abstract": paper.abstract,
            "full_text_path": None,
            "imported_at": imported_at,
            "source_provider": paper.source_provider,
            "source_query": paper.source_query,
            "external_ids": paper.external_ids,
            "pdf_url": paper.pdf_url,
            "year": paper.year,
            "discovered_at": imported_at,
        }
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        imported_paths.append(raw_path)
    return imported_paths


def _discover_arxiv(query: str, limit: int) -> list[DiscoveredPaper]:
    params = urllib.parse.urlencode(
        {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "lastUpdatedDate",
            "sortOrder": "descending",
        }
    )
    feed = _fetch_text(f"http://export.arxiv.org/api/query?{params}")
    return _parse_arxiv_feed(feed, query)


def _discover_semantic_scholar(query: str, limit: int) -> list[DiscoveredPaper]:
    params = urllib.parse.urlencode(
        {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,year,url,externalIds,openAccessPdf",
        }
    )
    payload = _fetch_json(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}")
    return _parse_semantic_scholar_payload(payload, query)


def _parse_arxiv_feed(feed_text: str, query: str) -> list[DiscoveredPaper]:
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(feed_text)
    papers: list[DiscoveredPaper] = []
    for entry in root.findall("atom:entry", namespace):
        title = _xml_text(entry.find("atom:title", namespace))
        summary = _xml_text(entry.find("atom:summary", namespace))
        published = _xml_text(entry.find("atom:published", namespace))
        authors = [
            _xml_text(author.find("atom:name", namespace))
            for author in entry.findall("atom:author", namespace)
            if _xml_text(author.find("atom:name", namespace))
        ]
        paper_url = ""
        pdf_url = None
        for link in entry.findall("atom:link", namespace):
            href = link.attrib.get("href")
            title_attr = link.attrib.get("title")
            rel_attr = link.attrib.get("rel")
            if href and title_attr == "pdf":
                pdf_url = href
            elif href and rel_attr == "alternate":
                paper_url = href
        entry_id = _xml_text(entry.find("atom:id", namespace))
        papers.append(
            DiscoveredPaper(
                title=title,
                abstract=summary,
                authors=authors,
                year=_parse_year(published),
                paper_url=paper_url or entry_id,
                pdf_url=pdf_url,
                external_ids={"ArXiv": _extract_arxiv_id(entry_id)},
                source_provider=DISCOVERY_PROVIDER_ARXIV,
                source_query=query,
            )
        )
    return papers


def _parse_semantic_scholar_payload(
    payload: dict[str, object],
    query: str,
) -> list[DiscoveredPaper]:
    entries = payload.get("data")
    if not isinstance(entries, list):
        return []
    papers: list[DiscoveredPaper] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        authors = []
        for author in entry.get("authors", []):
            if isinstance(author, dict) and isinstance(author.get("name"), str):
                authors.append(author["name"])
        open_access_pdf = entry.get("openAccessPdf")
        pdf_url = None
        if isinstance(open_access_pdf, dict) and isinstance(open_access_pdf.get("url"), str):
            pdf_url = open_access_pdf["url"]
        external_ids = entry.get("externalIds")
        papers.append(
            DiscoveredPaper(
                title=str(entry.get("title", "")).strip(),
                abstract=str(entry.get("abstract", "")).strip(),
                authors=authors,
                year=entry.get("year") if isinstance(entry.get("year"), int) else None,
                paper_url=str(entry.get("url", "")).strip(),
                pdf_url=pdf_url,
                external_ids=external_ids if isinstance(external_ids, dict) else {},
                source_provider=DISCOVERY_PROVIDER_SEMANTIC_SCHOLAR,
                source_query=query,
            )
        )
    return [paper for paper in papers if paper.title]


def _fetch_text(url: str, headers: dict[str, str] | None = None) -> str:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def _fetch_json(url: str, headers: dict[str, str] | None = None) -> dict[str, object]:
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _xml_text(node: ET.Element | None) -> str:
    if node is None or node.text is None:
        return ""
    return node.text.strip()


def _parse_year(value: str) -> int | None:
    if len(value) < 4 or not value[:4].isdigit():
        return None
    return int(value[:4])


def _extract_arxiv_id(entry_id: str) -> str:
    if "/" not in entry_id:
        return entry_id
    return entry_id.rsplit("/", 1)[-1].removesuffix("v1")
