"""
Tool 32 - DNS Lookup Tool
===========================
Resolves DNS records for any domain with support for all common record types:
- A (IPv4 addresses)
- AAAA (IPv6 addresses)
- MX (mail servers with priority)
- NS (name servers)
- TXT (text records, SPF, DKIM, etc.)
- CNAME (canonical names)
- SOA (start of authority)
- PTR (reverse DNS)
- SRV (service records)
- CAA (certification authority)
- Uses dnspython with socket fallback
- Supports custom DNS resolver (e.g., 8.8.8.8)

Usage:
    python 32_dns_lookup.py
    python 32_dns_lookup.py --domain google.com
    python 32_dns_lookup.py --domain google.com --type MX
    python 32_dns_lookup.py --domain google.com --all
    python 32_dns_lookup.py --ip 8.8.8.8  (reverse lookup)
    python 32_dns_lookup.py --domain example.com --resolver 1.1.1.1

Dependencies:
    pip install dnspython rich
"""

import argparse
import socket
import sys
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV", "CAA", "PTR"]

RECORD_DESCRIPTIONS = {
    "A": "IPv4 address records",
    "AAAA": "IPv6 address records",
    "MX": "Mail exchange servers",
    "NS": "Name servers",
    "TXT": "Text records (SPF, DKIM, verification)",
    "CNAME": "Canonical name (alias)",
    "SOA": "Start of authority",
    "SRV": "Service location records",
    "CAA": "Certificate authority authorization",
    "PTR": "Reverse DNS lookup",
}


def resolve_with_dnspython(domain: str, record_type: str, resolver_ip: str | None) -> list[dict]:
    """Resolve using dnspython."""
    import dns.resolver
    import dns.exception

    resolver = dns.resolver.Resolver()
    if resolver_ip:
        resolver.nameservers = [resolver_ip]

    records = []
    try:
        answers = resolver.resolve(domain, record_type)
        for rdata in answers:
            record = {"type": record_type, "raw": str(rdata), "ttl": answers.rrset.ttl}
            # Parse type-specific fields
            if record_type == "MX":
                record["priority"] = rdata.preference
                record["exchange"] = str(rdata.exchange).rstrip(".")
            elif record_type == "NS":
                record["nameserver"] = str(rdata.target).rstrip(".")
            elif record_type == "SOA":
                record["mname"] = str(rdata.mname).rstrip(".")
                record["rname"] = str(rdata.rname).rstrip(".")
                record["serial"] = rdata.serial
                record["refresh"] = rdata.refresh
                record["retry"] = rdata.retry
                record["expire"] = rdata.expire
                record["minimum"] = rdata.minimum
            elif record_type == "SRV":
                record["priority"] = rdata.priority
                record["weight"] = rdata.weight
                record["port"] = rdata.port
                record["target"] = str(rdata.target).rstrip(".")
            elif record_type == "CAA":
                record["flags"] = rdata.flags
                record["tag"] = rdata.tag.decode() if isinstance(rdata.tag, bytes) else str(rdata.tag)
                record["value"] = rdata.value.decode() if isinstance(rdata.value, bytes) else str(rdata.value)
            records.append(record)

    except dns.resolver.NXDOMAIN:
        return [{"type": record_type, "error": "NXDOMAIN — domain does not exist"}]
    except dns.resolver.NoAnswer:
        return []  # No records of this type
    except dns.resolver.Timeout:
        return [{"type": record_type, "error": "DNS query timed out"}]
    except dns.exception.DNSException as e:
        return [{"type": record_type, "error": str(e)}]

    return records


def resolve_with_socket(domain: str, record_type: str) -> list[dict]:
    """Fallback resolver using socket module (A records only)."""
    records = []
    if record_type == "A":
        try:
            addrs = socket.getaddrinfo(domain, None, socket.AF_INET)
            seen = set()
            for addr in addrs:
                ip = addr[4][0]
                if ip not in seen:
                    seen.add(ip)
                    records.append({"type": "A", "raw": ip, "ttl": None})
        except socket.gaierror as e:
            records.append({"type": "A", "error": str(e)})
    elif record_type == "AAAA":
        try:
            addrs = socket.getaddrinfo(domain, None, socket.AF_INET6)
            seen = set()
            for addr in addrs:
                ip = addr[4][0]
                if ip not in seen:
                    seen.add(ip)
                    records.append({"type": "AAAA", "raw": ip, "ttl": None})
        except socket.gaierror:
            pass
    return records


def resolve_ptr(ip: str, resolver_ip: str | None) -> list[dict]:
    """Perform a reverse DNS (PTR) lookup."""
    try:
        import dns.reversename
        import dns.resolver
        rev = dns.reversename.from_address(ip)
        resolver = dns.resolver.Resolver()
        if resolver_ip:
            resolver.nameservers = [resolver_ip]
        answers = resolver.resolve(rev, "PTR")
        return [{"type": "PTR", "raw": str(r).rstrip("."), "ttl": answers.rrset.ttl} for r in answers]
    except Exception:
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return [{"type": "PTR", "raw": hostname, "ttl": None}]
        except socket.herror:
            return [{"type": "PTR", "error": f"No PTR record for {ip}"}]


def resolve_record(domain: str, record_type: str, resolver_ip: str | None) -> list[dict]:
    """Resolve a record type, using dnspython if available."""
    try:
        import dns.resolver
        return resolve_with_dnspython(domain, record_type, resolver_ip)
    except ImportError:
        return resolve_with_socket(domain, record_type)


def build_record_table(record_type: str, records: list[dict]) -> Table | None:
    """Build a rich table for a given record type."""
    if not records:
        return None

    has_error = any("error" in r for r in records)
    real_records = [r for r in records if "error" not in r]

    if not real_records and not has_error:
        return None

    desc = RECORD_DESCRIPTIONS.get(record_type, "")
    table = Table(
        title=f"[bold]{record_type}[/] — {desc}",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=False,
    )

    if has_error:
        table.add_column("Error", style="red")
        for r in records:
            if "error" in r:
                table.add_row(r["error"])
        return table

    # Type-specific columns
    if record_type == "MX":
        table.add_column("Priority", style="bold yellow", justify="right", width=10)
        table.add_column("Mail Server", style="cyan")
        table.add_column("TTL", style="dim", justify="right", width=8)
        for r in sorted(real_records, key=lambda x: x.get("priority", 0)):
            table.add_row(str(r.get("priority", "")), r.get("exchange", r["raw"]),
                          str(r.get("ttl", "—")))

    elif record_type == "NS":
        table.add_column("Name Server", style="cyan")
        table.add_column("TTL", style="dim", justify="right", width=8)
        for r in real_records:
            table.add_row(r.get("nameserver", r["raw"]), str(r.get("ttl", "—")))

    elif record_type == "TXT":
        table.add_column("Value", style="white", max_width=90)
        table.add_column("TTL", style="dim", justify="right", width=8)
        for r in real_records:
            val = r["raw"]
            # Highlight SPF, DKIM, DMARC
            if val.startswith('"v=spf'):
                val = f"[green]{val}[/]"
            elif "DKIM" in val.upper() or "dkim" in val:
                val = f"[yellow]{val[:80]}[/]"
            elif val.startswith('"v=DMARC'):
                val = f"[blue]{val}[/]"
            table.add_row(val, str(r.get("ttl", "—")))

    elif record_type == "SOA":
        table.add_column("Field", style="bold")
        table.add_column("Value", style="cyan")
        for r in real_records:
            table.add_row("Primary NS", r.get("mname", "?"))
            table.add_row("Responsible", r.get("rname", "?"))
            table.add_row("Serial", str(r.get("serial", "?")))
            table.add_row("Refresh", f"{r.get('refresh', '?')}s")
            table.add_row("Retry", f"{r.get('retry', '?')}s")
            table.add_row("Expire", f"{r.get('expire', '?')}s")
            table.add_row("Min TTL", f"{r.get('minimum', '?')}s")
            break  # Only one SOA record

    elif record_type == "SRV":
        table.add_column("Priority", justify="right", width=10)
        table.add_column("Weight", justify="right", width=8)
        table.add_column("Port", justify="right", width=8)
        table.add_column("Target", style="cyan")
        table.add_column("TTL", style="dim", justify="right", width=8)
        for r in sorted(real_records, key=lambda x: x.get("priority", 0)):
            table.add_row(
                str(r.get("priority", "")), str(r.get("weight", "")),
                str(r.get("port", "")), r.get("target", ""),
                str(r.get("ttl", "—"))
            )

    elif record_type == "CAA":
        table.add_column("Flags", justify="right", width=7)
        table.add_column("Tag", style="bold yellow", width=12)
        table.add_column("Value", style="cyan")
        for r in real_records:
            table.add_row(str(r.get("flags", "")), r.get("tag", ""), r.get("value", r["raw"]))

    else:
        # Generic: A, AAAA, CNAME, PTR
        table.add_column("Value", style="bold cyan")
        table.add_column("TTL", style="dim", justify="right", width=8)
        for r in real_records:
            table.add_row(r["raw"], str(r.get("ttl", "—")))

    return table


def do_lookup(domain: str, record_types: list[str], resolver_ip: str | None, show_empty: bool):
    """Perform lookups and display results."""
    console.rule(f"[bold cyan]🔍 DNS Lookup: {domain}[/]")

    resolver_display = resolver_ip or "system default"
    console.print(f"[dim]Using resolver: {resolver_display}[/]\n")

    found_any = False

    for rtype in record_types:
        with console.status(f"[cyan]Querying {rtype} records…[/]", spinner="dots"):
            records = resolve_record(domain, rtype, resolver_ip)

        table = build_record_table(rtype, records)
        if table:
            console.print(table)
            console.print()
            found_any = True
        elif show_empty:
            console.print(f"[dim]{rtype}: no records[/]")

    if not found_any:
        console.print(Panel(
            f"[yellow]No DNS records found for [bold]{domain}[/][/]",
            title="Result",
            border_style="yellow"
        ))


def main():
    parser = argparse.ArgumentParser(
        description="DNS lookup tool — resolve A, AAAA, MX, NS, TXT, and more."
    )
    parser.add_argument("--domain", "-d", help="Domain name to look up")
    parser.add_argument("--ip", "-i", help="IP address for reverse PTR lookup")
    parser.add_argument("--type", "-t", choices=RECORD_TYPES + ["ALL"], default="ALL",
                        metavar="TYPE", help=f"Record type: {', '.join(RECORD_TYPES)}, ALL")
    parser.add_argument("--all", "-a", dest="show_all", action="store_true",
                        help="Query all record types")
    parser.add_argument("--resolver", "-r", metavar="IP",
                        help="Custom DNS resolver IP (e.g. 8.8.8.8)")
    parser.add_argument("--show-empty", action="store_true",
                        help="Show empty record types")
    args = parser.parse_args()

    if args.ip:
        # Reverse lookup
        console.rule(f"[bold cyan]🔍 Reverse DNS: {args.ip}[/]")
        records = resolve_ptr(args.ip, args.resolver)
        table = build_record_table("PTR", records)
        if table:
            console.print(table)
        return

    domain = args.domain
    if not domain:
        domain = Prompt.ask("[bold]Enter domain name[/]", default="google.com")

    domain = domain.lower().strip().rstrip(".")

    if args.type == "ALL" or args.show_all:
        record_types = RECORD_TYPES
    else:
        record_types = [args.type]

    do_lookup(domain, record_types, args.resolver, args.show_empty)


if __name__ == "__main__":
    main()
