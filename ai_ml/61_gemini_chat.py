"""
61_gemini_chat.py
─────────────────────────────────────────────────────────────────────────────
Multi-turn Gemini AI Chatbot
─────────────────────────────────────────────────────────────────────────────
A rich terminal chatbot powered by Google Gemini. Supports multi-turn
conversation with full history, markdown rendering, and conversation export.

Usage:
    python 61_gemini_chat.py
    python 61_gemini_chat.py --model gemini-1.5-pro
    python 61_gemini_chat.py --system "You are a Python expert."

Requirements:
    pip install google-generativeai rich
    Set env var: GEMINI_API_KEY
"""

import os
import sys
import json
import argparse
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    print("Missing package: pip install google-generativeai")
    sys.exit(1)

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box

console = Console()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        console.print(
            Panel(
                "[bold red]GEMINI_API_KEY not set![/bold red]\n\n"
                "Please set it with:\n"
                "  [cyan]$env:GEMINI_API_KEY = 'your_key_here'[/cyan]  (PowerShell)\n"
                "  [cyan]export GEMINI_API_KEY='your_key_here'[/cyan]   (bash)\n\n"
                "Get your key at: [link]https://aistudio.google.com/app/apikey[/link]",
                title="[red]Missing API Key",
                border_style="red",
            )
        )
        sys.exit(1)
    return key


def show_welcome(model_name: str, system_prompt: str | None) -> None:
    console.print(
        Panel(
            f"[bold cyan]Gemini AI Chatbot[/bold cyan]\n\n"
            f"[dim]Model:[/dim] [green]{model_name}[/green]\n"
            f"[dim]System:[/dim] [yellow]{system_prompt or 'Default assistant'}[/yellow]\n\n"
            "[dim]Commands:[/dim]\n"
            "  [bold]/history[/bold]  – show conversation history\n"
            "  [bold]/clear[/bold]    – clear conversation\n"
            "  [bold]/save[/bold]     – export conversation to JSON\n"
            "  [bold]/model[/bold]    – show model info\n"
            "  [bold]/exit[/bold]     – quit",
            title="[bold]🤖 Gemini Chat",
            border_style="cyan",
        )
    )


def render_response(text: str) -> None:
    """Render Gemini's response with markdown formatting."""
    console.print(Panel(Markdown(text), title="[bold green]Gemini", border_style="green"))


def show_history(history: list[dict]) -> None:
    """Display a compact conversation history table."""
    if not history:
        console.print("[yellow]No messages yet.[/yellow]")
        return
    table = Table(title="Conversation History", box=box.ROUNDED, border_style="dim")
    table.add_column("#", style="dim", width=4)
    table.add_column("Role", style="bold", width=10)
    table.add_column("Preview", overflow="fold")
    for i, msg in enumerate(history, 1):
        role = msg["role"]
        preview = msg["content"][:80].replace("\n", " ") + ("…" if len(msg["content"]) > 80 else "")
        color = "cyan" if role == "user" else "green"
        table.add_row(str(i), f"[{color}]{role}[/{color}]", preview)
    console.print(table)


def save_conversation(history: list[dict], model_name: str) -> None:
    """Export conversation to a JSON file."""
    filename = f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = {
        "model": model_name,
        "exported_at": datetime.now().isoformat(),
        "messages": history,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✓ Conversation saved to[/green] [bold]{filename}[/bold]")


def show_model_info(model: genai.GenerativeModel) -> None:
    table = Table(title="Model Information", box=box.SIMPLE_HEAVY, border_style="cyan")
    table.add_column("Property", style="bold")
    table.add_column("Value")
    table.add_row("Name", model.model_name)
    console.print(table)

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-turn Gemini AI Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model", default="gemini-1.5-flash", help="Gemini model name")
    parser.add_argument("--system", default=None, help="System prompt / persona")
    args = parser.parse_args()

    api_key = get_api_key()
    genai.configure(api_key=api_key)

    system_instruction = args.system or (
        "You are a helpful, knowledgeable, and concise AI assistant. "
        "Provide clear, well-structured answers. Use markdown formatting when helpful."
    )

    try:
        model = genai.GenerativeModel(
            model_name=args.model,
            system_instruction=system_instruction,
        )
        chat = model.start_chat(history=[])
    except Exception as e:
        console.print(f"[red]Failed to initialize model:[/red] {e}")
        sys.exit(1)

    show_welcome(args.model, args.system)

    # Internal history tracker (mirrors Gemini's)
    history: list[dict] = []

    while True:
        console.print()
        try:
            user_input = Prompt.ask("[bold cyan]You[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input:
            continue

        # ── Built-in commands ──
        if user_input.lower() == "/exit":
            console.print("[dim]Goodbye! 👋[/dim]")
            break
        elif user_input.lower() == "/history":
            show_history(history)
            continue
        elif user_input.lower() == "/clear":
            chat = model.start_chat(history=[])
            history.clear()
            console.print("[yellow]✓ Conversation cleared.[/yellow]")
            continue
        elif user_input.lower() == "/save":
            save_conversation(history, args.model)
            continue
        elif user_input.lower() == "/model":
            show_model_info(model)
            continue

        # ── Send message ──
        history.append({"role": "user", "content": user_input})

        with console.status("[bold green]Gemini is thinking…[/bold green]", spinner="dots"):
            try:
                response = chat.send_message(user_input)
                reply = response.text
            except Exception as e:
                console.print(f"[red]Error from API:[/red] {e}")
                history.pop()  # Remove failed user message
                continue

        history.append({"role": "assistant", "content": reply})
        console.print()
        render_response(reply)


if __name__ == "__main__":
    main()
