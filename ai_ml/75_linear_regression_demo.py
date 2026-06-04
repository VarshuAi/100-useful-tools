"""
Tool 75 - Linear Regression Demo
Interactive fitting of linear regression line over custom data points.
"""
import numpy as np
import matplotlib.pyplot as plt
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold yellow]📉 LINEAR REGRESSION DEMO[/bold yellow]\n")
    
    # Simple data points
    console.print("Using data points relating Study Hours (X) and Test Scores (Y):")
    X = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    Y = np.array([52, 58, 63, 64, 72, 75, 80, 85, 89, 95])
    
    for x, y in zip(X, Y):
        console.print(f"  Study Hours: {x} -> Score: {y}")
        
    console.print("\nFitting linear regression line...")
    
    # Calculate fit line manually: y = mx + c
    n = len(X)
    m = (n * np.sum(X*Y) - np.sum(X)*np.sum(Y)) / (n * np.sum(X**2) - (np.sum(X))**2)
    c = (np.sum(Y) - m * np.sum(X)) / n
    
    # Predictions
    preds = m * X + c
    
    # Calculate R-squared
    ss_res = np.sum((Y - preds)**2)
    ss_tot = np.sum((Y - np.mean(Y))**2)
    r2 = 1 - (ss_res / ss_tot)
    
    console.print(f"\n[green]Equation of line:[/green] Y = [bold cyan]{m:.2f} * X + {c:.2f}[/bold cyan]")
    console.print(f"R-squared accuracy: [bold cyan]{r2:.4f}[/bold cyan]")
    
    plt.figure(figsize=(8, 5))
    plt.scatter(X, Y, color='red', label='Actual Scores')
    plt.plot(X, preds, color='blue', label=f'Fit Line (R²={r2:.2f})')
    plt.xlabel('Study Hours')
    plt.ylabel('Test Score')
    plt.title('Study Hours vs Test Score')
    plt.legend()
    plt.grid(True)
    
    out_file = "regression.png"
    plt.savefig(out_file)
    plt.close()
    console.print(f"\n[green]Regression plot saved to '{out_file}'[/green]\n")

if __name__ == "__main__":
    main()
