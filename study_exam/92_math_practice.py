"""
Tool 92 - Math Practice Generator
Generates random mathematical problems at chosen difficulty.
"""
import random
import time
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold magenta]🔢 MATH PRACTICE GENERATOR[/bold magenta]\n")
    console.print("[1] Arithmetic (Basic)")
    console.print("[2] Algebra (Equations)")
    console.print("[3] Calculus (Derivatives)")
    
    choice = Prompt.ask("Choose category", choices=["1","2","3"])
    score = 0
    total = 3
    
    start_time = time.time()
    
    for i in range(total):
        if choice == "1":
            a = random.randint(10, 99)
            b = random.randint(10, 99)
            op = random.choice(['+', '-', '*'])
            ans = eval(f"{a} {op} {b}")
            prompt_str = f"Q{i+1}: {a} {op} {b} = ?"
        elif choice == "2":
            x = random.randint(1, 10)
            a = random.randint(2, 6)
            b = random.randint(1, 15)
            # ax + b = c
            c = a*x + b
            ans = x
            prompt_str = f"Q{i+1}: Solve for x: {a}x + {b} = {c}"
        else:
            # simple power rule derivatives: f(x) = ax^b => f'(x) = ab x^(b-1)
            a = random.randint(2, 5)
            b = random.randint(2, 4)
            ans = a * b
            prompt_str = f"Q{i+1}: What is coefficient of derivative f'(x) for f(x) = {a}x^{b} ?"
            
        user_ans = Prompt.ask(prompt_str)
        if user_ans.strip() and int(user_ans) == ans:
            console.print("[green]Correct![/green]")
            score += 1
        else:
            console.print(f"[red]Incorrect. The answer is {ans}[/red]")
            
    elapsed = time.time() - start_time
    console.print(f"\n[bold green]Session Completed![/bold green]")
    console.print(f"Score: {score}/{total} | Accuracy: {score/total*100:.0f}%")
    console.print(f"Time Taken: {elapsed:.1f} seconds")

if __name__ == "__main__":
    main()
