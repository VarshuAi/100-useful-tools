"""
64_sentiment_analyzer.py
─────────────────────────────────────────────────────────────────────────────
AI Sentiment Analyzer using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Analyze sentiment (Positive / Negative / Neutral / Mixed) for individual
texts, interactive input, or batch CSV files. Includes confidence scores,
sentiment breakdown, and emotional tone detection.

Usage:
    python 64_sentiment_analyzer.py
    python 64_sentiment_analyzer.py --text "I love this product!"
    python 64_sentiment_analyzer.py --csv reviews.csv --column text --output results.csv

Requirements:
    pip install google-generativeai rich
    Set env var: GEMINI_API_KEY
"""

import os
import sys
import json
import argparse
import textwrap

try:
    import google.generativeai as genai
except ImportError:
    print("Missing: pip install google-generativeai")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from rich.text import Text
from rich.rule import Rule
from rich import box

console = Console()

SENTIMENT_COLORS = {
    "Positive": "bold green",
    "Negative": "bold red",
    "Neutral": "bold yellow",
    "Mixed": "bold magenta",
}

SENTIMENT_EMOJI = {
    "Positive": "😊",
    "Negative": "😞",
    "Neutral": "😐",
    "Mixed": "🤔",
}

# ─── API Key ──────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        console.print(
            Panel(
                "[bold red]GEMINI_API_KEY not set![/bold red]\n\n"
                "Set it with:\n"
                "  [cyan]$env:GEMINI_API_KEY = 'your_key'[/cyan]  (PowerShell)\n"
                "  [cyan]export GEMINI_API_KEY='your_key'[/cyan]   (bash)\n\n"
                "Get a key: [link]https://aistudio.google.com/app/apikey[/link]",
                title="[red]Missing API Key",
                border_style="red",
            )
        )
        sys.exit(1)
    return key

# ─── Sentiment Analysis ───────────────────────────────────────────────────────

ANALYSIS_PROMPT = """Analyze the sentiment of the following text. 
Respond ONLY with a JSON object with this exact structure:
{{
  "sentiment": "<Positive|Negative|Neutral|Mixed>",
  "confidence": <0.0-1.0>,
  "positive_score": <0.0-1.0>,
  "negative_score": <0.0-1.0>,
  "neutral_score": <0.0-1.0>,
  "emotions": ["<emotion1>", "<emotion2>"],
  "reasoning": "<one sentence explanation>",
  "key_phrases": ["<phrase1>", "<phrase2>"]
}}

TEXT: {text}"""


def analyze_sentiment(text: str, model: genai.GenerativeModel) -> dict:
    """Call Gemini to analyze sentiment, return structured dict."""
    prompt = ANALYSIS_PROMPT.format(text=text[:2000])  # Limit per call
    resp = model.generate_content(prompt)
    raw = resp.text.strip()

    # Extract JSON
    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"sentiment": "Unknown", "confidence": 0.0, "reasoning": raw, "emotions": [], "key_phrases": []}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"sentiment": "Unknown", "confidence": 0.0, "reasoning": raw, "emotions": [], "key_phrases": []}

# ─── Display ─────────────────────────────────────────────────────────────────

def confidence_bar(score: float, width: int = 20) -> str:
    """Return an ASCII confidence bar."""
    filled = int(score * width)
    return "█" * filled + "░" * (width - filled)


def display_single_result(text: str, result: dict) -> None:
    sentiment = result.get("sentiment", "Unknown")
    confidence = result.get("confidence", 0.0)
    color = SENTIMENT_COLORS.get(sentiment, "white")
    emoji = SENTIMENT_EMOJI.get(sentiment, "❓")

    # Header panel
    preview = text[:120] + ("…" if len(text) > 120 else "")
    console.print()
    console.print(Panel(f'[dim]"{preview}"[/dim]', title="[bold]Input Text[/bold]", border_style="dim"))

    # Main result
    scores_text = (
        f"[green]Positive:[/green] {confidence_bar(result.get('positive_score', 0), 15)} "
        f"{result.get('positive_score', 0):.0%}\n"
        f"[red]Negative:[/red] {confidence_bar(result.get('negative_score', 0), 15)} "
        f"{result.get('negative_score', 0):.0%}\n"
        f"[yellow]Neutral:[/yellow]  {confidence_bar(result.get('neutral_score', 0), 15)} "
        f"{result.get('neutral_score', 0):.0%}\n\n"
        f"[bold]Confidence:[/bold] {confidence_bar(confidence, 20)} {confidence:.0%}\n\n"
        f"[bold]Emotions:[/bold]  {', '.join(result.get('emotions', [])) or 'none detected'}\n"
        f"[bold]Key Phrases:[/bold] {', '.join(result.get('key_phrases', [])) or 'none'}\n\n"
        f"[bold]Reasoning:[/bold] [italic]{result.get('reasoning', '')}[/italic]"
    )

    console.print(
        Panel(
            f"{emoji} [{color}]{sentiment}[/{color}]\n\n" + scores_text,
            title="[bold]Sentiment Analysis Result[/bold]",
            border_style=sentiment.lower() if sentiment in ("positive", "negative") else "cyan",
        )
    )


def display_batch_results(texts: list[str], results: list[dict]) -> None:
    """Show a summary table for batch analysis."""
    table = Table(
        title="Batch Sentiment Analysis Results",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Text Preview", overflow="fold", max_width=45)
    table.add_column("Sentiment", justify="center")
    table.add_column("Confidence", justify="right")
    table.add_column("Emotions", overflow="fold", max_width=25)

    counts: dict[str, int] = {}
    for i, (text, result) in enumerate(zip(texts, results), 1):
        sentiment = result.get("sentiment", "Unknown")
        counts[sentiment] = counts.get(sentiment, 0) + 1
        color = SENTIMENT_COLORS.get(sentiment, "white")
        emoji = SENTIMENT_EMOJI.get(sentiment, "❓")
        conf = result.get("confidence", 0.0)
        preview = text[:50].replace("\n", " ") + ("…" if len(text) > 50 else "")
        emotions = ", ".join(result.get("emotions", [])[:2])
        table.add_row(
            str(i),
            preview,
            f"{emoji} [{color}]{sentiment}[/{color}]",
            f"{conf:.0%}",
            emotions,
        )

    console.print(table)

    # Summary
    summary_table = Table(title="Summary", box=box.SIMPLE_HEAVY, border_style="dim")
    summary_table.add_column("Sentiment")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Percentage", justify="right")
    total = len(results)
    for sentiment, count in sorted(counts.items(), key=lambda x: -x[1]):
        color = SENTIMENT_COLORS.get(sentiment, "white")
        emoji = SENTIMENT_EMOJI.get(sentiment, "❓")
        summary_table.add_row(
            f"{emoji} [{color}]{sentiment}[/{color}]",
            str(count),
            f"{count/total:.0%}",
        )
    console.print(summary_table)

# ─── CSV Handling ─────────────────────────────────────────────────────────────

def load_csv(path: str, column: str) -> tuple[list[str], list[dict]]:
    """Load texts from CSV file. Returns (texts, rows)."""
    import csv
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    texts = []
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if column not in row:
                console.print(f"[red]Column '{column}' not found. Available: {list(row.keys())}[/red]")
                sys.exit(1)
            texts.append(row[column])
            rows.append(row)
    return texts, rows


def save_csv_results(rows: list[dict], results: list[dict], output_path: str) -> None:
    """Append sentiment columns to original rows and save."""
    import csv
    extra_cols = ["sentiment", "confidence", "positive_score", "negative_score", "neutral_score", "emotions", "reasoning"]
    fieldnames = list(rows[0].keys()) + extra_cols
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row, result in zip(rows, results):
            combined = dict(row)
            for col in extra_cols:
                val = result.get(col, "")
                combined[col] = ", ".join(val) if isinstance(val, list) else str(val)
            writer.writerow(combined)
    console.print(f"[green]✓ Results saved to[/green] [bold]{output_path}[/bold]")

# ─── Interactive Mode ─────────────────────────────────────────────────────────

def interactive_mode(model: genai.GenerativeModel) -> None:
    console.print(
        Panel(
            "Enter text to analyze. Type [bold]done[/bold] to stop.",
            title="[cyan]Interactive Sentiment Analysis[/cyan]",
            border_style="cyan",
        )
    )
    while True:
        console.print()
        text = Prompt.ask("[bold cyan]Text[/bold cyan]").strip()
        if text.lower() in ("done", "exit", "quit", ""):
            break
        with console.status("[green]Analyzing…[/green]", spinner="dots"):
            result = analyze_sentiment(text, model)
        display_single_result(text, result)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Sentiment Analyzer powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 64_sentiment_analyzer.py
              python 64_sentiment_analyzer.py --text "The service was terrible!"
              python 64_sentiment_analyzer.py --csv reviews.csv --column review_text --output out.csv
        """),
    )
    parser.add_argument("--text", help="Single text to analyze")
    parser.add_argument("--csv", help="CSV file for batch analysis")
    parser.add_argument("--column", default="text", help="Column name in CSV (default: text)")
    parser.add_argument("--output", help="Output CSV path for batch results")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model name")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]AI Sentiment Analyzer[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    if args.text:
        with console.status("[green]Analyzing…[/green]", spinner="dots"):
            result = analyze_sentiment(args.text, model)
        display_single_result(args.text, result)

    elif args.csv:
        texts, rows = load_csv(args.csv, args.column)
        console.print(f"[green]✓ Loaded {len(texts)} texts from[/green] [bold]{args.csv}[/bold]")
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Analyzing…", total=len(texts))
            for text in texts:
                results.append(analyze_sentiment(text, model))
                progress.advance(task)

        display_batch_results(texts, results)
        if args.output:
            save_csv_results(rows, results, args.output)
        elif Confirm.ask("[dim]Save results to CSV?[/dim]", default=False):
            from datetime import datetime
            out = f"sentiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            save_csv_results(rows, results, out)
    else:
        interactive_mode(model)


if __name__ == "__main__":
    main()
