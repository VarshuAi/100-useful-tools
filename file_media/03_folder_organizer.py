"""
Tool 03 - Smart Folder Organizer
Automatically sorts files in a folder into subfolders by type (images, docs, videos, etc.)
"""

import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

CATEGORIES = {
    "🖼️ Images":     [".jpg",".jpeg",".png",".gif",".bmp",".svg",".webp",".ico",".tiff"],
    "🎬 Videos":     [".mp4",".avi",".mkv",".mov",".wmv",".flv",".webm",".m4v"],
    "🎵 Audio":      [".mp3",".wav",".flac",".aac",".ogg",".m4a",".wma"],
    "📄 Documents":  [".pdf",".doc",".docx",".txt",".odt",".rtf",".md"],
    "📊 Spreadsheets": [".xls",".xlsx",".csv",".ods"],
    "📦 Archives":   [".zip",".rar",".7z",".tar",".gz",".bz2"],
    "💻 Code":       [".py",".js",".ts",".html",".css",".java",".cpp",".c",".go",".rs",".json",".xml",".yaml",".yml"],
    "📐 Executables":[".exe",".msi",".dmg",".deb",".rpm",".sh",".bat"],
    "🎮 3D/Design":  [".obj",".fbx",".blend",".psd",".ai",".sketch",".fig"],
}

def organize_folder():
    console.print("\n[bold cyan]📂 SMART FOLDER ORGANIZER[/bold cyan]", justify="center")
    console.print("[dim]Automatically sort your messy folders[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Folder to organize", default=str(Path.home() / "Downloads"))
    folder = Path(folder)
    if not folder.exists():
        console.print("[red]Folder not found![/red]")
        return

    files = [f for f in folder.iterdir() if f.is_file()]
    plan = {}  # file -> category folder

    for f in files:
        moved = False
        for category, exts in CATEGORIES.items():
            if f.suffix.lower() in exts:
                # Strip emoji for folder name
                cat_name = category.split(" ", 1)[1]
                plan[f] = folder / cat_name
                moved = True
                break
        if not moved:
            plan[f] = folder / "Misc"

    # Preview
    table = Table(title=f"Organization Plan - {len(files)} files", header_style="bold magenta")
    table.add_column("File", style="cyan", max_width=40)
    table.add_column("→ Destination Folder", style="green")
    for f, dest in list(plan.items())[:25]:
        table.add_row(f.name, dest.name)
    if len(plan) > 25:
        table.add_row(f"... +{len(plan)-25} more", "")
    console.print(table)

    if Confirm.ask(f"\n[yellow]Organize {len(files)} files into subfolders?[/yellow]"):
        moved_count = 0
        for f, dest in plan.items():
            dest.mkdir(exist_ok=True)
            target = dest / f.name
            if target.exists():
                # Avoid overwriting
                stem = f.stem
                i = 1
                while target.exists():
                    target = dest / f"{stem}_{i}{f.suffix}"
                    i += 1
            shutil.move(str(f), str(target))
            moved_count += 1
        console.print(f"\n[bold green]✅ Organized {moved_count} files![/bold green]")
    else:
        console.print("[yellow]Cancelled.[/yellow]")

if __name__ == "__main__":
    organize_folder()
