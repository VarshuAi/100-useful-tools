"""
Tool 95 - Memory Palace Builder
Associate facts with mental rooms to recall information.
"""
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# Simple storage in session
palace = {
    "Front Door": "Key Formula: E = mc2",
    "Living Room": "First 3 elements: Hydrogen, Helium, Lithium",
    "Kitchen": "Biology Tip: Powerhouse is Mitochondria"
}

def main():
    console.print("\n[bold yellow]🏛️  MEMORY PALACE BUILDER[/bold yellow]\n")
    
    while True:
        console.print("[1] Walk through Memory Palace")
        console.print("[2] Associate new fact with location")
        console.print("[3] Quit")
        choice = Prompt.ask("Choose option", choices=["1","2","3"], default="1")
        
        if choice == "1":
            table = Table(title="Your Memory Palace walkthrough")
            table.add_column("Mental Location", style="bold cyan")
            table.add_column("Associated Fact", style="yellow")
            
            for loc, fact in palace.items():
                table.add_row(loc, fact)
            console.print(table)
            
        elif choice == "2":
            loc = Prompt.ask("Enter room/location (e.g. Bathroom, Bedroom)")
            fact = Prompt.ask("Fact to associate with it")
            palace[loc] = fact
            console.print(f"[green]Associated fact successfully with {loc}![/green]\n")
        else:
            break

if __name__ == "__main__":
    main()
