"""Deterministic normalization helpers for compile payload generation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CanonicalRule:
    needle: str
    title: str
    aliases: tuple[str, ...] = ()


CONCEPT_RULES = (
    CanonicalRule(
        needle="indirect prompt injection",
        title="Prompt Injection",
        aliases=("Indirect Prompt Injection",),
    ),
    CanonicalRule(needle="prompt injection", title="Prompt Injection"),
    CanonicalRule(needle="environmental injection", title="Environmental Injection"),
    CanonicalRule(needle="multimodal agent", title="Multimodal Agents"),
    CanonicalRule(needle="multimodal", title="Multimodal Agents"),
    CanonicalRule(needle="benchmark", title="Agent Benchmarks"),
    CanonicalRule(needle="defense", title="Agent Defenses"),
)

METHOD_RULES = (
    CanonicalRule(needle="red teaming", title="Red Teaming Method"),
    CanonicalRule(needle="benchmark", title="Benchmark Evaluation Method"),
)

GAP_RULES = (
    CanonicalRule(needle="cross-modal evaluation gap", title="Cross-Modal Evaluation Gap"),
    CanonicalRule(needle="evaluation gap", title="Evaluation Coverage Gap"),
)


def detect_concepts(haystack: str, paper_title: str) -> list[dict[str, object]]:
    return _detect_rules(CONCEPT_RULES, haystack, paper_title)


def detect_methods(haystack: str, paper_title: str) -> list[dict[str, object]]:
    payloads = _detect_rules(METHOD_RULES, haystack, paper_title)
    for payload in payloads:
        payload["introduced_by"] = [paper_title]
        payload["applies_to"] = []
        payload["limitations"] = []
    return payloads


def detect_gaps(haystack: str, paper_title: str) -> list[dict[str, object]]:
    payloads = _detect_rules(GAP_RULES, haystack, paper_title)
    for payload in payloads:
        payload["gap_kind"] = "evaluation"
        payload["raised_by"] = [paper_title]
        payload["potential_directions"] = []
    return payloads


def build_author_payloads(author_names: list[str], paper_title: str) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for author_name in author_names:
        if not isinstance(author_name, str) or not author_name.strip():
            continue
        payloads.append(
            {
                "title": author_name.strip(),
                "paper_refs": [paper_title],
                "related": [],
            }
        )
    return payloads


def _detect_rules(
    rules: tuple[CanonicalRule, ...],
    haystack: str,
    paper_title: str,
) -> list[dict[str, object]]:
    lowered = haystack.lower()
    payloads_by_title: dict[str, dict[str, object]] = {}
    for rule in rules:
        if rule.needle not in lowered:
            continue
        payload = payloads_by_title.setdefault(
            rule.title,
            {
                "title": rule.title,
                "aliases": [],
                "paper_refs": [paper_title],
                "related": [],
            },
        )
        aliases = payload["aliases"]
        if isinstance(aliases, list):
            for alias in rule.aliases:
                if alias not in aliases:
                    aliases.append(alias)
    return list(payloads_by_title.values())
