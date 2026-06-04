"""
Tool 59 - Clipboard content formatter
Get current clipboard text, format it, and re-copy it.
"""
import pyperclip
import re
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold cyan]✏️  CLIPBOARD CONTENT FORMATTER[/bold cyan]\n")
    text = pyperclip.paste()
    if not text:
        console.print("[red]Clipboard is empty! Copy some text first.[/red]")
        return
        
    console.print("[cyan]Current Clipboard Content preview:[/cyan]")
    console.print(f"[dim]{text[:200]}...[/dim]\n")
    
    console.print("[1] Convert to UPPERCASE")
    console.print("[2] Convert to lowercase")
    console.print("[3] Convert to Title Case")
    console.print("[4] Remove all double spaces & clean whitespace")
    console.print("[5] Slugify (URL friendly: lower-case-with-hyphens)")
    
    choice = Prompt.ask("Select format option", choices=["1","2","3","4","5"])
    
    if choice == "1":
        formatted = text.upper()
    elif choice == "2":
        formatted = text.lower()
    elif choice == "3":
        formatted = text.title()
    elif choice == "4":
        formatted = re.sub(r'\s+', ' ', text).strip()
    else:
        # Slugify
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).lower().strip()
        formatted = re.sub(r'[\s-]+', '-', clean)
        
    pyperclip.copy(formatted)
    console.print("\n[green]Formatted text copied back to clipboard successfully![/green]")
    console.print(f"[dim]{formatted[:200]}...[/dim]")

if __name__ == "__main__":
    main()
