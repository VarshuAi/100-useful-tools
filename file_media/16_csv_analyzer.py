"""
Tool 16 - CSV Analyzer & Visualizer
Load CSV files, show stats, filter, sort, and plot data.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()

def csv_analyzer():
    console.print("\n[bold cyan]📊 CSV ANALYZER[/bold cyan]", justify="center")
    console.print("[dim]Explore, filter, and visualize CSV data[/dim]\n", justify="center")

    try:
        import pandas as pd
        import matplotlib.pyplot as plt
    except ImportError:
        console.print("[red]Install: pip install pandas matplotlib[/red]")
        return

    filepath = Path(Prompt.ask("📄 CSV file path"))
    if not filepath.exists():
        console.print("[red]File not found![/red]")
        return

    df = pd.read_csv(filepath)
    console.print(f"\n[green]Loaded: {len(df)} rows × {len(df.columns)} columns[/green]")
    console.print(f"[dim]Columns: {', '.join(df.columns)}[/dim]\n")

    while True:
        console.print("[cyan]1[/cyan] - Show first/last rows")
        console.print("[cyan]2[/cyan] - Statistics summary")
        console.print("[cyan]3[/cyan] - Filter rows")
        console.print("[cyan]4[/cyan] - Sort by column")
        console.print("[cyan]5[/cyan] - Plot column histogram")
        console.print("[cyan]6[/cyan] - Export filtered CSV")
        console.print("[cyan]0[/cyan] - Exit")
        choice = Prompt.ask("Choice", choices=["0","1","2","3","4","5","6"])

        if choice == "0":
            break

        elif choice == "1":
            n = int(Prompt.ask("How many rows?", default="5"))
            pos = Prompt.ask("Position", choices=["head","tail"], default="head")
            rows = df.head(n) if pos == "head" else df.tail(n)
            table = Table(title=f"{pos.capitalize()} {n} rows", box=box.ROUNDED, header_style="bold magenta")
            for col in df.columns:
                table.add_column(col, style="cyan", max_width=20)
            for _, row in rows.iterrows():
                table.add_row(*[str(v)[:20] for v in row.values])
            console.print(table)

        elif choice == "2":
            numeric = df.select_dtypes(include="number")
            if numeric.empty:
                console.print("[yellow]No numeric columns found.[/yellow]")
            else:
                stats = numeric.describe()
                table = Table(title="Statistical Summary", box=box.ROUNDED, header_style="bold magenta")
                table.add_column("Stat", style="dim")
                for col in stats.columns:
                    table.add_column(col, style="cyan", justify="right")
                for idx in stats.index:
                    table.add_row(idx, *[f"{v:.2f}" for v in stats.loc[idx]])
                console.print(table)

        elif choice == "3":
            col = Prompt.ask(f"Column to filter [{', '.join(df.columns)}]")
            op = Prompt.ask("Operator", choices=["==","!=",">","<","contains"])
            val = Prompt.ask("Value")
            try:
                if op == "==":
                    filtered = df[df[col].astype(str) == val]
                elif op == "!=":
                    filtered = df[df[col].astype(str) != val]
                elif op == ">":
                    filtered = df[pd.to_numeric(df[col], errors='coerce') > float(val)]
                elif op == "<":
                    filtered = df[pd.to_numeric(df[col], errors='coerce') < float(val)]
                elif op == "contains":
                    filtered = df[df[col].astype(str).str.contains(val, case=False, na=False)]
                console.print(f"[green]{len(filtered)} rows match[/green]")
                df = filtered
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

        elif choice == "4":
            col = Prompt.ask(f"Sort by column [{', '.join(df.columns)}]")
            asc = Prompt.ask("Order", choices=["asc","desc"], default="asc") == "asc"
            df = df.sort_values(col, ascending=asc)
            console.print(f"[green]Sorted by {col} ({'asc' if asc else 'desc'})[/green]")

        elif choice == "5":
            numeric_cols = list(df.select_dtypes(include="number").columns)
            if not numeric_cols:
                console.print("[yellow]No numeric columns![/yellow]")
                continue
            col = Prompt.ask(f"Column to plot [{', '.join(numeric_cols)}]")
            plt.figure(figsize=(10, 6))
            plt.style.use("dark_background")
            df[col].hist(bins=30, color="#58a6ff", edgecolor="white")
            plt.title(f"Distribution of {col}", color="white")
            plt.xlabel(col, color="white")
            plt.ylabel("Frequency", color="white")
            plt.tight_layout()
            plt.savefig(f"{col}_histogram.png", dpi=120)
            plt.show()
            console.print(f"[green]Saved histogram to {col}_histogram.png[/green]")

        elif choice == "6":
            out = Prompt.ask("Output filename", default="filtered_output.csv")
            df.to_csv(out, index=False)
            console.print(f"[bold green]✅ Exported {len(df)} rows to {out}[/bold green]")

if __name__ == "__main__":
    csv_analyzer()
