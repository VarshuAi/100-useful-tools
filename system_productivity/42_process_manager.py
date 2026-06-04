"""
42_process_manager.py
─────────────────────────────────────────────────────────────────────────────
Interactive Process Manager
─────────────────────────────────────────────────────────────────────────────
Features:
  • List all running processes sorted by CPU or RAM usage
  • Search processes by name (substring match)
  • Kill a process by PID or name
  • View detailed info for a specific PID
  • Auto-refresh live table

Usage:
    python 42_process_manager.py
    python 42_process_manager.py --sort ram
    python 42_process_manager.py --search chrome
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import time
from typing import Optional

import psutil
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

console = Console()


# ── helpers ──────────────────────────────────────────────────────────────────

def human_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def cpu_color(pct: float) -> str:
    if pct >= 80:
        return "bold red"
    if pct >= 40:
        return "yellow"
    return "green"


def mem_color(pct: float) -> str:
    if pct >= 50:
        return "bold red"
    if pct >= 20:
        return "yellow"
    return "cyan"


def get_processes(sort_by: str = "cpu", search: str = "") -> list[dict]:
    """Fetch all processes, optionally filtered by name."""
    attrs = ["pid", "name", "cpu_percent", "memory_percent",
             "memory_info", "status", "num_threads", "username", "create_time"]
    procs = []
    for p in psutil.process_iter(attrs):
        try:
            info = p.info
            if search and search.lower() not in (info.get("name") or "").lower():
                continue
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    procs.sort(key=lambda x: x.get(key) or 0, reverse=True)
    return procs


def build_table(procs: list[dict], sort_by: str, search: str) -> Table:
    title_parts = [f"⚙  Processes  [dim](sort: {sort_by.upper()})[/dim]"]
    if search:
        title_parts.append(f"  [yellow]filter: '{search}'[/yellow]")
    title = "".join(title_parts)

    table = Table(
        title=title, box=box.ROUNDED, header_style="bold white",
        expand=True, show_lines=False, padding=(0, 1),
    )
    table.add_column("#", style="dim", width=5)
    table.add_column("PID", style="bold", width=8)
    table.add_column("Name", style="cyan", no_wrap=True, max_width=30)
    table.add_column("User", style="dim", max_width=15)
    table.add_column("CPU %", justify="right", width=8)
    table.add_column("MEM %", justify="right", width=8)
    table.add_column("RSS", justify="right", width=10)
    table.add_column("Threads", justify="right", width=8)
    table.add_column("Status", width=12)

    for i, proc in enumerate(procs[:50], 1):
        cpu_p = proc.get("cpu_percent") or 0.0
        mem_p = proc.get("memory_percent") or 0.0
        rss = (proc.get("memory_info") or psutil._common.pmem(0, 0)).rss
        status = proc.get("status", "")

        status_style = {
            "running": "bold green",
            "sleeping": "dim",
            "idle": "dim blue",
            "zombie": "bold red",
            "stopped": "yellow",
        }.get(status, "")

        table.add_row(
            str(i),
            str(proc.get("pid", "")),
            proc.get("name", "?"),
            proc.get("username", "?") or "?",
            f"[{cpu_color(cpu_p)}]{cpu_p:5.1f}[/{cpu_color(cpu_p)}]",
            f"[{mem_color(mem_p)}]{mem_p:5.2f}[/{mem_color(mem_p)}]",
            human_bytes(rss),
            str(proc.get("num_threads", "")),
            f"[{status_style}]{status}[/{status_style}]" if status_style else status,
        )

    return table


def show_process_details(pid: int) -> None:
    """Display detailed info about one process."""
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            info = {
                "PID": p.pid,
                "Name": p.name(),
                "Status": p.status(),
                "User": p.username(),
                "CPU %": f"{p.cpu_percent(interval=0.1):.2f}",
                "MEM %": f"{p.memory_percent():.2f}",
                "RSS": human_bytes(p.memory_info().rss),
                "VMS": human_bytes(p.memory_info().vms),
                "Threads": p.num_threads(),
                "Open Files": len(p.open_files()) if hasattr(p, "open_files") else "N/A",
                "Created": time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(p.create_time())),
                "CWD": p.cwd() if hasattr(p, "cwd") else "N/A",
                "Exe": p.exe() if hasattr(p, "exe") else "N/A",
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        console.print(f"[red]Error: {e}[/red]")
        return

    table = Table(box=box.SIMPLE_HEAVY, show_header=False, expand=False,
                  border_style="blue", padding=(0, 2))
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")
    for k, v in info.items():
        table.add_row(k, str(v))

    console.print(Panel(table, title=f"🔍  Process Detail — PID {pid}",
                        border_style="cyan"))


def kill_by_pid(pid: int) -> None:
    try:
        p = psutil.Process(pid)
        name = p.name()
        if Confirm.ask(f"[red]Kill process [bold]{name}[/bold] (PID {pid})?[/red]"):
            p.terminate()
            console.print(f"[bold green]✓ Sent SIGTERM to {name} (PID {pid})[/bold green]")
    except psutil.NoSuchProcess:
        console.print(f"[red]No process with PID {pid}[/red]")
    except psutil.AccessDenied:
        console.print(f"[red]Access denied — try running as administrator[/red]")


def kill_by_name(name: str) -> None:
    killed = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if name.lower() in p.info["name"].lower():
                killed.append((p.info["pid"], p.info["name"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not killed:
        console.print(f"[red]No processes found matching '{name}'[/red]")
        return

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("PID")
    table.add_column("Name")
    for pid, pname in killed:
        table.add_row(str(pid), pname)
    console.print(table)

    if Confirm.ask(f"[red]Kill all {len(killed)} listed processes?[/red]"):
        for pid, pname in killed:
            try:
                psutil.Process(pid).terminate()
                console.print(f"[green]  ✓ Killed {pname} (PID {pid})[/green]")
            except Exception as e:
                console.print(f"[red]  ✗ {pname} (PID {pid}): {e}[/red]")


# ── main menu ─────────────────────────────────────────────────────────────────

def interactive_menu(sort_by: str, search: str) -> None:
    """Main interactive loop."""
    console.print(Panel(
        "[bold cyan]Interactive Process Manager[/bold cyan]\n"
        "[dim]Commands: [bold]r[/bold]=refresh  [bold]s[/bold]=sort  "
        "[bold]f[/bold]=filter  [bold]k[/bold]=kill  "
        "[bold]d[/bold]=details  [bold]q[/bold]=quit[/dim]",
        border_style="blue",
    ))

    # Prime CPU percentages
    psutil.cpu_percent()
    for p in psutil.process_iter(["cpu_percent"]):
        pass
    time.sleep(0.5)

    while True:
        procs = get_processes(sort_by, search)
        console.print(build_table(procs, sort_by, search))
        console.print(f"\n[dim]Showing top 50 of {len(procs)} processes[/dim]")

        cmd = Prompt.ask(
            "\n[bold cyan]Command[/bold cyan]",
            choices=["r", "s", "f", "k", "d", "q"],
            default="r",
        )

        if cmd == "q":
            console.print("[yellow]Goodbye![/yellow]")
            break
        elif cmd == "r":
            console.clear()
        elif cmd == "s":
            sort_by = Prompt.ask("Sort by", choices=["cpu", "ram"], default=sort_by)
            console.clear()
        elif cmd == "f":
            search = Prompt.ask("Filter by name (leave empty to clear)", default="")
            console.clear()
        elif cmd == "k":
            target = Prompt.ask("Enter PID or process name to kill")
            if target.isdigit():
                kill_by_pid(int(target))
            else:
                kill_by_name(target)
        elif cmd == "d":
            pid_str = Prompt.ask("Enter PID to inspect")
            if pid_str.isdigit():
                show_process_details(int(pid_str))
            else:
                console.print("[red]Invalid PID[/red]")


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Interactive Process Manager")
    parser.add_argument("--sort", choices=["cpu", "ram"], default="cpu",
                        help="Initial sort order (default: cpu)")
    parser.add_argument("--search", default="",
                        help="Filter processes by name substring")
    args = parser.parse_args()
    interactive_menu(args.sort, args.search)


if __name__ == "__main__":
    main()
