import argparse

from brain_graph.cli import build_parser

def test_cli_parser_wires_expected_subcommands():
    parser = build_parser()

    assert parser.prog == "brain-graph"
    subparsers_action = next(
        action for action in parser._actions if isinstance(action, argparse._SubParsersAction)
    )
    assert set(subparsers_action.choices) == {
        "new-note",
        "ingest-raw",
        "lint",
        "export-graph",
    }
