"""
49_focus_timer.py
─────────────────────────────────────────────────────────────────────────────
Deep Focus Timer
─────────────────────────────────────────────────────────────────────────────
Helps you maintain deep focus sessions with:
  • Set focus duration and track time with a live countdown
  • Track interruptions (press 'i' to log an interruption)
  • Focus Score: 100 - (interruptions * 10), capped at 0
  • Terminal bell alerts at start and end
  • Session log persisted to JSON
  • Summary stats after each session

Usage:
    python 49_focus_timer.py
    python 49_focus_timer.py --duration 45 --task "Study math"
    python 49_focus_timer.py history
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

console = Console()

DATA_FILE = Path(__file__).parent / "focus_sessions.json"


# ── persistence ───────────────────────────────────────────────────────────────

def load_sessions() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_sessions(sessions: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(sessions, indent=2, ensure_ascii=False), encoding="utf-8")


# ── helpers ───────────────────────────────────────────────────────────────────

def fmt_time(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


def terminal_bell(times: int = 1) -> None:
    for _ in range(times):
        sys.stdout.write("\a")
        sys.stdout.flush()
        time.sleep(0.3)


def focus_score(duration_min: int, interruptions: int) -> int:
    return max(0, 100 - interruptions * 10)


def score_label(score: int) -> tuple[str, str]:
    """Return (label, color) based on focus score."""
    if score >= 90:
        return "🏆 Excellent", "bold green"
    if score >= 70:
        return "✅ Good", "green"
    if score >= 50:
        return "⚠  Fair", "yellow"
    return "❌ Poor", "red"


# ── main session logic ────────────────────────────────────────────────────────

class FocusSession:
    def __init__(self, duration_min: int, task: str):
        self.duration_sec = duration_min * 60
        self.task = task
        self.interruptions = 0
        self.interrupt_times: list[str] = []
        self.start_time = time.time()
        self.running = True
        self.completed = False

    def interrupt(self) -> None:
        self.interruptions += 1
        self.interrupt_times.append(datetime.now().strftime("%H:%M:%S"))

    def elapsed(self) -> float:
        return time.time() - self.start_time

    def remaining(self) -> int:
        return max(0, self.duration_sec - int(self.elapsed()))

    def build_panel(self) -> Panel:
        rem = self.remaining()
        elapsed = int(self.elapsed())
        pct = min(1.0, elapsed / self.duration_sec)
        bar_width = 40
        filled = int(pct * bar_width)
        bar = f"[cyan]{'█' * filled}[/cyan][dim]{'░' * (bar_width - filled)}[/dim]"
        score = focus_score(self.duration_sec // 60, self.interruptions)
        score_lbl, score_color = score_label(score)

        content = Text()
        content.append("\n")
        content.append(f"  🎯  {self.task}\n\n", style="bold white")
        content.append(f"  {fmt_time(rem)}", style="bold cyan")
        content.append("  remaining\n\n", style="dim")
        content.append(f"  {bar}\n\n", style="")
        content.append(f"  Interruptions: ", style="dim")
        content.append(f"{self.interruptions}", style="bold red" if self.interruptions else "bold green")
        content.append(f"   Focus Score: ", style="dim")
        content.append(f"{score}", style=score_color)
        content.append(f"  {score_lbl}\n\n", style=score_color)
        content.append("  [dim]Press [bold]Ctrl+C[/bold] to end early  |  "
                       "Type [bold]i[/bold] + Enter to log an interruption[/dim]\n")

        return Panel(
            Align.center(content),
            title=f"[bold cyan]🧠  Deep Focus Mode[/bold cyan]",
            border_style="cyan",
            box=box.HEAVY,
        )


def input_listener(session: FocusSession) -> None:
    """Listen for interruption commands in a background thread."""
    while session.running:
        try:
            line = input()
            if line.strip().lower() == "i":
                session.interrupt()
        except EOFError:
            break


def run_focus_session(duration_min: int, task: str) -> dict:
    session = FocusSession(duration_min, task)

    terminal_bell(2)
    console.print(Panel(
        f"[bold green]🧠 Focus session starting![/bold green]\n"
        f"Task: [bold cyan]{task}[/bold cyan]\n"
        f"Duration: [bold]{duration_min} minutes[/bold]\n\n"
        f"[dim]Type [bold]i[/bold] + Enter to log an interruption\n"
        f"Press Ctrl+C to end early[/dim]",
        border_style="green"
    ))
    time.sleep(2)

    # Start input listener thread
    listener = threading.Thread(target=input_listener, args=(session,), daemon=True)
    listener.start()

    try:
        with Live(session.build_panel(), refresh_per_second=2,
                  console=console, screen=True) as live:
            while session.remaining() > 0:
                live.update(session.build_panel())
                time.sleep(0.5)
            session.completed = True
    except KeyboardInterrupt:
        session.completed = False
    finally:
        session.running = False

    if session.completed:
        terminal_bell(3)

    elapsed_min = session.elapsed() / 60
    score = focus_score(duration_min, session.interruptions)
    score_lbl, _ = score_label(score)

    result = {
        "task": task,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "start": datetime.fromtimestamp(session.start_time).strftime("%Y-%m-%d %H:%M"),
        "end": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "planned_min": duration_min,
        "actual_min": round(elapsed_min, 1),
        "interruptions": session.interruptions,
        "interrupt_times": session.interrupt_times,
        "focus_score": score,
        "completed": session.completed,
    }

    return result


def show_result(result: dict) -> None:
    score = result["focus_score"]
    _, color = score_label(score)
    score_lbl, _ = score_label(score)

    table = Table(box=box.ROUNDED, show_header=False, border_style=color)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    table.add_row("Task", result["task"])
    table.add_row("Planned", f"{result['planned_min']} min")
    table.add_row("Actual", f"{result['actual_min']} min")
    table.add_row("Interruptions", str(result["interruptions"]))
    table.add_row("Focus Score", f"[{color}]{score}/100 — {score_lbl}[/{color}]")
    table.add_row("Completed", "✅ Yes" if result["completed"] else "⚠  Ended early")
    if result["interrupt_times"]:
        table.add_row("Interrupt Times", ", ".join(result["interrupt_times"]))

    console.print(Panel(table, title="📊  Session Summary", border_style=color))


def cmd_history() -> None:
    sessions = load_sessions()
    if not sessions:
        console.print("[yellow]No focus sessions recorded yet.[/yellow]")
        return

    table = Table(
        title=f"📜  Focus Session History ({len(sessions)} sessions)",
        box=box.ROUNDED, header_style="bold white", expand=True,
    )
    table.add_column("Date", style="dim", width=12)
    table.add_column("Task", style="cyan", max_width=30)
    table.add_column("Planned", justify="right", width=8)
    table.add_column("Actual", justify="right", width=8)
    table.add_column("Interrupts", justify="right", width=11)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Done", width=6)

    for s in reversed(sessions[-20:]):
        score = s.get("focus_score", 0)
        _, color = score_label(score)
        table.add_row(
            s["date"],
            s["task"],
            f"{s['planned_min']}m",
            f"{s['actual_min']}m",
            str(s["interruptions"]),
            f"[{color}]{score}[/{color}]",
            "✅" if s.get("completed") else "⚠",
        )

    console.print(table)

    avg_score = sum(s.get("focus_score", 0) for s in sessions) / len(sessions)
    total_min = sum(s.get("actual_min", 0) for s in sessions)
    console.print(f"\n  [bold]Avg Score:[/bold] [cyan]{avg_score:.1f}[/cyan]  "
                  f"[bold]Total Focused:[/bold] [yellow]{total_min:.0f} min[/yellow]  "
                  f"[dim]({total_min / 60:.1f} hours)[/dim]")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Deep Focus Timer")
    parser.add_argument("command", nargs="?", default="start",
                        help="'start' (default) or 'history'")
    parser.add_argument("--duration", type=int, default=0,
                        help="Focus duration in minutes")
    parser.add_argument("--task", type=str, default="",
                        help="Task name")
    args = parser.parse_args()

    if args.command == "history":
        cmd_history()
        return

    duration = args.duration
    task = args.task

    if not duration:
        duration = IntPrompt.ask(
            "[bold cyan]Focus duration[/bold cyan] (minutes)", default=25
        )
    if not task:
        task = Prompt.ask("[bold cyan]What will you focus on?[/bold cyan]",
                          default="Deep work")

    result = run_focus_session(duration, task)
    show_result(result)

    sessions = load_sessions()
    sessions.append(result)
    save_sessions(sessions)
    console.print(f"\n[dim]Session saved to {DATA_FILE}[/dim]")


if __name__ == "__main__":
    main()
