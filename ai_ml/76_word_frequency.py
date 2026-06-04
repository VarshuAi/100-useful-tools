"""
Tool 76 - Word Frequency Analyzer
Analyze word occurrences in a text block, cleaning stopwords.
"""
import re
from collections import Counter
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold magenta]📊 WORD FREQUENCY ANALYZER[/bold magenta]\n")
    text = Prompt.ask("Paste your paragraph of text")
    
    # Clean text
    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    
    stopwords = {"the", "and", "a", "of", "to", "is", "in", "it", "that", "you", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i", "at", "be", "this", "have"}
    
    filtered_words = [w for w in words if w not in stopwords]
    
    counter = Counter(filtered_words)
    top_10 = counter.most_common(10)
    
    table = Table(title="Most Common Words (excluding stopwords)")
    table.add_column("Word", style="bold cyan")
    table.add_column("Frequency", style="yellow", justify="right")
    
    for word, count in top_10:
        table.add_row(word, str(count))
        
    console.print(table)
    console.print(f"\n[dim]Total words: {len(words)} | Unique (non-stop): {len(counter)}[/dim]")

if __name__ == "__main__":
    main()
