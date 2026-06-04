"""
Tool 90 - AI Revision Note Generator
Input a chapter name and get key points, formulas, and facts using Gemini.
"""
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def generate_notes(chapter):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"""[bold yellow]Revision Notes: {chapter}[/bold yellow] (Set GEMINI_API_KEY for AI version)

1. Key Concept: Memorize the definitions and basic equations first.
2. Formulas/Mnemonics: PMT (Project Management Triangle), VIP (Voltage, Current, Power).
3. Critical Fact: Double check units and exponents during calculations.
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Create a concise, structured revision sheet of study notes for competitive exams like NEET for the chapter '{chapter}'. Include key topics, 3 key formulas or equations, and 1 mnemonic memory aid."
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Failed to generate AI notes: {e}[/red]"

def main():
    console.print("\n[bold cyan]📖 AI REVISION NOTES GENERATOR[/bold cyan]\n")
    chapter = Prompt.ask("Enter chapter/topic name (e.g. Photoelectric Effect, Cell Cycle)", default="Cell Cycle")
    
    console.print(f"[cyan]Generating revision notes for {chapter}...[/cyan]")
    notes = generate_notes(chapter)
    console.print("\n", Panel(notes, title=f"Revision Cheat Sheet: {chapter}", expand=False))

if __name__ == "__main__":
    main()
