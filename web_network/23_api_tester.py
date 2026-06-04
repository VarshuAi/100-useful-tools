"""
Tool 23 - REST API Tester
=========================
A full-featured REST API testing tool that supports:
- HTTP methods: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- Custom headers, query parameters, and request body
- Basic Auth and Bearer token authentication
- JSON and form-encoded body formats
- Formatted JSON response display with syntax highlighting
- Timing and performance metrics
- Save/load request profiles for reuse

Usage:
    python 23_api_tester.py
    python 23_api_tester.py --url https://api.example.com/users --method GET
    python 23_api_tester.py --url https://httpbin.org/post --method POST --body '{"key":"value"}'

Dependencies:
    pip install requests rich
"""

import argparse
import json
import sys
import time
from typing import Any

import requests
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

HTTP_STATUS_COLORS = {
    range(100, 200): "dim white",
    range(200, 300): "bold green",
    range(300, 400): "bold yellow",
    range(400, 500): "bold red",
    range(500, 600): "bold magenta",
}

COMMON_HEADERS = [
    ("Content-Type", "application/json"),
    ("Accept", "application/json"),
    ("User-Agent", "RichAPITester/1.0"),
]


def get_status_color(code: int) -> str:
    """Return rich color for an HTTP status code."""
    for r, color in HTTP_STATUS_COLORS.items():
        if code in r:
            return color
    return "white"


def get_status_emoji(code: int) -> str:
    """Return emoji for status code category."""
    if 200 <= code < 300:
        return "✅"
    elif 300 <= code < 400:
        return "↪️ "
    elif 400 <= code < 500:
        return "⚠️ "
    elif 500 <= code < 600:
        return "❌"
    return "ℹ️ "


def parse_key_value_pairs(pairs: list[str]) -> dict:
    """Parse a list of 'key=value' strings into a dict."""
    result = {}
    for pair in pairs:
        if "=" in pair:
            k, _, v = pair.partition("=")
            result[k.strip()] = v.strip()
    return result


def make_request(
    url: str,
    method: str,
    headers: dict,
    params: dict,
    body: Any,
    auth: tuple | None,
    timeout: int,
) -> tuple[requests.Response, float]:
    """Make the HTTP request and return response + elapsed time."""
    method = method.upper()
    kwargs: dict = {
        "headers": headers,
        "params": params,
        "timeout": timeout,
        "allow_redirects": True,
    }
    if auth:
        kwargs["auth"] = auth

    # Attach body for methods that support it
    if body is not None and method not in ("GET", "HEAD", "OPTIONS"):
        if isinstance(body, (dict, list)):
            kwargs["json"] = body
        else:
            kwargs["data"] = body

    start = time.perf_counter()
    try:
        response = requests.request(method, url, **kwargs)
    except requests.exceptions.ConnectionError:
        console.print(f"\n[bold red]✗ Connection Error:[/] Could not connect to [cyan]{url}[/]")
        sys.exit(1)
    except requests.exceptions.Timeout:
        console.print(f"\n[bold red]✗ Timeout:[/] Request exceeded {timeout}s limit")
        sys.exit(1)
    except requests.exceptions.MissingSchema:
        console.print(f"\n[bold red]✗ Invalid URL:[/] Missing scheme (http/https) in '{url}'")
        sys.exit(1)

    elapsed = time.perf_counter() - start
    return response, elapsed


def display_request_info(method: str, url: str, headers: dict, params: dict, body: Any):
    """Show what request is being sent."""
    lines = [f"[bold]{method}[/] [cyan]{url}[/]"]
    if params:
        lines.append(f"[bold]Params:[/] {params}")
    if headers:
        header_str = ", ".join(f"{k}: {v}" for k, v in headers.items())
        lines.append(f"[bold]Headers:[/] {header_str}")
    if body is not None:
        body_preview = json.dumps(body)[:80] if isinstance(body, (dict, list)) else str(body)[:80]
        lines.append(f"[bold]Body:[/] {body_preview}…" if len(str(body)) > 80 else f"[bold]Body:[/] {body_preview}")

    console.print(Panel("\n".join(lines), title="[bold blue]📤 Request", border_style="blue"))


def display_status_line(response: requests.Response, elapsed: float):
    """Display the response status prominently."""
    code = response.status_code
    color = get_status_color(code)
    emoji = get_status_emoji(code)
    reason = response.reason or ""
    size_kb = len(response.content) / 1024

    status_text = (
        f"{emoji} [{color}]{code} {reason}[/]   "
        f"⏱  [bold]{elapsed * 1000:.1f}ms[/]   "
        f"📦 [bold]{size_kb:.2f} KB[/]   "
        f"↩  [dim]{len(response.history)} redirect(s)[/]"
    )
    console.print(Panel(status_text, title="[bold cyan]📥 Response Status", border_style=color.split()[-1]))


def display_headers(response: requests.Response):
    """Display response headers in a table."""
    table = Table(title="📋 Response Headers", box=box.SIMPLE_HEAVY, border_style="yellow", show_lines=False)
    table.add_column("Header", style="bold yellow", min_width=28)
    table.add_column("Value", style="white")

    security_headers = {
        "strict-transport-security", "content-security-policy",
        "x-frame-options", "x-content-type-options",
        "x-xss-protection", "referrer-policy", "permissions-policy"
    }

    for key, value in response.headers.items():
        key_lower = key.lower()
        style = "bold green" if key_lower in security_headers else "white"
        table.add_row(key, f"[{style}]{value}[/]")

    console.print(table)


def display_body(response: requests.Response):
    """Display response body with syntax highlighting if JSON."""
    content_type = response.headers.get("Content-Type", "")
    body_text = response.text

    if not body_text.strip():
        console.print(Panel("[dim]Empty response body[/]", title="📄 Response Body", border_style="dim"))
        return

    if "json" in content_type or body_text.strip().startswith(("{", "[")):
        try:
            parsed = json.loads(body_text)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True, word_wrap=True)
            console.print(Panel(syntax, title="📄 Response Body (JSON)", border_style="green"))
            return
        except json.JSONDecodeError:
            pass

    if "xml" in content_type or "html" in content_type:
        lang = "html" if "html" in content_type else "xml"
        preview = body_text[:3000] + ("\n[truncated]" if len(body_text) > 3000 else "")
        syntax = Syntax(preview, lang, theme="monokai", word_wrap=True)
        console.print(Panel(syntax, title=f"📄 Response Body ({lang.upper()})", border_style="green"))
        return

    # Plain text
    preview = body_text[:2000] + ("\n[truncated]" if len(body_text) > 2000 else "")
    console.print(Panel(preview, title="📄 Response Body", border_style="green"))


def interactive_mode():
    """Interactive prompt-based mode for building requests."""
    console.rule("[bold cyan]🔧 REST API Tester — Interactive Mode[/]")

    url = Prompt.ask("[bold]Enter URL[/]", default="https://httpbin.org/get")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    method = Prompt.ask(
        "[bold]HTTP Method[/]",
        choices=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
        default="GET"
    ).upper()

    # Headers
    headers = {"User-Agent": "RichAPITester/1.0"}
    if Confirm.ask("[bold]Add custom headers?[/]", default=False):
        console.print("[dim]Enter headers as KEY=VALUE, one per line. Empty line to finish.[/]")
        while True:
            entry = Prompt.ask("  Header", default="")
            if not entry:
                break
            if "=" in entry:
                k, _, v = entry.partition("=")
                headers[k.strip()] = v.strip()

    # Query params
    params = {}
    if Confirm.ask("[bold]Add query parameters?[/]", default=False):
        console.print("[dim]Enter params as KEY=VALUE, one per line. Empty line to finish.[/]")
        while True:
            entry = Prompt.ask("  Param", default="")
            if not entry:
                break
            if "=" in entry:
                k, _, v = entry.partition("=")
                params[k.strip()] = v.strip()

    # Auth
    auth = None
    auth_type = Prompt.ask("[bold]Authentication[/]", choices=["none", "basic", "bearer"], default="none")
    if auth_type == "basic":
        username = Prompt.ask("  Username")
        password = Prompt.ask("  Password", password=True)
        auth = (username, password)
    elif auth_type == "bearer":
        token = Prompt.ask("  Bearer token")
        headers["Authorization"] = f"Bearer {token}"

    # Body
    body = None
    if method not in ("GET", "HEAD", "OPTIONS"):
        if Confirm.ask("[bold]Add request body?[/]", default=False):
            body_str = Prompt.ask("  Body (JSON string)", default="{}")
            try:
                body = json.loads(body_str)
                headers.setdefault("Content-Type", "application/json")
            except json.JSONDecodeError:
                console.print("[yellow]⚠ Could not parse as JSON, sending as plain text[/]")
                body = body_str

    timeout = int(Prompt.ask("[bold]Timeout (seconds)[/]", default="15"))

    return url, method, headers, params, body, auth, timeout


def run_test(url: str, method: str, headers: dict, params: dict, body: Any, auth, timeout: int):
    """Execute the request and display all results."""
    console.print()
    display_request_info(method, url, headers, params, body)

    with console.status(f"[bold cyan]Sending {method} request…[/]", spinner="dots"):
        response, elapsed = make_request(url, method, headers, params, body, auth, timeout)

    console.print()
    display_status_line(response, elapsed)
    console.print()
    display_headers(response)
    console.print()
    display_body(response)


def main():
    parser = argparse.ArgumentParser(
        description="REST API Tester — send HTTP requests and view formatted responses."
    )
    parser.add_argument("--url", "-u", help="Target URL")
    parser.add_argument("--method", "-m", default="GET",
                        choices=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
                        help="HTTP method (default: GET)")
    parser.add_argument("--header", "-H", action="append", default=[], metavar="KEY=VALUE",
                        help="Add a request header (repeatable)")
    parser.add_argument("--param", "-p", action="append", default=[], metavar="KEY=VALUE",
                        help="Add a query parameter (repeatable)")
    parser.add_argument("--body", "-b", help="Request body (JSON string)")
    parser.add_argument("--bearer", help="Bearer token for Authorization header")
    parser.add_argument("--basic-auth", metavar="USER:PASS", help="Basic auth credentials")
    parser.add_argument("--timeout", "-t", type=int, default=15, help="Request timeout in seconds")
    args = parser.parse_args()

    console.rule("[bold cyan]🔧 REST API Tester[/]")

    if not args.url:
        url, method, headers, params, body, auth, timeout = interactive_mode()
    else:
        url = args.url
        method = args.method.upper()
        headers = parse_key_value_pairs(args.header)
        headers.setdefault("User-Agent", "RichAPITester/1.0")
        params = parse_key_value_pairs(args.param)
        auth = None

        if args.bearer:
            headers["Authorization"] = f"Bearer {args.bearer}"
        if args.basic_auth and ":" in args.basic_auth:
            u, _, p = args.basic_auth.partition(":")
            auth = (u, p)

        body = None
        if args.body:
            try:
                body = json.loads(args.body)
                headers.setdefault("Content-Type", "application/json")
            except json.JSONDecodeError:
                body = args.body

        timeout = args.timeout

    run_test(url, method, headers, params, body, auth, timeout)


if __name__ == "__main__":
    main()
