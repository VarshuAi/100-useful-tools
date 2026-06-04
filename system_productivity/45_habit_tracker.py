"""
45_habit_tracker.py
─────────────────────────────────────────────────────────────────────────────
Daily Habit Tracker
─────────────────────────────────────────────────────────────────────────────
Track daily habits with:
  • Add/remove habits
  • Mark habits as complete for today
  • View current streaks and best streaks
  • Weekly progress grid (last 7 days)
  • Motivational stats and completion percentage
  • Persisted to a local JSON file

Usage:
    python 45_habit_tracker.py
    python 45_habit_tracker.py add
    python 45_habit_tracker.py check
    python 45_habit_tracker.py stats
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

console = Console()

DATA_FILE = Path(__file__).parent / "habit_tracker_data.json"

MOTIVATIONAL_QUOTES = [
    "Small steps every day lead to big changes.",
    "You don't have to be great to start, but you have to start to be great.",
    "Discipline is choosing between what you want now and what you want most.",
    "Every day is a chance to be better than yesterday.",
    "The secret of your future is hidden in your daily routine.",
    "Motivation gets you started. Habit keeps you going.",
    "Success is the sum of small efforts repeated day in and day out.",
    "You are what you repeatedly do.",
]

# ── persistence ───────────────────────────────────────────────────────────────

def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"habits": []}


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def today_str() -> str:
    return date.today().isoformat()


def week_dates() -> list[str]:
    today = date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]


# ── streak calculation ────────────────────────────────────────────────────────

def calc_streak(completions: list[str]) -> tuple[int, int]:
    """Returns (current_streak, best_streak)."""
    if not completions:
        return 0, 0

    dates = sorted(set(completions), reverse=True)
    dates_set = set(dates)

    # Current streak
    current = 0
    check = date.today()
    while check.isoformat() in dates_set:
        current += 1
        check -= timedelta(days=1)

    # Best streak
    best = 0
    streak = 0
    prev = None
    for d_str in sorted(dates):
        d = date.fromisoformat(d_str)
        if prev and (d - prev).days == 1:
            streak += 1
        else:
            streak = 1
        best = max(best, streak)
        prev = d

    return current, best


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_add() -> None:
    data = load_data()
    console.print(Panel("[bold cyan]Add New Habit[/bold cyan]", border_style="cyan"))

    name = Prompt.ask("[bold]Habit name[/bold]")
    emoji = Prompt.ask("Emoji icon (optional)", default="✅")
    category = Prompt.ask("Category (health/productivity/mindfulness/other)", default="other")

    # Check for duplicate
    existing = [h["name"].lower() for h in data["habits"]]
    if name.lower() in existing:
        console.print(f"[yellow]Habit '{name}' already exists![/yellow]")
        return

    habit = {
        "id": name.lower().replace(" ", "_"),
        "name": name,
        "emoji": emoji,
        "category": category,
        "created": today_str(),
        "completions": [],
    }
    data["habits"].append(habit)
    save_data(data)
    console.print(f"[bold green]✓ Habit '{name}' added![/bold green]")


def cmd_remove() -> None:
    data = load_data()
    if not data["habits"]:
        console.print("[yellow]No habits to remove.[/yellow]")
        return

    console.print("[bold]Existing habits:[/bold]")
    for i, h in enumerate(data["habits"], 1):
        console.print(f"  {i}. {h['emoji']} {h['name']}")

    name = Prompt.ask("Enter habit name to remove (or number)")
    if name.isdigit():
        idx = int(name) - 1
        if 0 <= idx < len(data["habits"]):
            removed = data["habits"].pop(idx)
            save_data(data)
            console.print(f"[green]✓ Removed: {removed['name']}[/green]")
        else:
            console.print("[red]Invalid number[/red]")
    else:
        before = len(data["habits"])
        data["habits"] = [h for h in data["habits"] if h["name"].lower() != name.lower()]
        if len(data["habits"]) < before:
            save_data(data)
            console.print(f"[green]✓ Removed habit: {name}[/green]")
        else:
            console.print(f"[red]Habit '{name}' not found[/red]")


def cmd_check() -> None:
    """Mark habits as complete for today."""
    data = load_data()
    today = today_str()

    if not data["habits"]:
        console.print("[yellow]No habits yet. Use 'add' to create habits.[/yellow]")
        return

    console.print(Panel(
        f"[bold cyan]Mark Today's Habits[/bold cyan]  [dim]{today}[/dim]",
        border_style="cyan"
    ))

    changed = False
    for habit in data["habits"]:
        already_done = today in habit["completions"]
        status = "[bold green]✅ Done[/bold green]" if already_done else "[dim]Not done[/dim]"
        console.print(f"\n  {habit['emoji']} [bold]{habit['name']}[/bold]  {status}")

        if already_done:
            if Confirm.ask("  Unmark as done?", default=False):
                habit["completions"].remove(today)
                changed = True
        else:
            if Confirm.ask("  Mark as done?", default=True):
                habit["completions"].append(today)
                changed = True

    if changed:
        save_data(data)
        console.print("\n[bold green]✓ Progress saved![/bold green]")

    cmd_view()


def build_weekly_grid(habits: list[dict]) -> Table:
    dates = week_dates()
    short_dates = [d[-5:] for d in dates]  # MM-DD format
    weekdays = [(date.fromisoformat(d).strftime("%a")) for d in dates]

    table = Table(
        title="📅  Weekly Progress Grid  (last 7 days)",
        box=box.ROUNDED, header_style="bold white",
        expand=True, padding=(0, 1),
    )
    table.add_column("Habit", style="cyan", no_wrap=True, max_width=25)
    for day, d in zip(weekdays, short_dates):
        table.add_column(f"{day}\n{d}", justify="center", width=6)
    table.add_column("Streak", justify="center", style="yellow")
    table.add_column("Best", justify="center", style="dim")

    today = today_str()

    for habit in habits:
        comps = set(habit["completions"])
        streak, best = calc_streak(habit["completions"])
        cells = []
        for d in dates:
            if d in comps:
                cells.append("[bold green]✅[/bold green]")
            elif d == today:
                cells.append("[dim yellow]○[/dim yellow]")
            else:
                cells.append("[dim red]✗[/dim red]")

        table.add_row(
            f"{habit['emoji']}  {habit['name']}",
            *cells,
            f"[bold yellow]{streak}🔥[/bold yellow]" if streak > 0 else "0",
            str(best),
        )

    return table


def cmd_view() -> None:
    data = load_data()
    if not data["habits"]:
        console.print(Panel(
            "[yellow]No habits tracked yet.\n"
            "Run [bold]python 45_habit_tracker.py add[/bold] to get started![/yellow]",
            title="Habit Tracker", border_style="yellow",
        ))
        return

    console.print(build_weekly_grid(data["habits"]))

    # Today's completion rate
    today = today_str()
    done_today = sum(1 for h in data["habits"] if today in h["completions"])
    total = len(data["habits"])
    pct = (done_today / total * 100) if total else 0

    bar_filled = int(pct / 5)
    bar = f"[green]{'█' * bar_filled}[/green][dim]{'░' * (20 - bar_filled)}[/dim]"
    console.print(f"\n  Today: [bold]{done_today}/{total}[/bold]  {bar}  [bold cyan]{pct:.0f}%[/bold cyan] complete")


def cmd_stats() -> None:
    data = load_data()
    if not data["habits"]:
        console.print("[yellow]No habits to show stats for.[/yellow]")
        return

    console.print(Panel("[bold cyan]📊  Habit Statistics[/bold cyan]", border_style="cyan"))

    table = Table(box=box.ROUNDED, header_style="bold white", expand=True)
    table.add_column("Habit", style="cyan")
    table.add_column("Total Done", justify="right")
    table.add_column("Current Streak", justify="right")
    table.add_column("Best Streak", justify="right")
    table.add_column("Since", style="dim")
    table.add_column("30-Day %", justify="right")

    today = date.today()
    last_30 = [(today - timedelta(days=i)).isoformat() for i in range(30)]

    for habit in data["habits"]:
        comps = habit["completions"]
        streak, best = calc_streak(comps)
        done_30 = sum(1 for d in last_30 if d in comps)
        pct_30 = f"{done_30 / 30 * 100:.0f}%"
        table.add_row(
            f"{habit['emoji']}  {habit['name']}",
            str(len(comps)),
            f"[yellow]{streak}🔥[/yellow]" if streak > 0 else "0",
            str(best),
            habit.get("created", "?"),
            pct_30,
        )

    console.print(table)

    import random
    quote = random.choice(MOTIVATIONAL_QUOTES)
    console.print(Panel(f"[italic yellow]{quote}[/italic yellow]",
                        title="💡  Daily Motivation", border_style="yellow"))


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily Habit Tracker")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("add", help="Add a new habit")
    sub.add_parser("remove", help="Remove a habit")
    sub.add_parser("check", help="Mark today's habits as done")
    sub.add_parser("view", help="View weekly progress grid")
    sub.add_parser("stats", help="Show detailed statistics")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add()
    elif args.cmd == "remove":
        cmd_remove()
    elif args.cmd == "check":
        cmd_check()
    elif args.cmd == "stats":
        cmd_stats()
    else:
        # Default: show view + today's check-in prompt
        cmd_view()
        console.print("\n[dim]Commands: add | remove | check | view | stats[/dim]")


if __name__ == "__main__":
    main()
