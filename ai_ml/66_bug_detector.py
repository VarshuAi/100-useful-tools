"""
66_bug_detector.py
─────────────────────────────────────────────────────────────────────────────
AI Bug Detector using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Paste or load code to detect bugs, logical errors, security vulnerabilities,
and performance issues. Gemini explains each issue and suggests fixes
with diff-style highlights.

Usage:
    python 66_bug_detector.py
    python 66_bug_detector.py --file buggy_script.py
    python 66_bug_detector.py --file app.js --lang javascript

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
from rich.syntax import Syntax
from rich.rule import Rule
from rich.text import Text
from rich import box

console = Console()

SEVERITY_COLORS = {
    "Critical": "bold red",
    "High": "red",
    "Medium": "yellow",
    "Low": "green",
    "Info": "dim cyan",
}

SEVERITY_EMOJI = {
    "Critical": "🔴",
    "High": "🟠",
    "Medium": "🟡",
    "Low": "🟢",
    "Info": "ℹ️ ",
}

BUG_TYPE_ICONS = {
    "Logic Error": "🧠",
    "Runtime Error": "💥",
    "Security": "🔒",
    "Performance": "⚡",
    "Type Error": "🔤",
    "Off-by-One": "➕",
    "Null/None": "∅",
    "Style": "🎨",
    "Memory": "📦",
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

def detect_language(path: str) -> str:
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".java": "java", ".cpp": "c++", ".c": "c",
        ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
    }
    return ext_map.get(os.path.splitext(path)[1].lower(), "python")


def rich_lang(lang: str) -> str:
    return {"c++": "cpp", "javascript": "javascript"}.get(lang.lower(), lang.lower())

# ─── Code Reading ─────────────────────────────────────────────────────────────

def read_from_file(path: str) -> str:
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def read_from_stdin() -> str:
    console.print(
        Panel(
            "Paste your code below. Enter [bold]END[/bold] on a new line when done.",
            title="[cyan]Paste Code to Analyze[/cyan]",
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

# ─── Bug Detection ────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """You are an expert code reviewer and security engineer. Analyze the following {lang} code for:
1. Bugs and logic errors
2. Runtime errors and exceptions
3. Security vulnerabilities
4. Performance issues
5. Type errors or null/None issues
6. Off-by-one errors
7. Edge cases not handled

Respond ONLY with a JSON object with this structure:
{{
  "overall_health": "<Good|Fair|Poor|Critical>",
  "summary": "<one or two sentence overall assessment>",
  "bugs": [
    {{
      "id": 1,
      "type": "<Logic Error|Runtime Error|Security|Performance|Type Error|Off-by-One|Null/None|Style|Memory>",
      "severity": "<Critical|High|Medium|Low|Info>",
      "line": <line number or null>,
      "description": "<what is wrong>",
      "impact": "<what happens because of this bug>",
      "original_code": "<the problematic code snippet>",
      "fixed_code": "<corrected code snippet>",
      "explanation": "<why the fix works>"
    }}
  ],
  "fixed_full_code": "<the complete corrected version of the code>"
}}

CODE ({lang}):
```
{code}
```"""


def detect_bugs(code: str, lang: str, model: genai.GenerativeModel) -> dict:
    prompt = ANALYSIS_PROMPT.format(lang=lang, code=code[:8000])
    resp = model.generate_content(prompt)
    raw = resp.text.strip()

    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"overall_health": "Unknown", "summary": raw, "bugs": [], "fixed_full_code": ""}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"overall_health": "Unknown", "summary": "Parse error — raw response shown.", "bugs": [], "fixed_full_code": ""}

# ─── Display ─────────────────────────────────────────────────────────────────

HEALTH_COLORS = {
    "Good": "bold green",
    "Fair": "bold yellow",
    "Poor": "bold red",
    "Critical": "bold red on white",
}


def display_health_header(result: dict, lang: str, line_count: int) -> None:
    health = result.get("overall_health", "Unknown")
    summary = result.get("summary", "")
    bug_count = len(result.get("bugs", []))
    color = HEALTH_COLORS.get(health, "white")

    console.print()
    console.print(
        Panel(
            f"[{color}]Code Health: {health}[/{color}]\n\n"
            f"[dim]Language:[/dim] {lang}  |  "
            f"[dim]Lines:[/dim] {line_count}  |  "
            f"[dim]Issues Found:[/dim] [bold]{bug_count}[/bold]\n\n"
            f"[italic]{summary}[/italic]",
            title="[bold]🔍 Bug Detection Report[/bold]",
            border_style="cyan",
        )
    )


def display_bugs_table(bugs: list[dict]) -> None:
    if not bugs:
        console.print(Panel("[bold green]✓ No bugs detected! Code looks clean.[/bold green]", border_style="green"))
        return

    table = Table(title=f"Issues Found ({len(bugs)})", box=box.ROUNDED, border_style="cyan", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Severity", width=12)
    table.add_column("Type", width=16)
    table.add_column("Line", width=6, justify="right")
    table.add_column("Description", overflow="fold")

    for bug in bugs:
        severity = bug.get("severity", "Info")
        btype = bug.get("type", "Other")
        color = SEVERITY_COLORS.get(severity, "white")
        emoji = SEVERITY_EMOJI.get(severity, "")
        type_icon = BUG_TYPE_ICONS.get(btype, "🐛")
        line_str = str(bug.get("line", "—"))
        table.add_row(
            str(bug.get("id", "")),
            f"{emoji} [{color}]{severity}[/{color}]",
            f"{type_icon} {btype}",
            line_str,
            bug.get("description", ""),
        )
    console.print(table)


def display_bug_details(bugs: list[dict]) -> None:
    for bug in bugs:
        severity = bug.get("severity", "Info")
        color = SEVERITY_COLORS.get(severity, "white")
        emoji = SEVERITY_EMOJI.get(severity, "")
        btype = bug.get("type", "Other")
        bug_id = bug.get("id", "?")
        type_icon = BUG_TYPE_ICONS.get(btype, "🐛")
        line = bug.get("line")

        title_parts = [f"{emoji} #{bug_id} — {type_icon} {btype}"]
        if line:
            title_parts.append(f"(Line {line})")

        body = f"[{color}]Severity: {severity}[/{color}]\n\n"
        body += f"[bold]Description:[/bold] {bug.get('description', '')}\n"
        body += f"[bold]Impact:[/bold] {bug.get('impact', '')}\n\n"

        original = bug.get("original_code", "").strip()
        fixed = bug.get("fixed_code", "").strip()
        explanation = bug.get("explanation", "")

        if original:
            body += "[bold red]❌ Original (Buggy):[/bold red]\n"
        console.print(Panel(body.strip(), title=" ".join(title_parts), border_style=severity.lower() if severity in ("high", "critical") else "yellow"))

        if original:
            console.print(Syntax(original, "python", theme="monokai", line_numbers=False, background_color="dark_red"))
        if fixed:
            console.print("[bold green]✅ Fixed:[/bold green]")
            console.print(Syntax(fixed, "python", theme="monokai", line_numbers=False))
        if explanation:
            console.print(f"[dim]💡 {explanation}[/dim]")
        console.print()


def display_fixed_code(fixed_code: str, lang: str) -> None:
    if not fixed_code:
        return
    console.print(Rule("[bold green]Complete Fixed Code[/bold green]"))
    console.print(Syntax(fixed_code, rich_lang(lang), theme="monokai", line_numbers=True))

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Bug Detector powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 66_bug_detector.py
              python 66_bug_detector.py --file buggy_code.py
              python 66_bug_detector.py --file app.js --lang javascript
        """),
    )
    parser.add_argument("--file", help="Source file to analyze")
    parser.add_argument("--lang", help="Language (auto-detected from file)")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model")
    parser.add_argument("--show-fix", action="store_true", help="Show complete fixed code")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]🐛 AI Bug Detector[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Read code ──
    if args.file:
        code = read_from_file(args.file)
        lang = args.lang or detect_language(args.file)
        console.print(f"[green]✓ Loaded[/green] [bold]{args.file}[/bold] ({len(code.splitlines())} lines, {lang})")
    else:
        code = read_from_stdin()
        lang = args.lang or Prompt.ask(
            "[bold]Language[/bold]",
            choices=["python", "javascript", "java", "c++", "c", "go", "rust", "other"],
            default="python",
        )

    if not code.strip():
        console.print("[red]No code provided.[/red]")
        sys.exit(1)

    # ── Show code ──
    console.print()
    console.print(Rule("[dim]Source Code[/dim]"))
    console.print(Syntax(code[:3000], rich_lang(lang), theme="monokai", line_numbers=True))

    # ── Analyze ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    with console.status("[bold green]Scanning for bugs with Gemini…[/bold green]", spinner="dots"):
        try:
            result = detect_bugs(code, lang, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    bugs = result.get("bugs", [])
    display_health_header(result, lang, len(code.splitlines()))
    display_bugs_table(bugs)

    if bugs:
        console.print()
        if Confirm.ask(f"[dim]Show detailed breakdown of all {len(bugs)} issues?[/dim]", default=True):
            display_bug_details(bugs)

    if args.show_fix or (result.get("fixed_full_code") and Confirm.ask("[dim]Show complete fixed code?[/dim]", default=False)):
        display_fixed_code(result.get("fixed_full_code", ""), lang)

    # ── Save fix ──
    if result.get("fixed_full_code") and Confirm.ask("[dim]Save fixed code to file?[/dim]", default=False):
        ext = os.path.splitext(args.file)[1] if args.file else ".py"
        from datetime import datetime
        out = f"fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        with open(out, "w", encoding="utf-8") as f:
            f.write(result["fixed_full_code"])
        console.print(f"[green]✓ Fixed code saved to[/green] [bold]{out}[/bold]")


if __name__ == "__main__":
    main()
