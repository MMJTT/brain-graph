# Brain Graph

Brain Graph is a local-first research vault for growing a structured paper graph with `raw/` intake notes, curated `wiki/` notes, and exported graph artifacts.

## What Is Included

- A Python CLI for creating notes, discovering papers, compiling raw material, linting links, and exporting the graph.
- An Obsidian-friendly vault layout with `raw/`, `wiki/`, `views/`, and `shared/`.
- A seeded agent-security corpus imported from a local PDF folder, so the graph already contains connected paper, concept, and map notes.

## Quick Start

```bash
cd /Users/mijiatong/Code/brain-graph
python -m brain_graph.cli import-paper --pdf /Users/me/Desktop/papers/foo.pdf
python -m brain_graph.cli compile-paper --slug foo
python -m brain_graph.cli compile-batch --source raw/papers
python -m brain_graph.cli discover-papers --query "prompt injection" --provider both --limit 5
python -m brain_graph.cli research-loop --query "agent defense" --provider both --limit 5
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

Import a paper into the P0 pipeline:

```bash
python -m brain_graph.cli import-paper --pdf /Users/me/Desktop/papers/foo.pdf
python -m brain_graph.cli import-paper --url https://arxiv.org/abs/2512.16962 --title "MemoryGraft"
```

Compile one imported paper:

```bash
python -m brain_graph.cli compile-paper --slug foo
python -m brain_graph.cli compile-paper --slug foo --compiler openrouter --model openai/gpt-4.1-mini
```

Compile the queue in batch:

```bash
python -m brain_graph.cli compile-batch --source raw/papers --limit 20
python -m brain_graph.cli compile-batch --source raw/papers --compiler openrouter --model openai/gpt-4.1-mini
```

Discover papers from remote scholarly sources and import them into `raw/`:

```bash
python -m brain_graph.cli discover-papers --query "prompt injection" --provider both --limit 10
```

Run the end-to-end research loop:

```bash
python -m brain_graph.cli research-loop --query "agent defense" --provider both --limit 10
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

## P0 Workflow

1. Import a local PDF or paper URL into `raw/`.
2. Inspect the generated raw note and metadata sidecar in `raw/papers/` and `raw/metadata/papers/`.
3. Compile one paper into structured `wiki/papers/` and linked `wiki/concepts/`.
4. Run batch compilation to process the remaining imported queue.
5. Open `views/canvas/starter.canvas` in Obsidian to see the refreshed graph.

## P1/P2 Workflow

1. Discover fresh papers into `raw/` with `discover-papers`.
2. Compile one paper or a batch with richer graph generation for `concept`, `method`, `gap`, and `author` notes.
3. Let batch compile refresh topical maps such as `Attack Paper Map` and `System Paper Map`.
4. Use `research-loop` to chain discovery, compile, graph export, and a summary append to `shared/research.md`.
5. Open the generated maps and `views/canvas/starter.canvas` in Obsidian.

## Environment Variables

- `OPENROUTER_API_KEY`: required only when using `--compiler openrouter`
- `SEMANTIC_SCHOLAR_API_KEY`: optional future-proof slot for Semantic Scholar higher-rate access
