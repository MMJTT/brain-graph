"""Validation helpers for compiled paper payloads."""

from __future__ import annotations


def validate_compiled_payload(payload: dict[str, object]) -> None:
    paper = payload.get("paper")
    concepts = payload.get("concepts")

    if not isinstance(paper, dict):
        raise ValueError("compiled payload missing paper section")
    if not isinstance(paper.get("id"), str):
        raise ValueError("compiled payload paper.id must be a string")
    if not isinstance(paper.get("title"), str):
        raise ValueError("compiled payload paper.title must be a string")
    if not isinstance(paper.get("summary"), str):
        raise ValueError("compiled payload paper.summary must be a string")
    if not isinstance(concepts, list):
        raise ValueError("compiled payload concepts must be a list")

    for concept in concepts:
        if not isinstance(concept, dict):
            raise ValueError("compiled payload concept entries must be mappings")
        if not isinstance(concept.get("title"), str):
            raise ValueError("compiled payload concept.title must be a string")
