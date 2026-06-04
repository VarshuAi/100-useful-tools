"""
Tool 20 - Regex Tester & Extractor
Test regex patterns on text or files, extract all matches.
"""

import re
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

console = Console()

PRESETS = {
    "Email":      r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
    "URL":        r'https?://[^\s<>"]+',
    "Phone (IN)": r'(\+91[-\s]?)?[6-9]\d{9}',
    "IPv4":       r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
    "Date":       r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b',
    "Hex Color":  r'#(?:[0-9a-fA-F]{3}){1,2}\b',
    "JWT Token":  r'eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+',
    "Credit Card":r'\b(?:\d[ -]?){13,16}\b',
}

def regex_tester():
    console.print("\n[bold cyan]🔍 REGEX TESTER & EXTRACTOR[/bold cyan]", justify="center")
    console.print("[dim]Test patterns, extract matches from text or files[/dim]\n", justify="center")

    # Source
    src = Prompt.ask("Source", choices=["text","file"], default="text")
    if src == "text":
        console.print("[dim]Enter/paste text (type END to finish):[/dim]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        text = "\n".join(lines)
    else:
        fp = Path(Prompt.ask("File path"))
        if not fp.exists():
            console.print("[red]File not found![/red]")
            return
        text = fp.read_text(encoding="utf-8", errors="ignore")
        console.print(f"[green]Loaded {len(text)} chars[/green]")

    # Pattern
    console.print("\n[bold]Preset patterns:[/bold]")
    preset_list = list(PRESETS.keys())
    for i, name in enumerate(preset_list, 1):
        console.print(f"  [cyan]{i}[/cyan] - {name}")
    console.print(f"  [cyan]0[/cyan] - Custom pattern")

    pick = Prompt.ask("Choose", default="0")
    
    if pick == "0" or not pick.isdigit() or int(pick) > len(preset_list):
        pattern = Prompt.ask("Enter regex pattern")
        pattern_name = "Custom"
    else:
        pattern_name = preset_list[int(pick)-1]
        pattern = PRESETS[pattern_name]
        console.print(f"[dim]Pattern: {pattern}[/dim]")

    flags_input = Prompt.ask("Flags (i=ignore case, m=multiline, s=dotall)", default="")
    flags = 0
    if "i" in flags_input: flags |= re.IGNORECASE
    if "m" in flags_input: flags |= re.MULTILINE
    if "s" in flags_input: flags |= re.DOTALL

    try:
        compiled = re.compile(pattern, flags)
    except re.error as e:
        console.print(f"[bold red]Invalid regex: {e}[/bold red]")
        return

    matches = compiled.findall(text)
    all_matches = list(compiled.finditer(text))

    console.print(f"\n[bold green]Found {len(all_matches)} matches for '{pattern_name}'[/bold green]")

    if all_matches:
        table = Table(title="Matches", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("#", style="dim", width=5)
        table.add_column("Match", style="bold cyan")
        table.add_column("Position", style="dim")
        table.add_column("Line", style="dim")

        lines_list = text.split("\n")
        for i, m in enumerate(all_matches[:30], 1):
            # Find line number
            line_num = text[:m.start()].count("\n") + 1
            table.add_row(str(i), m.group(), f"{m.start()}-{m.end()}", str(line_num))
        
        if len(all_matches) > 30:
            table.add_row("...", f"+{len(all_matches)-30} more", "", "")
        console.print(table)

        if Confirm.ask("\nExtract unique matches to file?", default=False):
            unique = sorted(set(str(m.group()) for m in all_matches))
            out = Prompt.ask("Output file", default="matches.txt")
            Path(out).write_text("\n".join(unique), encoding="utf-8")
            console.print(f"[green]✅ {len(unique)} unique matches saved to {out}[/green]")

        # Replace mode
        if Confirm.ask("Replace matches with something?", default=False):
            replacement = Prompt.ask("Replace with")
            result = compiled.sub(replacement, text)
            out = Prompt.ask("Save result to", default="replaced.txt")
            Path(out).write_text(result, encoding="utf-8")
            console.print(f"[green]✅ Replaced and saved to {out}[/green]")

if __name__ == "__main__":
    regex_tester()
