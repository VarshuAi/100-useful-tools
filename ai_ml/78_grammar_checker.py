"""
Tool 78 - AI Grammar Checker
Find and explain grammatical errors using Gemini AI.
"""
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def check_grammar(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"[red]Error: GEMINI_API_KEY env var not set. Could not analyze writing via AI.[/red]"
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Correct the grammar of this text. Return the corrected version first, followed by a list of fixes/explanations: '{text}'"
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Grammar check error: {e}[/red]"

def main():
    console.print("\n[bold yellow]✍️  AI GRAMMAR CHECKER[/bold yellow]\n")
    text = Prompt.ask("Enter text to check")
    
    console.print(f"[dim]Analyzing writing...[/dim]")
    analysis = check_grammar(text)
    console.print("\n", Panel(analysis, title="Grammar & Style Report", expand=False))

if __name__ == "__main__":
    main()
