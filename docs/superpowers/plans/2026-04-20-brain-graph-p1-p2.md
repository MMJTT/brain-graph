# Brain Graph P1/P2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade Brain Graph from a P0 import pipeline into a research loop with richer graph compilation, discovery adapters, and an optional OpenRouter compiler.

**Architecture:** Build on the existing P0 commands instead of replacing them. First extend compile output and note generation for cross-paper graph growth, then add discovery providers and an orchestration command that chains discovery, compile, and export in one run.

**Tech Stack:** Python 3.12, pytest, stdlib HTTP/JSON/XML tooling, Obsidian markdown vault conventions

---

### Task 1: Extend compile payload and CLI surface

**Files:**
- Modify: `src/brain_graph/cli.py`
- Modify: `src/brain_graph/compiler_schema.py`
- Modify: `src/brain_graph/models.py`
- Test: `tests/test_cli.py`

- [ ] Add new CLI arguments for `--compiler` and `--model` on compile commands, plus new `discover-papers` and `research-loop` subcommands.
- [ ] Expand the compiler schema so payload validation covers `authors`, `methods`, `gaps`, and `research_notes`.
- [ ] Add parser tests that prove the new subcommands and flags are wired correctly.

### Task 2: Implement richer note writing and normalization

**Files:**
- Modify: `src/brain_graph/compile_paper.py`
- Create: `src/brain_graph/normalize_graph.py`
- Modify: `src/brain_graph/paths.py`
- Test: `tests/test_compile_paper.py`

- [ ] Add a normalized compile payload path that can emit paper, concept, method, gap, and author note payloads.
- [ ] Add deterministic concept normalization and alias handling before note creation.
- [ ] Extend compile tests to assert richer notes are created and re-runs remain idempotent.

### Task 3: Regenerate topical maps and strengthen lint

**Files:**
- Create: `src/brain_graph/topic_maps.py`
- Modify: `src/brain_graph/batch_compile.py`
- Modify: `src/brain_graph/lint.py`
- Test: `tests/test_batch_compile.py`
- Test: `tests/test_lint.py`

- [ ] Generate topical map notes from current graph content instead of relying on static seed files.
- [ ] Run topic-map refresh as part of batch compile and later research-loop execution.
- [ ] Add lint checks for duplicate aliases, orphaned generated references, and malformed normalized relationships.

### Task 4: Add discovery providers

**Files:**
- Create: `src/brain_graph/discover_papers.py`
- Modify: `src/brain_graph/import_paper.py`
- Test: `tests/test_discover_papers.py`
- Test: `tests/test_import_paper.py`

- [ ] Add `DiscoveredPaper` adapters for arXiv and Semantic Scholar.
- [ ] Reuse the import pipeline to write discovered items into `raw/papers` plus metadata sidecars.
- [ ] Add tests that mock provider responses and assert imported raw notes are created correctly.

### Task 5: Add OpenRouter compiler backend

**Files:**
- Create: `src/brain_graph/openrouter_client.py`
- Modify: `src/brain_graph/compile_paper.py`
- Test: `tests/test_openrouter_client.py`
- Test: `tests/test_compile_paper.py`

- [ ] Add a minimal OpenRouter chat client that reads `OPENROUTER_API_KEY` from the environment.
- [ ] Support structured compile output through the same normalized payload interface as the heuristic compiler.
- [ ] Keep tests fully mocked so the suite stays offline.

### Task 6: Add the research loop and docs

**Files:**
- Create: `src/brain_graph/research_loop.py`
- Modify: `src/brain_graph/cli.py`
- Modify: `README.md`
- Modify: `shared/research.md`
- Test: `tests/test_cli.py`

- [ ] Add `research-loop` to orchestrate discovery, compile, map refresh, export, and summary append.
- [ ] Document the P1/P2 workflow and required environment variables.
- [ ] Add a CLI integration test for one discovery-to-summary run with mocked network calls.

### Task 7: Verify end to end

**Files:**
- No code changes required unless verification reveals gaps.

- [ ] Run `pytest -q`.
- [ ] Run `python -m brain_graph.cli lint`.
- [ ] Run `python -m brain_graph.cli export-graph`.
- [ ] If all pass, prepare the branch for merge or PR handling.
