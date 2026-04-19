import argparse
import sys
from pathlib import Path

from brain_graph.models import NOTE_TYPES
from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note", help="Create a new note.")
    new_note.add_argument("--type", required=True, choices=NOTE_TYPES)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", required=True)
    new_note.add_argument("--force", action="store_true")

    subparsers.add_parser("ingest-raw", help="Ingest raw input.")
    subparsers.add_parser("lint", help="Lint the graph.")
    subparsers.add_parser("export-graph", help="Export the graph.")

    return parser


def _handle_new_note(args: argparse.Namespace) -> int:
    command = NewNoteCommand(
        note_type=args.type,
        title=args.title,
        note_id=args.id,
        force=args.force,
    )

    try:
        path = create_note(Path.cwd(), command)
    except FileExistsError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new-note":
        return _handle_new_note(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
