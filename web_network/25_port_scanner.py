"""
Tool 25 - TCP Port Scanner
===========================
A fast, threaded TCP port scanner that:
- Scans common ports or a custom range
- Identifies services by port number
- Shows open/closed/filtered status
- Performs banner grabbing on open ports
- Supports scanning multiple hosts

Usage:
    python 25_port_scanner.py
    python 25_port_scanner.py --host scanme.nmap.org --range 1-1024
    python 25_port_scanner.py --host 192.168.1.1 --ports 22,80,443,8080
    python 25_port_scanner.py --host example.com --common

Dependencies:
    pip install rich
"""

import argparse
import socket
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

# Common ports and their services
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 119, 123, 135, 139, 143, 161, 194,
    389, 443, 445, 465, 514, 515, 587, 631, 993, 995, 1080, 1194, 1433,
    1723, 2049, 2082, 2083, 2086, 2087, 2095, 2096, 3306, 3389, 4444,
    5432, 5900, 5901, 6379, 6881, 8080, 8443, 8888, 9200, 27017,
]

WELL_KNOWN_SERVICES = {
    20: "FTP (data)",
    21: "FTP (control)",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP Server",
    68: "DHCP Client",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    111: "RPCbind",
    119: "NNTP",
    123: "NTP",
    135: "MS RPC",
    137: "NetBIOS NS",
    138: "NetBIOS DGM",
    139: "NetBIOS Session",
    143: "IMAP",
    161: "SNMP",
    194: "IRC",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    500: "IKE/IPSec",
    514: "Syslog",
    515: "LPD/LPR",
    587: "SMTP (submission)",
    631: "IPP/CUPS",
    993: "IMAPS",
    995: "POP3S",
    1080: "SOCKS Proxy",
    1194: "OpenVPN",
    1433: "MSSQL",
    1723: "PPTP",
    2049: "NFS",
    2082: "cPanel",
    2083: "cPanel SSL",
    2086: "WHM",
    2087: "WHM SSL",
    3306: "MySQL",
    3389: "RDP",
    4444: "Metasploit",
    5432: "PostgreSQL",
    5900: "VNC",
    5901: "VNC #1",
    6379: "Redis",
    6881: "BitTorrent",
    8080: "HTTP Alt",
    8443: "HTTPS Alt",
    8888: "HTTP Alt",
    9200: "Elasticsearch",
    27017: "MongoDB",
}


def get_service_name(port: int) -> str:
    """Return service name for a port number."""
    if port in WELL_KNOWN_SERVICES:
        return WELL_KNOWN_SERVICES[port]
    try:
        return socket.getservbyport(port)
    except (OSError, OverflowError):
        return "Unknown"


def grab_banner(host: str, port: int, timeout: float = 1.5) -> str:
    """Attempt to grab a service banner."""
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            try:
                # For HTTP, send a minimal request
                if port in (80, 8080, 8888):
                    sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                elif port in (443, 8443):
                    return "SSL/TLS"
                banner = sock.recv(256).decode("utf-8", errors="replace").strip()
                banner = banner.replace("\r\n", " ").replace("\n", " ")
                return banner[:60] if banner else ""
            except socket.timeout:
                return ""
    except Exception:
        return ""


def scan_port(host: str, port: int, timeout: float, grab: bool) -> dict:
    """Scan a single TCP port."""
    result = {"port": port, "open": False, "service": get_service_name(port), "banner": ""}
    try:
        with socket.create_connection((host, port), timeout=timeout):
            result["open"] = True
            if grab:
                result["banner"] = grab_banner(host, port, timeout)
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    return result


def resolve_host(host: str) -> str:
    """Resolve hostname to IP address."""
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.gaierror:
        console.print(f"[bold red]✗ Cannot resolve hostname:[/] {host}")
        sys.exit(1)


def scan_ports(
    host: str,
    ports: list[int],
    timeout: float,
    workers: int,
    grab_banners: bool,
) -> list[dict]:
    """Scan all ports using thread pool."""
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Scanning {len(ports)} ports…", total=len(ports))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(scan_port, host, p, timeout, grab_banners): p
                for p in ports
            }
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                progress.advance(task)

    return sorted(results, key=lambda x: x["port"])


def display_results(host: str, ip: str, results: list[dict], start_time: datetime):
    """Display scan results in a rich table."""
    open_ports = [r for r in results if r["open"]]
    closed_count = len(results) - len(open_ports)
    elapsed = (datetime.now() - start_time).total_seconds()

    # Overview panel
    overview = (
        f"[bold]Target:[/]       {host}  ([cyan]{ip}[/])\n"
        f"[bold]Ports Scanned:[/] {len(results)}\n"
        f"[bold]Open:[/]         [bold green]{len(open_ports)}[/]\n"
        f"[bold]Closed:[/]       [dim]{closed_count}[/]\n"
        f"[bold]Duration:[/]     {elapsed:.2f}s"
    )
    console.print(Panel(overview, title="[bold cyan]🔍 Scan Summary", border_style="cyan"))
    console.print()

    if not open_ports:
        console.print(Panel(
            "[dim]No open ports found in the scanned range.[/]",
            title="Results",
            border_style="yellow"
        ))
        return

    table = Table(
        title=f"🔓 Open Ports on {host}",
        box=box.ROUNDED,
        border_style="green",
        show_lines=False,
    )
    table.add_column("Port", style="bold cyan", justify="right", width=8)
    table.add_column("State", width=8)
    table.add_column("Service", style="bold", width=18)
    table.add_column("Banner / Info", style="dim", max_width=60)

    for r in open_ports:
        table.add_row(
            str(r["port"]),
            "[bold green]OPEN[/]",
            r["service"],
            r["banner"] or "[dim]—[/]",
        )

    console.print(table)


def parse_ports(ports_str: str) -> list[int]:
    """Parse port specification like '80,443' or '1-1024'."""
    ports = []
    for part in ports_str.split(","):
        part = part.strip()
        if "-" in part:
            start, _, end = part.partition("-")
            try:
                ports.extend(range(int(start), int(end) + 1))
            except ValueError:
                console.print(f"[yellow]⚠ Invalid port range: {part}[/]")
        else:
            try:
                ports.append(int(part))
            except ValueError:
                console.print(f"[yellow]⚠ Invalid port: {part}[/]")
    return sorted(set(p for p in ports if 1 <= p <= 65535))


def main():
    parser = argparse.ArgumentParser(
        description="TCP Port Scanner — scan a host for open ports."
    )
    parser.add_argument("--host", "-H", help="Target host or IP address")
    parser.add_argument("--range", "-r", metavar="START-END", help="Port range, e.g. 1-1024")
    parser.add_argument("--ports", "-p", metavar="PORTS", help="Comma-separated port list, e.g. 22,80,443")
    parser.add_argument("--common", "-c", action="store_true", help="Scan common ports (default behavior)")
    parser.add_argument("--timeout", "-t", type=float, default=0.5, help="Timeout per port (default: 0.5s)")
    parser.add_argument("--workers", "-w", type=int, default=200, help="Number of threads (default: 200)")
    parser.add_argument("--banners", "-b", action="store_true", help="Grab service banners (slower)")
    args = parser.parse_args()

    console.rule("[bold cyan]🔍 TCP Port Scanner[/]")

    host = args.host
    if not host:
        host = Prompt.ask("[bold]Target host or IP[/]", default="scanme.nmap.org")

    ip = resolve_host(host)
    if ip != host:
        console.print(f"[dim]Resolved [bold]{host}[/] → [cyan]{ip}[/][/]")

    # Determine ports to scan
    if args.ports:
        ports = parse_ports(args.ports)
    elif args.range:
        ports = parse_ports(args.range)
    else:
        ports = COMMON_PORTS
        console.print(f"[dim]Scanning {len(ports)} common ports…[/]")

    if not ports:
        console.print("[bold red]✗ No valid ports to scan.[/]")
        sys.exit(1)

    console.print(
        f"[bold]Host:[/] [cyan]{host}[/]  |  "
        f"[bold]Ports:[/] {len(ports)}  |  "
        f"[bold]Timeout:[/] {args.timeout}s  |  "
        f"[bold]Threads:[/] {args.workers}"
    )
    console.print()

    start_time = datetime.now()
    results = scan_ports(host, ports, args.timeout, args.workers, args.banners)
    display_results(host, ip, results, start_time)


if __name__ == "__main__":
    main()
