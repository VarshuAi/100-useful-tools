"""
Tool 39 - Tech Stack Detector
Analyze web pages to identify backend technology, frameworks, and analytics.
"""
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold green]🔬 TECH STACK DETECTOR[/bold green]\n")
    url = Prompt.ask("Enter URL to detect stack")
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    console.print(f"[dim]Analyzing headers and scripts from {url}...[/dim]")
    
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        headers = r.headers
        soup = BeautifulSoup(r.text, 'html.parser')
        
        detected = []
        
        # Analyze headers
        server = headers.get('Server', '').lower()
        if 'cloudflare' in server:
            detected.append(("CDN/Security", "Cloudflare"))
        if 'nginx' in server:
            detected.append(("WebServer", "Nginx"))
        if 'apache' in server:
            detected.append(("WebServer", "Apache"))
            
        powered = headers.get('X-Powered-By', '').lower()
        if 'php' in powered:
            detected.append(("Backend Language", "PHP"))
        elif 'express' in powered:
            detected.append(("Backend Framework", "Express.js"))
            
        # Analyze scripts and html
        html_content = r.text.lower()
        
        # CMS
        if 'wp-content' in html_content:
            detected.append(("CMS", "WordPress"))
        elif 'shopify' in html_content:
            detected.append(("CMS", "Shopify"))
            
        # JS Frameworks / Libs
        scripts = [s.get('src', '').lower() for s in soup.find_all('script', src=True)]
        scripts_joined = " ".join(scripts)
        
        if 'react' in scripts_joined or 'react' in html_content:
            detected.append(("Frontend Library", "React"))
        if 'vue' in scripts_joined or 'vue' in html_content:
            detected.append(("Frontend Framework", "Vue.js"))
        if 'jquery' in scripts_joined or 'jquery' in html_content:
            detected.append(("Frontend Library", "jQuery"))
        if 'bootstrap' in html_content:
            detected.append(("CSS Framework", "Bootstrap"))
        if 'tailwind' in html_content:
            detected.append(("CSS Framework", "Tailwind CSS"))
            
        # Analytics
        if 'google-analytics' in html_content or 'gtag' in html_content:
            detected.append(("Analytics", "Google Analytics"))
            
        table = Table(title=f"Stack Detected on {url}")
        table.add_column("Category", style="cyan")
        table.add_column("Technology", style="bold yellow")
        
        for cat, tech in set(detected):
            table.add_row(cat, tech)
            
        if not detected:
            table.add_row("Unknown", "No clear technologies detected in body or headers.")
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error detecting tech stack: {e}[/red]")

if __name__ == "__main__":
    main()
