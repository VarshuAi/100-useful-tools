"""
Tool 99 - Mind Dump / Brain Dump
Timed brain dump with automatic key concept extractor via AI.
"""
import os
import time
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def summarize_dump(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[bold yellow]Fallback Extracted Ideas:[/bold yellow] (Set GEMINI_API_KEY for AI analysis)\n- Key points: Read through text to find action items."
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Extract a bullet-point summary of key ideas and action items from this brain dump text: '{text}'"
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Error performing dump summary: {e}[/red]"

def main():
    console.print("\n[bold cyan]🧠 TIMED MIND DUMP & AI SUMMARY[/bold cyan]\n")
    duration = int(Prompt.ask("Enter dump duration in seconds", default="30"))
    
    console.print(f"\n[bold yellow]Starting {duration}s brain dump. Start typing your thoughts below and hit enter when finished...[/bold yellow]\n")
    time.sleep(1)
    
    start = time.time()
    notes = []
    while time.time() - start < duration:
        line = input()
        notes.append(line)
        
    dump_text = " ".join(notes)
    console.print("\n[green]Mind dump completed! Running summary analysis...[/green]")
    
    summary = summarize_dump(dump_text)
    console.print("\n", Panel(summary, title="AI Mind Dump Analysis", expand=False))

if __name__ == "__main__":
    main()
