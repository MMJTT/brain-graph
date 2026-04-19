from pathlib import Path

import pytest

from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.paths import note_path_for_type
from brain_graph.templates import render_template


def test_note_path_for_type_uses_wiki_directory_mapping(tmp_path):
    path = note_path_for_type(tmp_path, "paper", "MemoryGraft")

    assert path.as_posix().endswith("wiki/papers/MemoryGraft.md")


def test_note_path_for_type_keeps_gap_titles_readable(tmp_path):
    path = note_path_for_type(tmp_path, "gap", "Provenance Gap")

    assert path.as_posix().endswith("wiki/gaps/Provenance Gap.md")


def test_frontmatter_round_trip_preserves_list_fields_and_body_blank_line():
    data = {
        "id": "paper-memorygraft",
        "title": "MemoryGraft",
        "tags": ["attacks", "memory"],
        "related": ["concept-semantic-imitation"],
    }

    content = dump_frontmatter(data)
    parsed, body = load_frontmatter(content + "\n\nBody line\n")

    assert parsed == data
    assert body == "\nBody line\n"


@pytest.mark.parametrize(
    ("note_type", "note_id", "title", "section_heading", "expected_fields"),
    [
        ("paper", "paper-memorygraft", "MemoryGraft", "## Summary", ("year", "venue", "authors", "paper_url", "raw_refs", "concept_refs", "method_refs", "gap_refs")),
        ("concept", "concept-semantic-imitation", "Semantic Imitation", "## Definition", ("aliases", "parent_concepts", "paper_refs", "method_refs")),
        ("method", "method-activation-steering", "Activation Steering", "## Mechanism", ("introduced_by", "applies_to", "limitations")),
        ("gap", "gap-evaluation-blindspot", "Evaluation Blindspot", "## Gap Statement", ("gap_kind", "raised_by", "potential_directions")),
        ("author", "author-someone", "Some Author", "## Profile", ("affiliation", "paper_refs")),
        ("map", "map-interpretability", "Interpretability Map", "## Focus", ("focus", "includes", "questions")),
    ],
)
def test_render_template_loads_repo_template_with_frontmatter_and_sections(
    note_type, note_id, title, section_heading, expected_fields
):
    project_root = Path(__file__).resolve().parents[1]

    rendered = render_template(
        project_root,
        note_type,
        title,
        note_id,
        "2026-04-19",
    )

    assert rendered.startswith(
        "---\n"
        f"id: {note_id}\n"
        f"title: {title}\n"
        f"node_type: {note_type}\n"
    )
    assert "status: seed" in rendered
    assert "tags: []" in rendered
    assert "source_refs: []" in rendered
    assert "related: []" in rendered
    for field in expected_fields:
        assert f"{field}: []" in rendered
    assert section_heading in rendered
