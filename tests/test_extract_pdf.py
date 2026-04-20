from pathlib import Path

from brain_graph.extract_pdf import ExtractedPaper, extract_pdf_text


def test_extract_pdf_text_prefers_pdftotext(monkeypatch, tmp_path):
    pdf_path = tmp_path / "memorygraft.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr("brain_graph.extract_pdf.shutil.which", lambda name: "/opt/homebrew/bin/pdftotext")
    monkeypatch.setattr(
        "brain_graph.extract_pdf._extract_with_pdftotext",
        lambda path: "MemoryGraft\nAlice, Bob\nAbstract\nA compact abstract.\n\nBody text.",
    )
    monkeypatch.setattr(
        "brain_graph.extract_pdf._extract_with_pypdf",
        lambda path: (_ for _ in ()).throw(AssertionError("pypdf fallback should not run")),
    )

    result = extract_pdf_text(pdf_path)

    assert result == ExtractedPaper(
        title="MemoryGraft",
        authors=["Alice, Bob"],
        abstract="A compact abstract.",
        full_text="MemoryGraft\nAlice, Bob\nAbstract\nA compact abstract.\n\nBody text.",
        extractor="pdftotext",
    )


def test_extract_pdf_text_falls_back_to_pypdf(monkeypatch, tmp_path):
    pdf_path = tmp_path / "memorygraft.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr("brain_graph.extract_pdf.shutil.which", lambda name: None)
    monkeypatch.setattr(
        "brain_graph.extract_pdf._extract_with_pypdf",
        lambda path: "MemoryGraft\nAlice\nAbstract\nFallback abstract.\n\nBody text.",
    )

    result = extract_pdf_text(pdf_path)

    assert result == ExtractedPaper(
        title="MemoryGraft",
        authors=["Alice"],
        abstract="Fallback abstract.",
        full_text="MemoryGraft\nAlice\nAbstract\nFallback abstract.\n\nBody text.",
        extractor="pypdf",
    )


def test_extract_pdf_text_returns_empty_result_without_crashing(monkeypatch, tmp_path):
    pdf_path = tmp_path / "memorygraft.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr("brain_graph.extract_pdf.shutil.which", lambda name: None)
    monkeypatch.setattr("brain_graph.extract_pdf._extract_with_pypdf", lambda path: "")

    result = extract_pdf_text(pdf_path)

    assert result == ExtractedPaper(
        title=None,
        authors=[],
        abstract="",
        full_text="",
        extractor="empty",
    )
