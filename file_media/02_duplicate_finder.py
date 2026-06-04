"""
Tool 02 - Duplicate File Finder & Cleaner
Scans folders recursively, finds exact duplicates by MD5, shows savings.
"""

import hashlib
import os
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt, Confirm

console = Console()

def md5(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates():
    console.print("\n[bold cyan]🔍 DUPLICATE FILE FINDER[/bold cyan]", justify="center")
    console.print("[dim]Find and remove exact duplicate files[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Scan folder", default=str(Path.home()))
    folder = Path(folder)
    if not folder.exists():
        console.print("[red]Folder not found![/red]")
        return

    all_files = list(folder.rglob("*"))
    all_files = [f for f in all_files if f.is_file()]
    console.print(f"[green]Scanning {len(all_files)} files...[/green]")

    hash_map = defaultdict(list)
    for f in track(all_files, description="Hashing files..."):
        try:
            h = md5(f)
            hash_map[h].append(f)
        except (PermissionError, OSError):
            pass

    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}

    if not duplicates:
        console.print("[bold green]🎉 No duplicates found! Your folder is clean.[/bold green]")
        return

    total_wasted = 0
    all_dupes = []

    table = Table(title=f"Found {len(duplicates)} duplicate groups", header_style="bold magenta")
    table.add_column("#", style="dim")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="yellow")
    table.add_column("Copies", style="red")

    for i, (h, paths) in enumerate(list(duplicates.items())[:30], 1):
        size = paths[0].stat().st_size
        wasted = size * (len(paths) - 1)
        total_wasted += wasted
        table.add_row(str(i), paths[0].name, f"{size/1024:.1f} KB", str(len(paths)))
        all_dupes.extend(paths[1:])  # Keep first, mark rest for deletion

    console.print(table)
    console.print(f"\n[bold red]💾 Wasted space: {total_wasted/1024/1024:.2f} MB[/bold red]")

    if Confirm.ask(f"\n[yellow]Delete {len(all_dupes)} duplicate files (keeping originals)?[/yellow]"):
        deleted = 0
        for f in all_dupes:
            try:
                f.unlink()
                deleted += 1
            except Exception as e:
                console.print(f"[red]Could not delete {f.name}: {e}[/red]")
        console.print(f"\n[bold green]✅ Deleted {deleted} duplicates, freed {total_wasted/1024/1024:.2f} MB![/bold green]")
    else:
        console.print("[yellow]No files deleted.[/yellow]")

if __name__ == "__main__":
    find_duplicates()
