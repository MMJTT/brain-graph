"""Validation helpers for compiled paper payloads."""

from __future__ import annotations


def validate_compiled_payload(payload: dict[str, object]) -> None:
    paper = payload.get("paper")
    concepts = payload.get("concepts")
    methods = payload.get("methods")
    gaps = payload.get("gaps")
    authors = payload.get("authors")

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
    if not isinstance(methods, list):
        raise ValueError("compiled payload methods must be a list")
    if not isinstance(gaps, list):
        raise ValueError("compiled payload gaps must be a list")
    if not isinstance(authors, list):
        raise ValueError("compiled payload authors must be a list")

    for concept in concepts:
        if not isinstance(concept, dict):
            raise ValueError("compiled payload concept entries must be mappings")
        if not isinstance(concept.get("title"), str):
            raise ValueError("compiled payload concept.title must be a string")
    for method in methods:
        if not isinstance(method, dict):
            raise ValueError("compiled payload method entries must be mappings")
        if not isinstance(method.get("title"), str):
            raise ValueError("compiled payload method.title must be a string")
    for gap in gaps:
        if not isinstance(gap, dict):
            raise ValueError("compiled payload gap entries must be mappings")
        if not isinstance(gap.get("title"), str):
            raise ValueError("compiled payload gap.title must be a string")
    for author in authors:
        if not isinstance(author, dict):
            raise ValueError("compiled payload author entries must be mappings")
        if not isinstance(author.get("title"), str):
            raise ValueError("compiled payload author.title must be a string")
