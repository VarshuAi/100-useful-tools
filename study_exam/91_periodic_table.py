"""
Tool 91 - Interactive Periodic Table CLI
Look up elements in the periodic table by symbol or atomic number.
"""
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

elements = {
    "H": {"name": "Hydrogen", "num": 1, "mass": 1.008, "type": "Reactive Nonmetal"},
    "HE": {"name": "Helium", "num": 2, "mass": 4.0026, "type": "Noble Gas"},
    "LI": {"name": "Lithium", "num": 3, "mass": 6.94, "type": "Alkali Metal"},
    "BE": {"name": "Beryllium", "num": 4, "mass": 9.0122, "type": "Alkaline Earth Metal"},
    "B": {"name": "Boron", "num": 5, "mass": 10.81, "type": "Metalloid"},
    "C": {"name": "Carbon", "num": 6, "mass": 12.011, "type": "Reactive Nonmetal"},
    "N": {"name": "Nitrogen", "num": 7, "mass": 14.007, "type": "Reactive Nonmetal"},
    "O": {"name": "Oxygen", "num": 8, "mass": 15.999, "type": "Reactive Nonmetal"},
    "F": {"name": "Fluorine", "num": 9, "mass": 18.998, "type": "Reactive Nonmetal"},
    "NE": {"name": "Neon", "num": 10, "mass": 20.180, "type": "Noble Gas"},
    "NA": {"name": "Sodium", "num": 11, "mass": 22.990, "type": "Alkali Metal"},
    "MG": {"name": "Magnesium", "num": 12, "mass": 24.305, "type": "Alkaline Earth Metal"}
}

def main():
    console.print("\n[bold red]⚗️  INTERACTIVE PERIODIC TABLE[/bold red]\n")
    
    table = Table(title="Quick View: First 12 Elements")
    table.add_column("Symbol", style="bold yellow")
    table.add_column("Name", style="cyan")
    table.add_column("Atomic No.", justify="right", style="green")
    table.add_column("Atomic Mass", justify="right", style="magenta")
    table.add_column("Type", style="white")
    
    for sym, details in elements.items():
        table.add_row(sym, details['name'], str(details['num']), str(details['mass']), details['type'])
        
    console.print(table)
    
    query = Prompt.ask("\nSearch Element (Symbol, e.g. H, He, Li)").upper()
    if query in elements:
        e = elements[query]
        console.print(f"\n[bold green]Element details for {query}:[/bold green]")
        console.print(f"  Name: [cyan]{e['name']}[/cyan]")
        console.print(f"  Atomic Number: [cyan]{e['num']}[/cyan]")
        console.print(f"  Atomic Mass: [cyan]{e['mass']}[/cyan]")
        console.print(f"  Classification: [cyan]{e['type']}[/cyan]")
    else:
        console.print("[yellow]Element not in first 12 element database. Add to element dictionary for extended search.[/yellow]")

if __name__ == "__main__":
    main()
