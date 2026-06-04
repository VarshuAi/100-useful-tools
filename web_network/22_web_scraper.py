"""
Tool 22 - Web Page Scraper
==========================
Scrapes a webpage and extracts structured data including:
- Page title and meta tags
- All headings (H1-H6)
- All hyperlinks (internal and external)
- All images with alt text
- Social media meta tags (Open Graph, Twitter Cards)

Usage:
    python 22_web_scraper.py
    python 22_web_scraper.py --url https://example.com
    python 22_web_scraper.py --url https://example.com --output results.json

Dependencies:
    pip install requests beautifulsoup4 rich
"""

import argparse
import json
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def fetch_page(url: str) -> tuple[BeautifulSoup, dict]:
    """Fetch a URL and return parsed BeautifulSoup + response metadata."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        with console.status(f"[bold cyan]Fetching {url}...", spinner="dots"):
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]✗ Connection error:[/] Could not reach {url}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        console.print(f"[bold red]✗ Timeout:[/] Request to {url} timed out after 15s")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]✗ HTTP Error:[/] {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    meta = {
        "status_code": response.status_code,
        "content_type": response.headers.get("Content-Type", "unknown"),
        "content_length": len(response.content),
        "encoding": response.encoding,
        "final_url": response.url,
    }
    return soup, meta


def extract_meta_tags(soup: BeautifulSoup) -> dict:
    """Extract standard and Open Graph meta tags."""
    meta_info = {}

    # Standard meta tags
    for tag in soup.find_all("meta"):
        name = tag.get("name") or tag.get("property") or tag.get("http-equiv")
        content = tag.get("content")
        if name and content:
            meta_info[name] = content

    return meta_info


def extract_headings(soup: BeautifulSoup) -> list[dict]:
    """Extract all headings with their level and text."""
    headings = []
    for level in range(1, 7):
        for tag in soup.find_all(f"h{level}"):
            text = tag.get_text(strip=True)
            if text:
                headings.append({"level": level, "text": text})
    return headings


def extract_links(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Extract all hyperlinks, classifying as internal or external."""
    base_domain = urlparse(base_url).netloc
    links = []
    seen = set()

    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        absolute = urljoin(base_url, href)
        if absolute in seen:
            continue
        seen.add(absolute)

        link_domain = urlparse(absolute).netloc
        link_type = "Internal" if link_domain == base_domain else "External"
        text = tag.get_text(strip=True) or "[no text]"

        links.append({
            "text": text[:60],
            "url": absolute,
            "type": link_type,
        })

    return links


def extract_images(soup: BeautifulSoup, base_url: str) -> list[dict]:
    """Extract all images with their src and alt attributes."""
    images = []
    for tag in soup.find_all("img", src=True):
        src = urljoin(base_url, tag["src"])
        alt = tag.get("alt", "").strip() or "[no alt]"
        images.append({"src": src, "alt": alt[:60]})
    return images


def display_overview(meta: dict, title: str, soup_meta: dict):
    """Display page overview panel."""
    lines = [
        f"[bold]Title:[/]        {title or '[none]'}",
        f"[bold]Status:[/]       [green]{meta['status_code']}[/]",
        f"[bold]Content-Type:[/] {meta['content_type']}",
        f"[bold]Size:[/]         {meta['content_length']:,} bytes",
        f"[bold]Encoding:[/]     {meta['encoding']}",
        f"[bold]Final URL:[/]    {meta['final_url']}",
    ]

    # Add common meta if present
    for key in ("description", "keywords", "author"):
        if key in soup_meta:
            lines.append(f"[bold]{key.capitalize()}:[/] {soup_meta[key][:80]}")

    console.print(Panel("\n".join(lines), title="[bold cyan]📄 Page Overview", border_style="cyan"))


def display_headings(headings: list[dict]):
    """Display headings table."""
    if not headings:
        console.print("[dim]No headings found.[/]")
        return

    table = Table(title="📑 Headings", box=box.ROUNDED, border_style="blue", show_lines=False)
    table.add_column("Level", style="bold magenta", width=7)
    table.add_column("Text", style="white")

    colors = {1: "bold red", 2: "bold yellow", 3: "bold green",
              4: "cyan", 5: "blue", 6: "dim"}

    for h in headings:
        level_str = f"H{h['level']}"
        table.add_row(
            f"[{colors[h['level']]}]{level_str}[/]",
            h["text"][:100]
        )

    console.print(table)


def display_links(links: list[dict]):
    """Display links table with pagination hint."""
    if not links:
        console.print("[dim]No links found.[/]")
        return

    show = links[:40]  # show first 40
    table = Table(
        title=f"🔗 Hyperlinks ({len(links)} total, showing {len(show)})",
        box=box.ROUNDED, border_style="green", show_lines=False
    )
    table.add_column("Type", width=9)
    table.add_column("Link Text", style="white", max_width=30)
    table.add_column("URL", style="cyan", max_width=70)

    for link in show:
        color = "green" if link["type"] == "Internal" else "yellow"
        table.add_row(
            f"[{color}]{link['type']}[/]",
            link["text"],
            link["url"]
        )

    console.print(table)
    if len(links) > 40:
        console.print(f"[dim]  … and {len(links) - 40} more links. Use --output to save all.[/]")


def display_images(images: list[dict]):
    """Display images table."""
    if not images:
        console.print("[dim]No images found.[/]")
        return

    show = images[:20]
    table = Table(
        title=f"🖼  Images ({len(images)} total, showing {len(show)})",
        box=box.ROUNDED, border_style="magenta", show_lines=False
    )
    table.add_column("Alt Text", style="italic", max_width=35)
    table.add_column("Source URL", style="cyan", max_width=80)

    for img in show:
        table.add_row(img["alt"], img["src"])

    console.print(table)
    if len(images) > 20:
        console.print(f"[dim]  … and {len(images) - 20} more images.[/]")


def display_meta_tags(soup_meta: dict):
    """Display meta tags table."""
    if not soup_meta:
        console.print("[dim]No meta tags found.[/]")
        return

    table = Table(title="🏷  Meta Tags", box=box.ROUNDED, border_style="yellow")
    table.add_column("Property / Name", style="bold yellow", max_width=30)
    table.add_column("Content", style="white", max_width=80)

    for key, value in list(soup_meta.items())[:30]:
        table.add_row(key, value[:100])

    console.print(table)


def scrape(url: str, output_path: str | None = None):
    """Main scraping logic."""
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    console.rule("[bold cyan]🕸  Web Page Scraper[/]")

    soup, meta = fetch_page(url)

    title = soup.title.get_text(strip=True) if soup.title else ""
    soup_meta = extract_meta_tags(soup)
    headings = extract_headings(soup)
    links = extract_links(soup, url)
    images = extract_images(soup, url)

    display_overview(meta, title, soup_meta)
    console.print()
    display_meta_tags(soup_meta)
    console.print()
    display_headings(headings)
    console.print()
    display_links(links)
    console.print()
    display_images(images)

    # Summary footer
    summary = (
        f"[bold]Headings:[/] {len(headings)}  "
        f"[bold]Links:[/] {len(links)}  "
        f"[bold]Images:[/] {len(images)}  "
        f"[bold]Meta tags:[/] {len(soup_meta)}"
    )
    console.print(Panel(summary, title="[bold green]✅ Summary", border_style="green"))

    # Save to file if requested
    if output_path:
        data = {
            "url": url,
            "title": title,
            "meta": meta,
            "meta_tags": soup_meta,
            "headings": headings,
            "links": links,
            "images": images,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        console.print(f"\n[bold green]💾 Results saved to:[/] {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Web page scraper — extract titles, links, images, headings, meta tags."
    )
    parser.add_argument("--url", "-u", help="URL to scrape")
    parser.add_argument("--output", "-o", help="Save results to JSON file", metavar="FILE")
    args = parser.parse_args()

    url = args.url
    if not url:
        url = Prompt.ask("[bold cyan]Enter URL to scrape[/]", default="https://example.com")

    scrape(url, output_path=args.output)


if __name__ == "__main__":
    main()
