"""Minimal OpenRouter client for structured paper compilation."""

from __future__ import annotations

import json
import os
import urllib.request


def compile_with_openrouter(
    metadata: dict[str, object],
    full_text: str,
    model: str | None,
) -> dict[str, object]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required for the openrouter compiler")

    payload = {
        "model": model or "openai/gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract structured research notes. "
                    "Return only valid JSON with keys: summary, concepts, methods, gaps, research_notes."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "title": metadata.get("title"),
                        "authors": metadata.get("authors", []),
                        "abstract": metadata.get("abstract", ""),
                        "full_text": full_text,
                    },
                    ensure_ascii=True,
                ),
            },
        ],
        "response_format": {"type": "json_object"},
    }
    response = _post_json(
        "https://openrouter.ai/api/v1/chat/completions",
        payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("OpenRouter response missing choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ValueError("OpenRouter response choice must be a mapping")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise ValueError("OpenRouter response missing message payload")
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("OpenRouter response missing message content")
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("OpenRouter content must decode to a JSON object")
    return parsed


def _post_json(
    url: str,
    payload: dict[str, object],
    headers: dict[str, str] | None = None,
) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=True).encode("utf-8"),
        headers=headers or {},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))
