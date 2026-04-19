import pytest

from brain_graph.cli import main
from brain_graph.frontmatter import load_frontmatter


def _write_paper_template(root):
    template = root / "templates" / "paper.md"
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text("## Summary\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("argv", "expected_error"),
    [
        (
            ["new-note", "--title", "MemoryGraft", "--id", "paper-memorygraft"],
            "the following arguments are required: --type",
        ),
        (
            ["new-note", "--type", "paper", "--id", "paper-memorygraft"],
            "the following arguments are required: --title",
        ),
        (
            ["new-note", "--type", "paper", "--title", "MemoryGraft"],
            "the following arguments are required: --id",
        ),
    ],
)
def test_new_note_requires_required_arguments(
    tmp_path, monkeypatch, capsys, argv, expected_error
):
    monkeypatch.chdir(tmp_path)
    _write_paper_template(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main(argv)

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert expected_error in captured.err


def test_new_note_rejects_unknown_note_type(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    _write_paper_template(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main(
            [
                "new-note",
                "--type",
                "unknown",
                "--title",
                "MemoryGraft",
                "--id",
                "paper-memorygraft",
            ]
        )

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "invalid choice" in captured.err


def test_cli_requires_subcommand(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main([])

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "the following arguments are required: command" in captured.err


def test_new_note_creates_paper_note_and_refuses_to_overwrite_without_force(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    _write_paper_template(tmp_path)

    exit_code = main(
        [
            "new-note",
            "--type",
            "paper",
            "--title",
            "MemoryGraft",
            "--id",
            "paper-memorygraft",
        ]
    )

    assert exit_code == 0
    created = tmp_path / "wiki" / "papers" / "MemoryGraft.md"
    assert created.exists()

    parsed, body = load_frontmatter(created.read_text(encoding="utf-8"))
    assert parsed["id"] == "paper-memorygraft"
    assert parsed["node_type"] == "paper"
    assert body.startswith("\n## Summary\n")

    capsys.readouterr()

    exit_code = main(
        [
            "new-note",
            "--type",
            "paper",
            "--title",
            "MemoryGraft",
            "--id",
            "paper-memorygraft",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "already exists" in captured.err
