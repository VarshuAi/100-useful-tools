"""
Tool 57 - Live Countdown Timer
Countdown to target date/time, e.g. NEET 2026.
"""
import time
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live

console = Console()

def get_countdown(target_dt):
    diff = target_dt - datetime.now()
    if diff.total_seconds() <= 0:
        return "[bold red]TIME IS UP![/bold red]"
    
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"[bold yellow]{days}d {hours}h {minutes}m {seconds}s[/bold yellow]"

def main():
    console.print("\n[bold cyan]⏳ LIVE COUNTDOWN TIMER[/bold cyan]\n")
    
    console.print("[1] NEET 2026 Countdown (June 21, 2026)")
    console.print("[2] Custom target date")
    choice = Prompt.ask("Choose target", choices=["1", "2"], default="1")
    
    if choice == "1":
        target_str = "2026-06-21 09:00:00"
        target_name = "NEET 2026"
    else:
        target_str = Prompt.ask("Enter target date/time (YYYY-MM-DD HH:MM:SS)", default="2026-06-21 09:00:00")
        target_name = Prompt.ask("Target Name", default="Custom Target")
        
    try:
        target_dt = datetime.strptime(target_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        console.print("[red]Invalid date format. Expected: YYYY-MM-DD HH:MM:SS[/red]")
        return
        
    console.print(f"\n[bold green]Active countdown to: {target_name}[/bold green]")
    console.print("[dim]Press Ctrl+C to exit countdown[/dim]\n")
    
    try:
        with Live(get_countdown(target_dt), refresh_per_second=1, console=console) as live:
            while True:
                time.sleep(1)
                live.update(get_countdown(target_dt))
    except KeyboardInterrupt:
        console.print("\n[yellow]Countdown terminated.[/yellow]")

if __name__ == "__main__":
    main()
