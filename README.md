# Brain Graph

Brain Graph is a local-first research vault for growing a structured paper graph with `raw/` intake notes, curated `wiki/` notes, and exported graph artifacts.

## What Is Included

- A Python CLI for creating notes, ingesting raw material, linting links, and exporting the graph.
- An Obsidian-friendly vault layout with `raw/`, `wiki/`, `views/`, and `shared/`.
- A seeded agent-security corpus imported from a local PDF folder, so the graph already contains connected paper, concept, and map notes.

## Quick Start

```bash
cd /Users/mijiatong/Code/brain-graph
python -m brain_graph.cli lint
python -m brain_graph.cli export-graph
```

This writes the current graph to:

- `exports/brain_graph.json`
- `exports/brain_graph.mmd`

## Common Commands

Create a new structured wiki note:

```bash
python -m brain_graph.cli new-note --type paper --title "MemoryGraft" --id paper-memorygraft
```

Ingest a raw source note:

```bash
python -m brain_graph.cli ingest-raw --kind paper --slug memorygraft --title "MemoryGraft" --summary "Imported from a local PDF or clip."
```

Check structural consistency:

```bash
python -m brain_graph.cli lint
```

Export the graph:

```bash
python -m brain_graph.cli export-graph
```

Run tests:

```bash
pytest -q
```

## Workspace Layout

- `raw/`: append-only source captures grouped by kind, such as `papers/`, `clips/`, and `metadata/`.
- `wiki/`: curated graph notes grouped by node type, such as `papers/`, `concepts/`, `methods/`, `gaps/`, `authors/`, and `maps/`.
- `views/`: derived views and graph-facing artifacts, including canvas and dataview output.
- `shared/research.md`: shared research notes and cross-cutting context for the graph.
- `exports/`: machine-readable graph exports for downstream tooling.

## Seed Corpus

The repository now includes an initial graph grown from a local agent-security PDF corpus. The first pass adds:

- `wiki/papers/` seed notes for the imported papers
- `wiki/concepts/` seed concepts such as `Prompt Injection`, `Red Teaming`, and `Agent Benchmarks`
- `wiki/maps/Agent Security Seed Corpus.md` as an overview note that links the initial clusters together
- `raw/papers/` intake notes that record the imported PDF filenames without copying the PDFs into the repo

These links are intentionally heuristic. They are meant to make the graph usable immediately, then be refined as you read and curate the notes.
