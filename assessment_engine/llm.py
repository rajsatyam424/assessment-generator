"""
LLM client — sends prompts to OpenAI-compatible APIs.
Supports OpenAI and OpenRouter out of the box.
"""

import logging
from typing import Optional

from openai import OpenAI

from . import config

logger = logging.getLogger(__name__)


def call_llm(
    prompt: str,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """
    Call an OpenAI-compatible LLM and return the raw response text.

    Args:
        prompt: The full prompt to send.
        model: Model name (default: config.MODEL).
        provider: 'openai' or 'openrouter' (default: config.PROVIDER).
        api_key: API key (default: config.API_KEY).

    Returns:
        Raw response text from the LLM.

    Raises:
        ValueError: If no API key is configured.
        openai.APIError: If the API call fails.
    """
    model = model or config.MODEL
    provider = provider or config.PROVIDER
    key = api_key or config.API_KEY

    if not key:
        raise ValueError(
            "No API key found. Set OPENAI_API_KEY env var "
            "or pass api_key explicitly."
        )

    client = OpenAI(api_key=key)
    base_url = None

    if provider == "openrouter":
        client.base_url = "https://openrouter.ai/api/v1"
    elif provider == "openai":
        pass  # default
    else:
        # Allow custom providers with a base_url
        env_url = config._env_str("OPENAI_BASE_URL", "")
        if env_url:
            client.base_url = env_url

    system = (
        "You are a precise learning assessment designer. "
        "Always return valid JSON matching the requested structure exactly. "
        "No markdown, no code fences, no extra text."
    )

    logger.info(
        "Calling LLM — provider=%s model=%s prompt_len=%d",
        provider, model, len(prompt),
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    logger.info("LLM response received — %d chars", len(raw))
    return raw
