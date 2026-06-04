"""
Tool 97 - Study Error Log Analyzer
Record exam errors and track topics requiring revision.
"""
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

errors = [
    {"topic": "Physics - Optics", "err": "Sign convention error in focal length"},
    {"topic": "Chemistry - Thermodynamics", "err": "Forgot negative sign in free energy equation"},
    {"topic": "Biology - Genetics", "err": "Confused homozygous vs heterozygous cross ratio"}
]

def main():
    console.print("\n[bold red]❌ STUDY ERROR LOG ANALYZER[/bold red]\n")
    
    while True:
        console.print("[1] Review current mistake log")
        console.print("[2] Log a new error/mistake")
        console.print("[3] Exit")
        choice = Prompt.ask("Choose option", choices=["1","2","3"], default="1")
        
        if choice == "1":
            table = Table(title="Study Error & Correction Log")
            table.add_column("Topic/Subject", style="bold cyan")
            table.add_column("Mistake / Concept", style="yellow")
            
            for item in errors:
                table.add_row(item['topic'], item['err'])
            console.print(table)
            
        elif choice == "2":
            topic = Prompt.ask("Topic/Chapter name")
            err = Prompt.ask("Describe the mistake made")
            errors.append({"topic": topic, "err": err})
            console.print("[green]Mistake logged. Review regularly to avoid repeating![/green]\n")
        else:
            break

if __name__ == "__main__":
    main()
