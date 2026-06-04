"""
43_task_scheduler.py
─────────────────────────────────────────────────────────────────────────────
Simple Task Scheduler
─────────────────────────────────────────────────────────────────────────────
Uses the `schedule` library to run commands or Python scripts at intervals.
Tasks are persisted to a JSON file so they survive restarts.

Commands:
    add      — Add a new scheduled task
    list     — List all scheduled tasks
    remove   — Remove a task by ID
    run      — Start the scheduler daemon loop
    run-once — Run all pending tasks once and exit

Usage:
    python 43_task_scheduler.py add
    python 43_task_scheduler.py list
    python 43_task_scheduler.py remove <task_id>
    python 43_task_scheduler.py run
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import schedule
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

console = Console()

DATA_FILE = Path(__file__).parent / "task_scheduler_data.json"

# ── persistence ───────────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


# ── task execution ────────────────────────────────────────────────────────────

def run_task(task: dict) -> None:
    """Execute a task command and log the result."""
    cmd = task["command"]
    task_id = task["id"]
    name = task["name"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    console.print(f"\n[bold cyan][{now}] Running task:[/bold cyan] [yellow]{name}[/yellow] "
                  f"[dim](ID: {task_id[:8]})[/dim]")
    console.print(f"  [dim]Command: {cmd}[/dim]")

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=300
        )
        if result.stdout:
            console.print(f"  [green]Output:[/green] {result.stdout.strip()[:200]}")
        if result.stderr:
            console.print(f"  [red]Stderr:[/red] {result.stderr.strip()[:200]}")
        if result.returncode == 0:
            console.print(f"  [bold green]✓ Task completed successfully[/bold green]")
        else:
            console.print(f"  [bold red]✗ Task failed (exit code {result.returncode})[/bold red]")

        # Update last_run and run_count
        tasks = load_tasks()
        for t in tasks:
            if t["id"] == task_id:
                t["last_run"] = now
                t["run_count"] = t.get("run_count", 0) + 1
                break
        save_tasks(tasks)

    except subprocess.TimeoutExpired:
        console.print(f"  [red]✗ Task timed out after 300 seconds[/red]")
    except Exception as e:
        console.print(f"  [red]✗ Error running task: {e}[/red]")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_add() -> None:
    """Interactively add a new task."""
    console.print(Panel("[bold cyan]Add New Scheduled Task[/bold cyan]", border_style="cyan"))

    name = Prompt.ask("[bold]Task name[/bold]")
    command = Prompt.ask("[bold]Command or script path[/bold]",
                         default="python my_script.py")

    console.print("\n[bold]Interval options:[/bold]")
    console.print("  1) Every N seconds")
    console.print("  2) Every N minutes")
    console.print("  3) Every N hours")
    console.print("  4) Daily at HH:MM")
    console.print("  5) Every N days")

    choice = Prompt.ask("Choose interval type", choices=["1", "2", "3", "4", "5"])

    interval_type: str
    interval_value: str

    if choice == "1":
        n = IntPrompt.ask("Every how many seconds", default=60)
        interval_type, interval_value = "seconds", str(n)
    elif choice == "2":
        n = IntPrompt.ask("Every how many minutes", default=30)
        interval_type, interval_value = "minutes", str(n)
    elif choice == "3":
        n = IntPrompt.ask("Every how many hours", default=1)
        interval_type, interval_value = "hours", str(n)
    elif choice == "4":
        t = Prompt.ask("Time (HH:MM)", default="08:00")
        interval_type, interval_value = "daily", t
    else:
        n = IntPrompt.ask("Every how many days", default=1)
        interval_type, interval_value = "days", str(n)

    task = {
        "id": str(uuid.uuid4()),
        "name": name,
        "command": command,
        "interval_type": interval_type,
        "interval_value": interval_value,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_run": None,
        "run_count": 0,
        "enabled": True,
    }

    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)

    console.print(f"\n[bold green]✓ Task '[/bold green][cyan]{name}[/cyan]"
                  f"[bold green]' added successfully![/bold green]")
    console.print(f"  [dim]ID: {task['id']}[/dim]")
    console.print(f"  [dim]Schedule: every {interval_value} {interval_type}[/dim]")


def cmd_list() -> None:
    """List all tasks in a table."""
    tasks = load_tasks()

    if not tasks:
        console.print(Panel("[yellow]No tasks scheduled yet. Use 'add' to create one.[/yellow]",
                            title="Task Scheduler", border_style="yellow"))
        return

    table = Table(title="📅  Scheduled Tasks", box=box.ROUNDED,
                  header_style="bold white", expand=True)
    table.add_column("ID (short)", style="dim", width=10)
    table.add_column("Name", style="cyan", max_width=25)
    table.add_column("Command", style="white", max_width=35)
    table.add_column("Schedule", style="green")
    table.add_column("Last Run", style="dim")
    table.add_column("Runs", justify="right", style="yellow")
    table.add_column("Enabled", justify="center")

    for t in tasks:
        itype = t["interval_type"]
        ival = t["interval_value"]
        if itype == "daily":
            schedule_str = f"Daily @ {ival}"
        else:
            schedule_str = f"Every {ival} {itype}"

        enabled_icon = "[bold green]✓[/bold green]" if t.get("enabled", True) else "[red]✗[/red]"

        table.add_row(
            t["id"][:8] + "…",
            t["name"],
            t["command"][:35],
            schedule_str,
            t.get("last_run") or "never",
            str(t.get("run_count", 0)),
            enabled_icon,
        )

    console.print(table)
    console.print(f"\n[dim]Data file: {DATA_FILE}[/dim]")


def cmd_remove(task_id: Optional[str] = None) -> None:
    """Remove a task by full or partial ID."""
    tasks = load_tasks()
    if not tasks:
        console.print("[yellow]No tasks to remove.[/yellow]")
        return

    if not task_id:
        cmd_list()
        task_id = Prompt.ask("\nEnter task ID (or first 8 chars)")

    matching = [t for t in tasks if t["id"].startswith(task_id)]
    if not matching:
        console.print(f"[red]No task found matching ID '{task_id}'[/red]")
        return
    if len(matching) > 1:
        console.print(f"[red]Multiple tasks match '{task_id}', be more specific[/red]")
        return

    task = matching[0]
    tasks = [t for t in tasks if t["id"] != task["id"]]
    save_tasks(tasks)
    console.print(f"[bold green]✓ Removed task: [cyan]{task['name']}[/cyan][/bold green]")


def register_all(tasks: list[dict]) -> None:
    """Register all enabled tasks with the schedule library."""
    schedule.clear()
    for task in tasks:
        if not task.get("enabled", True):
            continue
        itype = task["interval_type"]
        ival = task["interval_value"]

        def make_job(t: dict):
            return lambda: run_task(t)

        job_fn = make_job(task)

        try:
            if itype == "seconds":
                schedule.every(int(ival)).seconds.do(job_fn)
            elif itype == "minutes":
                schedule.every(int(ival)).minutes.do(job_fn)
            elif itype == "hours":
                schedule.every(int(ival)).hours.do(job_fn)
            elif itype == "days":
                schedule.every(int(ival)).days.do(job_fn)
            elif itype == "daily":
                schedule.every().day.at(ival).do(job_fn)
        except Exception as e:
            console.print(f"[red]Error scheduling '{task['name']}': {e}[/red]")


def cmd_run() -> None:
    """Start the scheduler daemon."""
    tasks = load_tasks()
    enabled = [t for t in tasks if t.get("enabled", True)]

    if not enabled:
        console.print("[yellow]No enabled tasks. Use 'add' to create tasks first.[/yellow]")
        return

    register_all(enabled)

    console.print(Panel(
        f"[bold cyan]Task Scheduler Running[/bold cyan]\n"
        f"[dim]{len(enabled)} task(s) scheduled | Press Ctrl+C to stop[/dim]",
        border_style="green",
    ))

    cmd_list()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Scheduler stopped.[/bold yellow]")


def cmd_run_once() -> None:
    """Run all pending jobs once and exit."""
    tasks = load_tasks()
    register_all([t for t in tasks if t.get("enabled", True)])
    schedule.run_all()
    console.print("[bold green]✓ All pending jobs executed.[/bold green]")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Simple Task Scheduler with JSON persistence")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("add", help="Add a new scheduled task")
    sub.add_parser("list", help="List all scheduled tasks")
    remove_p = sub.add_parser("remove", help="Remove a task by ID")
    remove_p.add_argument("task_id", nargs="?", help="Task ID (or prefix)")
    sub.add_parser("run", help="Start the scheduler daemon")
    sub.add_parser("run-once", help="Run all pending tasks once")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add()
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "remove":
        cmd_remove(getattr(args, "task_id", None))
    elif args.cmd == "run":
        cmd_run()
    elif args.cmd == "run-once":
        cmd_run_once()
    else:
        parser.print_help()
        console.print("\n[dim]Data stored in:[/dim] " + str(DATA_FILE))


if __name__ == "__main__":
    main()
