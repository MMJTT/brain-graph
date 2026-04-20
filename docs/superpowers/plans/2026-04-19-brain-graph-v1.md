# Brain Graph V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, local-first Brain Graph workspace with an Obsidian-friendly folder structure, Python CLI, note templates, linting, and graph export.

**Architecture:** The project uses Markdown as the source of truth, organized into `raw/`, `wiki/`, `views/`, and companion folders. A focused Python package under `src/brain_graph/` provides CLI commands for note creation, raw ingestion, structural linting, and graph export, while tests validate behavior through small fixtures and end-to-end command execution.

**Tech Stack:** Python 3.11+, `pytest`, `argparse`, `pathlib`, `json`, `re`, `textwrap`, `datetime`, Markdown files, Obsidian-compatible vault structure

---

## File Map

### Project structure to create

- Create: `README.md`
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `discovery/inbox.md`
- Create: `discovery/sources.md`
- Create: `discovery/workflows.md`
- Create: `raw/inbox/.gitkeep`
- Create: `raw/papers/.gitkeep`
- Create: `raw/clips/.gitkeep`
- Create: `raw/metadata/.gitkeep`
- Create: `wiki/papers/.gitkeep`
- Create: `wiki/concepts/.gitkeep`
- Create: `wiki/methods/.gitkeep`
- Create: `wiki/gaps/.gitkeep`
- Create: `wiki/authors/.gitkeep`
- Create: `wiki/maps/.gitkeep`
- Create: `views/canvas/starter.canvas`
- Create: `views/dataview/wiki-index.md`
- Create: `views/graph/README.md`
- Create: `shared/research.md`
- Create: `templates/paper.md`
- Create: `templates/concept.md`
- Create: `templates/method.md`
- Create: `templates/gap.md`
- Create: `templates/author.md`
- Create: `templates/map.md`
- Create: `exports/.gitkeep`
- Create: `src/brain_graph/__init__.py`
- Create: `src/brain_graph/cli.py`
- Create: `src/brain_graph/paths.py`
- Create: `src/brain_graph/models.py`
- Create: `src/brain_graph/frontmatter.py`
- Create: `src/brain_graph/templates.py`
- Create: `src/brain_graph/new_note.py`
- Create: `src/brain_graph/ingest_raw.py`
- Create: `src/brain_graph/lint.py`
- Create: `src/brain_graph/export_graph.py`
- Create: `tests/conftest.py`
- Create: `tests/test_cli.py`
- Create: `tests/test_templates.py`
- Create: `tests/test_new_note.py`
- Create: `tests/test_ingest_raw.py`
- Create: `tests/test_lint.py`
- Create: `tests/test_export_graph.py`
- Create: `tests/fixtures/wiki/papers/MemoryGraft.md`
- Create: `tests/fixtures/wiki/concepts/Semantic Imitation.md`
- Create: `tests/fixtures/wiki/gaps/Provenance Gap.md`

### File responsibilities

- `src/brain_graph/paths.py`: central project paths, folder routing, note type to directory mapping
- `src/brain_graph/models.py`: note type constants, dataclasses, and validation rules
- `src/brain_graph/frontmatter.py`: parse and render minimal YAML-like frontmatter without extra runtime dependencies
- `src/brain_graph/templates.py`: template registry and variable substitution
- `src/brain_graph/new_note.py`: create curated wiki notes from templates
- `src/brain_graph/ingest_raw.py`: create append-only raw records
- `src/brain_graph/lint.py`: collect and report structural issues
- `src/brain_graph/export_graph.py`: transform notes into graph nodes and edges and write JSON and Mermaid
- `src/brain_graph/cli.py`: command wiring and terminal output
- `tests/*`: command-level and module-level verification

## Conventions Locked In

- Supported note types: `paper`, `concept`, `method`, `gap`, `author`, `map`
- Wiki note target directories:
  - `paper` -> `wiki/papers/`
  - `concept` -> `wiki/concepts/`
  - `method` -> `wiki/methods/`
  - `gap` -> `wiki/gaps/`
  - `author` -> `wiki/authors/`
  - `map` -> `wiki/maps/`
- Raw ingest kinds for v1: `paper`, `clip`, `metadata`
- Shared frontmatter keys:
  - `id`
  - `title`
  - `node_type`
  - `status`
  - `tags`
  - `created`
  - `updated`
  - `source_refs`
  - `related`
- Link extraction pattern: `[[Target]]`
- Exported edge labels:
  - `related_to` for explicit `related`
  - `supports_reference` for `source_refs`
  - `body_link` for wikilinks in note bodies
  - type-specific labels from list fields:
    - `concept_refs` -> `mentions`
    - `method_refs` -> `uses`
    - `gap_refs` -> `raises_gap`
    - `paper_refs` -> `supports`
    - `introduced_by` -> `introduces`
    - `raised_by` -> `raises_gap`

### Task 1: Scaffold The Repository And CLI Entry Point

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `src/brain_graph/__init__.py`
- Create: `src/brain_graph/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI smoke test**

```python
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "brain_graph.cli", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_help_lists_commands() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "new-note" in result.stdout
    assert "ingest-raw" in result.stdout
    assert "lint" in result.stdout
    assert "export-graph" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_cli_help_lists_commands -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'brain_graph'`

- [ ] **Step 3: Write minimal package and CLI implementation**

```python
# src/brain_graph/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"
```

```python
# src/brain_graph/cli.py
from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("new-note")
    subparsers.add_parser("ingest-raw")
    subparsers.add_parser("lint")
    subparsers.add_parser("export-graph")
    return parser


def main() -> int:
    parser = build_parser()
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "brain-graph"
version = "0.1.0"
description = "Local-first Brain Graph workspace"
requires-python = ">=3.11"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

```gitignore
# .gitignore
__pycache__/
.pytest_cache/
*.pyc
.DS_Store
```

```markdown
# README.md

# Brain Graph

Local-first research brain built around Markdown, Obsidian, and a small Python CLI.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_cli_help_lists_commands -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md .gitignore pyproject.toml src/brain_graph/__init__.py src/brain_graph/cli.py tests/test_cli.py
git commit -m "feat: scaffold brain graph cli"
```

### Task 2: Create The Vault Directory Layout And Starter Files

**Files:**
- Create: `discovery/inbox.md`
- Create: `discovery/sources.md`
- Create: `discovery/workflows.md`
- Create: `raw/inbox/.gitkeep`
- Create: `raw/papers/.gitkeep`
- Create: `raw/clips/.gitkeep`
- Create: `raw/metadata/.gitkeep`
- Create: `wiki/papers/.gitkeep`
- Create: `wiki/concepts/.gitkeep`
- Create: `wiki/methods/.gitkeep`
- Create: `wiki/gaps/.gitkeep`
- Create: `wiki/authors/.gitkeep`
- Create: `wiki/maps/.gitkeep`
- Create: `views/canvas/starter.canvas`
- Create: `views/dataview/wiki-index.md`
- Create: `views/graph/README.md`
- Create: `shared/research.md`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing structure test**

```python
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_project_layout_exists() -> None:
    expected_paths = [
        PROJECT_ROOT / "discovery" / "inbox.md",
        PROJECT_ROOT / "raw" / "papers" / ".gitkeep",
        PROJECT_ROOT / "wiki" / "papers" / ".gitkeep",
        PROJECT_ROOT / "views" / "canvas" / "starter.canvas",
        PROJECT_ROOT / "shared" / "research.md",
    ]
    for path in expected_paths:
        assert path.exists(), f"missing {path}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_project_layout_exists -v`
Expected: FAIL with one or more missing path assertions

- [ ] **Step 3: Create the starter vault files**

```markdown
# discovery/inbox.md

# Discovery Inbox

- Add paper leads here before promoting them into `raw/` or `wiki/`.
```

```markdown
# discovery/sources.md

# Sources

- arXiv
- Semantic Scholar
- Connected Papers
- Manual reading queue
```

```markdown
# discovery/workflows.md

# Workflows

1. Capture candidate in `discovery/inbox.md`
2. Ingest raw material into `raw/`
3. Curate structured notes into `wiki/`
4. Run `lint`
5. Run `export-graph`
```

```json
{
  "nodes": [
    {
      "id": "starter-map",
      "type": "text",
      "text": "Brain Graph starter canvas"
    }
  ],
  "edges": []
}
```

```markdown
# views/dataview/wiki-index.md

# Wiki Index

```dataview
TABLE node_type, status, updated
FROM "wiki"
SORT updated DESC
```
```

```markdown
# views/graph/README.md

# Graph Views

- Use `exports/brain_graph.mmd` for Mermaid previews.
- Use Obsidian Graph View for backlink exploration.
```

```markdown
# shared/research.md

# Shared Research Scratchpad

Use this file for temporary debate, synthesis, and cross-model comparison.
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_project_layout_exists -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add discovery raw wiki views shared tests/test_cli.py
git commit -m "feat: add brain graph vault layout"
```

### Task 3: Add Core Models, Path Routing, And Frontmatter Parsing

**Files:**
- Create: `src/brain_graph/paths.py`
- Create: `src/brain_graph/models.py`
- Create: `src/brain_graph/frontmatter.py`
- Test: `tests/test_templates.py`

- [ ] **Step 1: Write the failing core utility tests**

```python
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.paths import note_path_for_type


def test_note_path_for_type_routes_to_expected_folder(tmp_path: Path) -> None:
    assert note_path_for_type(tmp_path, "paper", "MemoryGraft").as_posix().endswith("wiki/papers/MemoryGraft.md")
    assert note_path_for_type(tmp_path, "gap", "Provenance Gap").as_posix().endswith("wiki/gaps/Provenance Gap.md")


def test_frontmatter_round_trip_preserves_lists() -> None:
    content = dump_frontmatter(
        {
            "id": "paper-memorygraft",
            "title": "MemoryGraft",
            "node_type": "paper",
            "tags": ["attacks", "memory"],
            "related": ["concept-semantic-imitation"],
        }
    )
    payload, body = load_frontmatter(content + "\nBody line\n")
    assert payload["id"] == "paper-memorygraft"
    assert payload["tags"] == ["attacks", "memory"]
    assert body.strip() == "Body line"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_templates.py -v`
Expected: FAIL with import errors for `brain_graph.paths` and `brain_graph.frontmatter`

- [ ] **Step 3: Write the core utility modules**

```python
# src/brain_graph/models.py
from __future__ import annotations

NOTE_TYPES = ("paper", "concept", "method", "gap", "author", "map")
RAW_KINDS = ("paper", "clip", "metadata")

WIKI_DIRS = {
    "paper": "papers",
    "concept": "concepts",
    "method": "methods",
    "gap": "gaps",
    "author": "authors",
    "map": "maps",
}

TEMPLATE_FIELDS = {
    "paper": ["year", "venue", "authors", "paper_url", "raw_refs", "concept_refs", "method_refs", "gap_refs"],
    "concept": ["aliases", "parent_concepts", "paper_refs", "method_refs"],
    "method": ["introduced_by", "applies_to", "limitations"],
    "gap": ["gap_kind", "raised_by", "potential_directions"],
    "author": ["affiliation", "paper_refs"],
    "map": ["focus", "includes", "questions"],
}
```

```python
# src/brain_graph/paths.py
from __future__ import annotations

from pathlib import Path

from brain_graph.models import WIKI_DIRS


def note_path_for_type(project_root: Path, note_type: str, title: str) -> Path:
    folder = WIKI_DIRS[note_type]
    return project_root / "wiki" / folder / f"{title}.md"


def raw_path_for_kind(project_root: Path, kind: str, slug: str, date_text: str) -> Path:
    folder_map = {"paper": "papers", "clip": "clips", "metadata": "metadata"}
    folder = folder_map[kind]
    return project_root / "raw" / folder / f"{date_text}-{slug}.md"
```

```python
# src/brain_graph/frontmatter.py
from __future__ import annotations

from typing import Any


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def load_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    _, rest = text.split("---\n", 1)
    raw_frontmatter, body = rest.split("\n---\n", 1)
    payload: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in raw_frontmatter.splitlines():
        if line.startswith("  - ") and current_list_key:
            payload[current_list_key].append(line[4:])
            continue
        key, value = line.split(": ", 1) if ": " in line else (line[:-1], "")
        if value == "":
            payload[key] = []
            current_list_key = key
        else:
            payload[key] = value
            current_list_key = None
    return payload, body
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_templates.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/brain_graph/models.py src/brain_graph/paths.py src/brain_graph/frontmatter.py tests/test_templates.py
git commit -m "feat: add core models and frontmatter utilities"
```

### Task 4: Add Markdown Templates And Rendering

**Files:**
- Create: `templates/paper.md`
- Create: `templates/concept.md`
- Create: `templates/method.md`
- Create: `templates/gap.md`
- Create: `templates/author.md`
- Create: `templates/map.md`
- Create: `src/brain_graph/templates.py`
- Test: `tests/test_templates.py`

- [ ] **Step 1: Write the failing template rendering test**

```python
from pathlib import Path

from brain_graph.templates import render_template


def test_render_template_includes_frontmatter_and_sections(tmp_path: Path) -> None:
    project_root = tmp_path
    templates_dir = project_root / "templates"
    templates_dir.mkdir()
    (templates_dir / "paper.md").write_text(
        "## Summary\n\n- Key idea\n",
        encoding="utf-8",
    )
    rendered = render_template(
        project_root,
        note_type="paper",
        title="MemoryGraft",
        note_id="paper-memorygraft",
        created="2026-04-19",
    )
    assert "id: paper-memorygraft" in rendered
    assert "title: MemoryGraft" in rendered
    assert "node_type: paper" in rendered
    assert "## Summary" in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_templates.py::test_render_template_includes_frontmatter_and_sections -v`
Expected: FAIL with import error for `brain_graph.templates`

- [ ] **Step 3: Write template files and renderer**

```markdown
<!-- templates/paper.md -->
## Summary

-

## Claims

-

## Evidence

-

## Links

- Concepts:
- Methods:
- Gaps:
```

```markdown
<!-- templates/concept.md -->
## Definition

-

## Why It Matters

-

## Related Papers

-
```

```markdown
<!-- templates/method.md -->
## Mechanism

-

## Inputs

-

## Limitations

-
```

```markdown
<!-- templates/gap.md -->
## Gap Statement

-

## Why Unresolved

-

## Potential Directions

-
```

```markdown
<!-- templates/author.md -->
## Profile

-

## Related Work

-
```

```markdown
<!-- templates/map.md -->
## Focus

-

## Included Nodes

-

## Open Questions

-
```

```python
# src/brain_graph/templates.py
from __future__ import annotations

from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.models import TEMPLATE_FIELDS


def _base_payload(note_type: str, title: str, note_id: str, created: str) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": note_id,
        "title": title,
        "node_type": note_type,
        "status": "seed",
        "tags": [],
        "created": created,
        "updated": created,
        "source_refs": [],
        "related": [],
    }
    for field in TEMPLATE_FIELDS[note_type]:
        payload[field] = []
    return payload


def render_template(project_root: Path, note_type: str, title: str, note_id: str, created: str) -> str:
    template_path = project_root / "templates" / f"{note_type}.md"
    body = template_path.read_text(encoding="utf-8").strip()
    frontmatter = dump_frontmatter(_base_payload(note_type, title, note_id, created))
    return f"{frontmatter}\n\n{body}\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_templates.py::test_render_template_includes_frontmatter_and_sections -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add templates src/brain_graph/templates.py tests/test_templates.py
git commit -m "feat: add note templates and renderer"
```

### Task 5: Implement `new-note` With TDD

**Files:**
- Create: `src/brain_graph/new_note.py`
- Modify: `src/brain_graph/cli.py`
- Test: `tests/test_new_note.py`

- [ ] **Step 1: Write the failing `new-note` command tests**

```python
from pathlib import Path
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "brain_graph.cli", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        env=env,
    )


def test_new_note_creates_paper_note(tmp_path: Path) -> None:
    (tmp_path / "templates").mkdir()
    (tmp_path / "wiki" / "papers").mkdir(parents=True)
    (tmp_path / "templates" / "paper.md").write_text("## Summary\n", encoding="utf-8")
    result = run_cli(tmp_path, "new-note", "--type", "paper", "--title", "MemoryGraft", "--id", "paper-memorygraft")
    assert result.returncode == 0
    note_path = tmp_path / "wiki" / "papers" / "MemoryGraft.md"
    assert note_path.exists()
    content = note_path.read_text(encoding="utf-8")
    assert "id: paper-memorygraft" in content
    assert "node_type: paper" in content


def test_new_note_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    paper_dir = tmp_path / "wiki" / "papers"
    paper_dir.mkdir(parents=True)
    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "paper.md").write_text("## Summary\n", encoding="utf-8")
    target = paper_dir / "MemoryGraft.md"
    target.write_text("existing", encoding="utf-8")
    result = run_cli(tmp_path, "new-note", "--type", "paper", "--title", "MemoryGraft", "--id", "paper-memorygraft")
    assert result.returncode == 1
    assert "already exists" in result.stderr
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_new_note.py -v`
Expected: FAIL because `new-note` is not wired and no file is created

- [ ] **Step 3: Write the minimal implementation**

```python
# src/brain_graph/new_note.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from brain_graph.paths import note_path_for_type
from brain_graph.templates import render_template


@dataclass
class NewNoteCommand:
    note_type: str
    title: str
    note_id: str
    force: bool = False


def create_note(project_root: Path, command: NewNoteCommand) -> Path:
    target = note_path_for_type(project_root, command.note_type, command.title)
    if target.exists() and not command.force:
        raise FileExistsError(f"{target} already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    content = render_template(
        project_root=project_root,
        note_type=command.note_type,
        title=command.title,
        note_id=command.note_id,
        created=date.today().isoformat(),
    )
    target.write_text(content, encoding="utf-8")
    return target
```

```python
# src/brain_graph/cli.py
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note")
    new_note.add_argument("--type", dest="note_type", required=True)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", dest="note_id", required=True)
    new_note.add_argument("--force", action="store_true")

    subparsers.add_parser("ingest-raw")
    subparsers.add_parser("lint")
    subparsers.add_parser("export-graph")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path.cwd()

    if args.command == "new-note":
        try:
            target = create_note(
                project_root,
                NewNoteCommand(
                    note_type=args.note_type,
                    title=args.title,
                    note_id=args.note_id,
                    force=args.force,
                ),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    return 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_new_note.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/brain_graph/new_note.py src/brain_graph/cli.py tests/test_new_note.py
git commit -m "feat: add new-note command"
```

### Task 6: Implement `ingest-raw` With Append-Only Semantics

**Files:**
- Create: `src/brain_graph/ingest_raw.py`
- Modify: `src/brain_graph/cli.py`
- Test: `tests/test_ingest_raw.py`

- [ ] **Step 1: Write the failing `ingest-raw` tests**

```python
from pathlib import Path

from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry


def test_ingest_raw_creates_timestamped_file(tmp_path: Path) -> None:
    command = IngestRawCommand(kind="paper", slug="memorygraft", title="MemoryGraft", source_url="https://arxiv.org/abs/2512.16962")
    target = ingest_raw_entry(tmp_path, command, date_text="2026-04-19")
    assert target.as_posix().endswith("raw/papers/2026-04-19-memorygraft.md")
    content = target.read_text(encoding="utf-8")
    assert "# MemoryGraft" in content
    assert "source_url: https://arxiv.org/abs/2512.16962" in content


def test_ingest_raw_never_overwrites_existing_file(tmp_path: Path) -> None:
    target_dir = tmp_path / "raw" / "papers"
    target_dir.mkdir(parents=True)
    existing = target_dir / "2026-04-19-memorygraft.md"
    existing.write_text("exists", encoding="utf-8")
    command = IngestRawCommand(kind="paper", slug="memorygraft", title="MemoryGraft")
    try:
        ingest_raw_entry(tmp_path, command, date_text="2026-04-19")
    except FileExistsError as exc:
        assert "append-only" in str(exc)
    else:
        raise AssertionError("expected FileExistsError")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ingest_raw.py -v`
Expected: FAIL with import error for `brain_graph.ingest_raw`

- [ ] **Step 3: Write the minimal implementation**

```python
# src/brain_graph/ingest_raw.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from brain_graph.frontmatter import dump_frontmatter
from brain_graph.paths import raw_path_for_kind


@dataclass
class IngestRawCommand:
    kind: str
    slug: str
    title: str
    source_url: str = ""
    summary: str = ""


def ingest_raw_entry(project_root: Path, command: IngestRawCommand, date_text: str) -> Path:
    target = raw_path_for_kind(project_root, command.kind, command.slug, date_text)
    if target.exists():
        raise FileExistsError(f"{target} already exists; raw is append-only")
    target.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = dump_frontmatter(
        {
            "kind": command.kind,
            "slug": command.slug,
            "title": command.title,
            "created": date_text,
            "source_url": command.source_url,
        }
    )
    body = f"# {command.title}\n\n{command.summary}\n"
    target.write_text(f"{frontmatter}\n\n{body}", encoding="utf-8")
    return target
```

```python
# src/brain_graph/cli.py
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry
from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note")
    new_note.add_argument("--type", dest="note_type", required=True)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", dest="note_id", required=True)
    new_note.add_argument("--force", action="store_true")

    ingest = subparsers.add_parser("ingest-raw")
    ingest.add_argument("--kind", required=True)
    ingest.add_argument("--slug", required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--source-url", default="")
    ingest.add_argument("--summary", default="")

    subparsers.add_parser("lint")
    subparsers.add_parser("export-graph")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path.cwd()

    if args.command == "new-note":
        try:
            target = create_note(
                project_root,
                NewNoteCommand(
                    note_type=args.note_type,
                    title=args.title,
                    note_id=args.note_id,
                    force=args.force,
                ),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    if args.command == "ingest-raw":
        try:
            target = ingest_raw_entry(
                project_root,
                IngestRawCommand(
                    kind=args.kind,
                    slug=args.slug,
                    title=args.title,
                    source_url=args.source_url,
                    summary=args.summary,
                ),
                date_text=date.today().isoformat(),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    return 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_ingest_raw.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/brain_graph/ingest_raw.py src/brain_graph/cli.py tests/test_ingest_raw.py
git commit -m "feat: add append-only raw ingestion"
```

### Task 7: Implement Linting For Schema, IDs, And Links

**Files:**
- Create: `src/brain_graph/lint.py`
- Modify: `src/brain_graph/cli.py`
- Test: `tests/test_lint.py`
- Create: `tests/fixtures/wiki/papers/MemoryGraft.md`
- Create: `tests/fixtures/wiki/concepts/Semantic Imitation.md`
- Create: `tests/fixtures/wiki/gaps/Provenance Gap.md`

- [ ] **Step 1: Write the failing lint tests**

```python
from pathlib import Path

from brain_graph.lint import collect_issues


def write_note(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_lint_detects_missing_required_field(tmp_path: Path) -> None:
    write_note(
        tmp_path / "wiki" / "papers" / "MemoryGraft.md",
        "---\n"
        "title: MemoryGraft\n"
        "node_type: paper\n"
        "status: seed\n"
        "tags:\n"
        "source_refs:\n"
        "related:\n"
        "---\n\n"
        "Body\n",
    )
    issues = collect_issues(tmp_path)
    assert any("missing required field: id" in issue for issue in issues)


def test_lint_detects_broken_wikilink_and_duplicate_id(tmp_path: Path) -> None:
    note = (
        "---\n"
        "id: paper-memorygraft\n"
        "title: MemoryGraft\n"
        "node_type: paper\n"
        "status: seed\n"
        "tags:\n"
        "created: 2026-04-19\n"
        "updated: 2026-04-19\n"
        "source_refs:\n"
        "related:\n"
        "---\n\n"
        "See [[Missing Note]].\n"
    )
    write_note(tmp_path / "wiki" / "papers" / "MemoryGraft.md", note)
    write_note(tmp_path / "wiki" / "papers" / "Duplicate.md", note)
    issues = collect_issues(tmp_path)
    assert any("broken wikilink: Missing Note" in issue for issue in issues)
    assert any("duplicate id: paper-memorygraft" in issue for issue in issues)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_lint.py -v`
Expected: FAIL with import error for `brain_graph.lint`

- [ ] **Step 3: Write the lint implementation**

```python
# src/brain_graph/lint.py
from __future__ import annotations

import re
from pathlib import Path

from brain_graph.frontmatter import load_frontmatter
from brain_graph.models import NOTE_TYPES


REQUIRED_FIELDS = {"id", "title", "node_type", "status", "tags", "created", "updated", "source_refs", "related"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def _wiki_notes(project_root: Path) -> list[Path]:
    return sorted((project_root / "wiki").glob("*/*.md"))


def collect_issues(project_root: Path) -> list[str]:
    issues: list[str] = []
    notes = _wiki_notes(project_root)
    title_index = {path.stem for path in notes}
    seen_ids: dict[str, Path] = {}
    for path in notes:
        payload, body = load_frontmatter(path.read_text(encoding="utf-8"))
        for field in sorted(REQUIRED_FIELDS):
            if field not in payload:
                issues.append(f"{path}: missing required field: {field}")
        node_type = payload.get("node_type")
        if node_type and node_type not in NOTE_TYPES:
            issues.append(f"{path}: invalid node_type: {node_type}")
        note_id = payload.get("id")
        if isinstance(note_id, str):
            if note_id in seen_ids:
                issues.append(f"{path}: duplicate id: {note_id}")
            else:
                seen_ids[note_id] = path
        for match in WIKILINK_RE.findall(body):
            if match not in title_index:
                issues.append(f"{path}: broken wikilink: {match}")
        for relation_field in ("related", "source_refs", "concept_refs", "method_refs", "gap_refs", "paper_refs", "raised_by", "introduced_by"):
            values = payload.get(relation_field, [])
            if isinstance(values, list):
                for value in values:
                    if value and value not in seen_ids and value not in title_index:
                        issues.append(f"{path}: unresolved relation in {relation_field}: {value}")
    return issues
```

```python
# src/brain_graph/cli.py
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry
from brain_graph.lint import collect_issues
from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note")
    new_note.add_argument("--type", dest="note_type", required=True)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", dest="note_id", required=True)
    new_note.add_argument("--force", action="store_true")

    ingest = subparsers.add_parser("ingest-raw")
    ingest.add_argument("--kind", required=True)
    ingest.add_argument("--slug", required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--source-url", default="")
    ingest.add_argument("--summary", default="")

    subparsers.add_parser("lint")
    subparsers.add_parser("export-graph")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path.cwd()

    if args.command == "new-note":
        try:
            target = create_note(
                project_root,
                NewNoteCommand(
                    note_type=args.note_type,
                    title=args.title,
                    note_id=args.note_id,
                    force=args.force,
                ),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    if args.command == "ingest-raw":
        try:
            target = ingest_raw_entry(
                project_root,
                IngestRawCommand(
                    kind=args.kind,
                    slug=args.slug,
                    title=args.title,
                    source_url=args.source_url,
                    summary=args.summary,
                ),
                date_text=date.today().isoformat(),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    if args.command == "lint":
        issues = collect_issues(project_root)
        if issues:
            print("\n".join(issues), file=sys.stderr)
            return 1
        print("lint ok")
        return 0

    return 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_lint.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/brain_graph/lint.py src/brain_graph/cli.py tests/test_lint.py tests/fixtures/wiki
git commit -m "feat: add note linting"
```

### Task 8: Implement Graph Export For JSON And Mermaid

**Files:**
- Create: `src/brain_graph/export_graph.py`
- Modify: `src/brain_graph/cli.py`
- Test: `tests/test_export_graph.py`

- [ ] **Step 1: Write the failing export tests**

```python
import json
from pathlib import Path

from brain_graph.export_graph import export_graph_files


def write_note(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_export_graph_writes_json_and_mermaid(tmp_path: Path) -> None:
    write_note(
        tmp_path / "wiki" / "papers" / "MemoryGraft.md",
        "---\n"
        "id: paper-memorygraft\n"
        "title: MemoryGraft\n"
        "node_type: paper\n"
        "status: seed\n"
        "tags:\n"
        "  - attacks\n"
        "created: 2026-04-19\n"
        "updated: 2026-04-19\n"
        "source_refs:\n"
        "related:\n"
        "concept_refs:\n"
        "  - concept-semantic-imitation\n"
        "---\n\n"
        "Body with [[Semantic Imitation]].\n"
    )
    write_note(
        tmp_path / "wiki" / "concepts" / "Semantic Imitation.md",
        "---\n"
        "id: concept-semantic-imitation\n"
        "title: Semantic Imitation\n"
        "node_type: concept\n"
        "status: seed\n"
        "tags:\n"
        "created: 2026-04-19\n"
        "updated: 2026-04-19\n"
        "source_refs:\n"
        "related:\n"
        "---\n\n"
        "Concept body.\n"
    )
    export_graph_files(tmp_path)
    graph_json = json.loads((tmp_path / "exports" / "brain_graph.json").read_text(encoding="utf-8"))
    graph_mmd = (tmp_path / "exports" / "brain_graph.mmd").read_text(encoding="utf-8")
    assert len(graph_json["nodes"]) == 2
    labels = {edge["label"] for edge in graph_json["edges"]}
    assert "mentions" in labels
    assert "body_link" in labels
    assert "graph LR" in graph_mmd
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_export_graph.py -v`
Expected: FAIL with import error for `brain_graph.export_graph`

- [ ] **Step 3: Write the graph exporter**

```python
# src/brain_graph/export_graph.py
from __future__ import annotations

import json
import re
from pathlib import Path

from brain_graph.frontmatter import load_frontmatter


WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FIELD_EDGE_LABELS = {
    "concept_refs": "mentions",
    "method_refs": "uses",
    "gap_refs": "raises_gap",
    "paper_refs": "supports",
    "introduced_by": "introduces",
    "raised_by": "raises_gap",
    "related": "related_to",
    "source_refs": "supports_reference",
}


def export_graph_files(project_root: Path) -> tuple[Path, Path]:
    notes = sorted((project_root / "wiki").glob("*/*.md"))
    id_to_title: dict[str, str] = {}
    title_to_id: dict[str, str] = {}
    parsed: list[tuple[Path, dict[str, object], str]] = []

    for path in notes:
        payload, body = load_frontmatter(path.read_text(encoding="utf-8"))
        parsed.append((path, payload, body))
        note_id = str(payload["id"])
        title = str(payload["title"])
        id_to_title[note_id] = title
        title_to_id[title] = note_id

    nodes = []
    edges = []
    for _, payload, body in parsed:
        source_id = str(payload["id"])
        nodes.append(
            {
                "id": source_id,
                "title": str(payload["title"]),
                "node_type": str(payload["node_type"]),
                "status": str(payload["status"]),
            }
        )
        for field_name, label in FIELD_EDGE_LABELS.items():
            raw_value = payload.get(field_name, [])
            values = raw_value if isinstance(raw_value, list) else [raw_value]
            for value in values:
                if value:
                    edges.append({"source": source_id, "target": str(value), "label": label})
        for target_title in WIKILINK_RE.findall(body):
            target_id = title_to_id.get(target_title)
            if target_id:
                edges.append({"source": source_id, "target": target_id, "label": "body_link"})

    export_dir = project_root / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    json_path = export_dir / "brain_graph.json"
    mermaid_path = export_dir / "brain_graph.mmd"
    json_path.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=2), encoding="utf-8")

    mermaid_lines = ["graph LR"]
    for node in nodes:
        mermaid_lines.append(f'  {node["id"]}["{node["title"]}"]')
    for edge in edges:
        mermaid_lines.append(f'  {edge["source"]} -- "{edge["label"]}" --> {edge["target"]}')
    mermaid_path.write_text("\n".join(mermaid_lines) + "\n", encoding="utf-8")
    return json_path, mermaid_path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_export_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/brain_graph/export_graph.py tests/test_export_graph.py
git commit -m "feat: add graph export outputs"
```

### Task 9: Add End-To-End CLI Coverage And README Usage

**Files:**
- Modify: `README.md`
- Modify: `tests/test_cli.py`
- Modify: `src/brain_graph/cli.py`

- [ ] **Step 1: Write the failing end-to-end CLI tests**

```python
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "brain_graph.cli", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def test_lint_command_succeeds_on_clean_workspace() -> None:
    result = run_cli("lint")
    assert result.returncode == 0
    assert "lint ok" in result.stdout


def test_export_graph_command_creates_outputs() -> None:
    run_cli("new-note", "--type", "concept", "--title", "Semantic Imitation", "--id", "concept-semantic-imitation")
    run_cli("export-graph")
    assert (PROJECT_ROOT / "exports" / "brain_graph.json").exists()
    assert (PROJECT_ROOT / "exports" / "brain_graph.mmd").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_lint_command_succeeds_on_clean_workspace tests/test_cli.py::test_export_graph_command_creates_outputs -v`
Expected: FAIL because the workspace lacks clean starter notes or export wiring

- [ ] **Step 3: Tighten CLI behavior and README usage**

```python
# src/brain_graph/cli.py
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

from brain_graph.export_graph import export_graph_files
from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry
from brain_graph.lint import collect_issues
from brain_graph.models import NOTE_TYPES, RAW_KINDS
from brain_graph.new_note import NewNoteCommand, create_note


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brain-graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_note = subparsers.add_parser("new-note")
    new_note.add_argument("--type", dest="note_type", choices=NOTE_TYPES, required=True)
    new_note.add_argument("--title", required=True)
    new_note.add_argument("--id", dest="note_id", required=True)
    new_note.add_argument("--force", action="store_true")

    ingest = subparsers.add_parser("ingest-raw")
    ingest.add_argument("--kind", choices=RAW_KINDS, required=True)
    ingest.add_argument("--slug", required=True)
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--source-url", default="")
    ingest.add_argument("--summary", default="")

    subparsers.add_parser("lint")
    subparsers.add_parser("export-graph")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    project_root = Path.cwd()

    if args.command == "new-note":
        try:
            target = create_note(
                project_root,
                NewNoteCommand(
                    note_type=args.note_type,
                    title=args.title,
                    note_id=args.note_id,
                    force=args.force,
                ),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    if args.command == "ingest-raw":
        try:
            target = ingest_raw_entry(
                project_root,
                IngestRawCommand(
                    kind=args.kind,
                    slug=args.slug,
                    title=args.title,
                    source_url=args.source_url,
                    summary=args.summary,
                ),
                date_text=date.today().isoformat(),
            )
        except FileExistsError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(target)
        return 0

    if args.command == "lint":
        issues = collect_issues(project_root)
        if issues:
            print("\n".join(issues), file=sys.stderr)
            return 1
        print("lint ok")
        return 0

    if args.command == "export-graph":
        json_path, mermaid_path = export_graph_files(project_root)
        print(json_path)
        print(mermaid_path)
        return 0

    return 0
```

```markdown
# README.md

# Brain Graph

Local-first research brain built around Markdown, Obsidian, and a small Python CLI.

## Commands

```bash
python -m brain_graph.cli new-note --type paper --title "MemoryGraft" --id paper-memorygraft
python -m brain_graph.cli ingest-raw --kind paper --slug memorygraft --title "MemoryGraft"
python -m brain_graph.cli lint
python -m brain_graph.cli export-graph
```

## Structure

- `raw/`: append-only source material
- `wiki/`: curated knowledge notes
- `views/`: canvas, dataview, and graph helpers
- `shared/research.md`: temporary cross-model scratchpad
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md src/brain_graph/cli.py tests/test_cli.py
git commit -m "feat: document and verify cli workflows"
```

### Task 10: Run Full Verification

**Files:**
- Verify only: `README.md`, `src/brain_graph/*.py`, `tests/*.py`, project directories

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: PASS for all tests

- [ ] **Step 2: Run command-line smoke checks**

Run: `python -m brain_graph.cli --help`
Expected: lists `new-note`, `ingest-raw`, `lint`, `export-graph`

Run: `python -m brain_graph.cli lint`
Expected: `lint ok`

Run: `python -m brain_graph.cli export-graph`
Expected: prints paths to `exports/brain_graph.json` and `exports/brain_graph.mmd`

- [ ] **Step 3: Inspect output files**

Run: `ls -R exports wiki raw views | sed -n '1,120p'`
Expected: graph exports exist and starter vault folders are present

- [ ] **Step 4: Commit verification-safe final state**

```bash
git add README.md exports src tests views wiki raw discovery shared pyproject.toml .gitignore
git commit -m "feat: complete brain graph v1"
```

## Self-Review

### Spec coverage

- Project shape and standalone root: covered by Tasks 1 and 2
- Standard note templates and schema: covered by Tasks 3 and 4
- `new-note` CLI: covered by Task 5
- `ingest-raw` CLI and append-only raw behavior: covered by Task 6
- Linting for missing fields, duplicates, and broken links: covered by Task 7
- Graph export to JSON and Mermaid: covered by Task 8
- README and starter Obsidian view files: covered by Tasks 2 and 9
- Final verification: covered by Task 10

### Placeholder scan

- No unresolved placeholder markers remain
- All code-writing steps include concrete snippets
- All verification steps include exact commands and expected outcomes

### Type consistency

- Note type constants match spec and CLI choices
- `new-note`, `ingest-raw`, `lint`, and `export-graph` command names match Task 1 and later tasks
- Field names used in templates, lint, and export are consistent with the spec
