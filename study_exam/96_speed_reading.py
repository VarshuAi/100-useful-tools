"""
Tool 96 - Speed Reading RSVP Trainer
Display words in a rapid serial visual presentation at configurable WPM.
"""
import time
import os
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold white]⚡ SPEED READING TRAINER[/bold white]\n")
    text = Prompt.ask("Enter or paste text to read", 
                      default="Rapid Serial Visual Presentation displays words one by one at high speed to train your brain to read faster and absorb information without subvocalization.")
    wpm = int(Prompt.ask("Words per Minute (WPM)", default="250"))
    
    delay = 60.0 / wpm
    words = text.split()
    
    console.print(f"\nReady? Starting in 3 seconds... WPM={wpm}")
    time.sleep(1)
    time.sleep(1)
    time.sleep(1)
    
    # clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    for word in words:
        # Pad and print centered
        console.print(f"\n\n\n[bold yellow]{word.center(40)}[/bold yellow]", justify="center")
        time.sleep(delay)
        os.system('cls' if os.name == 'nt' else 'clear')
        
    console.print("\n[green]Done! Practice regularly to improve speed.[/green]\n")

if __name__ == "__main__":
    main()
