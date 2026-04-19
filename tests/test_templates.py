from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.paths import note_path_for_type


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
