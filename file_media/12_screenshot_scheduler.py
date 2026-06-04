"""
Tool 12 - Screenshot Scheduler
Automatically take screenshots at intervals for time-lapses or monitoring.
"""

import time
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def screenshot_scheduler():
    console.print("\n[bold cyan]📸 SCREENSHOT SCHEDULER[/bold cyan]", justify="center")
    console.print("[dim]Auto-capture screenshots at set intervals[/dim]\n", justify="center")

    try:
        import pyautogui
    except ImportError:
        console.print("[red]Install pyautogui: pip install pyautogui[/red]")
        return

    output_dir = Prompt.ask("💾 Save screenshots to", default="screenshots")
    Path(output_dir).mkdir(exist_ok=True)

    interval = float(Prompt.ask("Interval between screenshots (seconds)", default="5"))
    max_shots = int(Prompt.ask("Max screenshots (0=unlimited)", default="0"))
    prefix = Prompt.ask("Filename prefix", default="screenshot")

    console.print(f"\n[bold green]📸 Starting scheduler (Ctrl+C to stop)[/bold green]")
    console.print(f"[dim]Interval: {interval}s | Max: {max_shots if max_shots else 'Unlimited'}[/dim]\n")

    count = 0
    try:
        while True:
            if max_shots and count >= max_shots:
                console.print("[yellow]Reached max screenshots![/yellow]")
                break

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            filepath = Path(output_dir) / filename
            
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))
            count += 1
            console.print(f"[cyan][{count}][/cyan] Captured: {filename}")
            
            time.sleep(interval)

    except KeyboardInterrupt:
        console.print(f"\n\n[bold green]✅ Done! Captured {count} screenshots in {output_dir}[/bold green]")

if __name__ == "__main__":
    screenshot_scheduler()
