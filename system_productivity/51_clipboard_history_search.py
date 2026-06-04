"""
Tool 51 - Clipboard History Search
Monitor and search historical items copied to your clipboard.
"""
import time
import pyperclip
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold magenta]📋 CLIPBOARD MONITOR & SEARCH[/bold magenta]")
    console.print("[dim]Press Ctrl+C to stop monitoring and enter search mode[/dim]\n")
    
    history = []
    last_text = pyperclip.paste()
    if last_text:
        history.append(last_text)
        console.print(f"[cyan]Added current clipboard:[/cyan] {last_text[:50]}...")
        
    try:
        while True:
            current_text = pyperclip.paste()
            if current_text and current_text != last_text:
                history.append(current_text)
                last_text = current_text
                console.print(f"[green]+ Clipboard item added:[/green] {current_text[:50]}...")
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Monitoring stopped. Clipboard Search Mode Activated.[/yellow]")
        
    while True:
        query = Prompt.ask("\nSearch clipboard history (or 'q' to quit)")
        if query.lower() == 'q':
            break
            
        results = [item for item in history if query.lower() in item.lower()]
        
        if not results:
            console.print("[red]No matches found.[/red]")
            continue
            
        table = Table(title=f"Search Results for '{query}'")
        table.add_column("No.", style="dim")
        table.add_column("Clip Content", style="cyan")
        
        for i, item in enumerate(results, 1):
            table.add_row(str(i), item[:80] + ("..." if len(item) > 80 else ""))
        console.print(table)
        
        copy_idx = Prompt.ask("Enter number to copy back to clipboard (or blank to search again)", default="")
        if copy_idx.isdigit():
            idx = int(copy_idx) - 1
            if 0 <= idx < len(results):
                pyperclip.copy(results[idx])
                console.print("[green]Copied back to clipboard![/green]")

if __name__ == "__main__":
    main()
