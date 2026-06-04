"""
Tool 80 - Dataset Profiler
Generate a summary statistics and profiles report for CSV datasets.
"""
import os
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def main():
    console.print("\n[bold cyan]🔬 DATASET PROFILER[/bold cyan]\n")
    csv_path = Prompt.ask("Enter CSV file path")
    
    if not os.path.exists(csv_path):
        console.print(f"[red]File not found: {csv_path}[/red]")
        return
        
    try:
        df = pd.read_csv(csv_path)
        
        table = Table(title="Dataset Summary Statistics")
        table.add_column("Column Name", style="bold yellow")
        table.add_column("Data Type", style="cyan")
        table.add_column("Null Values", justify="right", style="red")
        table.add_column("Unique Values", justify="right", style="green")
        table.add_column("Mean/Freq", justify="right", style="magenta")
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            dtype = str(df[col].dtype)
            
            if pd.api.types.is_numeric_dtype(df[col]):
                mean_val = f"{df[col].mean():.2f}"
            else:
                mean_val = str(df[col].mode().iloc[0]) if not df[col].mode().empty else "N/A"
                
            table.add_row(col, dtype, str(null_count), str(unique_count), mean_val)
            
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to profile dataset: {e}[/red]")

if __name__ == "__main__":
    main()
