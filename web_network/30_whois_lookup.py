"""
Tool 30 - WHOIS Domain Lookup
================================
Performs WHOIS lookups for domain names and IP addresses:
- Registrar information
- Registration and expiry dates
- Domain status flags
- Name servers
- Registrant details (if available)
- Days until expiry with color-coded warning
- Check if domain is available for registration
- Batch lookup from file

Usage:
    python 30_whois_lookup.py
    python 30_whois_lookup.py --domain example.com
    python 30_whois_lookup.py --domain python.org --check-available
    python 30_whois_lookup.py --batch domains.txt

Dependencies:
    pip install python-whois rich
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def parse_whois(domain: str) -> dict:
    """Perform WHOIS lookup and return parsed data."""
    try:
        import whois
    except ImportError:
        console.print("[bold red]✗ python-whois not installed.[/]")
        console.print("  Run: [cyan]pip install python-whois[/]")
        sys.exit(1)

    try:
        w = whois.whois(domain)
        return dict(w)
    except whois.parser.PywhoisError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def normalize_date(d: Any) -> datetime | None:
    """Normalize various date formats from WHOIS."""
    if d is None:
        return None
    if isinstance(d, list):
        d = d[0]
    if isinstance(d, datetime):
        return d
    if isinstance(d, str):
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(d, fmt)
            except ValueError:
                pass
    return None


def normalize_list(val: Any) -> list[str]:
    """Normalize a value to a list of strings."""
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    if isinstance(val, list):
        return [str(v) for v in val if v]
    return [str(val)]


def days_until(dt: datetime | None) -> int | None:
    """Calculate days until a future date."""
    if dt is None:
        return None
    now = datetime.now()
    # Make both naive if needed
    if dt.tzinfo is not None:
        now = datetime.now(timezone.utc)
    return (dt - now).days


def format_date(dt: datetime | None) -> str:
    if dt is None:
        return "[dim]N/A[/]"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def display_whois(domain: str, data: dict):
    """Display WHOIS information in a rich format."""
    if "error" in data:
        # Check if domain might be available
        err = data["error"].lower()
        if any(kw in err for kw in ["no match", "not found", "no data", "domain not found"]):
            console.print(Panel(
                f"[bold green]✅ {domain}[/]\n\nThis domain does not appear to be registered.\n"
                f"It may be [bold green]available for registration![/]",
                title="[bold cyan]🔍 WHOIS Lookup",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]✗ WHOIS Error:[/] {data['error']}",
                title="[bold cyan]🔍 WHOIS Lookup",
                border_style="red"
            ))
        return

    # Parse common fields
    registrar = normalize_list(data.get("registrar"))
    registrant_name = normalize_list(data.get("name") or data.get("registrant_name"))
    registrant_org = normalize_list(data.get("org") or data.get("registrant_org"))
    registrant_country = normalize_list(data.get("country") or data.get("registrant_country"))
    creation_date = normalize_date(data.get("creation_date"))
    expiry_date = normalize_date(data.get("expiration_date"))
    updated_date = normalize_date(data.get("updated_date"))
    name_servers = normalize_list(data.get("name_servers"))
    status = normalize_list(data.get("status"))
    emails = normalize_list(data.get("emails"))
    dnssec = str(data.get("dnssec", "Unknown"))

    # Days until expiry
    days_left = days_until(expiry_date)
    if days_left is not None:
        if days_left < 0:
            expiry_str = f"[bold red]⚠ EXPIRED {abs(days_left)} days ago[/]"
        elif days_left < 30:
            expiry_str = f"[bold red]⚠ Expires in {days_left} days![/]"
        elif days_left < 90:
            expiry_str = f"[yellow]⏰ Expires in {days_left} days[/]"
        else:
            expiry_str = f"[green]✓ Expires in {days_left} days[/]"
    else:
        expiry_str = "[dim]Unknown[/]"

    # Main panel
    overview_lines = [
        f"[bold]Domain:[/]      [cyan]{domain}[/]",
        f"[bold]Registrar:[/]   {registrar[0] if registrar else '[dim]N/A[/]'}",
        f"[bold]Created:[/]     {format_date(creation_date)}",
        f"[bold]Updated:[/]     {format_date(updated_date)}",
        f"[bold]Expires:[/]     {format_date(expiry_date)}",
        f"[bold]Expiry:[/]      {expiry_str}",
        f"[bold]DNSSEC:[/]      {dnssec}",
    ]

    if registrant_name or registrant_org:
        overview_lines.append("")
        if registrant_name:
            overview_lines.append(f"[bold]Registrant:[/]  {registrant_name[0]}")
        if registrant_org:
            overview_lines.append(f"[bold]Org:[/]         {registrant_org[0]}")
        if registrant_country:
            overview_lines.append(f"[bold]Country:[/]     {registrant_country[0]}")

    console.print(Panel(
        "\n".join(overview_lines),
        title=f"[bold cyan]🔍 WHOIS: {domain}",
        border_style="cyan"
    ))
    console.print()

    # Name Servers
    if name_servers:
        ns_table = Table(title="🗄  Name Servers", box=box.ROUNDED, border_style="blue", show_header=False)
        ns_table.add_column("NS", style="cyan")
        for ns in name_servers[:10]:
            ns_table.add_row(ns.lower().rstrip("."))
        console.print(ns_table)
        console.print()

    # Domain Status
    if status:
        st_table = Table(title="📋 Domain Status", box=box.ROUNDED, border_style="yellow")
        st_table.add_column("Status Code", style="bold")
        st_table.add_column("Meaning", style="dim")

        status_meanings = {
            "clientDeleteProhibited": "Cannot be deleted by registrant",
            "clientTransferProhibited": "Transfer to another registrar locked",
            "clientUpdateProhibited": "Updates locked by registrant",
            "serverDeleteProhibited": "Registry prevents deletion",
            "serverTransferProhibited": "Registry prevents transfer",
            "serverUpdateProhibited": "Registry prevents updates",
            "ok": "Normal status, no operations restricted",
            "active": "Domain is active",
        }
        for s in status[:8]:
            key = s.split(" ")[0].lower() if s else ""
            meaning = status_meanings.get(key, "")
            st_table.add_row(s[:60], meaning)
        console.print(st_table)

    # Contact emails
    if emails:
        console.print()
        console.print(Panel(
            "\n".join(f"  📧 {e}" for e in emails[:5]),
            title="Contacts",
            border_style="dim"
        ))


def check_availability(domain: str) -> bool:
    """Heuristically determine if a domain is likely available."""
    data = parse_whois(domain)
    if "error" in data:
        err = data["error"].lower()
        if any(kw in err for kw in ["no match", "not found", "no data", "no entries"]):
            return True
        return False
    # If we got actual data back, it's registered
    if data.get("registrar") or data.get("creation_date"):
        return False
    return True


def batch_lookup(file_path: str):
    """Look up multiple domains from a file."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]✗ File not found:[/] {file_path}")
        sys.exit(1)

    domains = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not domains:
        console.print("[yellow]File is empty.[/]")
        return

    table = Table(
        title=f"🔍 Batch WHOIS ({len(domains)} domains)",
        box=box.ROUNDED, border_style="cyan", show_lines=False,
    )
    table.add_column("Domain", style="bold cyan")
    table.add_column("Registrar", max_width=25)
    table.add_column("Created", style="dim")
    table.add_column("Expires")
    table.add_column("Days Left", justify="right")
    table.add_column("Status")

    with Progress(
        SpinnerColumn(), TextColumn("[cyan]{task.description}"),
        BarColumn(), TaskProgressColumn(),
        console=console, transient=True,
    ) as progress:
        task = progress.add_task("Looking up…", total=len(domains))

        for domain in domains:
            progress.update(task, description=f"Looking up {domain}…")
            data = parse_whois(domain)
            progress.advance(task)

            if "error" in data:
                table.add_row(domain, "[dim]Error[/]", "—", "—", "—", "[red]Error[/]")
                continue

            registrar = normalize_list(data.get("registrar"))
            creation_date = normalize_date(data.get("creation_date"))
            expiry_date = normalize_date(data.get("expiration_date"))
            days_left = days_until(expiry_date)

            if days_left is not None:
                if days_left < 30:
                    days_str = f"[bold red]{days_left}[/]"
                elif days_left < 90:
                    days_str = f"[yellow]{days_left}[/]"
                else:
                    days_str = f"[green]{days_left}[/]"
            else:
                days_str = "[dim]?[/]"

            table.add_row(
                domain,
                registrar[0][:25] if registrar else "[dim]?[/]",
                format_date(creation_date)[:10],
                format_date(expiry_date)[:10],
                days_str,
                "[green]Registered[/]",
            )

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="WHOIS domain lookup — registrar, dates, name servers, availability."
    )
    parser.add_argument("--domain", "-d", help="Domain name to look up")
    parser.add_argument("--check-available", "-c", action="store_true",
                        help="Check if domain is available for registration")
    parser.add_argument("--batch", "-b", metavar="FILE",
                        help="Batch lookup domains from a file")
    args = parser.parse_args()

    console.rule("[bold cyan]🔍 WHOIS Domain Lookup[/]")

    if args.batch:
        batch_lookup(args.batch)
        return

    domain = args.domain
    if not domain:
        domain = Prompt.ask("[bold]Enter domain name[/]", default="python.org")

    # Strip URL components if user pasted a full URL
    domain = domain.lower().strip()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

    if args.check_available:
        with console.status(f"[cyan]Checking availability of {domain}…[/]", spinner="dots"):
            available = check_availability(domain)
        if available:
            console.print(Panel(
                f"[bold green]✅ {domain} appears to be AVAILABLE![/]\n"
                f"Check with a registrar to confirm and register.",
                title="Domain Availability",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]❌ {domain} is already REGISTERED.[/]",
                title="Domain Availability",
                border_style="red"
            ))
        console.print()

    with console.status(f"[cyan]Looking up {domain}…[/]", spinner="dots"):
        data = parse_whois(domain)

    display_whois(domain, data)


if __name__ == "__main__":
    main()
