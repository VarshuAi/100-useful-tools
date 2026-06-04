"""
Tool 36 - Broken Link Checker
Scan a website and find broken or redirection links.
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import concurrent.futures

console = Console()

def check_link(link):
    try:
        resp = requests.head(link, timeout=5, allow_redirects=True)
        return link, resp.status_code
    except Exception:
        try:
            # Fallback to GET
            resp = requests.get(link, timeout=5)
            return link, resp.status_code
        except Exception as e:
            return link, 0

def main():
    console.print("\n[bold red]🔗 BROKEN LINK CHECKER[/bold red]\n")
    target_url = Prompt.ask("Enter URL to scan")
    
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url
        
    console.print(f"[cyan]Scraping links from {target_url}...[/cyan]")
    try:
        r = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(target_url, href)
            # Only check http/https links
            parsed = urlparse(full_url)
            if parsed.scheme in ('http', 'https'):
                links.add(full_url)
                
        console.print(f"[green]Found {len(links)} unique links. Checking status...[/green]")
        
        table = Table(title="Link Status Report")
        table.add_column("URL", style="dim", max_width=60)
        table.add_column("Status", justify="center")
        table.add_column("Details")
        
        # Parallel testing
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(check_link, list(links)[:30]) # check top 30
            
        for link, status in results:
            if status == 200:
                table.add_row(link, "[green]200 OK[/green]", "Healthy")
            elif status == 0:
                table.add_row(link, "[red]ERR[/red]", "Connection Failed")
            elif 300 <= status < 400:
                table.add_row(link, f"[yellow]{status}[/yellow]", "Redirect")
            else:
                table.add_row(link, f"[red]{status}[/red]", "Broken")
                
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error checking page links: {e}[/red]")

if __name__ == "__main__":
    main()
