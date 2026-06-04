"""
44_pomodoro_timer.py
─────────────────────────────────────────────────────────────────────────────
Pomodoro Timer
─────────────────────────────────────────────────────────────────────────────
Classic 25-min work + 5-min break productivity timer with:
  • Live countdown in the terminal using rich.live
  • Desktop notification at end of each phase (via plyer)
  • ASCII progress bar
  • Session log saved to CSV (date, type, duration, task name)
  • Configurable work/break durations

Usage:
    python 44_pomodoro_timer.py
    python 44_pomodoro_timer.py --work 25 --break-time 5 --long-break 15
    python 44_pomodoro_timer.py --task "Write report" --sessions 4
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

console = Console()

LOG_FILE = Path(__file__).parent / "pomodoro_log.csv"

# ── helpers ───────────────────────────────────────────────────────────────────

def ensure_log() -> None:
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["date", "type", "task", "duration_min", "completed"])


def log_session(session_type: str, task: str, duration_min: int, completed: bool) -> None:
    ensure_log()
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            session_type, task, duration_min,
            "yes" if completed else "no",
        ])


def notify(title: str, message: str) -> None:
    """Send desktop notification (gracefully degrade if unavailable)."""
    try:
        from plyer import notification
        notification.notify(title=title, message=message,
                            app_name="Pomodoro Timer", timeout=8)
    except Exception:
        pass  # silently skip if plyer isn't installed or fails


def terminal_bell() -> None:
    sys.stdout.write("\a")
    sys.stdout.flush()


def fmt_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"


# ── countdown ─────────────────────────────────────────────────────────────────

def run_timer(duration_sec: int, label: str, color: str,
              task: str, emoji: str) -> bool:
    """Run a single countdown. Returns True if completed (not interrupted)."""
    start = time.time()
    end = start + duration_sec

    def make_panel(remaining: int) -> Panel:
        pct = 1.0 - (remaining / duration_sec)
        bar_width = 40
        filled = int(pct * bar_width)
        bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (bar_width - filled)}[/dim]"

        content = Text.assemble(
            "\n",
            (f"{emoji}  {label}\n\n", f"bold {color}"),
            (f"  {fmt_time(remaining)}\n\n", f"bold white"),
            (f"  {bar}\n\n", ""),
            (f"  Task: ", "dim"),
            (task, "bold white"),
            ("\n  [dim]Press Ctrl+C to interrupt[/dim]\n", ""),
        )
        return Panel(
            Align.center(content),
            border_style=color,
            box=box.HEAVY,
            title=f"[bold {color}]Pomodoro Timer[/bold {color}]",
        )

    completed = True
    try:
        with Live(make_panel(duration_sec), refresh_per_second=2,
                  console=console, screen=True) as live:
            while True:
                remaining = max(0, int(end - time.time()))
                live.update(make_panel(remaining))
                if remaining == 0:
                    break
                time.sleep(0.5)
    except KeyboardInterrupt:
        completed = False

    return completed


# ── session summary ───────────────────────────────────────────────────────────

def show_summary(task: str, sessions_done: int, total_sessions: int) -> None:
    ensure_log()
    all_rows = []
    try:
        with open(LOG_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)
    except Exception:
        pass

    today = datetime.now().strftime("%Y-%m-%d")
    today_work = [r for r in all_rows if r.get("date", "").startswith(today)
                  and r.get("type") == "work" and r.get("completed") == "yes"]

    table = Table(box=box.ROUNDED, border_style="cyan", expand=False)
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("Task", task)
    table.add_row("Sessions This Run", f"{sessions_done} / {total_sessions}")
    table.add_row("Work Sessions Today", str(len(today_work)))
    table.add_row("Total Focus Today",
                  f"{len(today_work) * 25} min  (~{len(today_work) * 25 // 60}h)")
    table.add_row("Log File", str(LOG_FILE))

    console.print("\n")
    console.print(Panel(table, title="📊  Session Summary", border_style="green"))


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    parser.add_argument("--work", type=int, default=25,
                        help="Work duration in minutes (default: 25)")
    parser.add_argument("--break-time", type=int, default=5,
                        help="Short break in minutes (default: 5)")
    parser.add_argument("--long-break", type=int, default=15,
                        help="Long break after 4 sessions in minutes (default: 15)")
    parser.add_argument("--sessions", type=int, default=4,
                        help="Number of work sessions (default: 4)")
    parser.add_argument("--task", type=str, default="",
                        help="Task name to log")
    args = parser.parse_args()

    task = args.task or Prompt.ask(
        "[bold cyan]What are you working on?[/bold cyan]",
        default="Focus session"
    )

    console.print(Panel(
        f"[bold green]🍅 Pomodoro Timer Started[/bold green]\n\n"
        f"  Task: [bold]{task}[/bold]\n"
        f"  Work: [cyan]{args.work} min[/cyan]  |  "
        f"Break: [yellow]{args.break_time} min[/yellow]  |  "
        f"Long Break: [magenta]{args.long_break} min[/magenta]\n"
        f"  Sessions: [bold]{args.sessions}[/bold]",
        border_style="green",
    ))

    sessions_done = 0

    for i in range(1, args.sessions + 1):
        console.print(f"\n[bold cyan]═══ Session {i} / {args.sessions} ═══[/bold cyan]")

        # ── Work phase ────────────────────────────────────────────────────────
        completed = run_timer(
            args.work * 60, f"Work Session {i}", "green", task, "🍅"
        )
        log_session("work", task, args.work, completed)

        if not completed:
            console.print("\n[yellow]Session interrupted. Logging partial session.[/yellow]")
            if not Confirm.ask("Continue with next session?"):
                break

        if completed:
            sessions_done += 1
            terminal_bell()
            notify("🍅 Pomodoro Complete!", f"Session {i} done! Time for a break.")
            console.print(f"\n[bold green]✅ Session {i} complete![/bold green]")

        if i >= args.sessions:
            break

        # ── Break phase ───────────────────────────────────────────────────────
        is_long = (i % 4 == 0)
        break_dur = args.long_break if is_long else args.break_time
        break_label = "Long Break 🌴" if is_long else "Short Break ☕"
        break_color = "magenta" if is_long else "yellow"

        if Confirm.ask(f"\n[{break_color}]Start {break_label} ({break_dur} min)?[/{break_color}]"):
            completed_break = run_timer(
                break_dur * 60, break_label, break_color, "Rest!", "☕"
            )
            log_session("break", task, break_dur, completed_break)
            if completed_break:
                terminal_bell()
                notify("Break Over!", "Time to get back to work! 🍅")
        else:
            console.print("[dim]Skipping break…[/dim]")

    show_summary(task, sessions_done, args.sessions)
    console.print("\n[bold green]🎉 All done! Great work![/bold green]\n")


if __name__ == "__main__":
    main()
