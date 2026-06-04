"""
41_system_monitor.py
─────────────────────────────────────────────────────────────────────────────
Real-Time System Monitor Dashboard
─────────────────────────────────────────────────────────────────────────────
Displays a live, auto-refreshing dashboard with:
  • CPU usage per-core + overall
  • RAM and swap memory usage
  • Disk I/O and disk space per partition
  • Network I/O (sent/received bytes/s)
  • Top 10 processes sorted by CPU or RAM

Usage:
    python 41_system_monitor.py
    python 41_system_monitor.py --sort ram
    python 41_system_monitor.py --interval 3
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import time
from datetime import datetime

import psutil
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()

# ── helpers ──────────────────────────────────────────────────────────────────

def human_bytes(n: float) -> str:
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:6.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def cpu_color(pct: float) -> str:
    if pct >= 85:
        return "bold red"
    if pct >= 60:
        return "yellow"
    return "green"


def mem_color(pct: float) -> str:
    if pct >= 85:
        return "bold red"
    if pct >= 65:
        return "yellow"
    return "cyan"


# ── section builders ─────────────────────────────────────────────────────────

def build_cpu_panel() -> Panel:
    """Per-core + total CPU usage bars."""
    progress = Progress(
        TextColumn("{task.description}", style="bold"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
        expand=False,
    )
    per_cpu = psutil.cpu_percent(percpu=True)
    overall = psutil.cpu_percent()
    freq = psutil.cpu_freq()

    with progress:
        for i, pct in enumerate(per_cpu):
            progress.add_task(f"Core {i:<2}", total=100, completed=pct,
                              style=cpu_color(pct))
        progress.add_task("Overall", total=100, completed=overall,
                          style=cpu_color(overall))

    freq_str = f"{freq.current:.0f} MHz" if freq else "N/A"
    header = Text(f"🖥  CPU  — {psutil.cpu_count(logical=True)} logical cores  |  {freq_str}", style="bold white")
    return Panel(progress, title=header, border_style="blue", padding=(0, 1))


def build_memory_panel() -> Panel:
    """RAM and Swap usage bars."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()

    progress = Progress(
        TextColumn("{task.description}", style="bold"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>5.1f}%"),
        TextColumn("{task.fields[used]}", style="dim"),
        expand=False,
    )
    with progress:
        progress.add_task(
            "RAM ", total=100, completed=vm.percent,
            used=f"{human_bytes(vm.used)} / {human_bytes(vm.total)}",
            style=mem_color(vm.percent),
        )
        progress.add_task(
            "Swap", total=100, completed=sw.percent,
            used=f"{human_bytes(sw.used)} / {human_bytes(sw.total)}",
            style=mem_color(sw.percent),
        )
    return Panel(progress, title="💾  Memory", border_style="magenta", padding=(0, 1))


def build_disk_panel() -> Panel:
    """Disk space per partition + I/O counters."""
    table = Table(show_header=True, header_style="bold white", box=box.SIMPLE_HEAVY,
                  expand=True, padding=(0, 1))
    table.add_column("Mount", style="cyan", no_wrap=True)
    table.add_column("FS", style="dim")
    table.add_column("Total", justify="right")
    table.add_column("Used", justify="right")
    table.add_column("Free", justify="right")
    table.add_column("Usage", justify="right")

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        pct = usage.percent
        color = "red" if pct > 85 else "yellow" if pct > 65 else "green"
        bar_filled = int(pct / 5)
        bar = f"[{color}]{'█' * bar_filled}{'░' * (20 - bar_filled)}[/{color}] {pct:4.1f}%"
        table.add_row(
            part.mountpoint, part.fstype,
            human_bytes(usage.total),
            human_bytes(usage.used),
            human_bytes(usage.free),
            bar,
        )

    try:
        io = psutil.disk_io_counters()
        if io:
            io_text = (f"  Read: {human_bytes(io.read_bytes)}  "
                       f"Write: {human_bytes(io.write_bytes)}")
            table.caption = io_text
    except Exception:
        pass

    return Panel(table, title="💿  Disk", border_style="yellow", padding=(0, 1))


_prev_net: dict = {}

def build_network_panel() -> Panel:
    """Network I/O rates."""
    global _prev_net
    global _prev_time

    now = time.time()
    counters = psutil.net_io_counters(pernic=True)

    table = Table(show_header=True, header_style="bold white", box=box.SIMPLE_HEAVY,
                  expand=True, padding=(0, 1))
    table.add_column("Interface", style="cyan")
    table.add_column("↑ Sent", justify="right", style="green")
    table.add_column("↓ Recv", justify="right", style="blue")
    table.add_column("↑ Speed", justify="right", style="bold green")
    table.add_column("↓ Speed", justify="right", style="bold blue")

    elapsed = now - _prev_time if _prev_net else 1.0

    for nic, stats in counters.items():
        prev = _prev_net.get(nic)
        if prev:
            s_rate = (stats.bytes_sent - prev.bytes_sent) / elapsed
            r_rate = (stats.bytes_recv - prev.bytes_recv) / elapsed
        else:
            s_rate = r_rate = 0.0
        table.add_row(
            nic,
            human_bytes(stats.bytes_sent),
            human_bytes(stats.bytes_recv),
            f"{human_bytes(s_rate)}/s",
            f"{human_bytes(r_rate)}/s",
        )

    _prev_net = counters
    _prev_time = now
    return Panel(table, title="🌐  Network", border_style="green", padding=(0, 1))


def build_process_panel(sort_by: str = "cpu") -> Panel:
    """Top 10 processes by CPU or RAM."""
    attrs = ["pid", "name", "cpu_percent", "memory_percent", "status", "num_threads"]
    procs = []
    for p in psutil.process_iter(attrs):
        try:
            info = p.info
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    procs.sort(key=lambda x: x.get(key) or 0, reverse=True)

    table = Table(show_header=True, header_style="bold white", box=box.SIMPLE_HEAVY,
                  expand=True, padding=(0, 1))
    table.add_column("PID", style="dim", width=7)
    table.add_column("Name", style="cyan", no_wrap=True, max_width=28)
    table.add_column("CPU %", justify="right")
    table.add_column("MEM %", justify="right")
    table.add_column("Threads", justify="right")
    table.add_column("Status", style="dim")

    for proc in procs[:10]:
        cpu_p = proc.get("cpu_percent") or 0.0
        mem_p = proc.get("memory_percent") or 0.0
        table.add_row(
            str(proc.get("pid", "")),
            proc.get("name", "?"),
            f"[{cpu_color(cpu_p)}]{cpu_p:5.1f}[/{cpu_color(cpu_p)}]",
            f"[{mem_color(mem_p)}]{mem_p:5.1f}[/{mem_color(mem_p)}]",
            str(proc.get("num_threads", "")),
            proc.get("status", ""),
        )

    sort_label = "CPU" if sort_by == "cpu" else "RAM"
    return Panel(table, title=f"⚙  Top Processes (sorted by {sort_label})",
                 border_style="red", padding=(0, 1))


def build_header() -> Panel:
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    boot = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
    uptime_secs = int(time.time() - psutil.boot_time())
    h, r = divmod(uptime_secs, 3600)
    m, s = divmod(r, 60)
    uptime = f"{h}h {m}m {s}s"
    text = Text.assemble(
        ("⚡  System Monitor  ", "bold white"),
        (f"│  {now}  ", "bold cyan"),
        ("│  Boot: ", "dim"),
        (boot, "dim white"),
        ("  │  Uptime: ", "dim"),
        (uptime, "bold green"),
    )
    return Panel(text, border_style="white", padding=(0, 2))


# ── main ──────────────────────────────────────────────────────────────────────

def build_dashboard(sort_by: str) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(build_header(), name="header", size=3),
        Layout(name="body"),
    )
    layout["body"].split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=2),
    )
    layout["left"].split_column(
        Layout(build_cpu_panel(), name="cpu"),
        Layout(build_memory_panel(), name="memory"),
    )
    layout["right"].split_column(
        Layout(name="top_right"),
        Layout(build_process_panel(sort_by), name="procs"),
    )
    layout["right"]["top_right"].split_row(
        Layout(build_disk_panel(), name="disk"),
        Layout(build_network_panel(), name="net"),
    )
    return layout


def main():
    parser = argparse.ArgumentParser(description="Real-time System Monitor Dashboard")
    parser.add_argument("--sort", choices=["cpu", "ram"], default="cpu",
                        help="Sort processes by cpu or ram (default: cpu)")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="Refresh interval in seconds (default: 2)")
    args = parser.parse_args()

    global _prev_time
    _prev_time = time.time()

    # Prime cpu_percent (first call always returns 0)
    psutil.cpu_percent(percpu=True)
    psutil.cpu_percent()

    console.print(Panel(
        "[bold cyan]Real-Time System Monitor[/bold cyan]\n"
        "[dim]Press Ctrl+C to exit[/dim]",
        border_style="blue"
    ))
    time.sleep(0.5)

    try:
        with Live(build_dashboard(args.sort), refresh_per_second=1,
                  console=console, screen=True) as live:
            while True:
                time.sleep(args.interval)
                live.update(build_dashboard(args.sort))
    except KeyboardInterrupt:
        console.print("\n[bold yellow]System Monitor stopped.[/bold yellow]")


if __name__ == "__main__":
    main()
