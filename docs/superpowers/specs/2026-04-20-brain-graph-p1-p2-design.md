# Brain Graph P1/P2 Design

> User-approved baseline: continue directly from the earlier P1/P2 roadmap without pausing for another review round.

## Goal

Extend the completed P0 import and compile pipeline into a practical research loop that can:

1. discover papers from scholarly APIs,
2. compile papers into richer graph notes with authors, methods, and gaps,
3. normalize cross-paper concepts and regenerate topical maps, and
4. optionally use an OpenRouter-backed LLM compiler before writing the graph back to Obsidian.

## Scope

### P1: Graph Enrichment

- Upgrade paper compilation from keyword-only concept detection to a richer normalized payload.
- Generate or update `author`, `method`, and `gap` notes during compile.
- Normalize repeated concepts into canonical titles with alias support.
- Regenerate topical maps from graph content instead of only from a seeded one-off script.
- Strengthen lint checks around duplicate aliases, orphan nodes, and unresolved graph references.

### P2: Discovery And Research Loop

- Add paper discovery from arXiv and Semantic Scholar.
- Add an optional OpenRouter-backed compiler for structured paper extraction.
- Add a `research-loop` command that chains discovery, import, compile, map refresh, and summary update.
- Keep the system local-first: Obsidian remains the read surface, and all durable state stays in the repository.

## Non-Goals

- Full Zotero integration.
- Connected Papers integration.
- Browser automation or scheduled jobs.
- Multi-provider live debate orchestration across separate external CLIs.
- Perplexity-style novelty scoring. P2 only records candidate novelty questions and evidence.

## Design

### 1. Discovery Layer

Add a new `discover-papers` CLI command with provider adapters:

- `arxiv`
- `semantic-scholar`
- `both`

Each adapter returns a shared `DiscoveredPaper` shape:

- `title`
- `abstract`
- `authors`
- `year`
- `paper_url`
- `pdf_url`
- `external_ids`
- `source_provider`
- `source_query`

Discovery does not write directly to `wiki/`. It creates raw paper notes plus metadata sidecars, reusing the existing P0 import conventions.

### 2. Compiler Backends

Compilation gains backend selection:

- `heuristic`
- `openrouter`

The heuristic backend remains the offline fallback.

The OpenRouter backend calls the official OpenAI-compatible chat completions endpoint and asks for one structured JSON payload. The API key is read only from `OPENROUTER_API_KEY` at runtime and is never written to disk.

Both backends must emit the same normalized compile payload before note-writing starts:

- `paper`
- `concepts`
- `methods`
- `gaps`
- `authors`
- `maps`
- `research_notes`

### 3. Graph Normalization

Add a normalization layer between extraction and note-writing:

- Canonicalize concepts by slug and alias map.
- Collapse close variants like `Prompt Injection` and `Indirect Prompt Injection` only when an explicit alias rule exists.
- Preserve manual note text outside compiler-managed blocks.
- Keep note IDs stable after the first write.

Normalization will be deterministic and file-backed so graph exports stay reproducible even when an LLM backend is used.

### 4. Note Generation

Compilation writes or updates:

- `wiki/papers/`
- `wiki/concepts/`
- `wiki/methods/`
- `wiki/gaps/`
- `wiki/authors/`
- `wiki/maps/`

Compiler-managed blocks are extended so generated sections can refresh safely while leaving manual curation intact.

### 5. Research Loop

Add a `research-loop` command that executes:

1. discover papers,
2. import missing raw notes,
3. compile the imported set with the chosen backend,
4. refresh topical maps and exports,
5. append a compact run summary to `shared/research.md`.

The command should be resumable and idempotent enough for repeated use on the same topic query.

## Commands

New commands:

- `discover-papers --query ... --provider ... --limit ...`
- `research-loop --query ... --provider ... --limit ... --compiler ...`

Extended commands:

- `compile-paper --slug ... --compiler heuristic|openrouter --model ...`
- `compile-batch --source ... --limit ... --compiler heuristic|openrouter --model ...`

## Data Model Additions

Raw metadata gains optional discovery fields:

- `source_provider`
- `source_query`
- `external_ids`
- `pdf_url`
- `discovered_at`

Compiler payload adds:

- `methods`
- `gaps`
- `authors`
- `research_notes`

Concept notes gain stable alias bookkeeping.
Map notes gain a generated topical body based on current linked papers.

## Error Handling

- Discovery should skip malformed provider records, not abort the full run.
- OpenRouter failures should fall back to heuristic compile only when the user explicitly requested fallback behavior in that command path.
- Missing API keys must produce clear CLI errors.
- Lint must fail if normalization produces duplicate titles or duplicate aliases.

## Testing Strategy

- Unit tests for provider parsers.
- Unit tests for OpenRouter payload parsing via mocked HTTP responses.
- Compile tests that assert author, method, and gap notes are created.
- Batch tests that assert topical maps regenerate from compiled papers.
- CLI tests for `discover-papers` and `research-loop`.

## External API Notes

- arXiv API: official user manual documents `http://export.arxiv.org/api/query` with `search_query`, `start`, `max_results`, `sortBy`, and `sortOrder`.
- Semantic Scholar API: official tutorial documents Graph API usage and `x-api-key` as optional but recommended.
- OpenRouter API: official docs expose `POST /api/v1/chat/completions` with bearer auth and structured response options.
