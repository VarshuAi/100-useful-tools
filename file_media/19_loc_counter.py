"""
Tool 19 - Code Line Counter
Count lines of code, comments, and blank lines across a project.
"""

import os
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box

console = Console()

COMMENT_CHARS = {
    ".py": "#", ".js": "//", ".ts": "//", ".java": "//",
    ".c": "//", ".cpp": "//", ".go": "//", ".rs": "//",
    ".rb": "#", ".sh": "#", ".bash": "#", ".r": "#",
    ".html": "<!--", ".css": "/*", ".php": "//",
}

def count_lines(filepath: Path):
    ext = filepath.suffix.lower()
    comment_char = COMMENT_CHARS.get(ext, "#")
    code = blank = comment = 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if not stripped:
                    blank += 1
                elif stripped.startswith(comment_char):
                    comment += 1
                else:
                    code += 1
    except:
        pass
    return code, comment, blank

def loc_counter():
    console.print("\n[bold cyan]📏 CODE LINE COUNTER[/bold cyan]", justify="center")
    console.print("[dim]Count LOC across your entire project[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Project folder", default=".")
    folder = Path(folder)
    
    exts_input = Prompt.ask("File extensions to count (e.g. py,js,ts or blank=all)", default="py,js,ts,java,cpp,c,go")
    target_exts = set("." + e.strip() for e in exts_input.split(",") if e.strip())
    
    exclude_dirs = {".git", "__pycache__", "node_modules", ".venv", "dist", "build", ".next"}

    stats = defaultdict(lambda: {"files": 0, "code": 0, "comment": 0, "blank": 0})
    
    all_files = []
    for f in folder.rglob("*"):
        if f.is_file() and f.suffix.lower() in target_exts:
            if not any(part in exclude_dirs for part in f.parts):
                all_files.append(f)

    console.print(f"[green]Found {len(all_files)} files to analyze...[/green]")
    
    for f in all_files:
        code, comment, blank = count_lines(f)
        ext = f.suffix.lower()
        stats[ext]["files"] += 1
        stats[ext]["code"] += code
        stats[ext]["comment"] += comment
        stats[ext]["blank"] += blank

    # Results table
    table = Table(title=f"Lines of Code - {folder}", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Language", style="cyan")
    table.add_column("Files", style="dim", justify="right")
    table.add_column("Code Lines", style="bold green", justify="right")
    table.add_column("Comments", style="yellow", justify="right")
    table.add_column("Blank", style="dim", justify="right")
    table.add_column("Total", style="bold white", justify="right")

    totals = {"files": 0, "code": 0, "comment": 0, "blank": 0}
    lang_map = {".py":"Python", ".js":"JavaScript", ".ts":"TypeScript", ".java":"Java",
                ".cpp":"C++", ".c":"C", ".go":"Go", ".rs":"Rust", ".html":"HTML",
                ".css":"CSS", ".php":"PHP", ".rb":"Ruby"}
    
    for ext, data in sorted(stats.items(), key=lambda x: -x[1]["code"]):
        total = data["code"] + data["comment"] + data["blank"]
        lang = lang_map.get(ext, ext)
        table.add_row(lang, str(data["files"]), str(data["code"]),
                      str(data["comment"]), str(data["blank"]), str(total))
        for k in totals:
            totals[k] += data[k]

    table.add_section()
    grand = totals["code"] + totals["comment"] + totals["blank"]
    table.add_row("[bold]TOTAL[/bold]", str(totals["files"]), str(totals["code"]),
                  str(totals["comment"]), str(totals["blank"]), str(grand), style="bold")
    
    console.print(table)
    
    if stats:
        most_lang = max(stats.items(), key=lambda x: x[1]["code"])
        console.print(f"\n[bold]Dominant language:[/bold] [cyan]{lang_map.get(most_lang[0], most_lang[0])}[/cyan] ({most_lang[1]['code']} code lines)")
        if grand > 0:
            pct = totals["comment"] / grand * 100
            console.print(f"[bold]Comment ratio:[/bold] {pct:.1f}% (ideal: 10-30%)")

if __name__ == "__main__":
    loc_counter()
