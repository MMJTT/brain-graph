import argparse
import sys
from datetime import date
from pathlib import Path

from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry
from brain_graph.models import NOTE_TYPES, RAW_KINDS
from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note", help="Create a new note.")
    new_note.add_argument("--type", required=True, choices=NOTE_TYPES)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", required=True)
    new_note.add_argument("--force", action="store_true")

    ingest_raw = subparsers.add_parser("ingest-raw", help="Ingest raw input.")
    ingest_raw.add_argument("--kind", required=True, choices=RAW_KINDS)
    ingest_raw.add_argument("--slug", required=True)
    ingest_raw.add_argument("--title", required=True)
    ingest_raw.add_argument("--source-url", required=True)
    ingest_raw.add_argument("--summary")
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


def _handle_ingest_raw(args: argparse.Namespace) -> int:
    command = IngestRawCommand(
        kind=args.kind,
        slug=args.slug,
        title=args.title,
        source_url=args.source_url,
        summary=args.summary,
    )

    try:
        path = ingest_raw_entry(Path.cwd(), command, date.today().isoformat())
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
    if args.command == "ingest-raw":
        return _handle_ingest_raw(args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
