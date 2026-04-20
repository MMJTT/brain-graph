import json
from pathlib import Path

import pytest

from brain_graph.import_paper import ImportPaperCommand, import_paper_source


def test_import_pdf_creates_raw_note_asset_and_metadata(tmp_path):
    source_pdf = tmp_path / "MemoryGraft.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")

    raw_path, metadata_path = import_paper_source(
        tmp_path,
        ImportPaperCommand(
            pdf_path=str(source_pdf),
            url=None,
            title=None,
            slug=None,
        ),
        "2026-04-20",
    )

    assert raw_path == tmp_path / "raw" / "papers" / "2026-04-20-memorygraft.md"
    assert metadata_path == tmp_path / "raw" / "metadata" / "papers" / "memorygraft.json"
    assert raw_path.exists()
    assert metadata_path.exists()
    assert (tmp_path / "raw" / "assets" / "papers" / "memorygraft.pdf").read_bytes() == source_pdf.read_bytes()

    raw_text = raw_path.read_text(encoding="utf-8")
    assert "import_source: pdf" in raw_text
    assert "compile_status: imported" in raw_text
    assert "compiled_note: null" in raw_text
    assert "asset_path: raw/assets/papers/memorygraft.pdf" in raw_text
    assert "metadata_path: raw/metadata/papers/memorygraft.json" in raw_text

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata == {
        "slug": "memorygraft",
        "title": "MemoryGraft",
        "source_kind": "pdf",
        "source_path": str(source_pdf),
        "source_url": None,
        "authors": [],
        "abstract": "",
        "full_text_path": None,
        "imported_at": "2026-04-20",
    }


def test_import_url_creates_raw_note_and_metadata(tmp_path):
    raw_path, metadata_path = import_paper_source(
        tmp_path,
        ImportPaperCommand(
            pdf_path=None,
            url="https://arxiv.org/abs/2512.16962",
            title="MemoryGraft",
            slug="memorygraft",
        ),
        "2026-04-20",
    )

    assert raw_path == tmp_path / "raw" / "papers" / "2026-04-20-memorygraft.md"
    assert metadata_path == tmp_path / "raw" / "metadata" / "papers" / "memorygraft.json"
    assert raw_path.exists()
    assert metadata_path.exists()
    assert not (tmp_path / "raw" / "assets" / "papers" / "memorygraft.pdf").exists()

    raw_text = raw_path.read_text(encoding="utf-8")
    assert "import_source: url" in raw_text
    assert "asset_path: null" in raw_text
    assert "metadata_path: raw/metadata/papers/memorygraft.json" in raw_text

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata == {
        "slug": "memorygraft",
        "title": "MemoryGraft",
        "source_kind": "url",
        "source_path": None,
        "source_url": "https://arxiv.org/abs/2512.16962",
        "authors": [],
        "abstract": "",
        "full_text_path": None,
        "imported_at": "2026-04-20",
    }


def test_import_duplicate_slug_fails_without_overwriting(tmp_path):
    source_pdf = tmp_path / "MemoryGraft.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")

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

    with pytest.raises(FileExistsError, match="memorygraft"):
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
