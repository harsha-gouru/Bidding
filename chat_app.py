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
    """Generate assistant reply with streaming JSON then pricing table."""

    user_input = message or (file.read().decode() if file else "")
    if not user_input.strip():
        return "Please paste text or upload a .txt file."  # early return

    # Start JSON code block
    reply_prefix = "```json\n"
    json_buffer = ""

    # Stream extraction tokens
    for chunk in extractor.extract_stream(user_input):
        if isinstance(chunk, str):
            json_buffer += chunk
            yield reply_prefix + json_buffer  # intermediate partial
        else:
            bid_obj = chunk  # final object

    # Close JSON block and append pricing
    full_reply = reply_prefix + json_buffer + "\n```\n"

    priced = price_bid(bid_obj.items, bid_obj.bid_type, bid_obj.tax_percent)
    full_reply += dedent(
        f"""
        **Bid Summary – {priced['bid_type']}**
        {_markdown_table(priced)}
        """
    )

    yield full_reply  # final message


def main():
    chat = gr.ChatInterface(
        fn=chat_flow,
        title="Bid Estimator Chat",
        textbox=gr.Textbox(placeholder="Paste your bid text here…", scale=7),
        additional_inputs=gr.File(label="Upload bid text", file_types=[".txt"]),
        description="Paste or upload bid data. The bot streams extracted JSON then pricing table.",
        type="messages",
    )
    chat.launch()


if __name__ == "__main__":
    main() 