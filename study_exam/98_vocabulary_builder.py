"""
Tool 98 - Vocabulary Builder
Entrance exam vocabulary database and daily quiz.
"""
import random
from rich.console import Console
from rich.prompt import Prompt

console = Console()

vocab = {
    "Alacrity": "Brisk and cheerful readiness.",
    "Capricious": "Given to sudden and unaccountable changes of mood or behavior.",
    "Epistemic": "Relating to knowledge or the degree of its validation.",
    "Mitigate": "Make less severe, serious, or painful.",
    "Pragmatic": "Dealing with things sensibly and realistically based on practical factors."
}

def main():
    console.print("\n[bold magenta]📖 COMPETITIVE EXAM VOCAB BUILDER[/bold magenta]\n")
    console.print("Today's Curated Vocabulary:")
    
    for word, meaning in vocab.items():
        console.print(f"  [bold cyan]{word}[/bold cyan]: {meaning}")
        
    console.print("\n[1] Take quick quiz")
    console.print("[2] Exit")
    choice = Prompt.ask("Select", choices=["1","2"], default="1")
    
    if choice == "1":
        word = random.choice(list(vocab.keys()))
        meaning = vocab[word]
        
        console.print(f"\nWord: [yellow]{word}[/yellow]")
        ans = Prompt.ask("What is the meaning / definition?")
        console.print(f"\nOfficial Meaning: [cyan]'{meaning}'[/cyan]\n")

if __name__ == "__main__":
    main()
