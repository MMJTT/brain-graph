# Brain Graph

Brain Graph V1.

## CLI

- `python -m brain_graph.cli new-note --type paper --title "MemoryGraft" --id paper-memorygraft`
- `python -m brain_graph.cli ingest-raw --kind paper --slug memorygraft --title "MemoryGraft" --source-url ...`
- `python -m brain_graph.cli lint`
- `python -m brain_graph.cli export-graph`

## Workspace Layout

- `raw/`: append-only source captures grouped by kind, such as `papers/`, `clips/`, and `metadata/`.
- `wiki/`: curated graph notes grouped by node type, such as `papers/`, `concepts/`, `methods/`, `gaps/`, `authors/`, and `maps/`.
- `views/`: derived views and graph-facing artifacts, including canvas and dataview output.
- `shared/research.md`: shared research notes and cross-cutting context for the graph.
