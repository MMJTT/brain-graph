"""PDF text extraction helpers for Brain Graph imports."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(slots=True)
class ExtractedPaper:
    title: str | None
    authors: list[str]
    abstract: str
    full_text: str
    extractor: str


def extract_pdf_text(path: Path) -> ExtractedPaper:
    if shutil.which("pdftotext"):
        try:
            text = _extract_with_pdftotext(path)
        except (subprocess.CalledProcessError, OSError):
            text = ""
        if text.strip():
            return _build_result(text, "pdftotext")

    try:
        text = _extract_with_pypdf(path)
    except Exception:
        text = ""
    if text.strip():
        return _build_result(text, "pypdf")

    return ExtractedPaper(
        title=None,
        authors=[],
        abstract="",
        full_text="",
        extractor="empty",
    )


def _extract_with_pdftotext(path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _extract_with_pypdf(path: Path) -> str:
    reader = PdfReader(str(path), strict=False)
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts)


def _build_result(text: str, extractor: str) -> ExtractedPaper:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = lines[0] if lines else None

    abstract = ""
    authors: list[str] = []
    if lines and title is not None:
        abstract_index = next(
            (index for index, line in enumerate(lines) if line.lower() == "abstract"),
            None,
        )
        if abstract_index is not None:
            authors = lines[1:abstract_index]
            if abstract_index + 1 < len(lines):
                abstract = lines[abstract_index + 1]

    return ExtractedPaper(
        title=title,
        authors=authors,
        abstract=abstract,
        full_text=text,
        extractor=extractor,
    )
