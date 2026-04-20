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


def _import_gap_seed_paper(tmp_path: Path, monkeypatch) -> None:
    source_pdf = tmp_path / "IndirectAttack.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")
    monkeypatch.setattr(
        "brain_graph.import_paper.extract_pdf_text",
        lambda path: ExtractedPaper(
            title="IndirectAttack",
            authors=["Carol Researcher", "Dan Builder"],
            abstract=(
                "Indirect prompt injection remains a benchmark challenge for multimodal agents. "
                "We use red teaming as the primary method and highlight a cross-modal evaluation gap."
            ),
            full_text=(
                "IndirectAttack\nCarol Researcher\nDan Builder\nAbstract\n"
                "Indirect prompt injection remains a benchmark challenge for multimodal agents.\n\n"
                "Method: We use red teaming as the primary method.\n"
                "Gap: A cross-modal evaluation gap remains unsolved.\n"
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


def test_compile_imported_paper_creates_author_method_and_gap_notes(tmp_path, monkeypatch):
    _import_gap_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "indirectattack")

    author_note = tmp_path / "wiki" / "authors" / "Carol Researcher.md"
    method_note = tmp_path / "wiki" / "methods" / "Red Teaming Method.md"
    gap_note = tmp_path / "wiki" / "gaps" / "Cross-Modal Evaluation Gap.md"
    assert author_note.exists()
    assert method_note.exists()
    assert gap_note.exists()

    author_frontmatter, _ = load_frontmatter(author_note.read_text(encoding="utf-8"))
    method_frontmatter, _ = load_frontmatter(method_note.read_text(encoding="utf-8"))
    gap_frontmatter, _ = load_frontmatter(gap_note.read_text(encoding="utf-8"))
    assert author_frontmatter["paper_refs"] == ["IndirectAttack"]
    assert method_frontmatter["introduced_by"] == ["IndirectAttack"]
    assert gap_frontmatter["raised_by"] == ["IndirectAttack"]


def test_compile_imported_paper_normalizes_concept_aliases(tmp_path, monkeypatch):
    _import_gap_seed_paper(tmp_path, monkeypatch)

    compile_imported_paper(tmp_path, "indirectattack")

    paper_note = tmp_path / "wiki" / "papers" / "IndirectAttack.md"
    concept_note = tmp_path / "wiki" / "concepts" / "Prompt Injection.md"
    paper_frontmatter, _ = load_frontmatter(paper_note.read_text(encoding="utf-8"))
    concept_frontmatter, _ = load_frontmatter(concept_note.read_text(encoding="utf-8"))
    assert "Prompt Injection" in paper_frontmatter["concept_refs"]
    assert concept_frontmatter["aliases"] == ["Indirect Prompt Injection"]


def test_compile_imported_paper_supports_openrouter_backend(tmp_path, monkeypatch):
    _import_seed_paper(tmp_path, monkeypatch)
    monkeypatch.setattr(
        "brain_graph.compile_paper.compile_with_openrouter",
        lambda metadata, full_text, model: {
            "summary": "OpenRouter summary.",
            "concepts": [{"title": "Prompt Injection", "aliases": [], "related": []}],
            "methods": [{"title": "Red Teaming Method"}],
            "gaps": [{"title": "Cross-Modal Evaluation Gap", "gap_kind": "evaluation"}],
            "research_notes": ["Cross-check against stronger baselines."],
        },
    )

    compile_imported_paper(tmp_path, "memorygraft", compiler="openrouter", model="openai/gpt-4.1-mini")

    paper_note = tmp_path / "wiki" / "papers" / "MemoryGraft.md"
    method_note = tmp_path / "wiki" / "methods" / "Red Teaming Method.md"
    gap_note = tmp_path / "wiki" / "gaps" / "Cross-Modal Evaluation Gap.md"
    frontmatter, body = load_frontmatter(paper_note.read_text(encoding="utf-8"))
    assert method_note.exists()
    assert gap_note.exists()
    assert frontmatter["method_refs"] == ["Red Teaming Method"]
    assert frontmatter["gap_refs"] == ["Cross-Modal Evaluation Gap"]
    assert "OpenRouter summary." in body
