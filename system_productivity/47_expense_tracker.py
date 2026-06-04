"""
47_expense_tracker.py
─────────────────────────────────────────────────────────────────────────────
Personal Expense Tracker
─────────────────────────────────────────────────────────────────────────────
Track your spending with:
  • Log expenses with category, amount, date, and notes
  • Monthly summary with total spending
  • Category breakdown with percentage and bar chart
  • Budget vs actual (set monthly budgets per category)
  • Export data to CSV
  • All data stored in JSON

Usage:
    python 47_expense_tracker.py
    python 47_expense_tracker.py add
    python 47_expense_tracker.py summary
    python 47_expense_tracker.py budget
    python 47_expense_tracker.py export
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, Prompt
from rich.table import Table
from rich.text import Text

console = Console()

DATA_FILE = Path(__file__).parent / "expense_data.json"
EXPORT_FILE = Path(__file__).parent / "expenses_export.csv"

CATEGORIES = [
    "food", "transport", "rent", "utilities", "health",
    "entertainment", "shopping", "education", "savings", "other"
]

CATEGORY_COLORS = {
    "food":          "green",
    "transport":     "cyan",
    "rent":          "red",
    "utilities":     "yellow",
    "health":        "magenta",
    "entertainment": "blue",
    "shopping":      "bright_magenta",
    "education":     "bright_cyan",
    "savings":       "bright_green",
    "other":         "white",
}


# ── persistence ───────────────────────────────────────────────────────────────

def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"expenses": [], "budgets": {}}


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def current_month() -> str:
    return date.today().strftime("%Y-%m")


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_add() -> None:
    data = load_data()
    console.print(Panel("[bold cyan]💰  Add New Expense[/bold cyan]", border_style="cyan"))

    # Show category choices
    cat_list = "  ".join(
        f"[{CATEGORY_COLORS.get(c, 'white')}]{i}.[/{CATEGORY_COLORS.get(c, 'white')}]{c}"
        for i, c in enumerate(CATEGORIES, 1)
    )
    console.print(f"Categories: {cat_list}")

    cat_input = Prompt.ask("Category (name or number)", default="other")
    if cat_input.isdigit():
        idx = int(cat_input) - 1
        category = CATEGORIES[idx] if 0 <= idx < len(CATEGORIES) else "other"
    else:
        category = cat_input.lower() if cat_input.lower() in CATEGORIES else "other"

    amount_str = Prompt.ask("[bold]Amount[/bold]")
    try:
        amount = float(amount_str.replace(",", "").replace("$", ""))
    except ValueError:
        console.print("[red]Invalid amount[/red]")
        return

    description = Prompt.ask("Description", default="")
    date_str = Prompt.ask("Date (YYYY-MM-DD)", default=date.today().isoformat())
    try:
        date.fromisoformat(date_str)
    except ValueError:
        console.print("[red]Invalid date, using today.[/red]")
        date_str = date.today().isoformat()

    expense = {
        "id": len(data["expenses"]) + 1,
        "date": date_str,
        "category": category,
        "amount": round(amount, 2),
        "description": description,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    data["expenses"].append(expense)
    save_data(data)

    color = CATEGORY_COLORS.get(category, "white")
    console.print(
        f"[bold green]✓ Added:[/bold green] [{color}]{category}[/{color}]  "
        f"[bold white]${amount:.2f}[/bold white]"
        + (f"  [dim]{description}[/dim]" if description else "")
    )


def cmd_list(month: Optional[str] = None) -> None:
    data = load_data()
    month = month or current_month()
    expenses = [e for e in data["expenses"] if e["date"].startswith(month)]

    if not expenses:
        console.print(f"[yellow]No expenses found for {month}[/yellow]")
        return

    expenses.sort(key=lambda e: e["date"], reverse=True)

    table = Table(
        title=f"💸  Expenses — {month}", box=box.ROUNDED,
        header_style="bold white", expand=True,
    )
    table.add_column("Date", style="dim", width=12)
    table.add_column("Category", width=15)
    table.add_column("Amount", justify="right", style="bold white", width=12)
    table.add_column("Description", style="dim", max_width=40)

    total = 0.0
    for e in expenses:
        color = CATEGORY_COLORS.get(e["category"], "white")
        table.add_row(
            e["date"],
            f"[{color}]{e['category']}[/{color}]",
            f"${e['amount']:.2f}",
            e.get("description", ""),
        )
        total += e["amount"]

    console.print(table)
    console.print(f"\n  [bold]Total for {month}:[/bold]  [bold red]${total:.2f}[/bold red]  "
                  f"[dim]({len(expenses)} transactions)[/dim]")


def cmd_summary(month: Optional[str] = None) -> None:
    data = load_data()
    month = month or current_month()
    expenses = [e for e in data["expenses"] if e["date"].startswith(month)]

    if not expenses:
        console.print(f"[yellow]No expenses for {month}[/yellow]")
        return

    # Aggregate by category
    by_cat: dict[str, float] = {}
    for e in expenses:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]

    total = sum(by_cat.values())
    budgets = data.get("budgets", {}).get(month, {})

    table = Table(
        title=f"📊  Monthly Summary — {month}",
        box=box.ROUNDED, header_style="bold white", expand=True,
    )
    table.add_column("Category", style="white", width=16)
    table.add_column("Spent", justify="right", width=12)
    table.add_column("Budget", justify="right", width=12)
    table.add_column("Remaining", justify="right", width=12)
    table.add_column("% of Total", justify="right", width=10)
    table.add_column("Breakdown", width=30)

    for cat in sorted(by_cat.keys(), key=lambda c: -by_cat[c]):
        spent = by_cat[cat]
        budget = budgets.get(cat, 0)
        remaining = budget - spent if budget else None
        pct = spent / total * 100 if total else 0
        color = CATEGORY_COLORS.get(cat, "white")

        # Bar
        bar_filled = int(pct / 5)
        bar = f"[{color}]{'█' * bar_filled}[/{color}][dim]{'░' * (20 - bar_filled)}[/dim]"

        budget_str = f"${budget:.2f}" if budget else "[dim]—[/dim]"
        if remaining is not None:
            rem_color = "green" if remaining >= 0 else "red"
            rem_str = f"[{rem_color}]${remaining:.2f}[/{rem_color}]"
        else:
            rem_str = "[dim]—[/dim]"

        table.add_row(
            f"[{color}]{cat}[/{color}]",
            f"${spent:.2f}",
            budget_str,
            rem_str,
            f"{pct:.1f}%",
            bar,
        )

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold red]${total:.2f}[/bold red]",
        "", "", "", ""
    )

    console.print(table)


def cmd_budget() -> None:
    """Set monthly budget per category."""
    data = load_data()
    month = Prompt.ask("Month (YYYY-MM)", default=current_month())

    if "budgets" not in data:
        data["budgets"] = {}
    if month not in data["budgets"]:
        data["budgets"][month] = {}

    console.print(Panel(f"[bold cyan]Set Budgets for {month}[/bold cyan]", border_style="cyan"))
    console.print("[dim]Enter 0 or press Enter to skip a category[/dim]\n")

    for cat in CATEGORIES:
        current = data["budgets"][month].get(cat, 0)
        color = CATEGORY_COLORS.get(cat, "white")
        val_str = Prompt.ask(
            f"[{color}]{cat:16}[/{color}] budget",
            default=str(current) if current else "0"
        )
        try:
            val = float(val_str)
            if val > 0:
                data["budgets"][month][cat] = round(val, 2)
        except ValueError:
            pass

    save_data(data)
    console.print(f"[bold green]✓ Budgets saved for {month}[/bold green]")


def cmd_export() -> None:
    data = load_data()
    if not data["expenses"]:
        console.print("[yellow]No expenses to export.[/yellow]")
        return

    with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description", "added_at"])
        writer.writeheader()
        writer.writerows(data["expenses"])

    console.print(f"[bold green]✓ Exported {len(data['expenses'])} expenses to:[/bold green]")
    console.print(f"  [cyan]{EXPORT_FILE}[/cyan]")


def interactive_menu() -> None:
    while True:
        console.print(Panel(
            "[bold cyan]💰  Expense Tracker[/bold cyan]\n\n"
            "  [bold]a[/bold] = Add expense      [bold]l[/bold] = List expenses\n"
            "  [bold]s[/bold] = Monthly summary   [bold]b[/bold] = Set budgets\n"
            "  [bold]e[/bold] = Export to CSV     [bold]q[/bold] = Quit",
            border_style="blue",
        ))
        choice = Prompt.ask("[bold cyan]Action[/bold cyan]",
                            choices=["a", "l", "s", "b", "e", "q"])
        console.print()

        if choice == "q":
            console.print("[yellow]Goodbye![/yellow]")
            break
        elif choice == "a":
            cmd_add()
        elif choice == "l":
            m = Prompt.ask("Month (YYYY-MM)", default=current_month())
            cmd_list(m)
        elif choice == "s":
            m = Prompt.ask("Month (YYYY-MM)", default=current_month())
            cmd_summary(m)
        elif choice == "b":
            cmd_budget()
        elif choice == "e":
            cmd_export()
        console.print()


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Personal Expense Tracker")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("add", help="Add a new expense")
    list_p = sub.add_parser("list", help="List expenses for a month")
    list_p.add_argument("--month", default="", help="YYYY-MM (default: current month)")
    sum_p = sub.add_parser("summary", help="Show category summary")
    sum_p.add_argument("--month", default="", help="YYYY-MM (default: current month)")
    sub.add_parser("budget", help="Set monthly budgets")
    sub.add_parser("export", help="Export all expenses to CSV")

    args = parser.parse_args()

    if args.cmd == "add":
        cmd_add()
    elif args.cmd == "list":
        cmd_list(args.month or None)
    elif args.cmd == "summary":
        cmd_summary(args.month or None)
    elif args.cmd == "budget":
        cmd_budget()
    elif args.cmd == "export":
        cmd_export()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
