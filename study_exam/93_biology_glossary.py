"""
Tool 93 - Biology Glossary
Search and test your knowledge on essential biology terms.
"""
import random
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

glossary = {
    "Mitochondria": "Organelle that converts chemical energy in food into usable ATP.",
    "Ribosome": "Small cellular structure composed of RNA and protein, site of protein synthesis.",
    "Mitosis": "Type of cell division resulting in two daughter cells with identical chromosomes.",
    "Meiosis": "Type of cell division producing four gamete cells, each with half the chromosomes.",
    "Chloroplast": "Plastid in green plant cells where photosynthesis takes place.",
    "Eukaryote": "Organism whose cells contain a membrane-bound nucleus and organelles.",
    "Prokaryote": "Single-celled organism without a membrane-bound nucleus or organelles.",
    "Enzyme": "Biological catalyst that accelerates chemical reactions in cells."
}

def main():
    console.print("\n[bold green]🧬 BIOLOGY GLOSSARY[/bold green]\n")
    console.print("[1] Search glossary definitions")
    console.print("[2] Take definitions quiz")
    choice = Prompt.ask("Choose mode", choices=["1","2"], default="1")
    
    if choice == "1":
        query = Prompt.ask("Search term (e.g. Mitochondria, Cell)").strip().title()
        if query in glossary:
            console.print(f"\n[bold cyan]{query}:[/bold cyan] {glossary[query]}\n")
        else:
            console.print("[yellow]Term not found. Showing all items in database:[/yellow]")
            table = Table(title="Biology Terms")
            table.add_column("Term", style="bold cyan")
            table.add_column("Definition", style="white")
            for k, v in glossary.items():
                table.add_row(k, v)
            console.print(table)
            
    else:
        # Quiz mode
        term = random.choice(list(glossary.keys()))
        defn = glossary[term]
        
        console.print(f"\n[bold]Definition Quiz:[/bold]")
        console.print(f"\nDefinition: [cyan]'{defn}'[/cyan]")
        ans = Prompt.ask("Which term fits this definition?")
        
        if ans.strip().lower() == term.lower():
            console.print("[green]Correct! Excellent![/green]\n")
        else:
            console.print(f"[red]Incorrect. The correct term was: {term}[/red]\n")

if __name__ == "__main__":
    main()
