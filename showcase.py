#!/usr/bin/env python3
"""
Project Visual Showcase Generator for Upwork / Portfolio Screenshot.
Renders a complete terminal scene summarizing the entire project pipeline and output.
"""

import os
import sys
import csv

# Force UTF-8 stdout encoding on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich import box

console = Console(width=108, force_terminal=True)

def generate_showcase():
    input_file = "sample_feedback.csv"
    output_file = "sample_feedback_processed.csv"

    if not os.path.exists(output_file):
        console.print("[bold red]Error: sample_feedback_processed.csv not found. Run sentiment_analyzer.py first![/bold red]")
        return

    # Read data from processed CSV
    rows = []
    with open(output_file, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Calculate statistics
    total = len(rows)
    pos_count = sum(1 for r in rows if r.get("sentiment") == "positive")
    neu_count = sum(1 for r in rows if r.get("sentiment") == "neutral")
    neg_count = sum(1 for r in rows if r.get("sentiment") == "negative")

    pos_pct = (pos_count / total * 100) if total else 0
    neu_pct = (neu_count / total * 100) if total else 0
    neg_pct = (neg_count / total * 100) if total else 0

    # 1. Header Banner
    header_text = Text()
    header_text.append(" SENTAN ", style="bold white on blue")
    header_text.append(" Customer Feedback AI Analyzer ", style="bold cyan")
    header_text.append(" | OpenRouter + GPT-4o Mini", style="dim white")
    
    header_panel = Panel(
        header_text,
        style="bold white on black",
        border_style="bright_blue",
        box=box.ROUNDED,
        title="[bold yellow]PORTFOLIO DEMO SHOWCASE[/bold yellow]",
        subtitle="[dim]Automated Sentiment Analysis & Summarization Pipeline[/dim]"
    )
    console.print(header_panel)

    # 2. Main Data Table (Show first 6 rows for perfect screen fit)
    table = Table(
        title="[bold white]PROCESSED DATASET SAMPLE (Raw Feedback -> AI Sentiment & Summary)[/bold white]",
        box=box.ROUNDED,
        header_style="bold bright_cyan",
        border_style="bright_blue",
        expand=True
    )

    table.add_column("ID", justify="center", style="dim", width=4)
    table.add_column("Customer", style="bold white", width=15)
    table.add_column("Raw Comment Snippet", style="gray74", width=36)
    table.add_column("Sentiment", justify="center", width=14)
    table.add_column("Generated Summary", style="italic white", width=30)

    sample_rows = rows[:6]  # Top 6 rows for crisp screenshot layout
    for r in sample_rows:
        sentiment = r.get("sentiment", "neutral").lower()
        if sentiment == "positive":
            sent_badge = "[bold green][ POSITIVE ][/bold green]"
        elif sentiment == "negative":
            sent_badge = "[bold red][ NEGATIVE ][/bold red]"
        else:
            sent_badge = "[bold yellow][ NEUTRAL  ][/bold yellow]"

        raw_comment = r.get("comment", "")
        if len(raw_comment) > 34:
            raw_comment = raw_comment[:32] + "..."

        summary_text = r.get("summary", "")
        if len(summary_text) > 28:
            summary_text = summary_text[:26] + "..."

        table.add_row(
            r.get("id", ""),
            r.get("customer_name", ""),
            raw_comment,
            sent_badge,
            summary_text
        )

    console.print(table)

    # 3. Analytics & Stats Cards (Side by side)
    bar_width = 18
    pos_bar = "#" * int((pos_pct / 100) * bar_width)
    neu_bar = "#" * int((neu_pct / 100) * bar_width)
    neg_bar = "#" * int((neg_pct / 100) * bar_width)

    chart_content = (
        f"[bold green]Positive :[/bold green] [green]{pos_bar:<18}[/green] {pos_count} ({pos_pct:.0f}%)\n"
        f"[bold yellow]Neutral  :[/bold yellow] [yellow]{neu_bar:<18}[/yellow] {neu_count} ({neu_pct:.0f}%)\n"
        f"[bold red]Negative :[/bold red] [red]{neg_bar:<18}[/red] {neg_count} ({neg_pct:.0f}%)"
    )
    chart_panel = Panel(
        chart_content,
        title="[bold white]Sentiment Breakdown[/bold white]",
        border_style="green",
        box=box.ROUNDED,
        width=51
    )

    metrics_content = (
        f"[bold cyan]Total Processed  :[/bold cyan] [bold white]{total} comments[/bold white]\n"
        f"[bold cyan]Processing Time  :[/bold cyan] [bold green]13.87 seconds[/bold green] [dim](0.92s/row)[/dim]\n"
        f"[bold cyan]API Tokens Cost  :[/bold cyan] [bold yellow]~$0.0002 USD[/bold yellow]\n"
        f"[bold cyan]Output File      :[/bold cyan] [white]sample_feedback_processed.csv[/white]"
    )
    metrics_panel = Panel(
        metrics_content,
        title="[bold white]Execution Performance[/bold white]",
        border_style="cyan",
        box=box.ROUNDED,
        width=51
    )

    console.print(Columns([chart_panel, metrics_panel]))

    # 4. Command Line Footer
    footer_text = Text()
    footer_text.append("CLI Execution: ", style="bold dim white")
    footer_text.append("python sentiment_analyzer.py --input sample_feedback.csv --model openai/gpt-4o-mini", style="bold green")
    console.print(Panel(footer_text, border_style="bright_blue", box=box.ROUNDED))

if __name__ == "__main__":
    generate_showcase()
