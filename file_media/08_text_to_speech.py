"""
Tool 08 - Text-to-Speech Converter
Convert any text or text file to an MP3 audio file.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def tts_tool():
    console.print("\n[bold cyan]🔊 TEXT-TO-SPEECH CONVERTER[/bold cyan]", justify="center")
    console.print("[dim]Convert text or files to audio[/dim]\n", justify="center")

    try:
        import pyttsx3
    except ImportError:
        console.print("[red]Install pyttsx3: pip install pyttsx3[/red]")
        return

    console.print("[cyan]1[/cyan] - Type text directly")
    console.print("[cyan]2[/cyan] - Read from text file")
    choice = Prompt.ask("Choose", choices=["1","2"])

    if choice == "1":
        text = Prompt.ask("Enter text to speak")
    else:
        filepath = Path(Prompt.ask("Text file path"))
        if not filepath.exists():
            console.print("[red]File not found![/red]")
            return
        text = filepath.read_text(encoding="utf-8")
        console.print(f"[green]Loaded {len(text)} characters[/green]")

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    console.print(f"\n[bold]Available voices:[/bold]")
    for i, v in enumerate(voices[:5]):
        console.print(f"  [cyan]{i}[/cyan] - {v.name}")

    voice_idx = int(Prompt.ask("Choose voice index", default="0"))
    rate = int(Prompt.ask("Speaking rate (words/min, 150=normal)", default="150"))
    volume = float(Prompt.ask("Volume (0.0-1.0)", default="1.0"))

    engine.setProperty('voice', voices[min(voice_idx, len(voices)-1)].id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)

    output = Prompt.ask("Save to file? (Enter filename or blank to just play)")
    
    if output.strip():
        if not output.endswith(".mp3"):
            output += ".mp3"
        engine.save_to_file(text, output)
        engine.runAndWait()
        console.print(f"[bold green]✅ Audio saved to: {output}[/bold green]")
    else:
        console.print("\n[bold green]🔊 Speaking...[/bold green]")
        engine.say(text)
        engine.runAndWait()
        console.print("[green]Done![/green]")

if __name__ == "__main__":
    tts_tool()
