"""Minimal frontmatter reader and writer."""

from __future__ import annotations


def dump_frontmatter(data: dict[str, object]) -> str:
    lines: list[str] = ["---"]
    for key, value in data.items():
        if isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {_format_scalar(item)}")
            else:
                lines.append(f"{key}: []")
            continue

        lines.append(f"{key}: {_format_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def load_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text

    lines = text.splitlines(keepends=True)
    data: dict[str, object] = {}
    current_key: str | None = None
    body_start: int | None = None

    for index in range(1, len(lines)):
        raw_line = lines[index]
        line = raw_line.rstrip("\r\n")

        if line == "---":
            body_start = index + 1
            break

        if not line:
            continue

        if line.startswith("  - "):
            if current_key is None or not isinstance(data.get(current_key), list):
                current_key = None
                continue
            data[current_key].append(_parse_scalar(line[4:]))  # type: ignore[union-attr]
            continue

        if ":" not in line:
            current_key = None
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        current_key = key

        if value == "":
            data[key] = []
            continue

        data[key] = _parse_scalar(value)

    if body_start is None:
        return {}, text

    return data, "".join(lines[body_start:])


def _format_scalar(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, str):
        return value
    return str(value)


def _parse_scalar(value: str) -> object:
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        try:
            return int(value)
        except ValueError:
            return value
    return value
