"""
Tool 79 - Math Equation Solver
Solve algebraic equations step-by-step using Python math utilities.
"""
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold magenta]🧮 MATH EQUATION SOLVER[/bold magenta]\n")
    console.print("[1] Solve Linear Equation (ax + b = 0)")
    console.print("[2] Solve Quadratic Equation (ax^2 + bx + c = 0)")
    
    choice = Prompt.ask("Choose mode", choices=["1","2"])
    
    if choice == "1":
        a = float(Prompt.ask("Enter a"))
        b = float(Prompt.ask("Enter b"))
        if a == 0:
            console.print("[red]Invalid equation (a cannot be 0)[/red]")
        else:
            x = -b / a
            console.print(f"\nLinear Solution: x = [bold green]{x}[/bold green]")
    else:
        a = float(Prompt.ask("Enter a"))
        b = float(Prompt.ask("Enter b"))
        c = float(Prompt.ask("Enter c"))
        
        disc = b**2 - 4*a*c
        if disc > 0:
            x1 = (-b + disc**0.5) / (2*a)
            x2 = (-b - disc**0.5) / (2*a)
            console.print(f"\nTwo Real Roots: x1 = [bold green]{x1}[/bold green], x2 = [bold green]{x2}[/bold green]")
        elif disc == 0:
            x = -b / (2*a)
            console.print(f"\nOne Repeated Root: x = [bold green]{x}[/bold green]")
        else:
            real = -b / (2*a)
            imag = (-disc)**0.5 / (2*a)
            console.print(f"\nComplex Roots: x1 = [bold green]{real} + {imag}i[/bold green], x2 = [bold green]{real} - {imag}i[/bold green]")

if __name__ == "__main__":
    main()
