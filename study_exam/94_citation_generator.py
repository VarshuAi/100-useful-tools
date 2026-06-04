"""
Tool 94 - Citation Generator
Generates APA/MLA format reference citations.
"""
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def main():
    console.print("\n[bold magenta]📚 CITATION GENERATOR[/bold magenta]\n")
    
    author = Prompt.ask("Author Last Name, First Initial (e.g. Smith, J.)")
    year = Prompt.ask("Publication Year")
    title = Prompt.ask("Article/Book Title")
    publisher = Prompt.ask("Publisher / Journal Title")
    
    apa = f"{author} ({year}). *{title}*. {publisher}."
    mla = f"{author}. \"{title}.\" *{publisher}*, {year}."
    
    panel_content = (
        f"[bold cyan]APA Citation:[/bold cyan]\n{apa}\n\n"
        f"[bold cyan]MLA Citation:[/bold cyan]\n{mla}"
    )
    console.print("\n", Panel(panel_content, title="Formatted References", expand=False))

if __name__ == "__main__":
    main()
