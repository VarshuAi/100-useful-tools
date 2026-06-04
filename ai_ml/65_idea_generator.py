"""
65_idea_generator.py
─────────────────────────────────────────────────────────────────────────────
AI Idea Generator using Google Gemini
─────────────────────────────────────────────────────────────────────────────
Generate startup ideas, app ideas, project ideas, or research topics based
on your interests, skills, and constraints. Ideas are formatted with name,
description, target audience, difficulty, and market potential.

Usage:
    python 65_idea_generator.py
    python 65_idea_generator.py --type startup --interests "AI, healthcare" --count 5
    python 65_idea_generator.py --type research --interests "quantum computing" --save

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
from rich.columns import Columns
from rich.rule import Rule
from rich.text import Text
from rich import box

console = Console()

IDEA_TYPES = {
    "startup": {
        "label": "💼 Startup",
        "description": "Venture-ready business ideas with market potential",
        "fields": "name, one-line pitch, problem solved, target market, revenue model, difficulty (Easy/Medium/Hard), market potential (Low/Medium/High/Huge)",
    },
    "app": {
        "label": "📱 App",
        "description": "Mobile or web app ideas",
        "fields": "name, description, key features (3-4), target users, platform (Web/iOS/Android/Cross-platform), difficulty (Easy/Medium/Hard)",
    },
    "project": {
        "label": "🔧 Project",
        "description": "Personal or portfolio coding projects",
        "fields": "name, description, tech stack, what you'll learn, difficulty (Beginner/Intermediate/Advanced), estimated time",
    },
    "research": {
        "label": "🔬 Research Topic",
        "description": "Academic or professional research ideas",
        "fields": "title, research question, methodology, potential impact, field, novelty level (Incremental/Novel/Breakthrough)",
    },
    "content": {
        "label": "🎬 Content",
        "description": "YouTube, blog, podcast, or course ideas",
        "fields": "title, concept, target audience, content format, niche appeal, monetization potential",
    },
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

# ─── Idea Generation ──────────────────────────────────────────────────────────

def build_prompt(idea_type: str, interests: str, skills: str, count: int, constraints: str) -> str:
    type_info = IDEA_TYPES[idea_type]
    constraints_str = f"\nConstraints: {constraints}" if constraints else ""
    skills_str = f"\nSkills/Background: {skills}" if skills else ""

    return (
        f"You are a creative innovation consultant. Generate {count} unique, practical, and inspiring "
        f"{type_info['label']} ideas based on:\n"
        f"Interests: {interests}{skills_str}{constraints_str}\n\n"
        f"For each idea, provide: {type_info['fields']}.\n\n"
        f"Respond ONLY with a JSON array of {count} objects, each with fields matching the above. "
        f"Make ideas diverse, creative, and actionable. Avoid generic or clichéd ideas.\n"
        f"Example field names: name, description, difficulty, etc. Use camelCase for multi-word fields.\n"
        f"JSON array:"
    )


def generate_ideas(
    idea_type: str,
    interests: str,
    skills: str,
    count: int,
    constraints: str,
    model: genai.GenerativeModel,
) -> list[dict]:
    prompt = build_prompt(idea_type, interests, skills, count, constraints)
    resp = model.generate_content(prompt)
    raw = resp.text.strip()

    import re
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        console.print("[yellow]Warning: Could not parse JSON from response. Showing raw output.[/yellow]")
        console.print(Markdown(raw))
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        console.print("[yellow]Warning: JSON parse error. Showing raw output.[/yellow]")
        console.print(Markdown(raw))
        return []

# ─── Display ─────────────────────────────────────────────────────────────────

DIFFICULTY_COLORS = {
    "easy": "green", "beginner": "green",
    "medium": "yellow", "intermediate": "yellow",
    "hard": "red", "advanced": "red",
}

POTENTIAL_COLORS = {
    "low": "red", "medium": "yellow",
    "high": "green", "huge": "bold green",
    "incremental": "yellow", "novel": "green",
    "breakthrough": "bold magenta",
}


def color_field(value: str, color_map: dict) -> str:
    lower = value.lower() if value else ""
    color = color_map.get(lower, "white")
    return f"[{color}]{value}[/{color}]"


def display_ideas(ideas: list[dict], idea_type: str) -> None:
    type_info = IDEA_TYPES[idea_type]
    console.print()
    console.print(Rule(f"[bold cyan]{type_info['label']} Ideas[/bold cyan]"))

    for i, idea in enumerate(ideas, 1):
        name = idea.get("name", f"Idea {i}")

        # Build body content
        body_lines = [f"[bold white]{name}[/bold white]\n"]
        skip_keys = {"name"}

        for key, value in idea.items():
            if key in skip_keys:
                continue
            label = key.replace("_", " ").replace("camel", "").title()
            # Handle lists
            if isinstance(value, list):
                body_lines.append(f"[bold]{label}:[/bold]")
                for item in value:
                    body_lines.append(f"  • {item}")
            else:
                val_str = str(value)
                # Apply color coding for known fields
                if "difficulty" in key.lower():
                    val_str = color_field(val_str, DIFFICULTY_COLORS)
                elif "potential" in key.lower() or "novelty" in key.lower():
                    val_str = color_field(val_str, POTENTIAL_COLORS)
                body_lines.append(f"[bold]{label}:[/bold] {val_str}")

        body = "\n".join(body_lines)
        border_colors = ["cyan", "magenta", "green", "yellow", "blue"]
        border = border_colors[(i - 1) % len(border_colors)]
        console.print(Panel(body, title=f"[bold]#{i}[/bold]", border_style=border, padding=(0, 1)))


def save_ideas(ideas: list[dict], idea_type: str, interests: str) -> str:
    filename = f"ideas_{idea_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "type": idea_type,
        "interests": interests,
        "generated_at": datetime.now().isoformat(),
        "ideas": ideas,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filename

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Idea Generator powered by Google Gemini",
        epilog=textwrap.dedent("""\
            Examples:
              python 65_idea_generator.py
              python 65_idea_generator.py --type startup --interests "AI, sustainability" --count 5
              python 65_idea_generator.py --type project --interests "web dev, games" --skills "Python, JS"
        """),
    )
    parser.add_argument("--type", choices=list(IDEA_TYPES.keys()), help="Type of ideas to generate")
    parser.add_argument("--interests", help="Your interests or domain (comma-separated)")
    parser.add_argument("--skills", default="", help="Your skills or background")
    parser.add_argument("--constraints", default="", help="Any constraints (budget, time, team size, etc.)")
    parser.add_argument("--count", type=int, default=5, help="Number of ideas (1-10, default: 5)")
    parser.add_argument("--save", action="store_true", help="Save results to JSON")
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model name")
    args = parser.parse_args()

    console.print(
        Panel(
            "[bold cyan]💡 AI Idea Generator[/bold cyan]\n[dim]Powered by Google Gemini[/dim]",
            border_style="cyan",
        )
    )

    # ── Interactive prompts if not provided ──
    idea_type = args.type
    if not idea_type:
        console.print("\n[bold]Available idea types:[/bold]")
        for key, info in IDEA_TYPES.items():
            console.print(f"  [cyan]{key:10s}[/cyan] — {info['description']}")
        idea_type = Prompt.ask(
            "\n[bold]Choose type[/bold]",
            choices=list(IDEA_TYPES.keys()),
            default="startup",
        )

    interests = args.interests
    if not interests:
        interests = Prompt.ask("[bold]Your interests / domain[/bold] (e.g. 'AI, healthcare, Python')")

    skills = args.skills or Prompt.ask(
        "[bold]Your skills / background[/bold] [dim](optional, press Enter to skip)[/dim]",
        default="",
    )

    count = max(1, min(10, args.count))

    # ── Generate ──
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        args.model,
        generation_config={"temperature": 0.9},  # Higher creativity
    )

    type_label = IDEA_TYPES[idea_type]["label"]
    console.print(f"\n[dim]Generating {count} {type_label} ideas for:[/dim] [bold]{interests}[/bold]")

    with console.status(f"[bold green]Brainstorming {count} ideas…[/bold green]", spinner="dots"):
        try:
            ideas = generate_ideas(idea_type, interests, skills, count, args.constraints, model)
        except Exception as e:
            console.print(f"[red]API error:[/red] {e}")
            sys.exit(1)

    if not ideas:
        sys.exit(1)

    display_ideas(ideas, idea_type)

    # ── Save ──
    if args.save or Confirm.ask("\n[dim]Save ideas to JSON?[/dim]", default=False):
        filename = save_ideas(ideas, idea_type, interests)
        console.print(f"[green]✓ Saved to[/green] [bold]{filename}[/bold]")

    # ── Generate more? ──
    if Confirm.ask("\n[dim]Generate more ideas?[/dim]", default=False):
        interests2 = Prompt.ask("[bold]Updated interests or focus[/bold]", default=interests)
        with console.status("[bold green]Generating more ideas…[/bold green]", spinner="dots"):
            ideas2 = generate_ideas(idea_type, interests2, skills, count, args.constraints, model)
        display_ideas(ideas2, idea_type)


if __name__ == "__main__":
    main()
