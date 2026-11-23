"""Configure the browser-use model from the caller's environment."""

from __future__ import annotations

import os


def create_llm(
    model: str = "gpt-5.2-20251211",
    temperature: float = 0,
    api_version: str | None = None,
    salvage_multi_json: bool = False,
    reasoning_effort: str | None = None,
):
    options = {"model": model, "temperature": temperature}
    if reasoning_effort:
        options["reasoning_effort"] = reasoning_effort
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        from browser_use.llm.azure.chat import ChatAzureOpenAI as Chat

        if api_version or os.getenv("OPENAI_API_VERSION"):
            options["api_version"] = api_version or os.environ["OPENAI_API_VERSION"]
    else:
        from browser_use.llm.openai.chat import ChatOpenAI as Chat

        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("Set OPENAI_API_KEY for your model provider.")
        options["base_url"] = os.getenv("OPENAI_BASE_URL")
    if salvage_multi_json:
        if "salvage_multi_json" not in Chat.__dataclass_fields__:
            raise RuntimeError("Apply the included browser-use structured-output patch before enabling salvage.")
        options["salvage_multi_json"] = True
    return Chat(**options)
