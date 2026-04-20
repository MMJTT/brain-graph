# Brain Graph P0 Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first practical Brain Graph pipeline that can import local PDFs or paper links into `raw/`, compile one paper into structured `wiki/` notes, and run batch compilation to grow the graph with minimal manual note creation.

**Architecture:** P0 adds a three-stage pipeline on top of the existing vault. Stage 1 imports a source into `raw/` plus a machine-readable metadata sidecar. Stage 2 extracts normalized paper content and compiles it into `wiki/papers/` plus linked `concept` and `map` notes. Stage 3 runs the same flow in batch so a local folder of papers can become a connected graph with one command.

**Tech Stack:** Python 3.11+, `argparse`, `pathlib`, `json`, `re`, `datetime`, `pypdf`, optional `pdftotext`, Markdown frontmatter notes, Obsidian Canvas, existing `pytest` suite

---

## Scope Guardrails

This P0 plan intentionally does **not** include:

- arXiv RSS or Semantic Scholar syncing
- Connected Papers integration
- multi-model orchestration
- external novelty verification
- Zotero integration

P0 is only about the first usable ingestion-and-compilation loop.

## P0 User-Facing Commands

After P0, the CLI surface should be:

```bash
python -m brain_graph.cli import-paper --pdf /abs/path/to/paper.pdf
python -m brain_graph.cli import-paper --url https://arxiv.org/abs/2512.16962
python -m brain_graph.cli compile-paper --slug memorygraft
python -m brain_graph.cli compile-batch --source raw/papers --limit 20
python -m brain_graph.cli export-graph
python -m brain_graph.cli lint
```

Expected behavior:

- `import-paper` creates append-only raw notes and machine-readable metadata records.
- `compile-paper` reads one imported paper and creates or updates `paper`, `concept`, and `map` notes.
- `compile-batch` loops over uncompiled raw papers and refreshes graph-facing views.

## File Map

### Existing files to modify

- Modify: `src/brain_graph/cli.py`
- Modify: `src/brain_graph/models.py`
- Modify: `src/brain_graph/paths.py`
- Modify: `src/brain_graph/lint.py`
- Modify: `src/brain_graph/export_graph.py`
- Modify: `README.md`
- Modify: `views/graph/README.md`

### New implementation files

- Create: `src/brain_graph/import_paper.py`
- Create: `src/brain_graph/extract_pdf.py`
- Create: `src/brain_graph/compile_paper.py`
- Create: `src/brain_graph/batch_compile.py`
- Create: `src/brain_graph/slugify.py`
- Create: `src/brain_graph/compiler_schema.py`

### New test files

- Create: `tests/test_import_paper.py`
- Create: `tests/test_extract_pdf.py`
- Create: `tests/test_compile_paper.py`
- Create: `tests/test_batch_compile.py`

### New workspace files and folders

- Create: `raw/assets/papers/.gitkeep`
- Create: `raw/metadata/papers/.gitkeep`
- Create: `views/dataview/compilation-queue.md`

## Data Contracts Locked In

### 1. Raw intake note frontmatter

Each imported paper note in `raw/papers/` should include:

```yaml
kind: paper
slug: memorygraft
title: MemoryGraft
import_source: pdf
asset_path: raw/assets/papers/memorygraft.pdf
metadata_path: raw/metadata/papers/memorygraft.json
imported_at: 2026-04-20
compile_status: imported
compiled_note: null
```

### 2. Raw metadata sidecar JSON

Each imported paper should also get one JSON file in `raw/metadata/papers/`:

```json
{
  "slug": "memorygraft",
  "title": "MemoryGraft",
  "source_kind": "pdf",
  "source_path": "/abs/path/to/paper.pdf",
  "source_url": null,
  "authors": [],
  "abstract": "",
  "full_text_path": null,
  "imported_at": "2026-04-20"
}
```

### 3. Compile output contract

`compile-paper` should emit a normalized Python dict with this shape before writing notes:

```python
{
    "paper": {
        "id": "paper-memorygraft",
        "title": "MemoryGraft",
        "summary": "one paragraph",
        "authors": [],
        "raw_refs": ["2026-04-20-memorygraft"],
        "concept_refs": ["Prompt Injection"],
        "method_refs": [],
        "gap_refs": [],
        "related": [],
    },
    "concepts": [
        {
            "title": "Prompt Injection",
            "paper_refs": ["MemoryGraft"],
            "related": [],
        }
    ],
    "maps": [
        {
            "title": "Imported Paper Queue",
            "includes": ["MemoryGraft"],
        }
    ],
}
```

The first implementation may use heuristic extraction. It must be written so an LLM backend can replace the heuristic extractor later without changing the note-writing code.

## Task 1: Expand CLI Surface For P0

**Files:**
- Modify: `src/brain_graph/cli.py`
- Modify: `src/brain_graph/models.py`
- Test: `tests/test_cli.py`

- [ ] Add parser coverage for new subcommands in `tests/test_cli.py`.
- [ ] Run `pytest tests/test_cli.py::test_cli_parser_wires_expected_subcommands -v` and verify it fails because `import-paper`, `compile-paper`, and `compile-batch` are missing.
- [ ] Extend `src/brain_graph/models.py` with compile status constants:

```python
COMPILE_STATUS_IMPORTED = "imported"
COMPILE_STATUS_COMPILED = "compiled"
COMPILE_STATUS_FAILED = "failed"
```

- [ ] Extend `src/brain_graph/cli.py` with these command signatures:

```python
import_paper = subparsers.add_parser("import-paper", help="Import a paper source.")
source_group = import_paper.add_mutually_exclusive_group(required=True)
source_group.add_argument("--pdf")
source_group.add_argument("--url")
import_paper.add_argument("--title")
import_paper.add_argument("--slug")

compile_paper = subparsers.add_parser("compile-paper", help="Compile one imported paper.")
compile_paper.add_argument("--slug", required=True)

compile_batch = subparsers.add_parser("compile-batch", help="Compile imported papers in batch.")
compile_batch.add_argument("--source", default="raw/papers")
compile_batch.add_argument("--limit", type=int)
```

- [ ] Add stub handlers that return non-zero with `NotImplementedError` text until later tasks land.
- [ ] Run `pytest tests/test_cli.py -v` and make sure the CLI parser tests pass.
- [ ] Commit:

```bash
git add src/brain_graph/cli.py src/brain_graph/models.py tests/test_cli.py
git commit -m "feat: add p0 pipeline cli surface"
```

## Task 2: Implement Source Import For Local PDFs And URLs

**Files:**
- Create: `src/brain_graph/import_paper.py`
- Create: `src/brain_graph/slugify.py`
- Modify: `src/brain_graph/paths.py`
- Modify: `src/brain_graph/cli.py`
- Test: `tests/test_import_paper.py`

- [ ] Write failing tests for:
  - importing a local PDF creates one raw note and one metadata sidecar
  - importing a URL creates one raw note and one metadata sidecar
  - duplicate slug import fails without overwriting
- [ ] Run `pytest tests/test_import_paper.py -v` and verify failures.
- [ ] Add path helpers:

```python
def raw_asset_path_for_paper(project_root, slug: str, suffix: str) -> Path:
    return Path(project_root) / "raw" / "assets" / "papers" / f"{slug}{suffix}"


def raw_metadata_path_for_paper(project_root, slug: str) -> Path:
    return Path(project_root) / "raw" / "metadata" / "papers" / f"{slug}.json"
```

- [ ] Add a focused slug helper:

```python
def slugify_title(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
```

- [ ] Implement `ImportPaperCommand` in `src/brain_graph/import_paper.py`:

```python
@dataclass(slots=True)
class ImportPaperCommand:
    pdf_path: str | None
    url: str | None
    title: str | None
    slug: str | None
```

- [ ] Import behavior:
  - For `--pdf`, infer title from filename when `--title` is absent.
  - Copy the PDF into `raw/assets/papers/`.
  - Write raw note under `raw/papers/YYYY-MM-DD-<slug>.md`.
  - Write metadata sidecar JSON under `raw/metadata/papers/<slug>.json`.
  - Set `imported_at` on the raw note frontmatter.
  - Set `compile_status: imported`.
- [ ] For `--url`, do not fetch remote content yet. Store the URL and create the same raw note plus metadata sidecar with `source_kind: url`.
- [ ] Wire the handler into `src/brain_graph/cli.py`.
- [ ] Run `pytest tests/test_import_paper.py -v` and then `pytest tests/test_cli.py -v`.
- [ ] Commit:

```bash
git add src/brain_graph/import_paper.py src/brain_graph/slugify.py src/brain_graph/paths.py src/brain_graph/cli.py tests/test_import_paper.py tests/test_cli.py
git commit -m "feat: add paper import pipeline"
```

## Task 3: Add PDF Extraction Layer

**Files:**
- Create: `src/brain_graph/extract_pdf.py`
- Modify: `src/brain_graph/import_paper.py`
- Test: `tests/test_extract_pdf.py`

- [ ] Write failing tests for:
  - `extract_pdf_text()` prefers `pdftotext` when available
  - extraction falls back to `pypdf` when `pdftotext` is unavailable
  - empty extraction returns a structured failure result instead of crashing
- [ ] Run `pytest tests/test_extract_pdf.py -v` and verify failures.
- [ ] Implement extractor result contract:

```python
@dataclass(slots=True)
class ExtractedPaper:
    title: str | None
    authors: list[str]
    abstract: str
    full_text: str
    extractor: str
```

- [ ] Implement:
  - `_extract_with_pdftotext(path: Path) -> str`
  - `_extract_with_pypdf(path: Path) -> str`
  - `extract_pdf_text(path: Path) -> ExtractedPaper`
- [ ] Keep heuristics minimal:
  - title = first non-empty line
  - abstract = paragraph after the word `Abstract` when found
  - authors = lines between title and abstract if obvious; otherwise `[]`
- [ ] Update metadata sidecar writes so imported PDFs can store extracted text in:

```json
{
  "title": "...",
  "authors": [],
  "abstract": "...",
  "full_text_path": "raw/metadata/papers/memorygraft.txt",
  "extractor": "pdftotext"
}
```

- [ ] Run `pytest tests/test_extract_pdf.py -v` and `pytest tests/test_import_paper.py -v`.
- [ ] Commit:

```bash
git add src/brain_graph/extract_pdf.py src/brain_graph/import_paper.py tests/test_extract_pdf.py tests/test_import_paper.py
git commit -m "feat: add pdf extraction layer"
```

## Task 4: Compile One Raw Paper Into Wiki Notes

**Files:**
- Create: `src/brain_graph/compiler_schema.py`
- Create: `src/brain_graph/compile_paper.py`
- Modify: `src/brain_graph/cli.py`
- Modify: `src/brain_graph/templates.py`
- Modify: `src/brain_graph/lint.py`
- Test: `tests/test_compile_paper.py`

- [ ] Write failing tests for:
  - compiling one imported paper creates `wiki/papers/<Title>.md`
  - compile updates or creates linked concept notes
  - compile updates `compile_status` to `compiled`
  - re-running `compile-paper` is idempotent
- [ ] Run `pytest tests/test_compile_paper.py -v` and verify failures.
- [ ] Add a compiler schema helper that validates the normalized compile dict before any notes are written.
- [ ] Implement a heuristic first-pass compiler in `src/brain_graph/compile_paper.py`:

```python
def compile_imported_paper(project_root: Path, slug: str) -> dict[str, object]:
    ...
```

- [ ] Minimal heuristic rules:
  - paper title comes from metadata JSON, falling back to raw note title
  - summary comes from abstract, falling back to first paragraph of extracted text
  - concept candidates come from keyword matches:
    - `prompt injection` -> `Prompt Injection`
    - `environmental injection` -> `Environmental Injection`
    - `multimodal agent` -> `Multimodal Agents`
    - `benchmark` -> `Agent Benchmarks`
    - `defense` -> `Agent Defenses`
  - no `method` or `gap` generation yet unless explicit keywords are found
- [ ] Write note upsert helpers:
  - create the paper note if missing
  - update `paper_refs` on concept notes without duplicating entries
  - keep manual body sections intact when the note already exists by only rewriting frontmatter plus a compiler-managed summary block
- [ ] Update raw note frontmatter with:

```yaml
compile_status: compiled
compiled_note: wiki/papers/MemoryGraft.md
```

- [ ] Run `pytest tests/test_compile_paper.py -v`, then `pytest tests/test_lint.py -v`.
- [ ] Commit:

```bash
git add src/brain_graph/compiler_schema.py src/brain_graph/compile_paper.py src/brain_graph/cli.py src/brain_graph/templates.py src/brain_graph/lint.py tests/test_compile_paper.py tests/test_lint.py
git commit -m "feat: compile imported papers into wiki notes"
```

## Task 5: Batch Compilation And Map Refresh

**Files:**
- Create: `src/brain_graph/batch_compile.py`
- Modify: `src/brain_graph/cli.py`
- Modify: `src/brain_graph/export_graph.py`
- Modify: `views/graph/README.md`
- Create: `views/dataview/compilation-queue.md`
- Test: `tests/test_batch_compile.py`

- [ ] Write failing tests for:
  - `compile-batch` compiles multiple imported papers
  - `compile-batch --limit 2` stops after two papers
  - batch compile refreshes graph exports and starter canvas
- [ ] Run `pytest tests/test_batch_compile.py -v` and verify failures.
- [ ] Implement:

```python
def compile_batch(project_root: Path, source: str, limit: int | None) -> list[Path]:
    ...
```

- [ ] Batch selection rules:
  - read all `raw/papers/*.md`
  - skip entries whose `compile_status` is already `compiled`
  - process oldest imported items first
- [ ] After batch completion, always call:

```python
collect_issues(project_root)
export_graph_files(project_root)
```

- [ ] Add one maintained map note named `Imported Paper Queue` if missing. This map should list the most recently compiled papers and link to the four topical maps when present.
- [ ] Create `views/dataview/compilation-queue.md` with a Dataview table over raw papers:

```dataview
TABLE compile_status, imported_at
FROM "raw/papers"
SORT file.name ASC
```

- [ ] Run `pytest tests/test_batch_compile.py -v`, then `pytest tests/test_export_graph.py -v`.
- [ ] Commit:

```bash
git add src/brain_graph/batch_compile.py src/brain_graph/cli.py src/brain_graph/export_graph.py views/graph/README.md views/dataview/compilation-queue.md tests/test_batch_compile.py tests/test_export_graph.py
git commit -m "feat: add batch paper compilation"
```

## Task 6: End-To-End Docs And Verification

**Files:**
- Modify: `README.md`
- Modify: `views/graph/README.md`
- Test: `tests/test_cli.py`

- [ ] Update `README.md` with a P0 quickstart:

```bash
python -m brain_graph.cli import-paper --pdf /Users/me/Desktop/papers/foo.pdf
python -m brain_graph.cli compile-paper --slug foo
python -m brain_graph.cli compile-batch --source raw/papers
python -m brain_graph.cli lint
python -m brain_graph.cli export-graph
```

- [ ] Document the intended P0 workflow:
  - import source
  - inspect raw note
  - compile one paper
  - batch compile the queue
  - open `views/canvas/starter.canvas` in Obsidian
- [ ] Add one CLI integration test that covers:
  - import one sample paper
  - compile it
  - export graph
  - assert that `starter.canvas` exists
- [ ] Run the full verification suite:

```bash
pytest -q
python -m brain_graph.cli lint
python -m brain_graph.cli export-graph
```

- [ ] Commit:

```bash
git add README.md views/graph/README.md tests/test_cli.py
git commit -m "docs: document p0 paper pipeline"
```

## Execution Order

Implement tasks strictly in this order:

1. CLI surface
2. Source import
3. PDF extraction
4. Single-paper compile
5. Batch compile
6. Docs and end-to-end verification

Do not start arXiv or Semantic Scholar work before Task 6 is merged. That belongs to P1.

## Success Criteria

P0 is complete when all of the following are true:

- A local PDF can be imported with one command.
- An arXiv or paper URL can be registered into `raw/` with one command.
- One imported paper can be compiled into a `wiki/papers/` note without hand-writing the note.
- At least one linked concept note is created automatically when keywords match.
- A batch command can process a folder of raw papers and refresh the canvas plus graph exports.
- `pytest -q`, `brain_graph.cli lint`, and `brain_graph.cli export-graph` all pass after the workflow runs.

## Self-Review

- Spec coverage: This plan only targets P0 and intentionally leaves discovery sync, multi-model workflows, and novelty validation for later phases.
- Placeholder scan: No `TODO` or `TBD` markers remain; each task names files, commands, and expected behavior.
- Type consistency: Command names, metadata keys, and compile status values are consistent across tasks.
