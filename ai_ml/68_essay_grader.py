"""
68_essay_grader.py
─────────────────────────────────────────────────────────────────────────────
AI Essay Grader using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Grade essays on multiple dimensions: clarity, structure, grammar, argument
quality, evidence use, and originality. Provides rubric scores, detailed
feedback, and actionable suggestions for improvement.

Usage:
    python 68_essay_grader.py
    python 68_essay_grader.py --file essay.txt
    python 68_essay_grader.py --file essay.txt --type argumentative --level college

Requirements:
    pip install google-generativeai rich
    Set env var: GEMINI_API_KEY
"""

import os
import sys
import json
import argparse
import textwrap
from datetime import datetime

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
from rich.rule import Rule
from rich.progress import Progress
from rich import box

console = Console()

ESSAY_TYPES = ["argumentative", "expository", "narrative", "descriptive", "persuasive", "analytical"]
GRADE_LEVELS = ["middle school", "high school", "college", "graduate", "professional"]

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

# ─── Essay Input ──────────────────────────────────────────────────────────────

def read_essay_stdin() -> str:
    console.print(
        Panel(
            "Paste your essay below. Enter [bold]END[/bold] on a new line when done.",
            title="[cyan]Paste Essay[/cyan]",
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


def read_essay_file(path: str) -> str:
    if not os.path.exists(path):
        console.print(f"[red]File not found:[/red] {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

# ─── Grading ─────────────────────────────────────────────────────────────────

GRADING_PROMPT = """You are an experienced English teacher and essay grader. 
Grade the following {essay_type} essay written for a {level} audience.

Score each criterion from 0-10 and provide detailed feedback.

Respond ONLY with a JSON object:
{{
  "letter_grade": "<A+|A|A-|B+|B|B-|C+|C|C-|D|F>",
  "percentage_score": <0-100>,
  "rubric": {{
    "clarity": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "structure": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "grammar_mechanics": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "argument_quality": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "evidence_support": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "vocabulary": {{"score": <0-10>, "feedback": "<specific feedback>"}},
    "originality": {{"score": <0-10>, "feedback": "<specific feedback>"}}
  }},
  "overall_feedback": "<3-4 sentence comprehensive assessment>",
  "strengths": ["<strength>", ...],
  "areas_for_improvement": ["<improvement area>", ...],
  "specific_corrections": [
    {{"original": "<original phrase>", "suggested": "<corrected phrase>", "reason": "<why>"}}
  ],
  "thesis_strength": "<Strong|Adequate|Weak|Missing>",
  "reading_level": "<estimate>",
  "word_count_assessment": "<Too Short|Adequate|Too Long>",
  "encouragement": "<one motivational closing sentence>"
}}

ESSAY ({essay_type}, {level} level):
{essay}"""


def grade_essay(essay: str, essay_type: str, level: str, model: genai.GenerativeModel) -> dict:
    prompt = GRADING_PROMPT.format(
        essay_type=essay_type,
        level=level,
        essay=essay[:6000],
    )
    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"letter_grade": "?", "percentage_score": 0, "overall_feedback": raw}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"letter_grade": "?", "percentage_score": 0, "overall_feedback": "Parse error."}

# ─── Display ─────────────────────────────────────────────────────────────────

def grade_color(score: float) -> str:
    if score >= 90:
        return "bold green"
    elif score >= 80:
        return "green"
    elif score >= 70:
        return "yellow"
    elif score >= 60:
        return "bold yellow"
    elif score >= 50:
        return "red"
    return "bold red"


def letter_grade_color(grade: str) -> str:
    if grade.startswith("A"):
        return "bold green"
    elif grade.startswith("B"):
        return "green"
    elif grade.startswith("C"):
        return "yellow"
    elif grade.startswith("D"):
        return "red"
    return "bold red"


def score_bar(score: float, max_score: float = 10.0, width: int = 15) -> str:
    ratio = score / max_score
    filled = int(ratio * width)
    color = grade_color(ratio * 100)
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}]"


def display_results(result: dict, essay: str, essay_type: str, level: str) -> None:
    letter = result.get("letter_grade", "?")
    pct = result.get("percentage_score", 0)
    letter_color = letter_grade_color(letter)

    word_count = len(essay.split())

    # ── Header ──
    console.print()
    console.print(
        Panel(
            f"[{letter_color}]Grade: {letter}[/{letter_color}]  |  "
            f"[{grade_color(pct)}]{pct}%[/{grade_color(pct)}]\n\n"
            f"[dim]Type:[/dim] {essay_type.title()}  |  "
            f"[dim]Level:[/dim] {level.title()}  |  "
            f"[dim]Words:[/dim] {word_count:,}  |  "
            f"[dim]Assessment:[/dim] {result.get('word_count_assessment', '—')}\n\n"
            f"[dim]Thesis Strength:[/dim] {result.get('thesis_strength', '—')}  |  "
            f"[dim]Reading Level:[/dim] {result.get('reading_level', '—')}\n\n"
            f"[italic]{result.get('overall_feedback', '')}[/italic]",
            title="[bold]📝 Essay Grade Report[/bold]",
            border_style="cyan",
        )
    )

    # ── Rubric Table ──
    rubric = result.get("rubric", {})
    if rubric:
        console.print()
        console.print(Rule("[bold]Rubric Scores[/bold]"))
        table = Table(box=box.ROUNDED, border_style="dim", show_lines=True)
        table.add_column("Criterion", style="bold", width=22)
        table.add_column("Score", width=8, justify="right")
        table.add_column("Bar", width=20)
        table.add_column("Feedback", overflow="fold")

        total_score = 0
        for criterion, data in rubric.items():
            score = data.get("score", 0)
            total_score += score
            label = criterion.replace("_", " ").title()
            feedback = data.get("feedback", "")
            table.add_row(
                label,
                f"{score}/10",
                score_bar(score),
                feedback[:80] + ("…" if len(feedback) > 80 else ""),
            )

        avg = total_score / len(rubric) if rubric else 0
        table.add_row(
            "[bold]AVERAGE[/bold]",
            f"[bold]{avg:.1f}/10[/bold]",
            score_bar(avg),
            "",
        )
        console.print(table)

    # ── Strengths ──
    strengths = result.get("strengths", [])
    if strengths:
        console.print()
        console.print(Rule("[bold green]✅ Strengths[/bold green]"))
        for s in strengths:
            console.print(f"  [green]✓[/green] {s}")

    # ── Improvements ──
    improvements = result.get("areas_for_improvement", [])
    if improvements:
        console.print()
        console.print(Rule("[bold yellow]💡 Areas for Improvement[/bold yellow]"))
        for imp in improvements:
            console.print(f"  [yellow]→[/yellow] {imp}")

    # ── Specific Corrections ──
    corrections = result.get("specific_corrections", [])
    if corrections:
        console.print()
        console.print(Rule("[bold red]✏️ Specific Corrections[/bold red]"))
        for c in corrections[:5]:  # Show top 5
            original = c.get("original", "")
            suggested = c.get("suggested", "")
            reason = c.get("reason", "")
            console.print(
                Panel(
                    f"[red]Original:[/red] [italic]{original}[/italic]\n"
                    f"[green]Suggested:[/green] [italic]{suggested}[/italic]\n"
                    f"[dim]Reason: {reason}[/dim]",
                    border_style="dim",
                    padding=(0, 1),
                )
            )

    # ── Encouragement ──
    enc = result.get("encouragement", "")
    if enc:
        console.print()
        console.print(Panel(f"[bold green]{enc}[/bold green]", border_style="green"))


def save_report(result: dict, essay: str, essay_type: str, level: str) -> str:
    filename = f"essay_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "graded_at": datetime.now().isoformat(),
        "essay_type": essay_type,
        "level": level,
        "word_count": len(essay.split()),
        "result": result,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Essay Grader powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 68_essay_grader.py
              python 68_essay_grader.py --file essay.txt
              python 68_essay_grader.py --file essay.txt --type argumentative --level college
        """),
    )
    parser.add_argument("--file", help="Essay text file")
    parser.add_argument("--type", choices=ESSAY_TYPES, help="Essay type")
    parser.add_argument("--level", choices=GRADE_LEVELS, help="Target grade level")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]📝 AI Essay Grader[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Load essay ──
    if args.file:
        essay = read_essay_file(args.file)
        console.print(f"[green]✓ Loaded essay:[/green] {len(essay.split())} words")
    else:
        essay = read_essay_stdin()

    if not essay.strip():
        console.print("[red]No essay text provided.[/red]")
        sys.exit(1)

    # ── Settings ──
    essay_type = args.type or Prompt.ask(
        "[bold]Essay type[/bold]",
        choices=ESSAY_TYPES,
        default="argumentative",
    )
    level = args.level or Prompt.ask(
        "[bold]Grade level[/bold]",
        choices=GRADE_LEVELS,
        default="high school",
    )

    # ── Grade ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    with console.status("[bold green]Grading essay with Gemini…[/bold green]", spinner="dots"):
        try:
            result = grade_essay(essay, essay_type, level, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    display_results(result, essay, essay_type, level)

    if Confirm.ask("\n[dim]Save grading report?[/dim]", default=False):
        filename = save_report(result, essay, essay_type, level)
        console.print(f"[green]✓ Report saved to[/green] [bold]{filename}[/bold]")


if __name__ == "__main__":
    main()
