"""Helpers for stable Brain Graph slugs."""

from __future__ import annotations

import re


def slugify_title(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
