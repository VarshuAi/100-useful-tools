"""
Tool 18 - JSON Formatter & Validator
Format, validate, minify, and query JSON data.
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.syntax import Syntax
from rich.prompt import Prompt

console = Console()

def json_toolkit():
    console.print("\n[bold cyan]📋 JSON FORMATTER & VALIDATOR[/bold cyan]", justify="center")
    console.print("[dim]Format • Validate • Minify • Query JSON[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - Format/prettify JSON file")
    console.print("[cyan]2[/cyan] - Validate JSON")
    console.print("[cyan]3[/cyan] - Minify JSON")
    console.print("[cyan]4[/cyan] - Query value (simple dot notation)")
    console.print("[cyan]5[/cyan] - JSON ↔ Python dict converter")
    choice = Prompt.ask("Choose", choices=["1","2","3","4","5"])

    if choice in ["1","2","3","4"]:
        src = Prompt.ask("Source", choices=["file","paste"], default="file")
        if src == "file":
            fp = Path(Prompt.ask("JSON file path"))
            if not fp.exists():
                console.print("[red]File not found![/red]")
                return
            text = fp.read_text(encoding="utf-8")
        else:
            console.print("[dim]Paste JSON (type END on new line):[/dim]")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            text = "\n".join(lines)

        try:
            data = json.loads(text)
            console.print("[bold green]✅ Valid JSON![/bold green]")
        except json.JSONDecodeError as e:
            console.print(f"[bold red]❌ Invalid JSON: {e}[/bold red]")
            return

        if choice == "1":
            indent = int(Prompt.ask("Indent spaces", default="2"))
            formatted = json.dumps(data, indent=indent, ensure_ascii=False)
            syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
            if Prompt.ask("Save to file? (filename or blank)", default=""):
                out = Prompt.ask("Filename", default="formatted.json")
                Path(out).write_text(formatted, encoding="utf-8")
                console.print(f"[green]Saved to {out}[/green]")

        elif choice == "3":
            minified = json.dumps(data, separators=(",",":"), ensure_ascii=False)
            console.print(f"\n[cyan]Minified ({len(minified)} bytes):[/cyan]")
            console.print(minified[:500])
            out = Prompt.ask("Save to (blank=skip)", default="")
            if out:
                Path(out).write_text(minified, encoding="utf-8")
                console.print(f"[green]Saved to {out}[/green]")

        elif choice == "4":
            key_path = Prompt.ask("Key path (e.g. users.0.name)")
            try:
                result = data
                for key in key_path.split("."):
                    if key.isdigit():
                        result = result[int(key)]
                    else:
                        result = result[key]
                console.print(f"\n[bold green]Result:[/bold green] {json.dumps(result, indent=2)}")
            except (KeyError, IndexError, TypeError) as e:
                console.print(f"[red]Key not found: {e}[/red]")

    elif choice == "5":
        console.print("[dim]Paste Python dict repr (type END to finish):[/dim]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        try:
            import ast
            py_dict = ast.literal_eval("\n".join(lines))
            json_out = json.dumps(py_dict, indent=2, ensure_ascii=False)
            console.print("\n[bold cyan]JSON Output:[/bold cyan]")
            console.print(Syntax(json_out, "json", theme="monokai"))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    json_toolkit()
