"""
63_code_explainer.py
─────────────────────────────────────────────────────────────────────────────
AI Code Explainer using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Paste or load source code and get a detailed plain-English explanation.
Supports Python, JavaScript, C++, Java, and more. Offers a line-by-line mode
for granular breakdowns.

Usage:
    python 63_code_explainer.py
    python 63_code_explainer.py --file myscript.py
    python 63_code_explainer.py --file main.js --lang javascript --linewise

Requirements:
    pip install google-generativeai rich
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

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table
from rich import box

console = Console()

SUPPORTED_LANGS = ["python", "javascript", "typescript", "java", "c++", "c", "go", "rust", "bash", "sql", "other"]

LANG_ALIASES = {
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "cpp": "c++",
    "sh": "bash",
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

# ─── Language Detection ───────────────────────────────────────────────────────

def detect_language_from_file(path: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".cpp": "c++", ".c": "c",
        ".go": "go", ".rs": "rust", ".sh": "bash", ".sql": "sql",
    }
    ext = os.path.splitext(path)[1].lower()
    return ext_map.get(ext, "other")


def rich_lang_name(lang: str) -> str:
    """Return Rich's syntax highlighter name for a language."""
    mapping = {
        "python": "python", "javascript": "javascript", "typescript": "typescript",
        "java": "java", "c++": "cpp", "c": "c", "go": "go", "rust": "rust",
        "bash": "bash", "sql": "sql", "other": "text",
    }
    return mapping.get(lang.lower(), "text")

# ─── Code Input ───────────────────────────────────────────────────────────────

def read_code_from_file(path: str) -> str:
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_code_from_stdin() -> str:
    console.print(
        Panel(
            "Paste your code below. Enter [bold]END[/bold] on a new line when finished.",
            title="[cyan]Paste Code",
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

# ─── AI Explanation ───────────────────────────────────────────────────────────

def explain_overall(code: str, lang: str, model: genai.GenerativeModel) -> str:
    prompt = (
        f"You are an expert {lang} programmer and teacher. "
        f"Explain the following {lang} code in plain English.\n\n"
        "Your explanation should cover:\n"
        "1. **Purpose**: What does this code do overall?\n"
        "2. **Key Concepts**: What programming patterns, algorithms, or techniques are used?\n"
        "3. **How It Works**: Step-by-step walkthrough of the logic.\n"
        "4. **Inputs & Outputs**: What does it take in and produce?\n"
        "5. **Notable Details**: Anything clever, unusual, or worth highlighting.\n\n"
        "Use clear headings and bullet points. Assume the reader knows basic programming "
        "but not necessarily this language.\n\n"
        f"```{lang}\n{code}\n```"
    )
    resp = model.generate_content(prompt)
    return resp.text


def explain_linewise(code: str, lang: str, model: genai.GenerativeModel) -> list[tuple[int, str, str]]:
    """
    Ask Gemini to annotate every meaningful line or block.
    Returns list of (line_number, code_line, explanation).
    """
    lines = code.split("\n")
    numbered = "\n".join(f"{i+1:>4}: {line}" for i, line in enumerate(lines))
    prompt = (
        f"You are an expert {lang} programmer. Below is numbered {lang} source code.\n"
        "For EACH non-empty, non-comment line (or logical block), provide a brief one-sentence explanation.\n"
        "Respond ONLY with a JSON array with objects: "
        '{{"line": <number>, "code": "<snippet>", "explanation": "<brief explanation>"}}\n'
        "Skip blank lines. If a block spans multiple lines, use the first line number.\n\n"
        f"CODE:\n{numbered}"
    )
    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    # Extract JSON from response
    import re, json
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []
    try:
        items = json.loads(match.group(0))
        return [(item["line"], item["code"], item["explanation"]) for item in items]
    except (json.JSONDecodeError, KeyError):
        return []

# ─── Display ─────────────────────────────────────────────────────────────────

def display_code(code: str, lang: str) -> None:
    syntax = Syntax(code, rich_lang_name(lang), theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[bold magenta]Source Code ({lang})[/bold magenta]", border_style="magenta"))


def display_explanation(text: str) -> None:
    console.print(Panel(Markdown(text), title="[bold green]Explanation[/bold green]", border_style="green", padding=(1, 2)))


def display_linewise(annotations: list[tuple]) -> None:
    if not annotations:
        console.print("[red]Could not parse line-by-line annotations.[/red]")
        return
    table = Table(
        title="Line-by-Line Explanation",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("Line", style="dim yellow", width=6, justify="right")
    table.add_column("Code", style="bold cyan", overflow="fold", max_width=40)
    table.add_column("Explanation", overflow="fold")
    for line_num, code_snippet, explanation in annotations:
        table.add_row(str(line_num), code_snippet.strip()[:60], explanation)
    console.print(table)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Code Explainer powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 63_code_explainer.py
              python 63_code_explainer.py --file myscript.py
              python 63_code_explainer.py --file app.js --lang javascript --linewise
        """),
    )
    parser.add_argument("--file", help="Source file to explain")
    parser.add_argument("--lang", help="Programming language (auto-detected from file extension)")
    parser.add_argument("--linewise", action="store_true", help="Show line-by-line explanation")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model name")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]AI Code Explainer[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Read code ──
    if args.file:
        code = read_code_from_file(args.file)
        lang = args.lang or detect_language_from_file(args.file)
        lang = LANG_ALIASES.get(lang.lower(), lang.lower())
        console.print(f"[green]✓ Loaded {len(code.splitlines())} lines from[/green] [bold]{args.file}[/bold]")
    else:
        code = read_code_from_stdin()
        if args.lang:
            lang = LANG_ALIASES.get(args.lang.lower(), args.lang.lower())
        else:
            lang = Prompt.ask(
                "\n[bold]Programming language[/bold]",
                choices=SUPPORTED_LANGS,
                default="python",
            )

    if not code.strip():
        console.print("[red]No code provided.[/red]")
        sys.exit(1)

    # ── Mode ──
    linewise = args.linewise
    if not args.linewise and not args.file:
        linewise = Confirm.ask("[bold]Enable line-by-line mode?[/bold]", default=False)

    # ── Display code ──
    display_code(code, lang)

    # ── Initialize model ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    # ── Overall explanation ──
    console.print()
    console.print(Rule("[bold green]Overall Explanation[/bold green]"))
    with console.status("[bold green]Analyzing code with Gemini…[/bold green]", spinner="dots"):
        try:
            explanation = explain_overall(code, lang, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)
    display_explanation(explanation)

    # ── Line-by-line ──
    if linewise:
        console.print()
        console.print(Rule("[bold cyan]Line-by-Line Breakdown[/bold cyan]"))
        with console.status("[bold cyan]Generating line annotations…[/bold cyan]", spinner="dots"):
            try:
                annotations = explain_linewise(code, lang, model)
            except Exception as e:
                console.print(f"[red]API error (linewise):[/red] {e}")
                annotations = []
        display_linewise(annotations)


if __name__ == "__main__":
    main()
