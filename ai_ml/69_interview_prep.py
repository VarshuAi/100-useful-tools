"""
69_interview_prep.py
─────────────────────────────────────────────────────────────────────────────
AI Interview Prep Coach using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Practice for technical and behavioral interviews. Choose your domain
(CS, ML/AI, DSA, System Design, or HR), receive questions, answer
interactively in the terminal, and get detailed feedback on each answer.

Usage:
    python 69_interview_prep.py
    python 69_interview_prep.py --domain cs --difficulty medium --count 5
    python 69_interview_prep.py --domain hr --role "Software Engineer"

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
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
from rich.text import Text
from rich import box

console = Console()

DOMAINS = {
    "cs": {
        "label": "💻 Computer Science",
        "description": "Core CS: OOP, OS, Networks, Databases, Algorithms",
    },
    "ml": {
        "label": "🤖 Machine Learning / AI",
        "description": "ML fundamentals, deep learning, model evaluation, AI concepts",
    },
    "dsa": {
        "label": "🧮 Data Structures & Algorithms",
        "description": "Arrays, trees, graphs, sorting, DP, complexity analysis",
    },
    "sysdesign": {
        "label": "🏗️ System Design",
        "description": "Scalability, microservices, databases, load balancing, caching",
    },
    "hr": {
        "label": "🤝 HR / Behavioral",
        "description": "Situational questions, leadership, teamwork, conflict resolution",
    },
}

DIFFICULTIES = ["easy", "medium", "hard", "mixed"]

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

# ─── Question Generation ──────────────────────────────────────────────────────

QUESTION_PROMPT = """You are a senior technical interviewer at a top tech company.
Generate {count} {difficulty} interview questions for the {domain} domain.
{role_context}

Respond ONLY with a JSON array of {count} objects:
[
  {{
    "id": 1,
    "question": "<the interview question>",
    "difficulty": "<Easy|Medium|Hard>",
    "topic": "<specific topic within {domain}>",
    "type": "<Conceptual|Problem-Solving|Behavioral|Design|Coding>",
    "hints": ["<hint1>", "<hint2>"],
    "ideal_answer_points": ["<key point expected in a good answer>", ...]
  }}
]"""

FEEDBACK_PROMPT = """You are an expert technical interviewer. Evaluate this interview answer.

QUESTION: {question}
CANDIDATE'S ANSWER: {answer}
IDEAL KEY POINTS: {ideal_points}

Respond ONLY with a JSON object:
{{
  "score": <0-10>,
  "grade": "<Excellent|Good|Adequate|Needs Work|Poor>",
  "strengths": ["<what was done well>", ...],
  "missing_points": ["<important points not covered>", ...],
  "feedback": "<detailed constructive feedback (3-4 sentences)>",
  "model_answer": "<a concise ideal answer>",
  "follow_up_question": "<a natural follow-up question>",
  "tips": ["<specific tip to improve>", ...]
}}"""


def generate_questions(
    domain: str,
    difficulty: str,
    count: int,
    role: str,
    model: genai.GenerativeModel,
) -> list[dict]:
    domain_label = DOMAINS[domain]["description"]
    role_context = f"The candidate is applying for a {role} position." if role else ""
    prompt = QUESTION_PROMPT.format(
        count=count,
        difficulty=difficulty,
        domain=domain_label,
        role_context=role_context,
    )
    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    import re
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        console.print("[red]Failed to parse questions.[/red]")
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def get_feedback(question: dict, answer: str, model: genai.GenerativeModel) -> dict:
    ideal = json.dumps(question.get("ideal_answer_points", []))
    prompt = FEEDBACK_PROMPT.format(
        question=question["question"],
        answer=answer,
        ideal_points=ideal,
    )
    resp = model.generate_content(prompt)
    raw = resp.text.strip()
    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"score": 0, "grade": "?", "feedback": raw}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"score": 0, "grade": "?", "feedback": "Parse error."}

# ─── Display ─────────────────────────────────────────────────────────────────

GRADE_COLORS = {
    "Excellent": "bold green",
    "Good": "green",
    "Adequate": "yellow",
    "Needs Work": "red",
    "Poor": "bold red",
}

DIFF_COLORS = {
    "Easy": "green",
    "Medium": "yellow",
    "Hard": "red",
}


def display_question(q: dict, num: int, total: int) -> None:
    diff = q.get("difficulty", "Medium")
    diff_color = DIFF_COLORS.get(diff, "white")
    qtype = q.get("type", "")
    topic = q.get("topic", "")

    console.print()
    console.print(
        Panel(
            q["question"],
            title=f"[bold cyan]Question {num}/{total}[/bold cyan]  "
                  f"[{diff_color}]{diff}[/{diff_color}]  |  "
                  f"[dim]{qtype}[/dim]  |  [dim]{topic}[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def display_feedback(feedback: dict, question: dict) -> None:
    score = feedback.get("score", 0)
    grade = feedback.get("grade", "?")
    grade_color = GRADE_COLORS.get(grade, "white")

    score_bar_filled = "█" * score + "░" * (10 - score)
    console.print()
    console.print(
        Panel(
            f"[{grade_color}]{grade}[/{grade_color}]  [{grade_color}]{score_bar_filled}[/{grade_color}] {score}/10\n\n"
            f"[italic]{feedback.get('feedback', '')}[/italic]",
            title="[bold]📊 Feedback[/bold]",
            border_style=grade.lower() if grade in ("excellent", "good") else "yellow",
        )
    )

    strengths = feedback.get("strengths", [])
    missing = feedback.get("missing_points", [])
    tips = feedback.get("tips", [])
    model_ans = feedback.get("model_answer", "")
    follow_up = feedback.get("follow_up_question", "")

    if strengths:
        console.print("\n[bold green]✅ What You Did Well:[/bold green]")
        for s in strengths:
            console.print(f"  [green]✓[/green] {s}")

    if missing:
        console.print("\n[bold red]❌ Missing Points:[/bold red]")
        for m in missing:
            console.print(f"  [red]✗[/red] {m}")

    if tips:
        console.print("\n[bold yellow]💡 Tips:[/bold yellow]")
        for t in tips:
            console.print(f"  [yellow]→[/yellow] {t}")

    if model_ans:
        console.print()
        console.print(Panel(
            f"[dim]{model_ans}[/dim]",
            title="[dim]Model Answer[/dim]",
            border_style="dim",
        ))

    if follow_up:
        console.print(f"\n[bold magenta]🔄 Follow-up:[/bold magenta] [italic]{follow_up}[/italic]")


def display_session_summary(session_scores: list[tuple[dict, dict]]) -> None:
    console.print()
    console.print(Rule("[bold cyan]📊 Session Summary[/bold cyan]"))

    table = Table(box=box.ROUNDED, border_style="cyan")
    table.add_column("#", width=4, style="dim")
    table.add_column("Topic", overflow="fold")
    table.add_column("Score", width=10, justify="right")
    table.add_column("Grade", width=14)

    total = 0
    for i, (q, fb) in enumerate(session_scores, 1):
        score = fb.get("score", 0)
        grade = fb.get("grade", "?")
        total += score
        color = GRADE_COLORS.get(grade, "white")
        table.add_row(
            str(i),
            q.get("topic", q["question"][:40]),
            f"{score}/10",
            f"[{color}]{grade}[/{color}]",
        )

    avg = total / len(session_scores) if session_scores else 0
    table.add_row("[bold]AVG[/bold]", "", f"[bold]{avg:.1f}/10[/bold]", "")
    console.print(table)


def get_answer() -> str:
    """Get multiline answer from user."""
    console.print("[dim]Type your answer (enter a blank line when done):[/dim]")
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        pass
    return "\n".join(lines).strip()

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Interview Prep Coach powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 69_interview_prep.py
              python 69_interview_prep.py --domain dsa --difficulty hard --count 5
              python 69_interview_prep.py --domain hr --role "Software Engineer"
        """),
    )
    parser.add_argument("--domain", choices=list(DOMAINS.keys()), help="Interview domain")
    parser.add_argument("--difficulty", choices=DIFFICULTIES, default="medium", help="Question difficulty")
    parser.add_argument("--count", type=int, default=5, help="Number of questions (1-10)")
    parser.add_argument("--role", default="", help="Target role (e.g. 'Software Engineer at Google')")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]🎯 AI Interview Prep Coach[/bold cyan]\n[dim]Powered by Google Gemini[/dim]\n\n"
            "Practice interview questions and get instant AI feedback.",
            border_style="cyan",
        )
    )

    # ── Select domain ──
    domain = args.domain
    if not domain:
        console.print("\n[bold]Available Domains:[/bold]")
        for key, info in DOMAINS.items():
            console.print(f"  [cyan]{key:10s}[/cyan] — {info['description']}")
        domain = Prompt.ask("\n[bold]Choose domain[/bold]", choices=list(DOMAINS.keys()), default="cs")

    count = max(1, min(10, args.count))
    role = args.role or Prompt.ask("[bold]Target role[/bold] [dim](optional, press Enter to skip)[/dim]", default="")

    # ── Initialize Gemini ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(args.model)

    # ── Generate questions ──
    domain_label = DOMAINS[domain]["label"]
    console.print(f"\n[dim]Generating {count} {args.difficulty} {domain_label} questions…[/dim]")

    with console.status("[bold green]Preparing your interview session…[/bold green]", spinner="dots"):
        try:
            questions = generate_questions(domain, args.difficulty, count, role, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    if not questions:
        console.print("[red]Failed to generate questions. Try again.[/red]")
        sys.exit(1)

    console.print(
        Panel(
            f"[bold green]✓ {len(questions)} questions ready![/bold green]\n\n"
            f"[dim]Domain:[/dim] {domain_label}  |  "
            f"[dim]Difficulty:[/dim] {args.difficulty.title()}  |  "
            f"[dim]Questions:[/dim] {len(questions)}\n\n"
            "Answer each question, then press Enter on a blank line to submit.\n"
            "Type [bold]skip[/bold] to skip a question, [bold]hint[/bold] for a hint, [bold]quit[/bold] to end early.",
            title="[bold]📋 Interview Session[/bold]",
            border_style="green",
        )
    )

    # ── Interview loop ──
    session_scores: list[tuple[dict, dict]] = []

    for i, q in enumerate(questions, 1):
        display_question(q, i, len(questions))

        while True:
            answer = get_answer()
            if answer.lower() == "skip":
                console.print("[yellow]Question skipped.[/yellow]")
                break
            elif answer.lower() == "hint":
                hints = q.get("hints", [])
                if hints:
                    console.print(Panel("\n".join(f"💡 {h}" for h in hints), title="Hints", border_style="yellow"))
                else:
                    console.print("[dim]No hints available for this question.[/dim]")
                answer = get_answer()
            elif answer.lower() == "quit":
                console.print("[yellow]Ending session early…[/yellow]")
                break

            if not answer:
                console.print("[dim]Please type an answer, or 'skip'.[/dim]")
                continue
            break

        if answer.lower() == "quit":
            break
        if answer.lower() == "skip":
            continue

        with console.status("[bold green]Evaluating your answer…[/bold green]", spinner="dots"):
            try:
                feedback = get_feedback(q, answer, model)
            except Exception as e:
                console.print(f"[red]Feedback error:[/red] {e}")
                feedback = {"score": 0, "grade": "Error", "feedback": str(e)}

        display_feedback(feedback, q)
        session_scores.append((q, feedback))

        if i < len(questions):
            if not Confirm.ask("\n[dim]Continue to next question?[/dim]", default=True):
                break

    # ── Summary ──
    if session_scores:
        display_session_summary(session_scores)

        if Confirm.ask("\n[dim]Save session report?[/dim]", default=False):
            filename = f"interview_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                "domain": domain,
                "difficulty": args.difficulty,
                "role": role,
                "session_date": datetime.now().isoformat(),
                "results": [
                    {"question": q["question"], "score": fb.get("score", 0), "grade": fb.get("grade", "")}
                    for q, fb in session_scores
                ],
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✓ Saved to[/green] [bold]{filename}[/bold]")

    console.print("\n[bold green]Great practice! Keep it up! 💪[/bold green]")


if __name__ == "__main__":
    main()
