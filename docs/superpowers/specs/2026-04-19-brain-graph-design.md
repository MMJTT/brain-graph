# Brain Graph Design

Date: 2026-04-19
Project root: `/Users/mijiatong/Code/brain-graph`
Status: approved for planning

## 1. Goal

Build a fresh, local-first Brain Graph workspace that mirrors the workflow in the reference diagram:

1. paper discovery
2. raw ingestion
3. structured wiki curation
4. graph-based visualization
5. shared multi-model discussion context
6. iterative export, lint, and refinement

The first release should be usable from zero without connecting to existing repositories or notes under `/Users/mijiatong/Code`.

## 2. Non-goals

- No direct integration with existing `Paper/`, `Paper-Analyzer/`, or other local research folders.
- No mandatory online API integration in v1.
- No heavy web app in v1.
- No automatic LLM writing pipeline in v1. The system should support structured curation first, then optional automation.

## 3. Product Shape

The project is a standalone Obsidian-friendly vault plus a small Python CLI.

- Obsidian provides note editing, backlinks, graph view, canvas, and Dataview-based browsing.
- Python CLI provides repeatable project operations: create note skeletons, validate note schema, export graph data, and manage raw ingests.
- Markdown remains the source of truth.

This keeps the system close to the reference image while staying lightweight and inspectable.

## 4. Core Principles

### 4.1 Raw is append-only

`raw/` stores imported material and machine-generated ingestion outputs. These files are not manually edited except for obvious metadata repair when a file is malformed.

### 4.2 Wiki is curated

`wiki/` stores normalized knowledge notes that summarize, connect, and refine what was ingested into `raw/`.

### 4.3 Graph comes from links plus metadata

The Brain Graph is not stored as a separate database of record. It is derived from:

- Markdown wikilinks
- YAML frontmatter fields
- explicit relation lists
- generated exports in `exports/`

### 4.4 Local-first and inspectable

Every important artifact is readable as plain text. Users should be able to inspect, diff, and repair the system without vendor lock-in.

## 5. First Release Scope

The first release will include:

- a new project folder with a clean research-brain layout
- standard note templates for major node types
- a Python package with a CLI
- a lint command that validates note structure and links
- a graph export command that emits machine-readable graph data
- starter Obsidian view files and usage docs

The first release will not include:

- automatic download from arXiv or Semantic Scholar
- background agents
- Zotero sync
- advanced web UI

## 6. Proposed Directory Layout

```text
brain-graph/
├── .git/
├── .gitignore
├── README.md
├── pyproject.toml
├── docs/
│   └── superpowers/
│       └── specs/
├── discovery/
│   ├── inbox.md
│   ├── sources.md
│   └── workflows.md
├── raw/
│   ├── inbox/
│   ├── papers/
│   ├── clips/
│   └── metadata/
├── wiki/
│   ├── papers/
│   ├── concepts/
│   ├── methods/
│   ├── gaps/
│   ├── authors/
│   └── maps/
├── views/
│   ├── canvas/
│   ├── dataview/
│   └── graph/
├── shared/
│   └── research.md
├── templates/
│   ├── paper.md
│   ├── concept.md
│   ├── method.md
│   ├── gap.md
│   ├── author.md
│   └── map.md
├── exports/
│   ├── brain_graph.json
│   └── brain_graph.mmd
├── tests/
│   ├── fixtures/
│   └── test_cli.py
└── src/
    └── brain_graph/
        ├── __init__.py
        ├── cli.py
        ├── schema.py
        ├── templates.py
        ├── lint.py
        └── export_graph.py
```

## 7. Knowledge Model

### 7.1 Node Types

The system will support these note types in v1:

- `paper`: a paper-level note
- `concept`: a concept or theme
- `method`: a technique, mechanism, or pipeline
- `gap`: an open problem, contradiction, or missing evidence
- `author`: an optional person-level node
- `map`: a synthesis note that organizes a subgraph

### 7.2 Shared Frontmatter

All wiki notes will contain a shared minimal frontmatter schema:

```yaml
id: paper-memorygraft
title: MemoryGraft
node_type: paper
status: seed
tags:
  - attacks
created: 2026-04-19
updated: 2026-04-19
source_refs: []
related: []
```

### 7.3 Type-specific Fields

Paper notes:

- `year`
- `venue`
- `authors`
- `paper_url`
- `raw_refs`
- `concept_refs`
- `method_refs`
- `gap_refs`

Concept notes:

- `aliases`
- `parent_concepts`
- `paper_refs`
- `method_refs`

Method notes:

- `introduced_by`
- `applies_to`
- `limitations`

Gap notes:

- `gap_kind`
- `raised_by`
- `potential_directions`

Map notes:

- `focus`
- `includes`
- `questions`

### 7.4 Edge Semantics

The graph export will normalize a small set of explicit edge labels:

- `mentions`
- `introduces`
- `uses`
- `supports`
- `contradicts`
- `extends`
- `raises_gap`
- `related_to`

Markdown wikilinks stay human-friendly. The exporter translates them into normalized graph edges.

## 8. Workflow Mapping to the Reference Diagram

### 8.1 Discovery Layer

`discovery/` holds:

- source checklist
- manual workflow notes
- curated query ideas
- operating instructions for future arXiv or Semantic Scholar integration

This satisfies the "paper discovery" layer without hard-coding API dependencies in v1.

### 8.2 Raw Ingestion Layer

`raw/` receives imported files and simple metadata bundles.

Typical raw artifacts:

- copied abstracts
- markdown clips
- PDF sidecar metadata
- extracted notes from external tools

The CLI will support creating raw entries with stable names and timestamps.

### 8.3 LLM Wiki Core

`wiki/` is the durable knowledge layer.

The intended operating model is:

1. ingest something into `raw/`
2. create or update a structured note in `wiki/`
3. connect it with explicit links
4. run lint to catch missing metadata, missing targets, or inconsistent relations

The system will be designed so future LLM workflows can safely operate on `wiki/` while treating `raw/` as source evidence.

### 8.4 Visualization Layer

`views/` stores project-owned visualization assets:

- Canvas files for logic maps
- Dataview snippets for queries and summaries
- graph presets and export docs

Obsidian remains read/write for notes, but project-owned view assets live in versioned files.

### 8.5 Shared Multi-model Layer

`shared/research.md` acts as a common scratchpad for cross-model comparison, debate, and synthesis. It is intentionally lightweight and separate from final structured notes.

### 8.6 Output and Iteration Layer

The loop for each research pass is:

1. add to `raw/`
2. curate into `wiki/`
3. lint
4. export graph
5. inspect in Obsidian graph or Canvas
6. refine gaps and synthesis notes

## 9. CLI Design

The initial CLI commands will be:

### 9.1 `new-note`

Create a wiki note from a template.

Examples:

```bash
python -m brain_graph.cli new-note --type paper --slug memorygraft
python -m brain_graph.cli new-note --type concept --slug semantic-imitation
```

Responsibilities:

- choose the right template
- fill common frontmatter
- place the file in the right wiki subfolder
- prevent accidental overwrite unless `--force` is used

### 9.2 `ingest-raw`

Create a raw note or metadata entry with a stable path.

Example:

```bash
python -m brain_graph.cli ingest-raw --kind paper --slug memorygraft
```

Responsibilities:

- create a timestamped raw record
- preserve append-only behavior
- optionally attach a source URL or short description

### 9.3 `lint`

Validate note structure and link quality.

Checks:

- required frontmatter exists
- `node_type` matches folder and template rules
- wikilinks resolve
- relation fields point to existing notes
- duplicate ids are rejected

### 9.4 `export-graph`

Generate graph artifacts from wiki content.

Outputs:

- `exports/brain_graph.json` for tools and automation
- `exports/brain_graph.mmd` for Mermaid-based quick visualization

## 10. File Naming Rules

- IDs are lowercase kebab-case.
- Wiki file names are human-readable and may include title text, but IDs remain stable.
- Raw files use timestamp-prefixed slugs to preserve append-only semantics.

Examples:

- `wiki/papers/MemoryGraft.md`
- `wiki/concepts/Semantic Imitation.md`
- `raw/papers/2026-04-19-memorygraft.md`

## 11. Error Handling

The CLI should fail loudly and clearly for structural problems.

- If a template type is unknown, return a non-zero exit code with supported values.
- If a target note already exists, require `--force`.
- If lint finds broken links or duplicate ids, summarize all issues before exiting non-zero.
- If export sees malformed frontmatter, skip nothing silently. The error report must identify the exact file.

## 12. Testing Strategy

The first release will include automated tests for:

- template rendering
- correct output paths for each note type
- duplicate id detection
- missing link detection
- graph export shape

Testing stack:

- `pytest`
- fixture notes under `tests/fixtures/`

## 13. Obsidian Compatibility

The project should be directly openable as an Obsidian vault.

v1 compatibility goals:

- wiki links work without extra plugins
- Dataview snippets are stored as plain markdown examples
- Canvas files are versioned under `views/canvas/`
- no plugin lock-in is required to read the knowledge base

## 14. Implementation Sequence

The implementation plan should follow this order:

1. scaffold project files and Python package
2. add templates and note schema
3. implement `new-note`
4. implement `ingest-raw`
5. implement `lint`
6. implement `export-graph`
7. add tests
8. add README and starter view files

## 15. Acceptance Criteria

The first release is complete when:

- `/Users/mijiatong/Code/brain-graph` exists as a standalone project
- a user can create at least one `paper`, `concept`, and `gap` note from the CLI
- lint catches at least broken links, missing fields, and duplicate ids
- graph export emits valid JSON and Mermaid output
- the vault can be opened in Obsidian and browsed as a knowledge graph workspace

## 16. Open Decisions Resolved for v1

These decisions are intentionally fixed now to reduce ambiguity:

- Python is the implementation language.
- Obsidian is the default viewing environment.
- Markdown is the source of truth.
- No external API integration is required in v1.
- The project is standalone and does not read existing research folders.

## 17. Risks and Mitigations

Risk: the schema becomes too heavy for daily note-taking.
Mitigation: keep shared frontmatter minimal and push optional detail into body sections.

Risk: raw and wiki drift apart.
Mitigation: require `raw_refs` and `source_refs` fields where relevant.

Risk: graph exports become noisy.
Mitigation: normalize edge labels and validate note types strictly.

Risk: Obsidian-specific assets become fragile.
Mitigation: keep the knowledge layer readable without Obsidian plugins.
