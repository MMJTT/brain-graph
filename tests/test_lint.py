from pathlib import Path

from brain_graph.cli import main
from brain_graph.frontmatter import dump_frontmatter, load_frontmatter
from brain_graph.lint import collect_issues


FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def _copy_fixture(tmp_path: Path, relative_path: str) -> None:
    source = FIXTURES_ROOT / relative_path
    target = tmp_path / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _rewrite_fixture(
    tmp_path: Path,
    relative_path: str,
    *,
    mutate_frontmatter=None,
    mutate_body=None,
) -> None:
    target = tmp_path / relative_path
    frontmatter, body = load_frontmatter(target.read_text(encoding="utf-8"))
    if mutate_frontmatter is not None:
        mutate_frontmatter(frontmatter)
    if mutate_body is not None:
        body = mutate_body(body)
    target.write_text(f"{dump_frontmatter(frontmatter)}\n{body}", encoding="utf-8")


def _seed_clean_wiki(tmp_path: Path) -> None:
    for relative_path in [
        "wiki/papers/MemoryGraft.md",
        "wiki/concepts/Semantic Imitation.md",
        "wiki/gaps/Provenance Gap.md",
    ]:
        _copy_fixture(tmp_path, relative_path)


def test_clean_wiki_has_no_lint_issues(tmp_path):
    _seed_clean_wiki(tmp_path)

    assert collect_issues(tmp_path) == []


def test_missing_required_field_id_is_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.pop("id", None),
    )

    issues = collect_issues(tmp_path)

    assert any("missing required field: id" in issue for issue in issues)


def test_duplicate_ids_are_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _copy_fixture(tmp_path, "wiki/gaps/Provenance Gap.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/gaps/Provenance Gap.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__("id", "paper-memorygraft"),
    )

    issues = collect_issues(tmp_path)

    assert any("duplicate id" in issue for issue in issues)


def test_duplicate_titles_are_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _copy_fixture(tmp_path, "wiki/gaps/Provenance Gap.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/gaps/Provenance Gap.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__("title", "MemoryGraft"),
    )

    issues = collect_issues(tmp_path)

    assert any("duplicate title: MemoryGraft" in issue for issue in issues)


def test_invalid_node_type_is_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__("node_type", "unknown"),
    )

    issues = collect_issues(tmp_path)

    assert any("invalid node_type: unknown" in issue for issue in issues)


def test_folder_node_type_mismatch_is_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    concept_path = tmp_path / "wiki" / "concepts" / "MemoryGraft.md"
    concept_path.parent.mkdir(parents=True, exist_ok=True)
    concept_path.write_text(
        (tmp_path / "wiki" / "papers" / "MemoryGraft.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    issues = collect_issues(tmp_path)

    assert any("expected wiki/papers" in issue for issue in issues)


def test_broken_wikilink_is_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/papers/MemoryGraft.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_body=lambda body: f"{body.rstrip()}\n\nSee [[Missing Note]].\n",
    )

    issues = collect_issues(tmp_path)

    assert any("unresolved wikilink: Missing Note" in issue for issue in issues)


def test_unresolved_relation_reference_is_reported(tmp_path):
    _copy_fixture(tmp_path, "wiki/concepts/Semantic Imitation.md")
    _rewrite_fixture(
        tmp_path,
        "wiki/concepts/Semantic Imitation.md",
        mutate_frontmatter=lambda frontmatter: frontmatter.__setitem__("paper_refs", ["missing-paper"]),
    )

    issues = collect_issues(tmp_path)

    assert any(
        "unresolved relation reference in paper_refs: missing-paper" in issue for issue in issues
    )


def test_lint_cli_reports_ok_for_clean_input(tmp_path, monkeypatch, capsys):
    _seed_clean_wiki(tmp_path)
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lint"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == "lint ok\n"
    assert captured.err == ""


def test_lint_cli_reports_failures_on_bad_input(tmp_path, monkeypatch, capsys):
    _seed_clean_wiki(tmp_path)
    _rewrite_fixture(
        tmp_path,
        "wiki/papers/MemoryGraft.md",
        mutate_body=lambda body: f"{body.rstrip()}\n\nSee [[Missing Note]].\n",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = main(["lint"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "unresolved wikilink: Missing Note" in captured.err
