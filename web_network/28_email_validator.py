"""
Tool 28 - Email Validator
===========================
Validates email addresses through multiple checks:
1. Syntax validation (RFC 5322 compatible regex)
2. MX record lookup (does the domain accept email?)
3. Disposable email detection (known throwaway domains)
4. Role-based address detection (info@, admin@, etc.)
5. Common domain typo suggestions
6. Batch validation from a file

Usage:
    python 28_email_validator.py
    python 28_email_validator.py --email user@example.com
    python 28_email_validator.py --batch emails.txt
    python 28_email_validator.py --email test@gmail.com --verbose

Dependencies:
    pip install rich dnspython
"""

import argparse
import re
import socket
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

# RFC 5322-ish email regex
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9]"                      # must start with alphanumeric
    r"[a-zA-Z0-9._%+\-]*"                # local part
    r"@"
    r"[a-zA-Z0-9]"                        # domain start
    r"[a-zA-Z0-9\-]*"                     # domain characters
    r"(\.[a-zA-Z0-9\-]+)*"               # subdomains
    r"\.[a-zA-Z]{2,}$"                    # TLD (2+ chars)
)

# Role-based prefixes that often don't go to real people
ROLE_BASED = {
    "admin", "administrator", "webmaster", "postmaster", "hostmaster",
    "info", "contact", "support", "help", "sales", "marketing",
    "billing", "accounts", "finance", "hr", "jobs", "careers",
    "abuse", "security", "noreply", "no-reply", "donotreply",
    "mailer-daemon", "newsletter", "notifications", "alerts",
    "team", "hello", "hey", "hi", "mail", "email",
}

# Known disposable email domains (a sample — in production use a larger list)
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "10minutemail.com", "yopmail.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "guerrillamail.info", "guerrillamail.biz", "guerrillamail.de",
    "guerrillamail.net", "guerrillamail.org", "spam4.me", "trashmail.com",
    "trashmail.me", "trashmail.net", "trashmail.org", "trashmail.io",
    "dispostable.com", "maildrop.cc", "fakeinbox.com", "mailnull.com",
    "spamgourmet.com", "spamgourmet.net", "spamgourmet.org",
    "tempr.email", "discard.email", "mohmal.com", "tempinbox.com",
    "mailnesia.com", "mailnull.com", "meltmail.com", "einrot.com",
    "filzmail.com", "hmamail.com", "jetable.fr", "kasmail.com",
    "maileater.com", "mailexpire.com", "mailfs.com", "mailfreeonline.com",
    "mailguard.me", "mailimate.com", "mailin8r.com", "mailismagic.com",
    "mailme.lv", "mailnew.com", "mailsiphon.com", "mailslapping.com",
    "mailzilla.com", "nwldx.com", "sogetthis.com", "spamday.com",
    "spamevader.com", "spamfree24.org", "tempinbox.co.uk", "tempomail.fr",
    "thanksnospam.info", "throwam.com", "tradermail.info", "trash2009.com",
    "uggsrock.com", "xoxy.net",
}

# Common domain typos and corrections
DOMAIN_SUGGESTIONS = {
    "gmai.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gmail.co": "gmail.com",
    "gmail.cm": "gmail.com",
    "hotmai.com": "hotmail.com",
    "hotmial.com": "hotmail.com",
    "hotmail.co": "hotmail.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "outlok.com": "outlook.com",
    "outloo.com": "outlook.com",
    "outlookcom": "outlook.com",
    "iclod.com": "icloud.com",
    "icould.com": "icloud.com",
    "microsot.com": "microsoft.com",
    "protonmai.com": "protonmail.com",
}


def check_syntax(email: str) -> tuple[bool, str]:
    """Check if email syntax is valid."""
    if not email or len(email) > 254:
        return False, "Email too long or empty"
    if EMAIL_REGEX.match(email):
        return True, "Valid syntax"
    return False, "Invalid email format"


def check_mx_record(domain: str) -> tuple[bool, str]:
    """Check if domain has MX records (can receive email)."""
    try:
        import dns.resolver
        try:
            answers = dns.resolver.resolve(domain, "MX")
            mx_hosts = [str(r.exchange).rstrip(".") for r in answers]
            return True, f"MX: {mx_hosts[0]}"
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False, "No MX records found"
        except dns.resolver.Timeout:
            return None, "DNS timeout"
        except Exception as e:
            return None, f"DNS error: {e}"
    except ImportError:
        # Fallback: just check if domain resolves
        try:
            socket.gethostbyname(domain)
            return True, "Domain resolves (no dnspython for MX)"
        except socket.gaierror:
            return False, "Domain does not resolve"


def check_disposable(domain: str) -> tuple[bool, str]:
    """Check if domain is a known disposable email provider."""
    if domain.lower() in DISPOSABLE_DOMAINS:
        return True, "Known disposable email provider"
    return False, "Not a known disposable domain"


def check_role_based(local: str) -> tuple[bool, str]:
    """Check if the local part is a role-based address."""
    local_clean = local.lower().split("+")[0]  # ignore plus aliases
    if local_clean in ROLE_BASED:
        return True, f"Role-based address ({local_clean})"
    return False, "Not role-based"


def check_typo(domain: str) -> str | None:
    """Suggest correction for common domain typos."""
    return DOMAIN_SUGGESTIONS.get(domain.lower())


def validate_email(email: str, verbose: bool = False) -> dict:
    """Run all validation checks on an email address."""
    email = email.strip().lower()
    result = {
        "email": email,
        "checks": {},
        "score": 0,
        "verdict": "UNKNOWN",
    }

    # Extract parts
    if "@" in email:
        local, _, domain = email.rpartition("@")
    else:
        local, domain = email, ""

    # 1. Syntax
    syntax_ok, syntax_msg = check_syntax(email)
    result["checks"]["syntax"] = {"pass": syntax_ok, "message": syntax_msg}
    if not syntax_ok:
        result["verdict"] = "INVALID"
        return result

    # 2. MX record
    mx_ok, mx_msg = check_mx_record(domain)
    result["checks"]["mx_record"] = {"pass": mx_ok, "message": mx_msg}

    # 3. Disposable
    disp, disp_msg = check_disposable(domain)
    result["checks"]["disposable"] = {"pass": not disp, "message": disp_msg}

    # 4. Role-based
    role, role_msg = check_role_based(local)
    result["checks"]["role_based"] = {"pass": not role, "message": role_msg}

    # 5. Typo suggestion
    suggestion = check_typo(domain)
    result["suggestion"] = suggestion

    # Score
    score = 0
    if syntax_ok:
        score += 40
    if mx_ok:
        score += 35
    if not disp:
        score += 15
    if not role:
        score += 10
    result["score"] = score

    if score >= 85:
        result["verdict"] = "VALID"
    elif score >= 60:
        result["verdict"] = "LIKELY_VALID"
    elif score >= 40:
        result["verdict"] = "RISKY"
    else:
        result["verdict"] = "INVALID"

    return result


def display_single_result(result: dict):
    """Display validation result for one email."""
    email = result["email"]
    verdict = result["verdict"]
    score = result["score"]

    # Verdict color
    colors = {
        "VALID": ("bold green", "✅"),
        "LIKELY_VALID": ("green", "✔ "),
        "RISKY": ("yellow", "⚠️ "),
        "INVALID": ("bold red", "❌"),
        "UNKNOWN": ("dim", "❓"),
    }
    color, emoji = colors.get(verdict, ("white", "?"))

    # Score bar
    filled = int(score / 100 * 20)
    bar = "█" * filled + "░" * (20 - filled)
    score_color = "green" if score >= 75 else ("yellow" if score >= 50 else "red")

    lines = [
        f"[bold]Email:[/]    [cyan]{email}[/]",
        f"[bold]Verdict:[/]  [{color}]{emoji} {verdict}[/]",
        f"[bold]Score:[/]    [{score_color}]{bar}[/] {score}/100",
    ]

    if result.get("suggestion"):
        lines.append(
            f"\n[bold yellow]💡 Did you mean?[/]  "
            f"[cyan]{email.split('@')[0]}@{result['suggestion']}[/]"
        )

    # Checks table
    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
    table.add_column("Check", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")

    check_names = {
        "syntax": "Syntax",
        "mx_record": "MX Record",
        "disposable": "Not Disposable",
        "role_based": "Not Role-based",
    }

    for key, label in check_names.items():
        check = result["checks"].get(key, {})
        passed = check.get("pass")
        msg = check.get("message", "N/A")
        if passed is True:
            status = "[green]✓ Pass[/]"
        elif passed is False:
            status = "[red]✗ Fail[/]"
        else:
            status = "[yellow]? Unknown[/]"
        table.add_row(label, status, msg)

    console.print(Panel(
        "\n".join(lines) + "\n",
        title="[bold cyan]📧 Email Validation",
        border_style="cyan"
    ))
    console.print(table)


def batch_validate(file_path: str):
    """Validate emails from a file."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]✗ File not found:[/] {file_path}")
        sys.exit(1)

    emails = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not emails:
        console.print("[yellow]File is empty.[/]")
        return

    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console, transient=True,
    ) as progress:
        task = progress.add_task("Validating…", total=len(emails))
        for email in emails:
            results.append(validate_email(email))
            progress.advance(task)

    # Summary table
    table = Table(
        title=f"📧 Batch Email Validation ({len(emails)} addresses)",
        box=box.ROUNDED, border_style="cyan", show_lines=False,
    )
    table.add_column("Email", style="cyan", max_width=40)
    table.add_column("Verdict", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("MX", justify="center")
    table.add_column("Disposable", justify="center")
    table.add_column("Note", style="dim")

    colors = {
        "VALID": "bold green",
        "LIKELY_VALID": "green",
        "RISKY": "yellow",
        "INVALID": "bold red",
        "UNKNOWN": "dim",
    }

    for r in results:
        color = colors.get(r["verdict"], "white")
        mx = r["checks"].get("mx_record", {})
        disp = r["checks"].get("disposable", {})
        note = r.get("suggestion", "")
        if note:
            note = f"Did you mean …@{note}?"
        table.add_row(
            r["email"],
            f"[{color}]{r['verdict']}[/]",
            str(r["score"]),
            "[green]✓[/]" if mx.get("pass") else "[red]✗[/]",
            "[red]YES[/]" if not disp.get("pass") else "[green]NO[/]",
            note,
        )

    console.print(table)

    # Stats
    by_verdict = {}
    for r in results:
        by_verdict[r["verdict"]] = by_verdict.get(r["verdict"], 0) + 1

    stats = "  ".join(
        f"[{colors.get(v, 'white')}]{v}[/]: {c}" for v, c in sorted(by_verdict.items())
    )
    console.print(Panel(stats, title="Summary", border_style="green"))


def main():
    parser = argparse.ArgumentParser(
        description="Email validator — syntax, MX records, disposable detection."
    )
    parser.add_argument("--email", "-e", help="Email address to validate")
    parser.add_argument("--batch", "-b", metavar="FILE", help="Validate emails from a file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    console.rule("[bold cyan]📧 Email Validator[/]")

    if args.batch:
        batch_validate(args.batch)
    elif args.email:
        result = validate_email(args.email, args.verbose)
        display_single_result(result)
    else:
        # Interactive mode
        while True:
            email = Prompt.ask("\n[bold]Enter email to validate[/] (or 'quit')")
            if email.lower() in ("quit", "q", "exit"):
                break
            result = validate_email(email)
            display_single_result(result)


if __name__ == "__main__":
    main()
