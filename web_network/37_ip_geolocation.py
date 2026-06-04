"""
Tool 37 - IP Geolocation
Retrieve geographical and ISP details of an IP or domain.
"""
import requests
import socket
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold cyan]📍 IP GEOLOCATION[/bold cyan]\n")
    query = Prompt.ask("Enter IP or Domain (leave empty for current public IP)", default="")
    
    ip_to_check = ""
    if query:
        # Resolve domain to IP if needed
        try:
            ip_to_check = socket.gethostbyname(query)
            console.print(f"[dim]Resolved {query} to {ip_to_check}[/dim]")
        except Exception:
            ip_to_check = query
            
    url = f"http://ip-api.com/json/{ip_to_check}"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if data.get('status') == 'fail':
            console.print(f"[red]Failed to get info: {data.get('message')}[/red]")
            return
            
        table = Table(title=f"IP Geolocation for {data.get('query')}")
        table.add_column("Property", style="bold cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Country", f"{data.get('country')} ({data.get('countryCode')})")
        table.add_row("Region", data.get('regionName'))
        table.add_row("City", data.get('city'))
        table.add_row("Zip Code", data.get('zip'))
        table.add_row("ISP", data.get('isp'))
        table.add_row("Org/Company", data.get('org'))
        table.add_row("Latitude", str(data.get('lat')))
        table.add_row("Longitude", str(data.get('lon')))
        table.add_row("Timezone", data.get('timezone'))
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error fetching IP geolocation: {e}[/red]")

if __name__ == "__main__":
    main()
