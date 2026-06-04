"""
Tool 71 - Smart Data Visualizer
Load a CSV file, analyze columns, and plot charts using matplotlib.
"""
import pandas as pd
import matplotlib.pyplot as plt
import os
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold cyan]📈 SMART DATA VISUALIZER[/bold cyan]\n")
    csv_path = Prompt.ask("Enter path to CSV file")
    
    if not os.path.exists(csv_path):
        console.print(f"[red]File not found: {csv_path}[/red]")
        return
        
    try:
        df = pd.read_csv(csv_path)
        console.print(f"\n[green]Loaded CSV successfully! {df.shape[0]} rows, {df.shape[1]} columns.[/green]")
        console.print("\n[bold]Columns available:[/bold]")
        for i, col in enumerate(df.columns):
            console.print(f"  [{i}] {col} ({df[col].dtype})")
            
        x_idx = int(Prompt.ask("\nSelect X-axis column index"))
        y_idx = int(Prompt.ask("Select Y-axis column index"))
        
        x_col = df.columns[x_idx]
        y_col = df.columns[y_idx]
        
        console.print("[1] Line Plot | [2] Bar Plot | [3] Scatter Plot | [4] Histogram")
        chart_type = Prompt.ask("Choose chart type", choices=["1","2","3","4"], default="1")
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == "1":
            plt.plot(df[x_col], df[y_col], marker='o', color='skyblue')
        elif chart_type == "2":
            plt.bar(df[x_col], df[y_col], color='lightgreen')
        elif chart_type == "3":
            plt.scatter(df[x_col], df[y_col], color='coral')
        else:
            plt.hist(df[y_col], bins=15, color='gold', edgecolor='black')
            plt.xlabel(y_col)
            
        plt.title(f"{y_col} vs {x_col}")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        out_img = "chart.png"
        plt.savefig(out_img)
        console.print(f"\n[green]Chart saved successfully to '{out_img}'![/green]\n")
        plt.close()
        
    except Exception as e:
        console.print(f"[red]Error visualising CSV data: {e}[/red]")

if __name__ == "__main__":
    main()
