"""
Tool 29 - HTTP Security Header Analyzer
==========================================
Analyzes HTTP response headers for security best practices:
- Checks for HSTS (HTTP Strict Transport Security)
- Content Security Policy (CSP)
- X-Frame-Options (clickjacking protection)
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- CORS headers
- Cookie security flags
- Overall security score with letter grade

Usage:
    python 29_http_header_analyzer.py
    python 29_http_header_analyzer.py --url https://example.com
    python 29_http_header_analyzer.py --url https://github.com --all-headers
    python 29_http_header_analyzer.py --compare https://site1.com https://site2.com

Dependencies:
    pip install requests rich
"""

import argparse
import sys
from dataclasses import dataclass, field
from typing import Optional

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

console = Console()


@dataclass
class SecurityCheck:
    name: str
    header: str
    description: str
    weight: int  # importance score (out of 100 total)
    present: bool = False
    value: str = ""
    rating: str = "MISSING"  # GOOD, WARN, MISSING, BAD
    detail: str = ""


def fetch_headers(url: str) -> tuple[dict, dict]:
    """Fetch HTTP headers from a URL, return (response_headers, metadata)."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    headers = {"User-Agent": "SecurityHeaderAnalyzer/1.0"}

    with console.status(f"[bold cyan]Fetching headers from {url}…[/]", spinner="dots"):
        try:
            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        except requests.exceptions.ConnectionError:
            console.print(f"[bold red]✗ Cannot connect to {url}[/]")
            sys.exit(1)
        except requests.exceptions.Timeout:
            console.print(f"[bold red]✗ Request timed out[/]")
            sys.exit(1)

    meta = {
        "url": url,
        "final_url": resp.url,
        "status_code": resp.status_code,
        "server": resp.headers.get("Server", "Not disclosed"),
        "x_powered_by": resp.headers.get("X-Powered-By", "Not disclosed"),
        "is_https": resp.url.startswith("https://"),
        "redirects": len(resp.history),
    }

    return dict(resp.headers), meta


def analyze_hsts(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="HSTS",
        header="Strict-Transport-Security",
        description="Forces browsers to use HTTPS for future visits",
        weight=20,
    )
    val = headers.get("Strict-Transport-Security", "")
    check.value = val
    if val:
        check.present = True
        # Check for recommended attributes
        has_max_age = "max-age=" in val.lower()
        max_age = 0
        try:
            age_part = [p for p in val.split(";") if "max-age" in p.lower()][0]
            max_age = int(age_part.split("=")[1].strip())
        except Exception:
            pass

        has_subdomains = "includesubdomains" in val.lower()
        has_preload = "preload" in val.lower()

        if max_age >= 31536000 and has_subdomains:
            check.rating = "GOOD"
            check.detail = f"max-age={max_age:,}s{'  includeSubDomains' if has_subdomains else ''}{'  preload' if has_preload else ''}"
        elif max_age >= 86400:
            check.rating = "WARN"
            check.detail = f"max-age={max_age:,}s — consider ≥31536000 + includeSubDomains"
        else:
            check.rating = "WARN"
            check.detail = "max-age too short (< 1 day)"
    else:
        check.rating = "MISSING"
        check.detail = "Header not present — users can be downgraded to HTTP"
    return check


def analyze_csp(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="CSP",
        header="Content-Security-Policy",
        description="Controls which resources the browser can load",
        weight=20,
    )
    val = headers.get("Content-Security-Policy", "")
    check.value = val
    if val:
        check.present = True
        directives = [d.strip() for d in val.split(";") if d.strip()]
        has_default = any(d.startswith("default-src") for d in directives)
        unsafe_inline = "'unsafe-inline'" in val
        unsafe_eval = "'unsafe-eval'" in val

        if has_default and not unsafe_inline and not unsafe_eval:
            check.rating = "GOOD"
            check.detail = f"{len(directives)} directive(s) — no unsafe-inline/eval"
        elif has_default:
            check.rating = "WARN"
            issues = []
            if unsafe_inline:
                issues.append("'unsafe-inline'")
            if unsafe_eval:
                issues.append("'unsafe-eval'")
            check.detail = f"Has {', '.join(issues)} — weakens protection"
        else:
            check.rating = "WARN"
            check.detail = "Missing default-src directive"
    else:
        check.rating = "MISSING"
        check.detail = "XSS and injection attacks not mitigated"
    return check


def analyze_xframe(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="X-Frame-Options",
        header="X-Frame-Options",
        description="Prevents clickjacking attacks via iframes",
        weight=10,
    )
    val = headers.get("X-Frame-Options", "").upper()
    check.value = val
    if val:
        check.present = True
        if val in ("DENY", "SAMEORIGIN"):
            check.rating = "GOOD"
            check.detail = f"{'No framing allowed' if val == 'DENY' else 'Same-origin framing only'}"
        else:
            check.rating = "WARN"
            check.detail = f"Value '{val}' is non-standard; use DENY or SAMEORIGIN"
    else:
        check.rating = "MISSING"
        check.detail = "Site may be embeddable by any third-party site"
    return check


def analyze_xcto(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="X-Content-Type-Options",
        header="X-Content-Type-Options",
        description="Prevents MIME-type sniffing",
        weight=10,
    )
    val = headers.get("X-Content-Type-Options", "").lower()
    check.value = val
    if val == "nosniff":
        check.present = True
        check.rating = "GOOD"
        check.detail = "MIME sniffing disabled"
    elif val:
        check.present = True
        check.rating = "WARN"
        check.detail = f"Unexpected value '{val}' — use 'nosniff'"
    else:
        check.rating = "MISSING"
        check.detail = "Browser may misinterpret file types"
    return check


def analyze_referrer_policy(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="Referrer-Policy",
        header="Referrer-Policy",
        description="Controls referrer info sent with requests",
        weight=5,
    )
    val = headers.get("Referrer-Policy", "").lower()
    check.value = val
    STRICT_POLICIES = {"no-referrer", "strict-origin", "strict-origin-when-cross-origin"}
    LAX_POLICIES = {"same-origin", "origin", "origin-when-cross-origin"}
    if val in STRICT_POLICIES:
        check.present = True
        check.rating = "GOOD"
        check.detail = f"Strict policy: {val}"
    elif val in LAX_POLICIES:
        check.present = True
        check.rating = "WARN"
        check.detail = f"Moderate policy: {val} — consider stricter"
    elif val:
        check.present = True
        check.rating = "WARN"
        check.detail = f"Weak or non-standard policy: {val}"
    else:
        check.rating = "MISSING"
        check.detail = "Browser default (usually unsafe-url)"
    return check


def analyze_permissions_policy(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="Permissions-Policy",
        header="Permissions-Policy",
        description="Restricts browser features (camera, mic, etc.)",
        weight=5,
    )
    val = headers.get("Permissions-Policy", "") or headers.get("Feature-Policy", "")
    check.value = val
    if val:
        check.present = True
        check.rating = "GOOD"
        directives = len([d for d in val.split(",") if d.strip()])
        check.detail = f"{directives} feature directive(s) defined"
    else:
        check.rating = "MISSING"
        check.detail = "Browser features unrestricted"
    return check


def analyze_cors(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="CORS",
        header="Access-Control-Allow-Origin",
        description="Cross-Origin Resource Sharing policy",
        weight=10,
    )
    val = headers.get("Access-Control-Allow-Origin", "")
    check.value = val
    if val == "*":
        check.present = True
        check.rating = "WARN"
        check.detail = "Wildcard (*) allows any origin to read responses"
    elif val:
        check.present = True
        check.rating = "GOOD"
        check.detail = f"Restricted to: {val}"
    else:
        check.rating = "MISSING"
        check.detail = "No CORS header (may be intentional for non-API sites)"
    return check


def analyze_cookies(headers: dict) -> SecurityCheck:
    check = SecurityCheck(
        name="Cookie Security",
        header="Set-Cookie",
        description="Checks session cookies for security flags",
        weight=20,
    )
    cookies = headers.get("Set-Cookie", "")
    if not cookies:
        check.rating = "MISSING"
        check.detail = "No cookies set"
        return check

    check.present = True
    has_secure = "Secure" in cookies
    has_httponly = "HttpOnly" in cookies
    has_samesite = "SameSite" in cookies

    issues = []
    if not has_secure:
        issues.append("missing Secure flag")
    if not has_httponly:
        issues.append("missing HttpOnly flag")
    if not has_samesite:
        issues.append("missing SameSite attribute")

    if not issues:
        check.rating = "GOOD"
        check.detail = "Secure + HttpOnly + SameSite present"
    elif len(issues) <= 1:
        check.rating = "WARN"
        check.detail = f"Cookie issue: {issues[0]}"
    else:
        check.rating = "BAD"
        check.detail = f"Cookie issues: {', '.join(issues)}"
    return check


def run_analysis(headers: dict) -> list[SecurityCheck]:
    """Run all security checks."""
    analyzers = [
        analyze_hsts,
        analyze_csp,
        analyze_xframe,
        analyze_xcto,
        analyze_referrer_policy,
        analyze_permissions_policy,
        analyze_cors,
        analyze_cookies,
    ]
    return [fn(headers) for fn in analyzers]


def calculate_score(checks: list[SecurityCheck]) -> tuple[int, str]:
    """Calculate overall security score (0-100) and letter grade."""
    total_weight = sum(c.weight for c in checks)
    earned = 0
    for c in checks:
        if c.rating == "GOOD":
            earned += c.weight
        elif c.rating == "WARN":
            earned += c.weight * 0.5
        elif c.rating == "MISSING":
            earned += 0
        elif c.rating == "BAD":
            earned += 0

    score = int((earned / total_weight) * 100) if total_weight else 0
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 50:
        grade = "D"
    else:
        grade = "F"
    return score, grade


def display_analysis(url: str, headers: dict, meta: dict, show_all: bool):
    """Display the complete security analysis."""
    console.print(Panel(
        f"[bold]URL:[/]      {meta['final_url']}\n"
        f"[bold]Status:[/]   {meta['status_code']}\n"
        f"[bold]HTTPS:[/]    {'[green]Yes ✓[/]' if meta['is_https'] else '[red]No ✗[/]'}\n"
        f"[bold]Server:[/]   {meta['server']}\n"
        f"[bold]Redirects:[/] {meta['redirects']}",
        title="[bold cyan]🌐 Site Info",
        border_style="cyan"
    ))
    console.print()

    checks = run_analysis(headers)
    score, grade = calculate_score(checks)

    # Score panel
    grade_color = {
        "A+": "bold green", "A": "bold green", "B": "green",
        "C": "yellow", "D": "red", "F": "bold red"
    }.get(grade, "white")
    bar_filled = int(score / 100 * 30)
    score_bar = "█" * bar_filled + "░" * (30 - bar_filled)
    score_color = "green" if score >= 70 else ("yellow" if score >= 50 else "red")

    console.print(Panel(
        f"[{grade_color}]Grade: {grade}[/]    "
        f"Score: [{score_color}]{score}/100[/]\n"
        f"[{score_color}]{score_bar}[/]",
        title="[bold cyan]🔒 Security Score",
        border_style=score_color
    ))
    console.print()

    # Checks table
    table = Table(
        title="🛡  Security Header Analysis",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("Check", style="bold", width=22)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Weight", justify="right", width=8)
    table.add_column("Details", max_width=60)

    rating_display = {
        "GOOD": ("[bold green]✅ GOOD[/]", "green"),
        "WARN": ("[yellow]⚠  WARN[/]", "yellow"),
        "MISSING": ("[red]❌ MISSING[/]", "red"),
        "BAD": ("[bold red]🚨 BAD[/]", "bold red"),
    }

    for c in checks:
        status_str, _ = rating_display.get(c.rating, ("?", "white"))
        table.add_row(
            f"{c.name}\n[dim]{c.header}[/]",
            status_str,
            f"{c.weight}",
            c.detail,
        )

    console.print(table)

    # Recommendations
    missing = [c for c in checks if c.rating in ("MISSING", "BAD")]
    if missing:
        console.print()
        rec_table = Table(
            title="💡 Recommendations",
            box=box.SIMPLE,
            border_style="yellow",
            show_header=False,
        )
        rec_table.add_column("", style="yellow bold", width=22)
        rec_table.add_column("")
        for c in missing:
            rec_table.add_row(f"Add {c.name}", c.description)
        console.print(rec_table)

    # All headers if requested
    if show_all:
        console.print()
        ah_table = Table(
            title="📋 All Response Headers",
            box=box.ROUNDED,
            border_style="dim",
        )
        ah_table.add_column("Header", style="bold dim")
        ah_table.add_column("Value", style="dim")
        for k, v in headers.items():
            ah_table.add_row(k, v[:120])
        console.print(ah_table)


def main():
    parser = argparse.ArgumentParser(
        description="HTTP security header analyzer — score a site's security posture."
    )
    parser.add_argument("--url", "-u", help="URL to analyze")
    parser.add_argument("--all-headers", "-a", action="store_true",
                        help="Show all response headers")
    parser.add_argument("--compare", "-c", nargs="+", metavar="URL",
                        help="Compare security scores for multiple URLs")
    args = parser.parse_args()

    console.rule("[bold cyan]🔒 HTTP Security Header Analyzer[/]")

    if args.compare:
        # Compare mode
        results = []
        for url in args.compare:
            hdrs, meta = fetch_headers(url)
            checks = run_analysis(hdrs)
            score, grade = calculate_score(checks)
            results.append((url, score, grade, checks))

        table = Table(title="📊 Security Comparison", box=box.ROUNDED, border_style="cyan")
        table.add_column("URL", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Grade", justify="center")
        for check_name in ["HSTS", "CSP", "X-Frame-Options", "X-Content-Type-Options"]:
            table.add_column(check_name, justify="center", width=8)

        for url, score, grade, checks_list in results:
            grade_color = "green" if grade in ("A+", "A", "B") else ("yellow" if grade == "C" else "red")
            row = [url, str(score), f"[{grade_color}]{grade}[/]"]
            check_map = {c.name: c for c in checks_list}
            for check_name in ["HSTS", "CSP", "X-Frame-Options", "X-Content-Type-Options"]:
                c = check_map.get(check_name)
                if c and c.rating == "GOOD":
                    row.append("[green]✓[/]")
                elif c and c.rating == "WARN":
                    row.append("[yellow]~[/]")
                else:
                    row.append("[red]✗[/]")
            table.add_row(*row)

        console.print(table)
        return

    url = args.url
    if not url:
        url = Prompt.ask("[bold]Enter URL to analyze[/]", default="https://github.com")

    headers, meta = fetch_headers(url)
    display_analysis(url, headers, meta, show_all=args.all_headers)


if __name__ == "__main__":
    main()
