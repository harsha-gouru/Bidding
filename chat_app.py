"""Gradio chat UI that streams extraction JSON tokens and returns pricing summary.

Run with:
    python chat_app.py
This starts a local web server (typically http://127.0.0.1:7860) with a ChatGPT-style interface.
"""
from __future__ import annotations

import json
from textwrap import dedent

import gradio as gr

from extract import Extractor
from pricing_engine import price_bid

extractor = Extractor()


def _markdown_table(bid_result: dict) -> str:
    """Return GitHub-flavored Markdown table for pricing summary."""

    header = "| Line Item | Qty | Labor $/u | Labor Total | Material Total | M-Hrs |\n|---|---:|---:|---:|---:|---:|"
    rows = [
        f"| {l['name']} | {l['quantity']} | {l['labor_unit_sale']:.2f} | {l['labor_total_sale']:.2f} | {l['material_sale']:.2f} | {l['man_hours']:.2f} |"
        for l in bid_result["lines"]
    ]
    totals = f"| **Totals** |  |  | **{bid_result['labor']:.2f}** | **{bid_result['material']:.2f}** | |"
    tax = f"| **Tax** |  |  |  | **{bid_result['tax']:.2f}** | |"
    grand = f"| **Grand Total** |  |  | **{bid_result['total']:.2f}** |  | |"
    return "\n".join([header, *rows, totals, tax, grand])


def chat_flow(message, history, file):
    """Yield progressive status messages, then final Markdown table."""

    user_input = message or (file.read().decode() if file else "")
    if not user_input.strip():
        yield "Please paste text or upload a .txt file to estimate costs."
        return

    # Stream extraction as JSON tokens ----------------------------------
    json_buffer = ""
    base_prefix = "```json\n"
    yield "🔄 Parsing input..."

    bid_obj = None
    for chunk in extractor.extract_stream(user_input):
        if isinstance(chunk, str):
            json_buffer += chunk
            yield base_prefix + json_buffer  # live JSON
        else:
            bid_obj = chunk  # final object received

    if bid_obj is None:
        yield "❌ Failed to parse input."
        return

    # Parsed fully
    parsed_json_md = base_prefix + json_buffer + "\n```\n\n✅ Parsed input\n🔄 Calculating pricing..."
    yield parsed_json_md

    # Pricing ------------------------------------------------------------
    priced = price_bid(bid_obj.items, bid_obj.bid_type, bid_obj.tax_percent)

    # Stream table rows one-by-one, keeping JSON block on top
    header = (
        f"**Bid Summary – {priced['bid_type']}**\n"
        "| Item | Qty | Labor $ | Material $ | M-Hrs |\n"
        "|------|----:|--------:|-----------:|------:|"
    )

    current_reply = parsed_json_md + "\n" + header
    yield current_reply

    for line in priced["lines"]:
        row = (
            f"| {line['name']} | {line['quantity']} | {line['labor_total_sale']:.2f} | "
            f"{line['material_sale']:.2f} | {line['man_hours']:.2f} |"
        )
        current_reply += "\n" + row
        yield current_reply

    totals = (
        f"\n| **Totals** | | | **{priced['labor']:.2f}** | **{priced['material']:.2f}** | |"
        f"\n| **Tax** | | | | **{priced['tax']:.2f}** | |"
        f"\n| **Grand Total** | | | **{priced['total']:.2f}** | | |"
    )
    current_reply += totals

    # Final yield
    yield current_reply


def main():
    chat = gr.ChatInterface(
        fn=chat_flow,
        title="Bid Estimator Chat",
        textbox=gr.Textbox(placeholder="Paste your bid text here…", scale=7),
        additional_inputs=gr.File(label="Upload bid text", file_types=[".txt"]),
        description="Hi 👋 Paste or upload your bid data and I'll return a cost breakdown table.",
        type="messages",
    )
    chat.launch()


if __name__ == "__main__":
    main() 