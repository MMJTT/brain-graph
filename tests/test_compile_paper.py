from pathlib import Path

from brain_graph.compile_paper import compile_imported_paper
from brain_graph.extract_pdf import ExtractedPaper
from brain_graph.frontmatter import load_frontmatter
from brain_graph.import_paper import ImportPaperCommand, import_paper_source


def _import_seed_paper(tmp_path: Path, monkeypatch) -> None:
    source_pdf = tmp_path / "MemoryGraft.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")
    monkeypatch.setattr(
        "brain_graph.import_paper.extract_pdf_text",
        lambda path: ExtractedPaper(
            title="MemoryGraft",
            authors=["Alice", "Bob"],
            abstract="Prompt injection benchmark defense abstract.",
            full_text=(
                "MemoryGraft\nAlice\nBob\nAbstract\n"
                "Prompt injection benchmark defense abstract.\n\n"
                "This multimodal agent benchmark studies prompt injection defense."
            ),
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
        "2026-04-20",
    )


def test_compile_imported_paper_creates_paper_note(tmp_path, monkeypatch):
    _import_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "memorygraft")

    paper_note = tmp_path / "wiki" / "papers" / "MemoryGraft.md"
    assert paper_note.exists()
    frontmatter, body = load_frontmatter(paper_note.read_text(encoding="utf-8"))
    assert frontmatter["id"] == "paper-memorygraft"
    assert frontmatter["title"] == "MemoryGraft"
    assert frontmatter["node_type"] == "paper"
    assert frontmatter["raw_refs"] == ["2026-04-20-memorygraft"]
    assert "Prompt Injection" in frontmatter["concept_refs"]
    assert "## Summary" in body
    assert "Prompt injection benchmark defense abstract." in body


def test_compile_imported_paper_creates_or_updates_linked_concepts(tmp_path, monkeypatch):
    _import_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "memorygraft")

    concept_note = tmp_path / "wiki" / "concepts" / "Prompt Injection.md"
    assert concept_note.exists()
    frontmatter, body = load_frontmatter(concept_note.read_text(encoding="utf-8"))
    assert frontmatter["title"] == "Prompt Injection"
    assert frontmatter["paper_refs"] == ["MemoryGraft"]
    assert "[[MemoryGraft]]" in body


def test_compile_imported_paper_updates_compile_status(tmp_path, monkeypatch):
    _import_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "memorygraft")

    raw_note = tmp_path / "raw" / "papers" / "2026-04-20-memorygraft.md"
    frontmatter, _ = load_frontmatter(raw_note.read_text(encoding="utf-8"))
    assert frontmatter["compile_status"] == "compiled"
    assert frontmatter["compiled_note"] == "wiki/papers/MemoryGraft.md"


def test_compile_imported_paper_is_idempotent(tmp_path, monkeypatch):
    _import_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "memorygraft")
    compile_imported_paper(tmp_path, "memorygraft")

    concept_note = tmp_path / "wiki" / "concepts" / "Prompt Injection.md"
    frontmatter, _ = load_frontmatter(concept_note.read_text(encoding="utf-8"))
    assert frontmatter["paper_refs"] == ["MemoryGraft"]
