"""
Tool 74 - Stock Analyzer
Analyze simple price charts, moving averages, and key stats of any stock.
"""
import os
import requests
import matplotlib.pyplot as plt
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()

def main():
    console.print("\n[bold green]📈 STOCK ANALYZER[/bold green]\n")
    ticker = Prompt.ask("Enter stock ticker symbol (e.g. AAPL, MSFT)", default="AAPL").upper()
    
    console.print(f"[cyan]Fetching simulated/mock historical data for {ticker}...[/cyan]")
    
    # Mock stock prices for robust execution without api keys
    import random
    base_price = 150.0 if ticker == "AAPL" else (400.0 if ticker == "MSFT" else 100.0)
    prices = []
    current = base_price
    for _ in range(60):
        current += random.uniform(-4, 4)
        prices.append(round(current, 2))
        
    # Calculate simple moving averages (SMA)
    sma_5 = []
    for i in range(len(prices)):
        if i < 4:
            sma_5.append(prices[i])
        else:
            sma_5.append(round(sum(prices[i-4:i+1])/5, 2))
            
    # Draw chart
    plt.figure(figsize=(10, 5))
    plt.plot(prices, label="Closing Price", color="blue")
    plt.plot(sma_5, label="5-Day SMA", color="orange", linestyle="--")
    plt.title(f"{ticker} Price History (Last 60 Days)")
    plt.xlabel("Days")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.grid(True)
    
    out_file = "stock_chart.png"
    plt.savefig(out_file)
    plt.close()
    
    table = Table(title=f"Stock Summary for {ticker}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Current Price", f"${prices[-1]}")
    table.add_row("60-Day High", f"${max(prices)}")
    table.add_row("60-Day Low", f"${min(prices)}")
    table.add_row("5-Day Average", f"${sma_5[-1]}")
    
    console.print(table)
    console.print(f"\n[green]Stock chart saved to '{out_file}'[/green]\n")

if __name__ == "__main__":
    main()
