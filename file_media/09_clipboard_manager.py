"""
Tool 09 - Clipboard Manager
Track clipboard history, search past copies, paste any item.
"""

import time
import threading
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

try:
    import pyperclip
except ImportError:
    console.print("[red]Install pyperclip: pip install pyperclip[/red]")
    exit(1)

history = deque(maxlen=50)
running = True

def monitor_clipboard():
    last = ""
    while running:
        try:
            current = pyperclip.paste()
            if current and current != last:
                history.appendleft({"text": current, "time": time.strftime("%H:%M:%S")})
                last = current
        except Exception:
            pass
        time.sleep(0.5)

def clipboard_manager():
    global running
    console.print("\n[bold cyan]📋 CLIPBOARD MANAGER[/bold cyan]", justify="center")
    console.print("[dim]Track and search your clipboard history[/dim]", justify="center")
    console.print("[bold yellow]Monitoring clipboard... press Ctrl+C to stop[/bold yellow]\n")

    thread = threading.Thread(target=monitor_clipboard, daemon=True)
    thread.start()

    try:
        while True:
            console.clear()
            console.print("[bold cyan]📋 CLIPBOARD HISTORY[/bold cyan] (auto-refreshing)", justify="center")
            console.print("[dim]Press Ctrl+C to open interactive menu[/dim]\n")

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("#", style="dim", width=4)
            table.add_column("Time", style="cyan", width=10)
            table.add_column("Content", style="white", max_width=70)

            for i, item in enumerate(list(history)[:20], 1):
                preview = item["text"].replace("\n", " ").strip()
                table.add_row(str(i), item["time"], preview[:70])

            console.print(table)
            time.sleep(3)

    except KeyboardInterrupt:
        running = False
        console.print("\n\n[bold]📋 Clipboard Manager Menu[/bold]")
        console.print("[cyan]1[/cyan] - Paste item by number")
        console.print("[cyan]2[/cyan] - Search history")
        console.print("[cyan]3[/cyan] - Clear history")
        console.print("[cyan]4[/cyan] - Exit")

        choice = Prompt.ask("Choice", choices=["1","2","3","4"])

        if choice == "1":
            items = list(history)
            num = int(Prompt.ask("Item number")) - 1
            if 0 <= num < len(items):
                pyperclip.copy(items[num]["text"])
                console.print(f"[green]✅ Copied item #{num+1} to clipboard![/green]")
        
        elif choice == "2":
            query = Prompt.ask("Search term")
            results = [i for i in history if query.lower() in i["text"].lower()]
            for r in results[:10]:
                console.print(f"[cyan]{r['time']}[/cyan]: {r['text'][:80]}")
        
        elif choice == "3":
            history.clear()
            console.print("[green]History cleared![/green]")

if __name__ == "__main__":
    clipboard_manager()
