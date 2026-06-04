"""
Tool 27 - URL Shortener & Expander
=====================================
Shorten and expand URLs using TinyURL (no API key required):
- Shorten a single URL interactively or via CLI
- Expand a short URL to reveal the final destination (follows redirects)
- Batch process a list of URLs from a file
- Copy results to clipboard (optional)
- Track history of shortened/expanded URLs

Usage:
    python 27_url_shortener.py
    python 27_url_shortener.py --shorten https://www.example.com/very/long/path
    python 27_url_shortener.py --expand https://tinyurl.com/abc123
    python 27_url_shortener.py --batch urls.txt --action shorten

Dependencies:
    pip install requests rich pyshorteners
"""

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

HISTORY_FILE = Path.home() / ".url_shortener_history.json"

# TinyURL API endpoint (free, no key needed)
TINYURL_API = "https://tinyurl.com/api-create.php"


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return []
    return []


def save_history(entry: dict):
    history = load_history()
    history.append(entry)
    history = history[-100:]
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2))
    except Exception:
        pass


def validate_url(url: str) -> str:
    """Ensure URL has a scheme."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return url


def shorten_url(url: str) -> str:
    """Shorten a URL using TinyURL."""
    url = validate_url(url)
    try:
        resp = requests.get(TINYURL_API, params={"url": url}, timeout=10)
        resp.raise_for_status()
        short = resp.text.strip()
        if short.startswith("http"):
            return short
        raise ValueError(f"Unexpected response: {short}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Cannot connect to TinyURL. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise TimeoutError("TinyURL request timed out.")


def expand_url(url: str) -> dict:
    """Follow redirects to find the final destination URL."""
    url = validate_url(url)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (URL-Expander/1.0)"}
        resp = requests.get(url, headers=headers, allow_redirects=True, timeout=15)
        return {
            "original": url,
            "final_url": resp.url,
            "status_code": resp.status_code,
            "hops": len(resp.history),
            "redirect_chain": [r.url for r in resp.history] + [resp.url],
        }
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Cannot connect to {url}")
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Request to {url} timed out")


def display_shorten_result(original: str, short: str):
    """Display a nicely formatted shorten result."""
    lines = [
        f"[bold]Original:[/] [dim]{original[:80]}{'…' if len(original) > 80 else ''}[/]",
        f"[bold]Short URL:[/] [bold cyan]{short}[/]",
        f"[bold]Characters saved:[/] [green]{len(original) - len(short)}[/]",
    ]
    console.print(Panel("\n".join(lines), title="[bold green]✂  URL Shortened", border_style="green"))


def display_expand_result(result: dict):
    """Display a nicely formatted expand result."""
    chain = result["redirect_chain"]
    lines = [
        f"[bold]Input URL:[/]   [dim]{result['original']}[/]",
        f"[bold]Final URL:[/]   [bold cyan]{result['final_url']}[/]",
        f"[bold]Status Code:[/] [green]{result['status_code']}[/]",
        f"[bold]Redirects:[/]   {result['hops']}",
    ]
    if len(chain) > 1:
        lines.append("")
        lines.append("[bold]Redirect Chain:[/]")
        for i, hop in enumerate(chain):
            arrow = "→ " if i > 0 else "  "
            lines.append(f"  [dim]{arrow}[/] {hop}")

    console.print(Panel("\n".join(lines), title="[bold blue]🔍 URL Expanded", border_style="blue"))


def batch_process(file_path: str, action: str):
    """Process multiple URLs from a file."""
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]✗ File not found:[/] {file_path}")
        sys.exit(1)

    urls = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not urls:
        console.print("[yellow]⚠ File is empty.[/]")
        return

    table = Table(
        title=f"{'📤 Shortened' if action == 'shorten' else '📥 Expanded'} URLs ({len(urls)} total)",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Original URL", style="dim", max_width=45)
    if action == "shorten":
        table.add_column("Short URL", style="bold cyan")
        table.add_column("Saved", style="green", justify="right")
    else:
        table.add_column("Final URL", style="bold cyan", max_width=50)
        table.add_column("Hops", style="yellow", justify="right")

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"{action.capitalize()}ing URLs…", total=len(urls))

        for i, url in enumerate(urls, 1):
            progress.update(task, description=f"Processing {i}/{len(urls)}: {url[:40]}…")
            try:
                if action == "shorten":
                    short = shorten_url(url)
                    saved = max(0, len(url) - len(short))
                    table.add_row(str(i), url, short, f"{saved:+d} chars")
                    save_history({"action": "shorten", "original": url, "result": short})
                else:
                    result = expand_url(url)
                    table.add_row(
                        str(i), url, result["final_url"],
                        str(result["hops"])
                    )
                    save_history({"action": "expand", "original": url, "result": result["final_url"]})
            except Exception as e:
                err_col = f"[red]Error: {str(e)[:40]}[/]"
                if action == "shorten":
                    table.add_row(str(i), url, err_col, "—")
                else:
                    table.add_row(str(i), url, err_col, "—")

            progress.advance(task)
            time.sleep(0.3)  # rate limit

    console.print(table)


def show_history():
    """Display URL history."""
    history = load_history()
    if not history:
        console.print("[yellow]No history found.[/]")
        return

    table = Table(
        title="📋 URL History",
        box=box.ROUNDED,
        border_style="yellow",
    )
    table.add_column("Action", width=8)
    table.add_column("Original", max_width=45)
    table.add_column("Result", style="cyan", max_width=45)

    for entry in reversed(history[-30:]):
        action_str = "[green]shorten[/]" if entry.get("action") == "shorten" else "[blue]expand[/]"
        table.add_row(action_str, entry.get("original", "?"), entry.get("result", "?"))

    console.print(table)


def interactive_mode():
    """Run interactively."""
    console.rule("[bold cyan]✂  URL Shortener & Expander[/]")

    while True:
        choice = Prompt.ask(
            "\n[bold]Choose action[/]",
            choices=["shorten", "expand", "history", "batch", "quit"],
            default="shorten"
        )

        if choice == "quit":
            break
        elif choice == "history":
            show_history()
        elif choice == "batch":
            file_path = Prompt.ask("[bold]Path to URL list file[/]")
            action = Prompt.ask("[bold]Action[/]", choices=["shorten", "expand"], default="shorten")
            batch_process(file_path, action)
        elif choice == "shorten":
            url = Prompt.ask("[bold]URL to shorten[/]")
            with console.status("Shortening…", spinner="dots"):
                try:
                    short = shorten_url(url)
                    save_history({"action": "shorten", "original": url, "result": short})
                    display_shorten_result(url, short)
                except Exception as e:
                    console.print(f"[bold red]✗ Error:[/] {e}")
        elif choice == "expand":
            url = Prompt.ask("[bold]URL to expand[/]")
            with console.status("Following redirects…", spinner="dots"):
                try:
                    result = expand_url(url)
                    save_history({"action": "expand", "original": url, "result": result["final_url"]})
                    display_expand_result(result)
                except Exception as e:
                    console.print(f"[bold red]✗ Error:[/] {e}")


def main():
    parser = argparse.ArgumentParser(
        description="URL shortener and expander using TinyURL."
    )
    parser.add_argument("--shorten", "-s", metavar="URL", help="Shorten a URL")
    parser.add_argument("--expand", "-e", metavar="URL", help="Expand/reveal a short URL")
    parser.add_argument("--batch", "-b", metavar="FILE", help="Process URLs from a file")
    parser.add_argument("--action", "-a", choices=["shorten", "expand"], default="shorten",
                        help="Action for batch processing (default: shorten)")
    parser.add_argument("--history", "-H", action="store_true", help="Show URL history")
    args = parser.parse_args()

    if args.history:
        console.rule("[bold cyan]✂  URL History[/]")
        show_history()
    elif args.shorten:
        console.rule("[bold cyan]✂  URL Shortener[/]")
        with console.status("Shortening…", spinner="dots"):
            try:
                short = shorten_url(args.shorten)
                save_history({"action": "shorten", "original": args.shorten, "result": short})
                display_shorten_result(args.shorten, short)
            except Exception as e:
                console.print(f"[bold red]✗ Error:[/] {e}")
                sys.exit(1)
    elif args.expand:
        console.rule("[bold cyan]🔍 URL Expander[/]")
        with console.status("Following redirects…", spinner="dots"):
            try:
                result = expand_url(args.expand)
                save_history({"action": "expand", "original": args.expand, "result": result["final_url"]})
                display_expand_result(result)
            except Exception as e:
                console.print(f"[bold red]✗ Error:[/] {e}")
                sys.exit(1)
    elif args.batch:
        console.rule(f"[bold cyan]✂  Batch {'Shortening' if args.action == 'shorten' else 'Expanding'}[/]")
        batch_process(args.batch, args.action)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
