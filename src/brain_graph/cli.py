import argparse
import sys
from datetime import date
from pathlib import Path

from brain_graph.batch_compile import compile_batch
from brain_graph.compile_paper import compile_imported_paper
from brain_graph.import_paper import ImportPaperCommand, import_paper_source
from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry
from brain_graph.export_graph import export_graph_files
from brain_graph.lint import collect_issues
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
    ingest_raw.add_argument("--source-url")
    ingest_raw.add_argument("--summary")

    import_paper = subparsers.add_parser("import-paper", help="Import a paper source.")
    import_source = import_paper.add_mutually_exclusive_group(required=True)
    import_source.add_argument("--pdf")
    import_source.add_argument("--url")
    import_paper.add_argument("--title")
    import_paper.add_argument("--slug")

    compile_paper = subparsers.add_parser("compile-paper", help="Compile one imported paper.")
    compile_paper.add_argument("--slug", required=True)

    compile_batch = subparsers.add_parser(
        "compile-batch", help="Compile imported papers in batch."
    )
    compile_batch.add_argument("--source", default="raw/papers")
    compile_batch.add_argument("--limit", type=int)

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


def _handle_lint() -> int:
    issues = collect_issues(Path.cwd())

    if issues:
        print("\n".join(issues), file=sys.stderr)
        return 1

    print("lint ok")
    return 0


def _handle_export_graph() -> int:
    try:
        json_path, mermaid_path = export_graph_files(Path.cwd())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    canvas_path = Path.cwd() / "views" / "canvas" / "starter.canvas"
    print(json_path)
    print(mermaid_path)
    print(canvas_path)
    return 0


def _handle_import_paper(args: argparse.Namespace) -> int:
    command = ImportPaperCommand(
        pdf_path=args.pdf,
        url=args.url,
        title=args.title,
        slug=args.slug,
    )
    try:
        raw_path, metadata_path = import_paper_source(Path.cwd(), command, date.today().isoformat())
    except (FileExistsError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(raw_path)
    print(metadata_path)
    return 0


def _handle_compile_paper(args: argparse.Namespace) -> int:
    try:
        payload = compile_imported_paper(Path.cwd(), args.slug)
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(payload["paper"]["title"])
    return 0


def _handle_compile_batch(args: argparse.Namespace) -> int:
    try:
        compiled_paths = compile_batch(Path.cwd(), args.source, args.limit)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    for path in compiled_paths:
        print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new-note":
        return _handle_new_note(args)
    if args.command == "ingest-raw":
        return _handle_ingest_raw(args)
    if args.command == "import-paper":
        return _handle_import_paper(args)
    if args.command == "compile-paper":
        return _handle_compile_paper(args)
    if args.command == "compile-batch":
        return _handle_compile_batch(args)
    if args.command == "lint":
        return _handle_lint()
    if args.command == "export-graph":
        return _handle_export_graph()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
