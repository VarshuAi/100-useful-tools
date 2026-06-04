"""
Tool 33 - RSS/Atom Feed Reader
Parse news from any RSS URL and display headlines.
"""
import urllib.request
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import webbrowser

console = Console()

def parse_rss(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        if channel is None:
            return None, []
            
        title = channel.findtext('title', 'Unknown Feed')
        items = []
        for item in channel.findall('item')[:15]:  # limit to 15
            items.append({
                'title': item.findtext('title', 'No Title'),
                'link': item.findtext('link', ''),
                'pubDate': item.findtext('pubDate', 'No Date'),
                'description': item.findtext('description', '')[:100] + '...'
            })
        return title, items
    except Exception as e:
        console.print(f"[red]Error fetching RSS feed: {e}[/red]")
        return None, []

def main():
    console.print("\n[bold magenta]📰 RSS FEED READER[/bold magenta]\n")
    
    default_feeds = {
        "1": ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
        "2": ("NYT Technology", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
        "3": ("NASA Breaking News", "https://www.nasa.gov/rss/dyn/breaking_news.rss"),
    }
    
    for k, v in default_feeds.items():
        console.print(f"[{k}] {v[0]} ({v[1]})")
    console.print("[4] Enter custom RSS URL")
    
    choice = Prompt.ask("Select feed", choices=["1","2","3","4"], default="1")
    if choice == "4":
        url = Prompt.ask("Enter RSS URL")
    else:
        url = default_feeds[choice][1]
        
    console.print(f"[cyan]Fetching feed from {url}...[/cyan]")
    title, items = parse_rss(url)
    
    if not items:
        console.print("[red]No articles found.[/red]")
        return
        
    table = Table(title=f"Feed: {title}", show_lines=True)
    table.add_column("No.", style="dim", width=4)
    table.add_column("Article Title", style="bold cyan")
    table.add_column("Published Date", style="yellow")
    
    for i, item in enumerate(items, 1):
        table.add_row(str(i), item['title'], item['pubDate'])
        
    console.print(table)
    
    read_choice = Prompt.ask("Enter article number to open in browser (or 'q' to quit)", default="q")
    if read_choice.isdigit():
        idx = int(read_choice) - 1
        if 0 <= idx < len(items) and items[idx]['link']:
            webbrowser.open(items[idx]['link'])
            console.print(f"[green]Opened: {items[idx]['title']}[/green]")

if __name__ == "__main__":
    main()
