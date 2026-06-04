"""
Tool 34 - Weather CLI
wttr.in powered text/ansi weather CLI (no API keys required).
"""
import requests
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold yellow]🌤️  WEATHER CLI[/bold yellow]")
    console.print("[dim]Uses wttr.in for beautiful weather details[/dim]\n")
    
    city = Prompt.ask("Enter City Name (leave empty for auto-location)", default="")
    
    # Using wttr.in format with ANSI colors
    url = f"https://wttr.in/{city}?An"
    
    console.print(f"[cyan]Retrieving weather for {city or 'current location'}...[/cyan]\n")
    
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'curl'})
        if resp.status_code == 200:
            # wttr.in returns direct ANSI text, we can output it directly
            console.print(resp.text)
        else:
            console.print(f"[red]Failed to get weather. Status: {resp.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]Error fetching weather: {e}[/red]")

if __name__ == "__main__":
    main()
