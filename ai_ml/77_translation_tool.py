"""
Tool 77 - AI Translation Tool
Translate text to another language using Gemini AI.
"""
import os
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def translate(text, lang):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"[red]Error: GEMINI_API_KEY env var not set. Could not translate '{text}' to {lang} via AI.[/red]"
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Translate the following text to {lang}. Return ONLY the translated output: '{text}'"
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Translation Error: {e}[/red]"

def main():
    console.print("\n[bold cyan]🌍 AI TRANSLATION TOOL[/bold cyan]\n")
    text = Prompt.ask("Text to translate")
    lang = Prompt.ask("Target Language (e.g. Hindi, French, Spanish, German)", default="Hindi")
    
    console.print(f"[dim]Translating...[/dim]")
    res = translate(text, lang)
    console.print(f"\n[green]Translated text ({lang}):[/green] {res}\n")

if __name__ == "__main__":
    main()
