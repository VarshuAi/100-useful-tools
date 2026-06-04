"""
Tool 31 - Network Ping Sweep
==============================
Sweeps a range of IP addresses to discover live hosts on a network:
- Accepts CIDR notation (192.168.1.0/24) or range format (192.168.1.1-254)
- Uses ICMP ping via subprocess or TCP probe as fallback
- Parallel scanning with threading for speed
- Shows hostname resolution for live hosts
- Displays alive/dead summary with timing
- Export results to CSV

Usage:
    python 31_ping_sweep.py
    python 31_ping_sweep.py --range 192.168.1.1-254
    python 31_ping_sweep.py --cidr 192.168.1.0/24
    python 31_ping_sweep.py --range 10.0.0.1-50 --output results.csv

Dependencies:
    pip install rich
"""

import argparse
import csv
import ipaddress
import platform
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

console = Console()

IS_WINDOWS = platform.system() == "Windows"


def ping(ip: str, timeout: int = 1) -> tuple[bool, float]:
    """Ping an IP address and return (alive, response_time_ms)."""
    start = datetime.now()
    try:
        if IS_WINDOWS:
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
            result = subprocess.run(
                cmd, capture_output=True, timeout=timeout + 2, text=True
            )
            alive = result.returncode == 0
        else:
            cmd = ["ping", "-c", "1", "-W", str(timeout), ip]
            result = subprocess.run(
                cmd, capture_output=True, timeout=timeout + 2, text=True
            )
            alive = result.returncode == 0

        elapsed = (datetime.now() - start).total_seconds() * 1000
        return alive, elapsed if alive else 0.0
    except subprocess.TimeoutExpired:
        return False, 0.0
    except Exception:
        # Fallback: try TCP connect to port 80
        return tcp_probe(ip, timeout)


def tcp_probe(ip: str, timeout: int = 1) -> tuple[bool, float]:
    """Try TCP connection as fallback for hosts that block ICMP."""
    start = datetime.now()
    for port in (80, 443, 22, 8080):
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                elapsed = (datetime.now() - start).total_seconds() * 1000
                return True, elapsed
        except (socket.timeout, ConnectionRefusedError):
            # Port unreachable but host might still be up
            # ConnectionRefused means host IS up
            elapsed = (datetime.now() - start).total_seconds() * 1000
            if "ConnectionRefused" in type(Exception).__name__:
                return True, elapsed
        except OSError:
            pass
    return False, 0.0


def resolve_hostname(ip: str) -> str:
    """Attempt reverse DNS lookup."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return ""


def parse_ip_range(range_str: str) -> list[str]:
    """Parse an IP range like '192.168.1.1-254'."""
    if "-" in range_str:
        base, _, end_part = range_str.rpartition("-")
        # base is like '192.168.1.1', end_part is like '254'
        prefix = ".".join(base.split(".")[:-1])
        start_octet = int(base.split(".")[-1])
        end_octet = int(end_part)
        if start_octet > end_octet or end_octet > 255:
            raise ValueError(f"Invalid range: {range_str}")
        return [f"{prefix}.{i}" for i in range(start_octet, end_octet + 1)]
    return [range_str]


def parse_cidr(cidr: str) -> list[str]:
    """Parse CIDR notation into list of host IPs."""
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        # Only return host addresses (skip network and broadcast)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        console.print(f"[bold red]✗ Invalid CIDR:[/] {e}")
        sys.exit(1)


def scan_host(ip: str, timeout: int, resolve: bool) -> dict:
    """Scan a single host."""
    alive, rtt = ping(ip, timeout)
    hostname = ""
    if alive and resolve:
        hostname = resolve_hostname(ip)
    return {"ip": ip, "alive": alive, "rtt_ms": rtt, "hostname": hostname}


def sweep(
    ips: list[str],
    timeout: int,
    workers: int,
    resolve: bool,
) -> list[dict]:
    """Sweep all IPs in the list."""
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TextColumn("[dim]{task.completed}/{task.total}[/]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Sweeping {len(ips)} hosts…", total=len(ips))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(scan_host, ip, timeout, resolve): ip for ip in ips
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                progress.advance(task)

    # Sort by IP
    def ip_sort_key(r):
        try:
            return ipaddress.ip_address(r["ip"])
        except ValueError:
            return ipaddress.ip_address("0.0.0.0")

    return sorted(results, key=ip_sort_key)


def display_results(results: list[dict], start_time: datetime, range_str: str):
    """Display sweep results."""
    alive_hosts = [r for r in results if r["alive"]]
    dead_count = len(results) - len(alive_hosts)
    elapsed = (datetime.now() - start_time).total_seconds()

    # Summary
    console.print(Panel(
        f"[bold]Range:[/]       {range_str}\n"
        f"[bold]Hosts Scanned:[/] {len(results)}\n"
        f"[bold]Alive:[/]       [bold green]{len(alive_hosts)}[/]\n"
        f"[bold]No Response:[/] [dim]{dead_count}[/]\n"
        f"[bold]Duration:[/]    {elapsed:.2f}s  "
        f"({len(results)/elapsed:.0f} hosts/sec)",
        title="[bold cyan]📡 Ping Sweep Summary",
        border_style="cyan"
    ))
    console.print()

    if not alive_hosts:
        console.print("[yellow]No live hosts found in the scanned range.[/]")
        return

    table = Table(
        title=f"✅ Live Hosts ({len(alive_hosts)} found)",
        box=box.ROUNDED,
        border_style="green",
        show_lines=False,
    )
    table.add_column("#", style="dim", width=5)
    table.add_column("IP Address", style="bold cyan", width=18)
    table.add_column("RTT", style="green", justify="right", width=10)
    table.add_column("Hostname", style="dim")

    for i, host in enumerate(alive_hosts, 1):
        rtt = f"{host['rtt_ms']:.1f} ms" if host["rtt_ms"] > 0 else "—"
        table.add_row(
            str(i),
            host["ip"],
            rtt,
            host["hostname"] or "[dim]—[/]",
        )

    console.print(table)


def save_csv(results: list[dict], path: str):
    """Save results to CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "alive", "rtt_ms", "hostname"])
        writer.writeheader()
        writer.writerows(results)
    console.print(f"\n[bold green]💾 Results saved to:[/] {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Network ping sweep — discover live hosts in an IP range."
    )
    parser.add_argument("--range", "-r", metavar="IP_RANGE",
                        help="IP range, e.g. 192.168.1.1-254")
    parser.add_argument("--cidr", "-c", metavar="CIDR",
                        help="CIDR notation, e.g. 192.168.1.0/24")
    parser.add_argument("--timeout", "-t", type=int, default=1,
                        help="Ping timeout in seconds (default: 1)")
    parser.add_argument("--workers", "-w", type=int, default=100,
                        help="Parallel workers (default: 100)")
    parser.add_argument("--no-resolve", action="store_true",
                        help="Skip reverse DNS lookup (faster)")
    parser.add_argument("--output", "-o", metavar="FILE",
                        help="Save results to CSV file")
    args = parser.parse_args()

    console.rule("[bold cyan]📡 Network Ping Sweep[/]")

    # Determine IP list
    ips = []
    range_str = ""

    if args.cidr:
        range_str = args.cidr
        ips = parse_cidr(args.cidr)
    elif args.range:
        range_str = args.range
        try:
            ips = parse_ip_range(args.range)
        except ValueError as e:
            console.print(f"[bold red]✗ {e}[/]")
            sys.exit(1)
    else:
        user_input = Prompt.ask(
            "[bold]Enter IP range or CIDR[/]",
            default="192.168.1.1-10"
        )
        range_str = user_input
        if "/" in user_input:
            ips = parse_cidr(user_input)
        else:
            try:
                ips = parse_ip_range(user_input)
            except ValueError as e:
                console.print(f"[bold red]✗ {e}[/]")
                sys.exit(1)

    if not ips:
        console.print("[bold red]✗ No IPs to scan.[/]")
        sys.exit(1)

    console.print(
        f"[bold]Range:[/] {range_str}  |  "
        f"[bold]Hosts:[/] {len(ips)}  |  "
        f"[bold]Timeout:[/] {args.timeout}s  |  "
        f"[bold]Workers:[/] {args.workers}\n"
    )

    start_time = datetime.now()
    results = sweep(ips, args.timeout, args.workers, not args.no_resolve)
    display_results(results, start_time, range_str)

    if args.output:
        save_csv(results, args.output)


if __name__ == "__main__":
    main()
