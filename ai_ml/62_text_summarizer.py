"""
62_text_summarizer.py
─────────────────────────────────────────────────────────────────────────────
AI Text Summarizer using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Summarize long articles, research papers, or any text content. Read input
from a local file, a URL, or interactive stdin. Choose summary length:
brief (1–2 paragraphs) or detailed (structured with key points).

Usage:
    python 62_text_summarizer.py
    python 62_text_summarizer.py --file article.txt --mode brief
    python 62_text_summarizer.py --url https://example.com/article --mode detailed

Requirements:
    pip install google-generativeai rich requests
    Set env var: GEMINI_API_KEY
"""

import os
import sys
import argparse
import textwrap

try:
    import google.generativeai as genai
except ImportError:
    print("Missing: pip install google-generativeai")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

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
                "Get a key at: [link]https://aistudio.google.com/app/apikey[/link]",
                title="[red]Missing API Key",
                border_style="red",
            )
        )
        sys.exit(1)
    return key

# ─── Text Fetchers ─────────────────────────────────────────────────────────────

def fetch_from_url(url: str) -> str:
    """Fetch page text from a URL (simple HTML-to-text extraction)."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        # Strip HTML tags roughly
        import re
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        console.print(f"[red]Failed to fetch URL:[/red] {e}")
        sys.exit(1)


def read_from_file(path: str) -> str:
    """Read text from a local file."""
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_from_stdin() -> str:
    """Prompt user to paste text interactively."""
    console.print(
        Panel(
            "Paste your text below. When done, enter [bold]END[/bold] on a new line and press Enter.",
            title="[cyan]Paste Text",
            border_style="cyan",
        )
    )
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

# ─── Summarization ─────────────────────────────────────────────────────────────

PROMPTS = {
    "brief": (
        "You are an expert summarizer. Summarize the following text in 1–2 concise paragraphs. "
        "Capture the main idea and most important points only. Be clear and direct.\n\n"
        "TEXT:\n{text}\n\nSUMMARY:"
    ),
    "detailed": (
        "You are an expert summarizer. Provide a detailed, structured summary of the following text. "
        "Include:\n"
        "- **Overview**: One-sentence summary\n"
        "- **Key Points**: Bullet list of main ideas\n"
        "- **Details**: Important facts, arguments, data\n"
        "- **Conclusion**: Main takeaway\n\n"
        "TEXT:\n{text}\n\nSTRUCTURED SUMMARY:"
    ),
    "bullets": (
        "Summarize the following text as a concise bullet-point list. "
        "Each bullet should be one key idea. Maximum 10 bullets.\n\n"
        "TEXT:\n{text}\n\nBULLETS:"
    ),
}


def summarize(text: str, mode: str, model: genai.GenerativeModel) -> str:
    """Call Gemini to summarize text."""
    # Truncate extremely long texts to ~12000 chars (token limit safety)
    MAX_CHARS = 12000
    if len(text) > MAX_CHARS:
        console.print(
            f"[yellow]⚠ Text is {len(text):,} chars; truncating to {MAX_CHARS:,} for API limits.[/yellow]"
        )
        text = text[:MAX_CHARS] + "\n\n[...text truncated...]"

    prompt_template = PROMPTS.get(mode, PROMPTS["detailed"])
    prompt = prompt_template.format(text=text)

    response = model.generate_content(prompt)
    return response.text

# ─── Display ─────────────────────────────────────────────────────────────────

def display_summary(summary: str, mode: str, source: str) -> None:
    mode_label = {"brief": "📝 Brief", "detailed": "📋 Detailed", "bullets": "• Bullet Points"}.get(mode, mode)
    console.print()
    console.print(Rule(f"[bold green]{mode_label} Summary[/bold green]"))
    console.print(f"[dim]Source: {source}[/dim]")
    console.print()
    console.print(Panel(Markdown(summary), border_style="green", padding=(1, 2)))
    console.print()
    console.print(f"[dim]Summary length: {len(summary):,} characters[/dim]")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Text Summarizer powered by Google Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python 62_text_summarizer.py
              python 62_text_summarizer.py --file report.txt --mode brief
              python 62_text_summarizer.py --url https://en.wikipedia.org/wiki/Python_(programming_language) --mode bullets
        """),
    )
    parser.add_argument("--file", help="Path to a text file to summarize")
    parser.add_argument("--url", help="URL to fetch and summarize")
    parser.add_argument(
        "--mode",
        choices=["brief", "detailed", "bullets"],
        default=None,
        help="Summary mode: brief | detailed | bullets",
    )
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model name")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]AI Text Summarizer[/bold cyan]\n"
            "[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Get text ──
    source = "stdin"
    if args.file:
        with console.status("[cyan]Reading file…[/cyan]"):
            text = read_from_file(args.file)
        source = args.file
    elif args.url:
        with console.status("[cyan]Fetching URL…[/cyan]"):
            text = fetch_from_url(args.url)
        source = args.url
    else:
        text = read_from_stdin()

    if not text.strip():
        console.print("[red]No text provided. Exiting.[/red]")
        sys.exit(1)

    console.print(f"\n[green]✓ Got {len(text):,} characters of text.[/green]")

    # ── Choose mode ──
    mode = args.mode
    if not mode:
        mode = Prompt.ask(
            "\n[bold]Summary mode[/bold]",
            choices=["brief", "detailed", "bullets"],
            default="detailed",
        )

    # ── Summarize ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    with console.status("[bold green]Summarizing with Gemini…[/bold green]", spinner="dots"):
        try:
            summary = summarize(text, mode, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    display_summary(summary, mode, source)

    # ── Save option ──
    if Confirm.ask("[dim]Save summary to file?[/dim]", default=False):
        from datetime import datetime
        outfile = f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(f"Source: {source}\nMode: {mode}\n\n")
            f.write(summary)
        console.print(f"[green]✓ Saved to[/green] [bold]{outfile}[/bold]")


if __name__ == "__main__":
    main()
