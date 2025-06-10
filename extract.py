"""LLM-powered extraction utility.

Converts raw user text into a `BidInput` instance via OpenAI function calling.

Requirements:
- environment variable `OPENAI_API_KEY` or openai.api_key must be set.
- Uses GPT-4o-mini by default.
"""
from __future__ import annotations

import json
import os
from typing import Optional

import openai
from pydantic import ValidationError
from rich import print as rprint

from schema import BidInput

MODEL_DEFAULT = os.getenv("OPENAI_BID_EXTRACT_MODEL", "gpt-4o-mini")
MAX_RETRIES = 3

def _build_function_schema():
    return {
        "name": "submit_bid_input",
        "description": "Structured bid data extracted from user text.",
        "parameters": BidInput.schema(),
    }


def extract_bid(text: str, model: str = MODEL_DEFAULT, *, debug: bool = False) -> BidInput:
    """Return a validated `BidInput` from raw input text.

    Raises `ValueError` if extraction fails after retries.
    """

    client = openai.OpenAI()  # uses env var for key
    system_prompt = (
        "You are a data-extraction engine. Return ONLY valid JSON that matches the BidInput schema. "
        "Do not add commentary. If unsure, ask a follow-up question instead of guessing."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    fn_schema = _build_function_schema()

    for attempt in range(1, MAX_RETRIES + 1):
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            top_p=0.1,
            messages=messages,
            functions=[fn_schema],
            function_call="auto",
        )

        msg = response.choices[0].message
        if msg.function_call:
            try:
                args = json.loads(msg.function_call.arguments)
            except json.JSONDecodeError as err:
                if debug:
                    rprint(f"[red]JSON parse error:[/red] {err}")
                messages.append({
                    "role": "assistant",
                    "content": "The previous JSON could not be parsed. Please output valid JSON only.",
                })
                continue
        else:
            # Model didn't use function call path
            try:
                args = json.loads(msg.content)
            except json.JSONDecodeError:
                if debug:
                    rprint("[red]Assistant response lacked valid JSON. Retrying…[/red]")
                messages.append({
                    "role": "assistant",
                    "content": "Respond with ONLY valid JSON per schema.",
                })
                continue

        try:
            bid = BidInput(**args)
            return bid
        except ValidationError as err:
            if debug:
                rprint(f"[yellow]Validation error:[/yellow] {err}")
            # add error details and retry
            messages.append({
                "role": "assistant",
                "content": (
                    "The JSON you produced was invalid: "
                    f"{err}. Correct the JSON and output only valid JSON."
                ),
            })

    raise ValueError("Failed to extract bid data after multiple attempts.")


# ---------------------------------------------------------------------------
# Streaming extraction helper
# ---------------------------------------------------------------------------


class Extractor:
    """OpenAI-powered bid extractor supporting streaming and non-stream modes."""

    def __init__(self, model: str | None = None):
        self.model = model or MODEL_DEFAULT
        self.client = openai.OpenAI()

    # non-streaming (wrapper around existing function)
    def extract(self, text: str, debug: bool = False) -> BidInput:
        return extract_bid(text, model=self.model, debug=debug)

    # streaming version yields incremental strings and finally returns BidInput
    def extract_stream(self, text: str, debug: bool = False):
        """Yield tokens as they arrive, then final BidInput instance.

        Usage::

            extractor = Extractor()
            for chunk in extractor.extract_stream(text):
                if isinstance(chunk, BidInput):
                    final_bid = chunk
                else:
                    print(chunk, end="", flush=True)
        """

        system_prompt = (
            "You are a data-extraction engine. Return ONLY valid JSON that matches the BidInput schema. "
            "Do not add commentary. If unsure, ask a follow-up question instead of guessing."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]

        fn_schema = _build_function_schema()

        # NOTE: we stream only one attempt (no retries) for simplicity.
        stream = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            top_p=0.1,
            messages=messages,
            functions=[fn_schema],
            function_call="auto",
            stream=True,
        )

        # Collect content/argument string incrementally
        json_buffer = ""

        for chunk in stream:
            delta = chunk.choices[0].delta
            # Function-calling path
            if delta.function_call and delta.function_call.arguments is not None:
                token = delta.function_call.arguments
                json_buffer += token
                yield token
                continue

            # Plain content path (model returns raw JSON string)
            if delta.content is not None:
                json_buffer += delta.content
                yield delta.content
                continue

        # Once stream ends, attempt to parse
        if not json_buffer.strip():
            raise ValueError("Model streamed no JSON content")

        try:
            args = json.loads(json_buffer)
            bid = BidInput(**args)
            yield bid  # final object
        except Exception as err:  # pragma: no cover
            if debug:
                rprint(f"[red]Failed to parse streamed JSON:[/red] {err}")
            raise 