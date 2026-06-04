"""
Tool 40 - News Aggregator
Fetch and aggregate news articles from multiple topics.
"""
import urllib.request
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def fetch_rss_headlines(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            root = ET.fromstring(response.read())
        
        articles = []
        for item in root.findall('.//item')[:5]:  # top 5 headlines per feed
            articles.append(item.findtext('title', 'No Title'))
        return articles
    except Exception:
        return []

def main():
    console.print("\n[bold green]📡 TOP NEWS AGGREGATOR[/bold green]\n")
    
    categories = {
        "World": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRW9JTEdnd0NEM1Z5YzJ4bGNtVnpkQ1l1YW5SMWVTZ0FQAQ?hl=en-US&gl=US&ceid=US:en",
        "Technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRW9JTEdnd0NEM1p5ZUhNeldDVXdhbkoxTkhSdmN5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
        "Science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRW9JTEdnd0NEM0p5ZUhNeldDVXdhbkoxTkhSdmN5Z0FQAQ?hl=en-US&gl=US&ceid=US:en",
        "Business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRW9JTEdnd0NEM0p5ZUhNeldDVXdhbkoxTkhSdmN5Z0FQAQ?hl=en-US&gl=US&ceid=US:en"
    }
    
    table = Table(title="Aggregated Top Headlines", show_lines=True)
    table.add_column("Category", style="bold magenta", width=15)
    table.add_column("Top Headline", style="cyan")
    
    for name, url in categories.items():
        console.print(f"[dim]Fetching {name} headlines...[/dim]")
        headlines = fetch_rss_headlines(url)
        for h in headlines:
            table.add_row(name, h)
            
    console.print("\n", table)

if __name__ == "__main__":
    main()
