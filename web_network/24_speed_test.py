"""
Tool 24 - Internet Speed Test
==============================
Tests your internet connection speed using the Speedtest.net infrastructure.
Features:
- Download and upload speed measurement
- Ping / latency test
- Server selection (auto or manual)
- Results history stored locally
- Animated progress bars during testing

Usage:
    python 24_speed_test.py
    python 24_speed_test.py --server-id 1234
    python 24_speed_test.py --list-servers
    python 24_speed_test.py --history

Dependencies:
    pip install speedtest-cli rich
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TransferSpeedColumn,
)
from rich.table import Table
from rich.text import Text

console = Console()

HISTORY_FILE = Path.home() / ".speed_test_history.json"


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_result(result: dict):
    history = load_history()
    history.append(result)
    history = history[-50:]  # keep last 50
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2))
    except OSError:
        pass


def bps_to_mbps(bps: float) -> float:
    return bps / 1_000_000


def speed_bar(mbps: float, max_mbps: float = 1000) -> str:
    """Create a visual bar representing speed."""
    pct = min(mbps / max_mbps, 1.0)
    filled = int(pct * 30)
    bar = "█" * filled + "░" * (30 - filled)
    if pct < 0.1:
        color = "red"
    elif pct < 0.3:
        color = "yellow"
    elif pct < 0.7:
        color = "green"
    else:
        color = "bold cyan"
    return f"[{color}]{bar}[/]"


def speed_label(mbps: float) -> str:
    """Classify connection speed."""
    if mbps < 1:
        return "[red]Very Slow[/]"
    elif mbps < 5:
        return "[yellow]Slow[/]"
    elif mbps < 25:
        return "[yellow]Fair[/]"
    elif mbps < 100:
        return "[green]Good[/]"
    elif mbps < 500:
        return "[bold green]Fast[/]"
    else:
        return "[bold cyan]Ultra Fast[/]"


def run_speed_test(server_id: int | None = None) -> dict:
    """Run the speed test and return results."""
    try:
        import speedtest
    except ImportError:
        console.print("[bold red]✗ speedtest-cli not installed.[/]")
        console.print("  Run: [cyan]pip install speedtest-cli[/]")
        sys.exit(1)

    console.rule("[bold cyan]⚡ Internet Speed Test[/]")

    st = speedtest.Speedtest(secure=True)

    # Find best server
    with console.status("[bold cyan]🔍 Finding best server…[/]", spinner="dots"):
        try:
            if server_id:
                st.get_servers([server_id])
                st.get_best_server()
            else:
                st.get_best_server()
        except Exception as e:
            console.print(f"[bold red]✗ Server error:[/] {e}")
            sys.exit(1)

    server = st.results.server
    server_info = (
        f"[bold]{server.get('sponsor', 'Unknown')}[/] — "
        f"{server.get('name', '?')}, {server.get('country', '?')}  "
        f"[dim](ID: {server.get('id', '?')})[/]"
    )
    console.print(Panel(server_info, title="🖥  Server", border_style="blue"))
    console.print()

    results = {}

    # Ping
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Measuring ping…", total=None)
        ping = st.results.ping
        results["ping"] = ping
        progress.update(task, description=f"Ping: {ping:.1f} ms")
        time.sleep(0.5)

    ping_color = "green" if ping < 20 else ("yellow" if ping < 80 else "red")
    console.print(f"  📡 [bold]Ping:[/]     [{ping_color}]{ping:.1f} ms[/]")

    # Download
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("⬇  Measuring download speed…", total=100)
        # Simulate progress while actual test runs
        for i in range(0, 80, 10):
            progress.update(task, completed=i)
            time.sleep(0.1)
        download_bps = st.download()
        progress.update(task, completed=100, description="⬇  Download complete!")
        time.sleep(0.3)

    download_mbps = bps_to_mbps(download_bps)
    results["download_mbps"] = download_mbps
    console.print(
        f"  ⬇  [bold]Download:[/]  [bold green]{download_mbps:.2f} Mbps[/]  "
        f"{speed_bar(download_mbps)}  {speed_label(download_mbps)}"
    )

    # Upload
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold yellow]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("⬆  Measuring upload speed…", total=100)
        for i in range(0, 80, 10):
            progress.update(task, completed=i)
            time.sleep(0.12)
        upload_bps = st.upload()
        progress.update(task, completed=100, description="⬆  Upload complete!")
        time.sleep(0.3)

    upload_mbps = bps_to_mbps(upload_bps)
    results["upload_mbps"] = upload_mbps
    console.print(
        f"  ⬆  [bold]Upload:[/]    [bold yellow]{upload_mbps:.2f} Mbps[/]  "
        f"{speed_bar(upload_mbps)}  {speed_label(upload_mbps)}"
    )

    results.update({
        "timestamp": datetime.now().isoformat(),
        "server_name": server.get("sponsor", "?"),
        "server_location": f"{server.get('name', '?')}, {server.get('country', '?')}",
        "server_id": server.get("id"),
    })

    return results


def display_summary(results: dict):
    """Display final results panel."""
    console.print()
    lines = [
        f"  ⬇  Download:  [bold green]{results['download_mbps']:.2f} Mbps[/]",
        f"  ⬆  Upload:    [bold yellow]{results['upload_mbps']:.2f} Mbps[/]",
        f"  📡 Ping:      [bold cyan]{results['ping']:.1f} ms[/]",
        f"",
        f"  🖥  Server:    {results['server_name']} — {results['server_location']}",
        f"  🕒 Tested:    {results['timestamp'][:19].replace('T', ' ')}",
    ]
    console.print(Panel("\n".join(lines), title="[bold cyan]📊 Speed Test Results", border_style="cyan"))


def display_history():
    """Display past speed test results."""
    history = load_history()
    if not history:
        console.print("[yellow]No speed test history found.[/]")
        return

    table = Table(
        title="📈 Speed Test History",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=False
    )
    table.add_column("Date / Time", style="dim")
    table.add_column("⬇ Download", style="bold green", justify="right")
    table.add_column("⬆ Upload", style="bold yellow", justify="right")
    table.add_column("📡 Ping", style="bold cyan", justify="right")
    table.add_column("Server")

    for r in reversed(history[-20:]):
        table.add_row(
            r.get("timestamp", "?")[:19].replace("T", " "),
            f"{r.get('download_mbps', 0):.2f} Mbps",
            f"{r.get('upload_mbps', 0):.2f} Mbps",
            f"{r.get('ping', 0):.1f} ms",
            r.get("server_name", "?"),
        )

    console.print(table)


def list_servers():
    """List nearby speed test servers."""
    try:
        import speedtest
    except ImportError:
        console.print("[bold red]✗ speedtest-cli not installed.[/]")
        sys.exit(1)

    console.rule("[bold cyan]🌐 Available Speed Test Servers[/]")
    with console.status("Finding nearby servers…", spinner="dots"):
        st = speedtest.Speedtest(secure=True)
        st.get_servers()
        servers = st.get_best_server()
        nearby = list(st.servers.values())[:5]
        # Flatten list of lists
        flat = [s for sublist in nearby for s in (sublist if isinstance(sublist, list) else [sublist])]

    table = Table(box=box.ROUNDED, border_style="blue")
    table.add_column("ID", style="dim")
    table.add_column("Sponsor", style="bold")
    table.add_column("City")
    table.add_column("Country")
    table.add_column("Latency", justify="right")

    for s in flat[:15]:
        table.add_row(
            str(s.get("id", "?")),
            s.get("sponsor", "?"),
            s.get("name", "?"),
            s.get("country", "?"),
            f"{s.get('latency', 0):.1f} ms",
        )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Internet speed test — measure download, upload, and ping."
    )
    parser.add_argument("--list-servers", "-l", action="store_true",
                        help="List nearby speed test servers")
    parser.add_argument("--server-id", "-s", type=int, metavar="ID",
                        help="Use a specific server ID")
    parser.add_argument("--history", "-H", action="store_true",
                        help="Show past speed test results")
    args = parser.parse_args()

    if args.history:
        console.rule("[bold cyan]⚡ Speed Test History[/]")
        display_history()
        return

    if args.list_servers:
        list_servers()
        return

    results = run_speed_test(server_id=args.server_id)
    display_summary(results)
    save_result(results)
    console.print(f"\n[dim]History saved to {HISTORY_FILE}[/]")


if __name__ == "__main__":
    main()
