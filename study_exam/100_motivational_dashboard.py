"""
Tool 100 - Ultimate Student Motivational Dashboard
Show studious metrics, countdown to NEET 2026, affirmations, and study quotes.
"""
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich import box

console = Console()

def main():
    # NEET 2026 target
    target_dt = datetime(2026, 6, 21, 9, 0, 0)
    diff = target_dt - datetime.now()
    days_left = diff.days if diff.total_seconds() > 0 else 0
    
    quotes = [
        "Believe you can and you're halfway there.",
        "Your focus determines your reality.",
        "Success is the sum of small efforts, repeated day in and day out.",
        "Strive for progress, not perfection."
    ]
    
    # Select quote
    import random
    quote = random.choice(quotes)
    
    header = Panel("[bold yellow]🌟 ULTIMATE STUDENT MOTIVATIONAL DASHBOARD 🌟[/bold yellow]", border_style="yellow", box=box.ROUNDED)
    
    stats_content = (
        f"[bold cyan]🎯 Exam Target:[/bold cyan] NEET 2026\n"
        f"[bold cyan]⏳ Days Remaining:[/bold cyan] [bold red]{days_left}[/bold red] days\n"
        f"[bold cyan]🔥 Current Study Streak:[/bold cyan] 5 Days\n"
        f"[bold cyan]📚 Today's Goal:[/bold cyan] 6 Hours Study"
    )
    stats_panel = Panel(stats_content, title="🚀 Studious Metrics", border_style="cyan")
    
    motivation_content = (
        f"[bold green]Daily Affirmation:[/bold green] I am fully capable of mastering Physics, Chemistry, and Biology!\n\n"
        f"[italic magenta]Quote of the Day:[/italic magenta]\n\"{quote}\""
    )
    motivation_panel = Panel(motivation_content, title="💡 Motivation Hub", border_style="magenta")
    
    console.print(header)
    console.print(stats_panel)
    console.print(motivation_panel)

if __name__ == "__main__":
    main()
