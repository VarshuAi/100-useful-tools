"""
Tool 72 - Digit Classifier Demo
Train a simple KNN classifier on sklearn digits and classify an ASCII grid digit.
"""
import numpy as np
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold magenta]🔢 ASCII DIGIT CLASSIFIER DEMO[/bold magenta]")
    console.print("[dim]Draw an 8x8 pixel digit inside the console and watch AI classify it![/dim]\n")
    
    try:
        from sklearn import datasets
        from sklearn.neighbors import KNeighborsClassifier
        
        console.print("[cyan]Training K-Nearest Neighbors model on sklearn Digits dataset...[/cyan]")
        digits = datasets.load_digits()
        n_samples = len(digits.images)
        data = digits.images.reshape((n_samples, -1))
        
        clf = KNeighborsClassifier(n_neighbors=5)
        clf.fit(data, digits.target)
        console.print("[green]Model trained successfully![/green]\n")
        
    except Exception as e:
        console.print(f"[red]Could not load sklearn to train. Using fallback rule-based classifier. Error: {e}[/red]\n")
        clf = None
        
    console.print("Draw your digit below (8 rows of 8 chars. Use '.' for empty/black, '#' for drawn/white):")
    grid = []
    for r in range(8):
        row_str = Prompt.ask(f"Row {r+1} (e.g. ....#...)")
        # pad to 8
        row_str = (row_str + "........")[:8]
        # convert to values between 0 and 16
        vals = [16 if c == '#' else 0 for c in row_str]
        grid.append(vals)
        
    flat_grid = np.array(grid).reshape(1, -1)
    
    if clf:
        pred = clf.predict(flat_grid)[0]
        console.print(f"\n[bold yellow]Prediction:[/bold yellow] This looks like a [bold green]{pred}[/bold green]!")
    else:
        # Fallback prediction
        active_count = sum(sum(1 for val in r if val > 0) for r in grid)
        pred_fall = active_count % 10
        console.print(f"\n[bold yellow]Fallback Prediction:[/bold yellow] This looks like a [bold green]{pred_fall}[/bold green]!")

if __name__ == "__main__":
    main()
