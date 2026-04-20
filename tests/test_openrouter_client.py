import os

import pytest

from brain_graph.openrouter_client import compile_with_openrouter


def test_compile_with_openrouter_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        compile_with_openrouter(
            metadata={"title": "MemoryGraft", "authors": ["Alice"], "abstract": "Test abstract."},
            full_text="Test full text",
            model="openai/gpt-4.1-mini",
        )


def test_compile_with_openrouter_parses_json_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "brain_graph.openrouter_client._post_json",
        lambda url, payload, headers=None: {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"summary":"Model summary.","concepts":[{"title":"Prompt Injection","aliases":[]}],'
                            '"methods":[{"title":"Red Teaming Method"}],'
                            '"gaps":[{"title":"Cross-Modal Evaluation Gap","gap_kind":"evaluation"}],'
                            '"research_notes":["Look for stronger evaluation baselines."]}'
                        )
                    }
                }
            ]
        },
    )

    payload = compile_with_openrouter(
        metadata={"title": "MemoryGraft", "authors": ["Alice"], "abstract": "Test abstract."},
        full_text="Test full text",
        model="openai/gpt-4.1-mini",
    )

    assert payload["summary"] == "Model summary."
    assert payload["concepts"][0]["title"] == "Prompt Injection"
    assert payload["methods"][0]["title"] == "Red Teaming Method"
    assert payload["gaps"][0]["title"] == "Cross-Modal Evaluation Gap"
