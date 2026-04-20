import json
from pathlib import Path

from brain_graph.batch_compile import compile_batch
from brain_graph.extract_pdf import ExtractedPaper
from brain_graph.frontmatter import load_frontmatter
from brain_graph.import_paper import ImportPaperCommand, import_paper_source


def _import_seed_pdf(tmp_path: Path, monkeypatch, stem: str, abstract: str, imported_at: str) -> None:
    source_pdf = tmp_path / f"{stem}.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")
    monkeypatch.setattr(
        "brain_graph.import_paper.extract_pdf_text",
        lambda path: ExtractedPaper(
            title=stem,
            authors=["Alice"],
            abstract=abstract,
            full_text=f"{stem}\nAlice\nAbstract\n{abstract}",
            extractor="pdftotext",
        ),
    )
    import_paper_source(
        tmp_path,
        ImportPaperCommand(
            pdf_path=str(source_pdf),
            url=None,
            title=None,
            slug=None,
        ),
        imported_at,
    )


def test_compile_batch_compiles_multiple_imported_papers(tmp_path, monkeypatch):
    _import_seed_pdf(tmp_path, monkeypatch, "MemoryGraft", "Prompt injection benchmark abstract.", "2026-04-20")
    _import_seed_pdf(tmp_path, monkeypatch, "AgentShield", "Defense benchmark abstract.", "2026-04-21")

    compiled = compile_batch(tmp_path, "raw/papers", None)

    assert compiled == [
        tmp_path / "wiki" / "papers" / "MemoryGraft.md",
        tmp_path / "wiki" / "papers" / "AgentShield.md",
    ]
    assert (tmp_path / "wiki" / "papers" / "MemoryGraft.md").exists()
    assert (tmp_path / "wiki" / "papers" / "AgentShield.md").exists()


def test_compile_batch_limit_stops_after_requested_count(tmp_path, monkeypatch):
    _import_seed_pdf(tmp_path, monkeypatch, "MemoryGraft", "Prompt injection benchmark abstract.", "2026-04-20")
    _import_seed_pdf(tmp_path, monkeypatch, "AgentShield", "Defense benchmark abstract.", "2026-04-21")
    _import_seed_pdf(tmp_path, monkeypatch, "VisionGuard", "Multimodal benchmark abstract.", "2026-04-22")

    compiled = compile_batch(tmp_path, "raw/papers", 2)

    assert compiled == [
        tmp_path / "wiki" / "papers" / "MemoryGraft.md",
        tmp_path / "wiki" / "papers" / "AgentShield.md",
    ]
    frontmatter, _ = load_frontmatter(
        (tmp_path / "raw" / "papers" / "2026-04-22-visionguard.md").read_text(encoding="utf-8")
    )
    assert frontmatter["compile_status"] == "imported"


def test_compile_batch_refreshes_exports_canvas_and_queue_map(tmp_path, monkeypatch):
    _import_seed_pdf(tmp_path, monkeypatch, "MemoryGraft", "Prompt injection benchmark abstract.", "2026-04-20")

    compile_batch(tmp_path, "raw/papers", None)

    assert (tmp_path / "exports" / "brain_graph.json").exists()
    assert (tmp_path / "exports" / "brain_graph.mmd").exists()
    assert (tmp_path / "views" / "canvas" / "starter.canvas").exists()
    assert (tmp_path / "views" / "dataview" / "compilation-queue.md").exists()
    queue_map = tmp_path / "wiki" / "maps" / "Imported Paper Queue.md"
    assert queue_map.exists()
    graph = json.loads((tmp_path / "exports" / "brain_graph.json").read_text(encoding="utf-8"))
    assert any(node["title"] == "Imported Paper Queue" for node in graph["nodes"])
