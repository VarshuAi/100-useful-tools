"""
67_resume_analyzer.py
─────────────────────────────────────────────────────────────────────────────
AI Resume Analyzer using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Load a resume (plain text or PDF) and optionally a job description.
Gemini analyzes fit, gives a match score, highlights strengths and gaps,
and provides actionable improvement tips.

Usage:
    python 67_resume_analyzer.py
    python 67_resume_analyzer.py --resume resume.pdf --job "job_description.txt"
    python 67_resume_analyzer.py --resume resume.txt

Requirements:
    pip install google-generativeai rich pypdf
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
from rich.progress import Progress
from rich.rule import Rule
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
                "Get a key: [link]https://aistudio.google.com/app/apikey[/link]",
                title="[red]Missing API Key",
                border_style="red",
            )
        )
        sys.exit(1)
    return key

# ─── Text Extraction ──────────────────────────────────────────────────────────

def extract_pdf_text(path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        import pypdf
    except ImportError:
        console.print("[yellow]pypdf not installed. Run: pip install pypdf[/yellow]")
        sys.exit(1)
    text_parts = []
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
    return "\n\n".join(text_parts)


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_document(path: str, label: str) -> str:
    if not os.path.exists(path):
        console.print(f"[red]{label} not found:[/red] {path}")
        sys.exit(1)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        with console.status(f"[cyan]Extracting text from {label}…[/cyan]"):
            text = extract_pdf_text(path)
    else:
        text = read_text_file(path)
    console.print(f"[green]✓ Loaded {label}:[/green] {len(text):,} characters")
    return text


def read_from_stdin(label: str) -> str:
    console.print(
        Panel(
            f"Paste your [bold]{label}[/bold] below. Enter [bold]END[/bold] on a new line when done.",
            title=f"[cyan]Paste {label}[/cyan]",
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

# ─── Analysis ─────────────────────────────────────────────────────────────────

ANALYSIS_PROMPT_WITH_JD = """You are an expert career coach and recruiter. Analyze the resume against the job description.

Respond ONLY with a JSON object:
{{
  "match_score": <0-100>,
  "overall_assessment": "<2-3 sentence summary>",
  "strengths": ["<strength1>", "<strength2>", ...],
  "gaps": ["<gap1>", "<gap2>", ...],
  "missing_keywords": ["<keyword1>", ...],
  "present_keywords": ["<keyword1>", ...],
  "section_scores": {{
    "experience": <0-100>,
    "education": <0-100>,
    "skills": <0-100>,
    "achievements": <0-100>,
    "format": <0-100>
  }},
  "improvements": [
    {{"area": "<area>", "suggestion": "<actionable suggestion>", "priority": "<High|Medium|Low>"}}
  ],
  "ats_tips": ["<ATS optimization tip>", ...],
  "verdict": "<Strong Match|Good Match|Partial Match|Weak Match>"
}}

RESUME:
{resume}

JOB DESCRIPTION:
{job_desc}"""

ANALYSIS_PROMPT_NO_JD = """You are an expert career coach. Provide a comprehensive quality analysis of this resume.

Respond ONLY with a JSON object:
{{
  "overall_score": <0-100>,
  "overall_assessment": "<2-3 sentence summary>",
  "strengths": ["<strength1>", "<strength2>", ...],
  "weaknesses": ["<weakness1>", ...],
  "section_scores": {{
    "experience": <0-100>,
    "education": <0-100>,
    "skills": <0-100>,
    "achievements": <0-100>,
    "format_clarity": <0-100>
  }},
  "improvements": [
    {{"area": "<area>", "suggestion": "<actionable suggestion>", "priority": "<High|Medium|Low>"}}
  ],
  "ats_tips": ["<ATS optimization tip>", ...],
  "career_level": "<Entry|Junior|Mid|Senior|Executive>",
  "apparent_role": "<what role this person seems to be targeting>"
}}

RESUME:
{resume}"""


def analyze_resume(resume: str, job_desc: str | None, model: genai.GenerativeModel) -> dict:
    if job_desc:
        prompt = ANALYSIS_PROMPT_WITH_JD.format(
            resume=resume[:6000],
            job_desc=job_desc[:3000],
        )
    else:
        prompt = ANALYSIS_PROMPT_NO_JD.format(resume=resume[:8000])

    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"overall_score": 0, "overall_assessment": raw, "improvements": []}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"overall_score": 0, "overall_assessment": "Parse error.", "improvements": []}

# ─── Display ─────────────────────────────────────────────────────────────────

def score_color(score: int) -> str:
    if score >= 80:
        return "bold green"
    elif score >= 60:
        return "bold yellow"
    elif score >= 40:
        return "bold red"
    return "red"


def score_bar(score: int, width: int = 20) -> str:
    filled = int(score / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    color = score_color(score)
    return f"[{color}]{bar}[/{color}] {score}%"


def display_results(result: dict, has_jd: bool) -> None:
    # ── Overall Score ──
    score_key = "match_score" if has_jd else "overall_score"
    score = result.get(score_key, 0)
    assessment = result.get("overall_assessment", "")
    verdict = result.get("verdict", result.get("career_level", ""))
    color = score_color(score)

    console.print()
    console.print(
        Panel(
            f"[{color}]Overall {'Match' if has_jd else 'Resume'} Score: {score}/100[/{color}]\n\n"
            f"{score_bar(score)}\n\n"
            f"[bold]Verdict:[/bold] [yellow]{verdict}[/yellow]\n\n"
            f"[italic]{assessment}[/italic]",
            title="[bold]📄 Resume Analysis Report[/bold]",
            border_style="cyan",
        )
    )

    # ── Section Scores ──
    section_scores = result.get("section_scores", {})
    if section_scores:
        console.print(Rule("[bold]Section Scores[/bold]"))
        table = Table(box=box.SIMPLE_HEAVY, border_style="dim")
        table.add_column("Section", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Bar")
        for section, s in section_scores.items():
            sc = int(s) if isinstance(s, (int, float)) else 0
            label = section.replace("_", " ").title()
            table.add_row(label, f"{sc}/100", score_bar(sc, 15))
        console.print(table)

    # ── Strengths ──
    strengths = result.get("strengths", [])
    if strengths:
        console.print()
        console.print(Rule("[bold green]✅ Strengths[/bold green]"))
        for s in strengths:
            console.print(f"  [green]✓[/green] {s}")

    # ── Gaps / Weaknesses ──
    gaps = result.get("gaps", result.get("weaknesses", []))
    if gaps:
        console.print()
        console.print(Rule("[bold red]❌ Gaps / Weaknesses[/bold red]"))
        for g in gaps:
            console.print(f"  [red]✗[/red] {g}")

    # ── Keywords ──
    if has_jd:
        missing = result.get("missing_keywords", [])
        present = result.get("present_keywords", [])
        if missing or present:
            console.print()
            console.print(Rule("[bold yellow]🔑 Keywords[/bold yellow]"))
            if present:
                console.print(f"  [green]Present:[/green] {', '.join(present[:10])}")
            if missing:
                console.print(f"  [red]Missing:[/red] {', '.join(missing[:10])}")

    # ── Improvements ──
    improvements = result.get("improvements", [])
    if improvements:
        console.print()
        console.print(Rule("[bold cyan]💡 Improvement Tips[/bold cyan]"))
        prio_colors = {"High": "bold red", "Medium": "yellow", "Low": "green"}
        for tip in improvements:
            area = tip.get("area", "")
            suggestion = tip.get("suggestion", "")
            priority = tip.get("priority", "Medium")
            pcolor = prio_colors.get(priority, "white")
            console.print(
                Panel(
                    f"[bold]{area}[/bold]\n{suggestion}",
                    subtitle=f"[{pcolor}]Priority: {priority}[/{pcolor}]",
                    border_style="dim",
                    padding=(0, 1),
                )
            )

    # ── ATS Tips ──
    ats_tips = result.get("ats_tips", [])
    if ats_tips:
        console.print()
        console.print(Rule("[bold magenta]🤖 ATS Optimization Tips[/bold magenta]"))
        for tip in ats_tips:
            console.print(f"  [magenta]→[/magenta] {tip}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Analyzer powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 67_resume_analyzer.py
              python 67_resume_analyzer.py --resume resume.pdf
              python 67_resume_analyzer.py --resume resume.txt --job job_description.txt
        """),
    )
    parser.add_argument("--resume", help="Resume file path (.txt or .pdf)")
    parser.add_argument("--job", help="Job description file path (.txt)")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]📄 AI Resume Analyzer[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Load resume ──
    if args.resume:
        resume_text = load_document(args.resume, "Resume")
    else:
        resume_text = read_from_stdin("Resume")

    if not resume_text.strip():
        console.print("[red]No resume text provided.[/red]")
        sys.exit(1)

    # ── Load job description (optional) ──
    job_text = None
    if args.job:
        job_text = load_document(args.job, "Job Description")
    else:
        if Confirm.ask("[bold]Do you have a job description to match against?[/bold]", default=False):
            job_text = read_from_stdin("Job Description")

    # ── Analyze ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    mode_str = "against job description" if job_text else "for general quality"
    with console.status(f"[bold green]Analyzing resume {mode_str}…[/bold green]", spinner="dots"):
        try:
            result = analyze_resume(resume_text, job_text, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    display_results(result, has_jd=bool(job_text))

    # ── Save ──
    if Confirm.ask("\n[dim]Save report to JSON?[/dim]", default=False):
        from datetime import datetime
        outfile = f"resume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        console.print(f"[green]✓ Saved to[/green] [bold]{outfile}[/bold]")


if __name__ == "__main__":
    main()
