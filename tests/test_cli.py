import json
from pathlib import Path

import pytest

from brain_graph.cli import build_parser, main
from brain_graph.extract_pdf import ExtractedPaper
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def _copy_fixture(tmp_path: Path, relative_path: str) -> None:
    source = FIXTURES_ROOT / relative_path
    target = tmp_path / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _rewrite_fixture(
    tmp_path: Path,
    relative_path: str,
    *,
    mutate_frontmatter=None,
    mutate_body=None,
) -> None:
    target = tmp_path / relative_path
    frontmatter, body = load_frontmatter(target.read_text(encoding="utf-8"))
    if mutate_frontmatter is not None:
        mutate_frontmatter(frontmatter)
    if mutate_body is not None:
        body = mutate_body(body)
    target.write_text(f"{dump_frontmatter(frontmatter)}\n{body}", encoding="utf-8")


def _seed_clean_wiki(tmp_path: Path) -> None:
    for relative_path in [
        "wiki/papers/MemoryGraft.md",
        "wiki/concepts/Semantic Imitation.md",
        "wiki/gaps/Provenance Gap.md",
    ]:
        _copy_fixture(tmp_path, relative_path)


def _seed_graph_notes(tmp_path: Path) -> None:
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _copy_fixture(tmp_path, "wiki/concepts/Semantic Imitation.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__(
            "concept_refs", ["concept-semantic-imitation"]
        ),
        mutate_body=lambda body: f"{body.rstrip()}\n\nSee [[Semantic Imitation]].\n",
    )


def test_cli_parser_wires_expected_subcommands():
    parser = build_parser()

    assert parser.prog == "brain-graph"
    assert (
        parser.parse_args(
            [
                "new-note",
                "--type",
                "paper",
                "--title",
                "MemoryGraft",
                "--id",
                "paper-memorygraft",
            ]
        ).command
        == "new-note"
    )
    assert (
        parser.parse_args(
            [
                "ingest-raw",
                "--kind",
                "paper",
                "--slug",
                "memorygraft",
                "--title",
                "MemoryGraft",
                "--source-url",
                "https://arxiv.org/abs/2512.16962",
            ]
        ).command
        == "ingest-raw"
    )
    assert parser.parse_args(["lint"]).command == "lint"
    assert parser.parse_args(["export-graph"]).command == "export-graph"
    assert (
        parser.parse_args(
            [
                "import-paper",
                "--pdf",
                "/tmp/memorygraft.pdf",
            ]
        ).command
        == "import-paper"
    )
    assert (
        parser.parse_args(
            [
                "compile-paper",
                "--slug",
                "memorygraft",
            ]
        ).command
        == "compile-paper"
    )
    assert (
        parser.parse_args(
            [
                "compile-batch",
                "--source",
                "raw/papers",
                "--limit",
                "2",
            ]
        ).command
        == "compile-batch"
    )
    assert (
        parser.parse_args(["import-paper", "--pdf", "/tmp/memorygraft.pdf"]).command
        == "import-paper"
    )
    assert (
        parser.parse_args(["import-paper", "--url", "https://arxiv.org/abs/2512.16962"]).command
        == "import-paper"
    )
    assert parser.parse_args(["compile-paper", "--slug", "memorygraft"]).command == "compile-paper"
    assert parser.parse_args(["compile-batch"]).command == "compile-batch"
    assert (
        parser.parse_args(["compile-batch", "--source", "raw/papers", "--limit", "20"]).command
        == "compile-batch"
    )


def test_compile_status_constants_are_stable():
    from brain_graph import models

    assert models.COMPILE_STATUS_IMPORTED == "imported"
    assert models.COMPILE_STATUS_COMPILED == "compiled"
    assert models.COMPILE_STATUS_FAILED == "failed"


def test_cli_lint_reports_ok_for_clean_workspace(tmp_path, monkeypatch, capsys):
    _seed_clean_wiki(tmp_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lint"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "lint ok\n"
    assert captured.err == ""


def test_cli_new_note_refuses_to_overwrite_existing_file(tmp_path, monkeypatch, capsys):
    target = tmp_path / "wiki" / "papers" / "MemoryGraft.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("existing note", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        [
            "new-note",
            "--type",
            "paper",
            "--title",
            "MemoryGraft",
            "--id",
            "paper-memorygraft",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "already exists" in captured.err
    assert captured.out == ""


def test_cli_export_graph_creates_expected_files(tmp_path, monkeypatch, capsys):
    _seed_graph_notes(tmp_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["export-graph"])

    captured = capsys.readouterr()
    assert exit_code == 0
    json_path = tmp_path / "exports" / "brain_graph.json"
    mermaid_path = tmp_path / "exports" / "brain_graph.mmd"
    assert json_path.exists()
    assert mermaid_path.exists()
    graph = json.loads(json_path.read_text(encoding="utf-8"))
    assert graph["edges"] == [
        {
            "source": "paper-memorygraft",
            "target": "concept-semantic-imitation",
            "type": "mentions",
        },
        {
            "source": "paper-memorygraft",
            "target": "concept-semantic-imitation",
            "type": "body_link",
        },
    ]
    mermaid = mermaid_path.read_text(encoding="utf-8")
    assert mermaid.startswith("graph LR\n")
    assert "-->|mentions|" in mermaid
    assert str(tmp_path / "exports" / "brain_graph.json") in captured.out
    assert str(tmp_path / "exports" / "brain_graph.mmd") in captured.out
    assert captured.err == ""


def test_cli_lint_reports_failures_on_bad_input(tmp_path, monkeypatch, capsys):
    _seed_clean_wiki(tmp_path)
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_body=lambda body: f"{body.rstrip()}\n\nSee [[Missing Note]].\n",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lint"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "unresolved wikilink: Missing Note" in captured.err


def test_cli_export_graph_reports_validation_errors(tmp_path, monkeypatch, capsys):
    _seed_graph_notes(tmp_path)
    _copy_fixture(tmp_path, "wiki/gaps/Provenance Gap.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/gaps/Provenance Gap.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__(
            "title", "Semantic Imitation"
        ),
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["export-graph"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "duplicate note title" in captured.err


def test_starter_vault_structure_exists():
    root = Path(__file__).resolve().parents[1]

    expected_paths = [
        "discovery/inbox.md",
        "discovery/sources.md",
        "discovery/workflows.md",
        "raw/inbox/.gitkeep",
        "raw/papers/.gitkeep",
        "raw/clips/.gitkeep",
        "raw/metadata/.gitkeep",
        "wiki/papers/.gitkeep",
        "wiki/concepts/.gitkeep",
        "wiki/methods/.gitkeep",
        "wiki/gaps/.gitkeep",
        "wiki/authors/.gitkeep",
        "wiki/maps/.gitkeep",
        "views/canvas/starter.canvas",
        "views/dataview/compilation-queue.md",
        "views/dataview/wiki-index.md",
        "views/graph/README.md",
        "shared/research.md",
    ]

    for relative_path in expected_paths:
        assert (root / relative_path).exists(), relative_path


def test_cli_import_compile_and_export_pipeline(tmp_path, monkeypatch, capsys):
    source_pdf = tmp_path / "MemoryGraft.pdf"
    source_pdf.write_bytes(b"%PDF-1.4 fake pdf bytes")
    monkeypatch.setattr(
        "brain_graph.import_paper.extract_pdf_text",
        lambda path: ExtractedPaper(
            title="MemoryGraft",
            authors=["Alice"],
            abstract="Prompt injection benchmark abstract.",
            full_text="MemoryGraft\nAlice\nAbstract\nPrompt injection benchmark abstract.",
            extractor="pdftotext",
        ),
    )
    monkeypatch.chdir(tmp_path)

    assert main(["import-paper", "--pdf", str(source_pdf)]) == 0
    assert main(["compile-paper", "--slug", "memorygraft"]) == 0
    assert main(["export-graph"]) == 0

    captured = capsys.readouterr()
    assert str(tmp_path / "raw" / "papers" / "2026-04-20-memorygraft.md") in captured.out
    assert str(tmp_path / "wiki" / "papers" / "MemoryGraft.md") in captured.out
    assert str(tmp_path / "views" / "canvas" / "starter.canvas") in captured.out
    assert (tmp_path / "views" / "canvas" / "starter.canvas").exists()
    assert captured.err == ""
