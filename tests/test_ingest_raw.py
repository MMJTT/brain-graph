import pytest

from brain_graph.cli import main
import brain_graph.cli as cli_module
from brain_graph.frontmatter import load_frontmatter
from brain_graph.ingest_raw import IngestRawCommand, ingest_raw_entry


def test_ingest_raw_entry_creates_timestamped_raw_paper(tmp_path):
    command = IngestRawCommand(
        kind="paper",
        slug="memorygraft",
        title="MemoryGraft",
        source_url="https://arxiv.org/abs/2512.16962",
    )

    target = ingest_raw_entry(tmp_path, command, "2026-04-19")

    assert target == tmp_path / "raw" / "papers" / "2026-04-19-memorygraft.md"

    text = target.read_text(encoding="utf-8")
    assert "# MemoryGraft" in text
    assert "source_url: https://arxiv.org/abs/2512.16962" in text

    parsed, body = load_frontmatter(text)
    assert parsed["kind"] == "paper"
    assert parsed["slug"] == "memorygraft"
    assert parsed["title"] == "MemoryGraft"
    assert parsed["source_url"] == "https://arxiv.org/abs/2512.16962"
    assert body.startswith("\n# MemoryGraft\n")


def test_ingest_raw_entry_handles_missing_source_url(tmp_path):
    command = IngestRawCommand(
        kind="paper",
        slug="offline-note",
        title="Offline Note",
        source_url=None,
    )

    target = ingest_raw_entry(tmp_path, command, "2026-04-19")

    parsed, body = load_frontmatter(target.read_text(encoding="utf-8"))
    assert "source_url" not in parsed
    assert body.startswith("\n# Offline Note\n")
    assert "Source:" not in body


def test_ingest_raw_entry_is_append_only(tmp_path):
    command = IngestRawCommand(
        kind="paper",
        slug="memorygraft",
        title="MemoryGraft",
        source_url="https://arxiv.org/abs/2512.16962",
    )
    target = tmp_path / "raw" / "papers" / "2026-04-19-memorygraft.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError) as excinfo:
        ingest_raw_entry(tmp_path, command, "2026-04-19")

    assert "append-only" in str(excinfo.value)


def test_ingest_raw_cli_requires_required_arguments(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as excinfo:
        main(["ingest-raw", "--kind", "paper"])

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "the following arguments are required" in captured.err


def test_ingest_raw_cli_allows_missing_source_url(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class FrozenDate(cli_module.date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 19)

    monkeypatch.setattr(cli_module, "date", FrozenDate)

    exit_code = main(
        [
            "ingest-raw",
            "--kind",
            "paper",
            "--slug",
            "offline-note",
            "--title",
            "Offline Note",
        ]
    )

    assert exit_code == 0
    target = tmp_path / "raw" / "papers" / "2026-04-19-offline-note.md"
    parsed, body = load_frontmatter(target.read_text(encoding="utf-8"))
    assert "source_url" not in parsed
    assert body.startswith("\n# Offline Note\n")
    assert "Source:" not in body


def test_ingest_raw_cli_creates_file_and_preserves_summary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    class FrozenDate(cli_module.date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 19)

    monkeypatch.setattr(cli_module, "date", FrozenDate)

    exit_code = main(
        [
            "ingest-raw",
            "--kind",
            "paper",
            "--slug",
            "memorygraft",
            "--title",
            "MemoryGraft",
            "--source-url",
            "https://arxiv.org/abs/2512.16962",
            "--summary",
            "Short summary",
        ]
    )

    assert exit_code == 0
    target = tmp_path / "raw" / "papers" / "2026-04-19-memorygraft.md"
    assert target.exists()

    parsed, body = load_frontmatter(target.read_text(encoding="utf-8"))
    assert parsed["summary"] == "Short summary"
    assert body.startswith("\n# MemoryGraft\n")
    assert "Short summary" in body
