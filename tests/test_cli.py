from pathlib import Path

from brain_graph.cli import build_parser


def test_cli_parser_wires_expected_subcommands():
    parser = build_parser()

    assert parser.prog == "brain-graph"
    for command in ["new-note", "ingest-raw", "lint", "export-graph"]:
        assert parser.parse_args([command]).command == command


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
        "views/dataview/wiki-index.md",
        "views/graph/README.md",
        "shared/research.md",
    ]

    for relative_path in expected_paths:
        assert (root / relative_path).exists(), relative_path
