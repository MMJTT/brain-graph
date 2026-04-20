import json

from brain_graph.discover_papers import DiscoveredPaper, discover_papers, import_discovered_papers


def test_discover_papers_parses_arxiv_atom_feed(monkeypatch):
    monkeypatch.setattr(
        "brain_graph.discover_papers._fetch_text",
        lambda url, headers=None: """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2512.16962v1</id>
    <title>MemoryGraft</title>
    <summary>Prompt injection benchmark paper.</summary>
    <published>2026-04-20T00:00:00Z</published>
    <author><name>Alice</name></author>
    <author><name>Bob</name></author>
    <link rel="alternate" href="https://arxiv.org/abs/2512.16962v1" />
    <link title="pdf" href="https://arxiv.org/pdf/2512.16962v1" />
  </entry>
</feed>
""",
    )

    discovered = discover_papers("prompt injection", "arxiv", 5)

    assert len(discovered) == 1
    assert discovered[0].title == "MemoryGraft"
    assert discovered[0].authors == ["Alice", "Bob"]
    assert discovered[0].source_provider == "arxiv"
    assert discovered[0].paper_url == "https://arxiv.org/abs/2512.16962v1"
    assert discovered[0].pdf_url == "https://arxiv.org/pdf/2512.16962v1"


def test_discover_papers_parses_semantic_scholar_response(monkeypatch):
    monkeypatch.setattr(
        "brain_graph.discover_papers._fetch_json",
        lambda url, headers=None: {
            "data": [
                {
                    "title": "AgentShield",
                    "abstract": "Defense benchmark paper.",
                    "year": 2025,
                    "url": "https://www.semanticscholar.org/paper/agentshield",
                    "externalIds": {"ArXiv": "2512.00001"},
                    "openAccessPdf": {"url": "https://pdf.example/agentshield.pdf"},
                    "authors": [{"name": "Carol"}, {"name": "Dan"}],
                }
            ]
        },
    )

    discovered = discover_papers("agent defense", "semantic-scholar", 5)

    assert len(discovered) == 1
    assert discovered[0].title == "AgentShield"
    assert discovered[0].authors == ["Carol", "Dan"]
    assert discovered[0].source_provider == "semantic-scholar"
    assert discovered[0].external_ids == {"ArXiv": "2512.00001"}


def test_import_discovered_papers_creates_raw_entries_with_discovery_metadata(tmp_path):
    discovered = [
        DiscoveredPaper(
            title="MemoryGraft",
            abstract="Prompt injection benchmark paper.",
            authors=["Alice", "Bob"],
            year=2026,
            paper_url="https://arxiv.org/abs/2512.16962",
            pdf_url="https://arxiv.org/pdf/2512.16962",
            external_ids={"ArXiv": "2512.16962"},
            source_provider="arxiv",
            source_query="prompt injection",
        )
    ]

    raw_paths = import_discovered_papers(tmp_path, discovered, "2026-04-20")

    metadata_path = tmp_path / "raw" / "metadata" / "papers" / "memorygraft.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert raw_paths == [tmp_path / "raw" / "papers" / "2026-04-20-memorygraft.md"]
    assert metadata["source_provider"] == "arxiv"
    assert metadata["source_query"] == "prompt injection"
    assert metadata["external_ids"] == {"ArXiv": "2512.16962"}
    assert metadata["pdf_url"] == "https://arxiv.org/pdf/2512.16962"
