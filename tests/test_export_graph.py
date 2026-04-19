import json
from pathlib import Path

import pytest

from brain_graph.cli import main
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.export_graph import export_graph_files


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


def _seed_graph_notes(tmp_path: Path) -> None:
    for relative_path in [
        "wiki/papers/MemoryGraft.md",
        "wiki/concepts/Semantic Imitation.md",
    ]:
        _copy_fixture(tmp_path, relative_path)

    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__(
            "concept_refs", ["concept-semantic-imitation"]
        ),
        mutate_body=lambda body: f"{body.rstrip()}\n\nSee [[Semantic Imitation]].\n",
    )


def test_export_graph_writes_json_and_mermaid(tmp_path):
    _seed_graph_notes(tmp_path)

    json_path, mermaid_path = export_graph_files(tmp_path)

    assert json_path == tmp_path / "exports" / "brain_graph.json"
    assert mermaid_path == tmp_path / "exports" / "brain_graph.mmd"
    assert json_path.exists()
    assert mermaid_path.exists()

    graph = json.loads(json_path.read_text(encoding="utf-8"))
    assert graph == {
        "nodes": [
            {
                "id": "concept-semantic-imitation",
                "title": "Semantic Imitation",
                "node_type": "concept",
                "status": "seed",
            },
            {
                "id": "paper-memorygraft",
                "title": "MemoryGraft",
                "node_type": "paper",
                "status": "seed",
            },
        ],
        "edges": [
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
        ],
    }
    assert mermaid_path.read_text(encoding="utf-8").startswith("graph LR")


def test_export_graph_cli_prints_output_paths(tmp_path, monkeypatch, capsys):
    _seed_graph_notes(tmp_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["export-graph"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(tmp_path / "exports" / "brain_graph.json") in captured.out
    assert str(tmp_path / "exports" / "brain_graph.mmd") in captured.out
    assert captured.err == ""


def test_export_graph_rejects_duplicate_titles(tmp_path):
    _seed_graph_notes(tmp_path)
    _copy_fixture(tmp_path, "wiki/gaps/Provenance Gap.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/gaps/Provenance Gap.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__(
            "title", "Semantic Imitation"
        ),
    )

    with pytest.raises(ValueError, match="duplicate note title"):
        export_graph_files(tmp_path)


def test_export_graph_cli_reports_validation_errors(tmp_path, monkeypatch, capsys):
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
    assert "duplicate note title" in captured.err
    assert captured.out == ""
