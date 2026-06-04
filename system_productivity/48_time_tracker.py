"""
48_time_tracker.py
─────────────────────────────────────────────────────────────────────────────
Work Time Tracker
─────────────────────────────────────────────────────────────────────────────
Track time spent on tasks with:
  • Start / stop timer for named tasks
  • Add notes to sessions
  • View daily and weekly totals
  • Productivity report: most time-consuming tasks
  • All sessions persisted to JSON

Usage:
    python 48_time_tracker.py start "Write documentation"
    python 48_time_tracker.py stop
    python 48_time_tracker.py status
    python 48_time_tracker.py report
    python 48_time_tracker.py today
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

console = Console()

DATA_FILE = Path(__file__).parent / "time_tracker_data.json"
STATE_FILE = Path(__file__).parent / "time_tracker_state.json"


# ── helpers ───────────────────────────────────────────────────────────────────

def fmt_duration(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def load_sessions() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_sessions(sessions: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(sessions, indent=2, ensure_ascii=False), encoding="utf-8")


def load_state() -> Optional[dict]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def save_state(state: Optional[dict]) -> None:
    if state is None:
        STATE_FILE.unlink(missing_ok=True)
    else:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_start(task_name: str) -> None:
    state = load_state()
    if state:
        elapsed = time.time() - state["start_ts"]
        console.print(Panel(
            f"[yellow]Timer already running![/yellow]\n"
            f"Task: [cyan]{state['task']}[/cyan]\n"
            f"Running for: [bold]{fmt_duration(elapsed)}[/bold]\n"
            f"Use [bold]stop[/bold] to stop first.",
            border_style="yellow"
        ))
        return

    now = time.time()
    state = {
        "task": task_name,
        "start_ts": now,
        "start_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_state(state)
    console.print(Panel(
        f"[bold green]▶  Timer started![/bold green]\n"
        f"Task: [bold cyan]{task_name}[/bold cyan]\n"
        f"Started: [dim]{state['start_str']}[/dim]",
        border_style="green"
    ))


def cmd_stop(notes: str = "") -> None:
    state = load_state()
    if not state:
        console.print("[yellow]No timer running. Use 'start' to begin.[/yellow]")
        return

    end_ts = time.time()
    duration = end_ts - state["start_ts"]

    if not notes:
        notes = Prompt.ask("Add notes for this session (optional)", default="")

    session = {
        "task": state["task"],
        "start": state["start_str"],
        "end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": round(duration),
        "date": date.today().isoformat(),
        "notes": notes,
    }

    sessions = load_sessions()
    sessions.append(session)
    save_sessions(sessions)
    save_state(None)

    console.print(Panel(
        f"[bold red]■  Timer stopped![/bold red]\n\n"
        f"Task:     [bold cyan]{session['task']}[/bold cyan]\n"
        f"Started:  [dim]{session['start']}[/dim]\n"
        f"Ended:    [dim]{session['end']}[/dim]\n"
        f"Duration: [bold yellow]{fmt_duration(duration)}[/bold yellow]"
        + (f"\nNotes:    [dim]{notes}[/dim]" if notes else ""),
        border_style="red"
    ))


def cmd_status() -> None:
    state = load_state()
    if not state:
        console.print(Panel("[dim]No timer currently running.[/dim]", border_style="dim"))
        return

    def make_panel() -> Panel:
        elapsed = time.time() - state["start_ts"]
        return Panel(
            f"[bold green]▶  Timer Running[/bold green]\n\n"
            f"Task: [bold cyan]{state['task']}[/bold cyan]\n"
            f"Started: [dim]{state['start_str']}[/dim]\n"
            f"Elapsed: [bold yellow]{fmt_duration(elapsed)}[/bold yellow]\n\n"
            f"[dim]Press Ctrl+C to exit (timer keeps running)[/dim]",
            border_style="green"
        )

    try:
        with Live(make_panel(), refresh_per_second=1, console=console) as live:
            while True:
                time.sleep(1)
                live.update(make_panel())
    except KeyboardInterrupt:
        console.print("\n[dim]Exited status view. Timer still running.[/dim]")


def cmd_today() -> None:
    state = load_state()
    sessions = load_sessions()
    today = date.today().isoformat()
    today_sessions = [s for s in sessions if s["date"] == today]

    table = Table(
        title=f"📅  Today's Sessions — {today}",
        box=box.ROUNDED, header_style="bold white", expand=True,
    )
    table.add_column("Task", style="cyan", max_width=35)
    table.add_column("Start", style="dim", width=10)
    table.add_column("End", style="dim", width=10)
    table.add_column("Duration", justify="right", style="yellow", width=14)
    table.add_column("Notes", style="dim", max_width=30)

    total_sec = 0.0
    for s in today_sessions:
        table.add_row(
            s["task"],
            s["start"][11:16],
            s["end"][11:16],
            fmt_duration(s["duration_sec"]),
            s.get("notes", ""),
        )
        total_sec += s["duration_sec"]

    # If timer running, add it as in-progress
    if state:
        elapsed = time.time() - state["start_ts"]
        total_sec += elapsed
        table.add_row(
            f"[bold green]▶ {state['task']}[/bold green]",
            state["start_str"][11:16],
            "[green]running[/green]",
            f"[green]{fmt_duration(elapsed)}[/green]",
            "[dim]in progress[/dim]",
        )

    console.print(table)
    console.print(f"\n  [bold]Total today:[/bold] [bold yellow]{fmt_duration(total_sec)}[/bold yellow]  "
                  f"[dim]({len(today_sessions)} completed sessions)[/dim]")


def cmd_report(days: int = 7) -> None:
    sessions = load_sessions()
    if not sessions:
        console.print("[yellow]No sessions recorded yet.[/yellow]")
        return

    cutoff = (date.today() - timedelta(days=days)).isoformat()
    recent = [s for s in sessions if s["date"] >= cutoff]

    if not recent:
        console.print(f"[yellow]No sessions in the last {days} days.[/yellow]")
        return

    # Daily totals
    daily: dict[str, float] = {}
    for s in recent:
        daily[s["date"]] = daily.get(s["date"], 0) + s["duration_sec"]

    # Task totals
    tasks: dict[str, float] = {}
    for s in recent:
        tasks[s["task"]] = tasks.get(s["task"], 0) + s["duration_sec"]

    # Daily table
    daily_table = Table(
        title=f"📅  Daily Totals — Last {days} Days",
        box=box.ROUNDED, header_style="bold white", expand=False,
    )
    daily_table.add_column("Date", style="dim", width=12)
    daily_table.add_column("Duration", justify="right", style="yellow", width=16)
    daily_table.add_column("Bar", width=30)

    max_sec = max(daily.values()) if daily else 1
    for d in sorted(daily.keys()):
        sec = daily[d]
        bar_filled = int(sec / max_sec * 25)
        bar = f"[cyan]{'█' * bar_filled}[/cyan][dim]{'░' * (25 - bar_filled)}[/dim]"
        daily_table.add_row(d, fmt_duration(sec), bar)

    console.print(daily_table)

    # Task table
    task_table = Table(
        title="⚙  Time by Task",
        box=box.ROUNDED, header_style="bold white", expand=False,
    )
    task_table.add_column("Task", style="cyan", max_width=35)
    task_table.add_column("Sessions", justify="right", width=10)
    task_table.add_column("Total Time", justify="right", style="yellow", width=16)

    task_counts: dict[str, int] = {}
    for s in recent:
        task_counts[s["task"]] = task_counts.get(s["task"], 0) + 1

    for task, sec in sorted(tasks.items(), key=lambda x: -x[1]):
        task_table.add_row(task, str(task_counts[task]), fmt_duration(sec))

    console.print(task_table)

    total = sum(daily.values())
    avg = total / days
    console.print(f"\n  [bold]Total tracked:[/bold] [yellow]{fmt_duration(total)}[/yellow]  "
                  f"[bold]Daily avg:[/bold] [cyan]{fmt_duration(avg)}[/cyan]")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Work Time Tracker")
    sub = parser.add_subparsers(dest="cmd")

    start_p = sub.add_parser("start", help="Start timer for a task")
    start_p.add_argument("task", nargs="?", default="", help="Task name")

    stop_p = sub.add_parser("stop", help="Stop current timer")
    stop_p.add_argument("--notes", default="", help="Notes for this session")

    sub.add_parser("status", help="Show current timer status (live)")
    sub.add_parser("today", help="Show today's sessions")

    rep_p = sub.add_parser("report", help="Show weekly productivity report")
    rep_p.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if args.cmd == "start":
        task = args.task or Prompt.ask("[bold]Task name[/bold]")
        cmd_start(task)
    elif args.cmd == "stop":
        cmd_stop(args.notes)
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "today":
        cmd_today()
    elif args.cmd == "report":
        cmd_report(args.days)
    else:
        # Default: show status + today
        parser.print_help()
        console.print()
        cmd_status() if load_state() else cmd_today()


if __name__ == "__main__":
    main()
