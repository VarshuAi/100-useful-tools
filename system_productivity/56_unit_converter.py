"""
Tool 56 - Unit Converter
Interactive converter for standard scientific and computing units.
"""
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def length_convert():
    val = float(Prompt.ask("Enter value to convert"))
    console.print("Units: [1] Meters to Feet, [2] Feet to Meters, [3] Kilometers to Miles, [4] Miles to Kilometers")
    c = Prompt.ask("Choose conversion", choices=["1","2","3","4"])
    if c == "1":
        console.print(f"{val} m = [yellow]{val * 3.28084:.4f} ft[/yellow]")
    elif c == "2":
        console.print(f"{val} ft = [yellow]{val / 3.28084:.4f} m[/yellow]")
    elif c == "3":
        console.print(f"{val} km = [yellow]{val * 0.621371:.4f} miles[/yellow]")
    else:
        console.print(f"{val} miles = [yellow]{val / 0.621371:.4f} km[/yellow]")

def temp_convert():
    val = float(Prompt.ask("Enter value to convert"))
    console.print("Units: [1] C to F, [2] F to C")
    c = Prompt.ask("Choose conversion", choices=["1","2"])
    if c == "1":
        console.print(f"{val}°C = [yellow]{(val * 9/5) + 32:.2f}°F[/yellow]")
    else:
        console.print(f"{val}°F = [yellow]{(val - 32) * 5/9:.2f}°C[/yellow]")

def data_convert():
    val = float(Prompt.ask("Enter value to convert"))
    console.print("Units: [1] MB to GB, [2] GB to MB, [3] GB to TB, [4] TB to GB")
    c = Prompt.ask("Choose conversion", choices=["1","2","3","4"])
    if c == "1":
        console.print(f"{val} MB = [yellow]{val / 1024:.4f} GB[/yellow]")
    elif c == "2":
        console.print(f"{val} GB = [yellow]{val * 1024:.1f} MB[/yellow]")
    elif c == "3":
        console.print(f"{val} GB = [yellow]{val / 1024:.4f} TB[/yellow]")
    else:
        console.print(f"{val} TB = [yellow]{val * 1024:.1f} GB[/yellow]")

def main():
    console.print("\n[bold green]📐 UNIT CONVERTER[/bold green]\n")
    console.print("[1] Length / Distance")
    console.print("[2] Temperature")
    console.print("[3] Data storage")
    
    choice = Prompt.ask("Select category", choices=["1", "2", "3"])
    if choice == "1":
        length_convert()
    elif choice == "2":
        temp_convert()
    else:
        data_convert()

if __name__ == "__main__":
    main()
