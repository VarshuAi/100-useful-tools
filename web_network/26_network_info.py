"""
Tool 26 - Network Information Dashboard
========================================
Displays a comprehensive network information dashboard including:
- All network interfaces with IP, MAC, netmask
- Default gateway
- Public IP address
- DNS servers
- Active connections summary
- Network statistics (bytes sent/received)

Usage:
    python 26_network_info.py
    python 26_network_info.py --refresh 5   (auto-refresh every N seconds)

Dependencies:
    pip install psutil rich requests
"""

import argparse
import socket
import sys
import time
from datetime import datetime

import requests

try:
    import psutil
except ImportError:
    psutil = None

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def get_public_ip() -> str:
    """Fetch public IP from an external service."""
    services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://ipecho.net/plain",
    ]
    for url in services:
        try:
            r = requests.get(url, timeout=5)
            ip = r.text.strip()
            if ip:
                return ip
        except Exception:
            continue
    return "Unavailable"


def get_dns_servers() -> list[str]:
    """Attempt to read DNS servers from system config."""
    servers = []

    # Windows: parse ipconfig /all output via socket fallback
    try:
        import subprocess
        out = subprocess.check_output(
            ["ipconfig", "/all"], text=True, timeout=5,
            stderr=subprocess.DEVNULL
        )
        for line in out.splitlines():
            line = line.strip()
            if "DNS Servers" in line or (servers and line and line[0].isdigit()):
                parts = line.split(":")
                ip_part = parts[-1].strip() if ":" in line else line.strip()
                if ip_part and ip_part[0].isdigit():
                    servers.append(ip_part)
    except Exception:
        pass

    # Linux / macOS fallback
    if not servers:
        try:
            with open("/etc/resolv.conf") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        servers.append(line.split()[1])
        except Exception:
            pass

    return servers or ["Unable to detect"]


def get_default_gateway() -> str:
    """Get the default gateway address."""
    try:
        if psutil:
            gateways = psutil.net_if_stats()
        # Try to connect to an external IP (doesn't actually connect)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            # Guess gateway from local IP
            parts = local_ip.rsplit(".", 1)
            return parts[0] + ".1"
    except Exception:
        return "Unknown"


def bytes_to_human(n: int) -> str:
    """Convert bytes to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def build_interfaces_table() -> Table:
    """Build a table of network interfaces."""
    table = Table(
        title="🌐 Network Interfaces",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("Interface", style="bold cyan", min_width=14)
    table.add_column("IPv4 Address", style="green")
    table.add_column("IPv6 Address", style="dim green")
    table.add_column("MAC Address", style="yellow")
    table.add_column("Netmask", style="dim")
    table.add_column("Status", justify="center")

    if not psutil:
        table.add_row("[red]psutil not installed[/]", "", "", "", "", "")
        return table

    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    for iface, addr_list in addrs.items():
        ipv4 = ipv6 = mac = netmask = ""
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                ipv4 = addr.address
                netmask = addr.netmask or ""
            elif addr.family == socket.AF_INET6:
                ipv6 = addr.address.split("%")[0]  # strip zone ID
            elif addr.family == psutil.AF_LINK:
                mac = addr.address

        stat = stats.get(iface)
        is_up = stat.isup if stat else False
        status = "[bold green]UP[/]" if is_up else "[red]DOWN[/]"

        if ipv4 or mac:  # only show interfaces that have addresses
            table.add_row(iface, ipv4, ipv6[:30] if ipv6 else "", mac, netmask, status)

    return table


def build_stats_table() -> Table:
    """Build network I/O statistics table."""
    table = Table(
        title="📊 Network I/O Statistics",
        box=box.ROUNDED,
        border_style="magenta",
    )
    table.add_column("Interface", style="bold")
    table.add_column("↓ Bytes Recv", style="green", justify="right")
    table.add_column("↑ Bytes Sent", style="yellow", justify="right")
    table.add_column("↓ Packets Recv", style="dim green", justify="right")
    table.add_column("↑ Packets Sent", style="dim yellow", justify="right")
    table.add_column("Errors", style="red", justify="right")

    if not psutil:
        return table

    io = psutil.net_io_counters(pernic=True)
    for iface, counters in io.items():
        errors = counters.errin + counters.errout
        table.add_row(
            iface,
            bytes_to_human(counters.bytes_recv),
            bytes_to_human(counters.bytes_sent),
            f"{counters.packets_recv:,}",
            f"{counters.packets_sent:,}",
            f"[red]{errors}[/]" if errors else "[dim]0[/]",
        )

    return table


def build_connections_summary() -> str:
    """Get a summary of active network connections."""
    if not psutil:
        return "psutil not available"

    try:
        conns = psutil.net_connections(kind="inet")
    except (psutil.AccessDenied, PermissionError):
        return "Permission denied (try running as admin)"

    states: dict[str, int] = {}
    for c in conns:
        state = c.status or "UNKNOWN"
        states[state] = states.get(state, 0) + 1

    parts = [f"Total: [bold]{len(conns)}[/]"]
    for state, count in sorted(states.items(), key=lambda x: -x[1]):
        color = "green" if state == "ESTABLISHED" else ("yellow" if state == "TIME_WAIT" else "dim")
        parts.append(f"[{color}]{state}[/]: {count}")

    return "  |  ".join(parts)


def build_dashboard() -> list:
    """Build all panels for the dashboard."""
    panels = []

    # Public IP + hostname + gateway
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = "Unknown"

    with console.status("[bold cyan]Fetching public IP…[/]", spinner="dots"):
        pub_ip = get_public_ip()

    gateway = get_default_gateway()
    dns = get_dns_servers()

    overview_lines = [
        f"[bold]Hostname:[/]    {hostname}",
        f"[bold]Local IP:[/]    [cyan]{local_ip}[/]",
        f"[bold]Public IP:[/]   [bold cyan]{pub_ip}[/]",
        f"[bold]Gateway:[/]     {gateway}",
        f"[bold]DNS Servers:[/] {', '.join(dns[:3])}",
        f"[bold]Timestamp:[/]   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    panels.append(Panel(
        "\n".join(overview_lines),
        title="[bold cyan]📡 Network Overview",
        border_style="cyan"
    ))

    # Connection summary
    conn_summary = build_connections_summary()
    panels.append(Panel(
        conn_summary,
        title="[bold magenta]🔌 Active Connections",
        border_style="magenta"
    ))

    return panels


def display_dashboard():
    """Render the full network dashboard."""
    console.rule("[bold cyan]🖥  Network Information Dashboard[/]")

    panels = build_dashboard()
    for p in panels:
        console.print(p)

    console.print()
    console.print(build_interfaces_table())
    console.print()
    console.print(build_stats_table())


def main():
    parser = argparse.ArgumentParser(
        description="Network information dashboard — IPs, interfaces, stats."
    )
    parser.add_argument("--refresh", "-r", type=int, metavar="SECONDS",
                        help="Auto-refresh interval in seconds")
    args = parser.parse_args()

    if not psutil:
        console.print("[bold yellow]⚠ psutil not installed. Some features may be limited.[/]")
        console.print("  Run: [cyan]pip install psutil[/]")

    if args.refresh:
        console.print(f"[dim]Auto-refreshing every {args.refresh}s. Press Ctrl+C to stop.[/]\n")
        try:
            while True:
                console.clear()
                display_dashboard()
                time.sleep(args.refresh)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Stopped.[/]")
    else:
        display_dashboard()


if __name__ == "__main__":
    main()
