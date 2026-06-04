"""
46_todo_manager.py
─────────────────────────────────────────────────────────────────────────────
Feature-Rich TODO Manager
─────────────────────────────────────────────────────────────────────────────
Manage tasks with:
  • Priorities: HIGH / MEDIUM / LOW (color-coded)
  • Due dates with overdue detection
  • Categories (work, personal, study, other…)
  • Add / complete / delete / edit tasks
  • Filter by priority, category, or status
  • Interactive CLI menu
  • Persist to JSON

Usage:
    python 46_todo_manager.py
    python 46_todo_manager.py add "Buy groceries" --priority LOW --category personal
    python 46_todo_manager.py list
    python 46_todo_manager.py done <task_id>
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

console = Console()

DATA_FILE = Path(__file__).parent / "todo_data.json"

PRIORITY_COLORS = {
    "HIGH":   "bold red",
    "MEDIUM": "bold yellow",
    "LOW":    "bold green",
}

PRIORITY_SORT = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}

STATUS_ICON = {
    "pending":   "⬜",
    "completed": "✅",
}


# ── persistence ───────────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_tasks(tasks: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def gen_id() -> str:
    return str(uuid.uuid4())[:8]


# ── display ───────────────────────────────────────────────────────────────────

def build_table(
    tasks: list[dict],
    show_completed: bool = False,
    filter_priority: Optional[str] = None,
    filter_category: Optional[str] = None,
) -> Table:
    filtered = tasks
    if not show_completed:
        filtered = [t for t in filtered if t["status"] != "completed"]
    if filter_priority:
        filtered = [t for t in filtered if t.get("priority") == filter_priority.upper()]
    if filter_category:
        filtered = [t for t in filtered if t.get("category", "").lower() == filter_category.lower()]

    # Sort: pending first, then by priority, then by due date
    def sort_key(t: dict):
        status_ord = 0 if t["status"] == "pending" else 1
        prio_ord = PRIORITY_SORT.get(t.get("priority", "MEDIUM"), 1)
        due = t.get("due_date") or "9999-12-31"
        return (status_ord, prio_ord, due)

    filtered.sort(key=sort_key)

    today_str = date.today().isoformat()

    title = "📝  TODO Manager"
    if filter_priority:
        title += f"  [dim](priority: {filter_priority})[/dim]"
    if filter_category:
        title += f"  [dim](category: {filter_category})[/dim]"

    table = Table(
        title=title, box=box.ROUNDED, header_style="bold white",
        expand=True, padding=(0, 1),
    )
    table.add_column("ID", style="dim", width=10)
    table.add_column("S", width=3)
    table.add_column("Priority", width=10)
    table.add_column("Task", style="white", no_wrap=False, max_width=40)
    table.add_column("Category", style="cyan", width=14)
    table.add_column("Due Date", width=12)
    table.add_column("Created", style="dim", width=12)

    for t in filtered:
        priority = t.get("priority", "MEDIUM")
        pri_color = PRIORITY_COLORS.get(priority, "white")
        status_icon = STATUS_ICON.get(t["status"], "?")

        due = t.get("due_date", "")
        if due:
            if t["status"] == "pending" and due < today_str:
                due_display = f"[bold red]{due} ⚠[/bold red]"
            elif due == today_str:
                due_display = f"[bold yellow]{due} ★[/bold yellow]"
            else:
                due_display = due
        else:
            due_display = "[dim]—[/dim]"

        task_text = t["title"]
        if t["status"] == "completed":
            task_text = f"[dim strike]{task_text}[/dim strike]"

        if t.get("notes"):
            task_text += f"\n  [dim italic]{t['notes'][:60]}[/dim italic]"

        table.add_row(
            t["id"],
            status_icon,
            f"[{pri_color}]{priority}[/{pri_color}]",
            task_text,
            t.get("category", "other"),
            due_display,
            t.get("created", "")[:10],
        )

    if not filtered:
        table.add_row("[dim]—[/dim]", "", "", "[dim italic]No tasks found[/dim italic]",
                      "", "", "")

    return table


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_add(title: str = "", priority: str = "", category: str = "") -> None:
    tasks = load_tasks()
    console.print(Panel("[bold cyan]➕  Add New Task[/bold cyan]", border_style="cyan"))

    if not title:
        title = Prompt.ask("[bold]Task title[/bold]")
    if not priority:
        priority = Prompt.ask("Priority", choices=["HIGH", "MEDIUM", "LOW"], default="MEDIUM")
    if not category:
        category = Prompt.ask("Category", default="personal")

    due_input = Prompt.ask("Due date (YYYY-MM-DD, or leave empty)", default="")
    notes = Prompt.ask("Notes (optional)", default="")

    # Validate date
    due_date = ""
    if due_input:
        try:
            date.fromisoformat(due_input)
            due_date = due_input
        except ValueError:
            console.print("[red]Invalid date format, skipping due date.[/red]")

    task = {
        "id": gen_id(),
        "title": title,
        "priority": priority.upper(),
        "category": category,
        "due_date": due_date,
        "notes": notes,
        "status": "pending",
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    console.print(f"[bold green]✓ Task added: [cyan]{title}[/cyan]  [{PRIORITY_COLORS[priority.upper()]}]{priority.upper()}[/{PRIORITY_COLORS[priority.upper()]}][/bold green]")


def cmd_list(show_completed: bool = False, filter_priority: Optional[str] = None,
             filter_category: Optional[str] = None) -> None:
    tasks = load_tasks()
    console.print(build_table(tasks, show_completed, filter_priority, filter_category))

    pending = sum(1 for t in tasks if t["status"] == "pending")
    done = sum(1 for t in tasks if t["status"] == "completed")
    today_str = date.today().isoformat()
    overdue = sum(1 for t in tasks
                  if t["status"] == "pending" and t.get("due_date") and t["due_date"] < today_str)

    console.print(
        f"\n  [bold]Pending:[/bold] [yellow]{pending}[/yellow]  "
        f"[bold]Completed:[/bold] [green]{done}[/green]  "
        f"[bold]Overdue:[/bold] [red]{overdue}[/red]"
    )


def cmd_done(task_id: str = "") -> None:
    tasks = load_tasks()
    if not task_id:
        cmd_list()
        task_id = Prompt.ask("\nEnter task ID to mark as done")

    for t in tasks:
        if t["id"] == task_id or t["id"].startswith(task_id):
            if t["status"] == "completed":
                console.print(f"[yellow]Task already completed: {t['title']}[/yellow]")
                return
            t["status"] = "completed"
            t["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_tasks(tasks)
            console.print(f"[bold green]✅ Done: [cyan]{t['title']}[/cyan][/bold green]")
            return

    console.print(f"[red]No task found with ID '{task_id}'[/red]")


def cmd_delete(task_id: str = "") -> None:
    tasks = load_tasks()
    if not task_id:
        cmd_list(show_completed=True)
        task_id = Prompt.ask("\nEnter task ID to delete")

    matching = [t for t in tasks if t["id"] == task_id or t["id"].startswith(task_id)]
    if not matching:
        console.print(f"[red]No task found with ID '{task_id}'[/red]")
        return

    t = matching[0]
    if Confirm.ask(f"Delete task '[bold]{t['title']}[/bold]'?"):
        tasks = [x for x in tasks if x["id"] != t["id"]]
        save_tasks(tasks)
        console.print(f"[green]✓ Deleted: {t['title']}[/green]")


def cmd_clear_done() -> None:
    tasks = load_tasks()
    pending = [t for t in tasks if t["status"] == "pending"]
    removed = len(tasks) - len(pending)
    if removed == 0:
        console.print("[yellow]No completed tasks to clear.[/yellow]")
        return
    if Confirm.ask(f"Clear {removed} completed task(s)?"):
        save_tasks(pending)
        console.print(f"[green]✓ Cleared {removed} completed tasks.[/green]")


def interactive_menu() -> None:
    """Main interactive menu loop."""
    while True:
        console.print(Panel(
            "[bold cyan]📝  TODO Manager[/bold cyan]\n\n"
            "  [bold]a[/bold] = Add task        [bold]l[/bold] = List pending\n"
            "  [bold]d[/bold] = Mark done        [bold]A[/bold] = List all (with completed)\n"
            "  [bold]x[/bold] = Delete task      [bold]f[/bold] = Filter by priority\n"
            "  [bold]c[/bold] = Clear completed  [bold]C[/bold] = Filter by category\n"
            "  [bold]q[/bold] = Quit",
            border_style="blue",
        ))

        choice = Prompt.ask("[bold cyan]Action[/bold cyan]",
                            choices=["a", "l", "d", "x", "A", "f", "c", "C", "q"])

        console.print()
        if choice == "q":
            console.print("[yellow]Goodbye![/yellow]")
            break
        elif choice == "a":
            cmd_add()
        elif choice == "l":
            cmd_list()
        elif choice == "A":
            cmd_list(show_completed=True)
        elif choice == "d":
            cmd_done()
        elif choice == "x":
            cmd_delete()
        elif choice == "c":
            cmd_clear_done()
        elif choice == "f":
            p = Prompt.ask("Priority", choices=["HIGH", "MEDIUM", "LOW"])
            cmd_list(filter_priority=p)
        elif choice == "C":
            cat = Prompt.ask("Category name")
            cmd_list(filter_category=cat)
        console.print()


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Feature-rich TODO Manager")
    sub = parser.add_subparsers(dest="cmd")

    add_p = sub.add_parser("add", help="Add a task")
    add_p.add_argument("title", nargs="?", default="")
    add_p.add_argument("--priority", default="", choices=["HIGH", "MEDIUM", "LOW"])
    add_p.add_argument("--category", default="")

    sub.add_parser("list", help="List pending tasks")
    sub.add_parser("all", help="List all tasks including completed")

    done_p = sub.add_parser("done", help="Mark a task as complete")
    done_p.add_argument("task_id", nargs="?", default="")

    del_p = sub.add_parser("delete", help="Delete a task")
    del_p.add_argument("task_id", nargs="?", default="")

    sub.add_parser("clear", help="Remove all completed tasks")
    sub.add_parser("menu", help="Interactive menu")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add(args.title, args.priority, args.category)
    elif args.cmd == "list":
        cmd_list()
    elif args.cmd == "all":
        cmd_list(show_completed=True)
    elif args.cmd == "done":
        cmd_done(args.task_id)
    elif args.cmd == "delete":
        cmd_delete(args.task_id)
    elif args.cmd == "clear":
        cmd_clear_done()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
