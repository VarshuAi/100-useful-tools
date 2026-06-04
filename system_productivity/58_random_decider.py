"""
Tool 58 - Random Decision Maker
Flip coin, roll dice, pick random option.
"""
import random
import time
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def flip_coin():
    console.print("[dim]Flipping...[/dim]")
    time.sleep(1)
    res = random.choice(["HEADS", "TAILS"])
    console.print(f"Result: [bold yellow]{res}[/bold yellow] 🪙")

def roll_dice():
    sides = int(Prompt.ask("Enter number of sides (d4, d6, d8, d10, d12, d20)", default="6"))
    console.print(f"[dim]Rolling d{sides}...[/dim]")
    time.sleep(1)
    res = random.randint(1, sides)
    console.print(f"Result: [bold yellow]{res}[/bold yellow] 🎲")

def pick_name():
    names_input = Prompt.ask("Enter options/names (comma-separated)")
    names = [n.strip() for n in names_input.split(",") if n.strip()]
    if not names:
        console.print("[red]No choices entered.[/red]")
        return
    console.print("[dim]Choosing...[/dim]")
    time.sleep(1.2)
    choice = random.choice(names)
    console.print(f"Selected option: [bold yellow]{choice}[/bold yellow] 🎉")

def main():
    console.print("\n[bold magenta]🎲 RANDOM DECISION MAKER[/bold magenta]\n")
    console.print("[1] Flip Coin 🪙")
    console.print("[2] Roll Dice 🎲")
    console.print("[3] Random Option/Name Picker")
    choice = Prompt.ask("Select tool", choices=["1","2","3"])
    
    if choice == "1":
        flip_coin()
    elif choice == "2":
        roll_dice()
    else:
        pick_name()

if __name__ == "__main__":
    main()
