"""Interactive CLI for the bidding estimator MVP.

Run with:
    python driver.py

Environment:
    OPENAI_API_KEY – required for extraction.
"""
from pathlib import Path

import typer
from rich.pretty import Pretty
from rich.console import Console
from rich.table import Table

from extract import extract_bid
from pricing_engine import price_bid

app = typer.Typer()
console = Console()


@app.command()
def run(
    file: Path = typer.Option(
        None,
        "--file",
        "-f",
        exists=True,
        readable=True,
        help="Path to text file containing the project description.",
    ),
    stream: bool = typer.Option(False, "--stream", help="Display streaming extraction output."),
):
    """Start an interactive chat-like prompt in the terminal.

    You can either:
    1. Provide a description file via `--file path.txt`, or
    2. Pipe text via stdin (`python driver.py < data.txt`), or
    3. Paste interactively when prompted.
    """

    console.print("[bold cyan]Bidding Estimator – MVP[/bold cyan]")
    if file is not None:
        text = file.read_text()
    else:
        console.print(
            "Paste your project description below. End input with an empty line (or press Ctrl-D when done):\n"
        )

        # Read multiline input until blank line or EOF
        lines = []
        while True:
            try:
                line = input()
            except EOFError:  # user ended input (Ctrl-D or piped stdin EOF)
                break
            if line.strip() == "":
                break
            lines.append(line)

        text = "\n".join(lines)

    if not text.strip():
        console.print("[red]No input provided. Exiting.")
        raise typer.Exit(1)

    console.print("[green]\nExtracting data…[/green]")
    if stream:
        from extract import Extractor  # local import to avoid circular dependency

        extractor = Extractor()
        with Console().status("[cyan]Streaming JSON …") as status:
            for chunk in extractor.extract_stream(text):
                if isinstance(chunk, str):
                    status.update(f"[cyan]JSON: {chunk[-30:]} …")  # show tail
                else:
                    bid_input = chunk
                    break
    else:
        try:
            bid_input = extract_bid(text, debug=True)
        except Exception as err:
            console.print(f"[red]Extraction failed:[/red] {err}")
            raise typer.Exit(1)

    console.print("[green]✅ Extraction successful[/green]")
    console.print(Pretty(bid_input.model_dump(), expand_all=True))

    console.print("[green]\nCalculating pricing…[/green]")
    bid_result = price_bid(bid_input.items, bid_input.bid_type, bid_input.tax_percent)

    _print_summary(bid_result)


def _print_summary(bid):
    table = Table(title=f"Bid Summary – {bid['bid_type']}")
    table.add_column("Line Item")
    table.add_column("Qty", justify="right")
    table.add_column("Labor $/u", justify="right")
    table.add_column("Labor Total", justify="right")
    table.add_column("Material Total", justify="right")
    table.add_column("M-Hrs", justify="right")

    for line in bid["lines"]:
        table.add_row(
            line["name"],
            str(line["quantity"]),
            f"{line['labor_unit_sale']:.2f}",
            f"{line['labor_total_sale']:.2f}",
            f"{line['material_sale']:.2f}",
            f"{line['man_hours']:.2f}",
        )

    table.add_section()
    table.add_row("", "", "", f"[bold]{bid['labor']:.2f}[/bold]", f"[bold]{bid['material']:.2f}[/bold]", "")
    table.add_row("Tax", "", "", "", f"{bid['tax']:.2f}", "")
    table.add_row("Grand Total", "", "", f"[bold]{bid['total']:.2f}[/bold]", "", "")

    console = Console()
    console.print(table)


if __name__ == "__main__":
    app() 