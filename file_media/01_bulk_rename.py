"""
Tool 01 - Bulk File Renamer
Rename hundreds of files at once with custom patterns, numbering, prefix/suffix, date stamps.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

def bulk_rename():
    console.print("\n[bold cyan]🔧 BULK FILE RENAMER[/bold cyan]", justify="center")
    console.print("[dim]Rename files with smart patterns[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Enter folder path", default=str(Path.home() / "Downloads"))
    folder = Path(folder)
    if not folder.exists():
        console.print(f"[red]Folder not found: {folder}[/red]")
        return

    files = [f for f in folder.iterdir() if f.is_file()]
    console.print(f"\n[green]Found {len(files)} files[/green]")

    console.print("\n[bold]Rename Modes:[/bold]")
    console.print("  [cyan]1[/cyan] - Add prefix/suffix")
    console.print("  [cyan]2[/cyan] - Sequential numbering (001, 002...)")
    console.print("  [cyan]3[/cyan] - Replace text in filename")
    console.print("  [cyan]4[/cyan] - Add date stamp")
    console.print("  [cyan]5[/cyan] - Change extension")

    mode = Prompt.ask("Choose mode", choices=["1","2","3","4","5"])

    preview = []

    ext_filter = Prompt.ask("Filter by extension (e.g. .jpg, leave blank for all)", default="")
    filtered = [f for f in files if f.suffix == ext_filter or ext_filter == ""]

    if mode == "1":
        prefix = Prompt.ask("Prefix (blank = none)", default="")
        suffix = Prompt.ask("Suffix before extension (blank = none)", default="")
        for f in filtered:
            new_name = f"{prefix}{f.stem}{suffix}{f.suffix}"
            preview.append((f.name, new_name))

    elif mode == "2":
        base = Prompt.ask("Base name", default="file")
        pad = int(Prompt.ask("Padding digits", default="3"))
        for i, f in enumerate(sorted(filtered), 1):
            new_name = f"{base}_{str(i).zfill(pad)}{f.suffix}"
            preview.append((f.name, new_name))

    elif mode == "3":
        find = Prompt.ask("Text to find")
        replace = Prompt.ask("Replace with")
        for f in filtered:
            new_stem = f.stem.replace(find, replace)
            preview.append((f.name, f"{new_stem}{f.suffix}"))

    elif mode == "4":
        stamp = datetime.now().strftime("%Y%m%d")
        pos = Prompt.ask("Position", choices=["prefix", "suffix"], default="prefix")
        for f in filtered:
            if pos == "prefix":
                new_name = f"{stamp}_{f.name}"
            else:
                new_name = f"{f.stem}_{stamp}{f.suffix}"
            preview.append((f.name, new_name))

    elif mode == "5":
        new_ext = Prompt.ask("New extension (e.g. .txt)")
        if not new_ext.startswith("."):
            new_ext = "." + new_ext
        for f in filtered:
            preview.append((f.name, f"{f.stem}{new_ext}"))

    # Show preview table
    table = Table(title="Preview", show_header=True, header_style="bold magenta")
    table.add_column("Original", style="red")
    table.add_column("New Name", style="green")
    for orig, new in preview[:20]:
        table.add_row(orig, new)
    if len(preview) > 20:
        table.add_row(f"... +{len(preview)-20} more", "...")
    console.print(table)

    if Confirm.ask("\n[bold yellow]Proceed with rename?[/bold yellow]"):
        renamed = 0
        for orig, new in preview:
            try:
                (folder / orig).rename(folder / new)
                renamed += 1
            except Exception as e:
                console.print(f"[red]Error renaming {orig}: {e}[/red]")
        console.print(f"\n[bold green]✅ Renamed {renamed} files successfully![/bold green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")

if __name__ == "__main__":
    bulk_rename()
