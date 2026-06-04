"""
Tool 10 - File Size Analyzer & Disk Space Report
Visualize folder sizes, find large files, track disk usage.
"""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.prompt import Prompt
from rich import box

console = Console()

def get_size(path: Path) -> int:
    total = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for entry in path.rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except (PermissionError, OSError):
                pass
    except (PermissionError, OSError):
        pass
    return total

def human_size(n: int) -> str:
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def disk_analyzer():
    console.print("\n[bold cyan]💾 DISK SPACE ANALYZER[/bold cyan]", justify="center")
    console.print("[dim]Find large files and visualize folder sizes[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Analyze folder", default=str(Path.home()))
    folder = Path(folder)
    if not folder.exists():
        console.print("[red]Folder not found![/red]")
        return

    console.print("[cyan]1[/cyan] - Top 20 largest files")
    console.print("[cyan]2[/cyan] - Subfolder size breakdown")
    console.print("[cyan]3[/cyan] - File type distribution")
    console.print("[cyan]4[/cyan] - All of the above")
    choice = Prompt.ask("Choose", choices=["1","2","3","4"], default="4")

    if choice in ["1","4"]:
        console.print("\n[bold]🔍 Scanning for large files...[/bold]")
        all_files = []
        for f in folder.rglob("*"):
            try:
                if f.is_file():
                    all_files.append((f, f.stat().st_size))
            except:
                pass
        
        all_files.sort(key=lambda x: x[1], reverse=True)
        
        table = Table(title="Top 20 Largest Files", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("File", style="cyan")
        table.add_column("Size", style="bold yellow", justify="right")
        table.add_column("Path", style="dim", max_width=40)

        for i, (f, size) in enumerate(all_files[:20], 1):
            table.add_row(str(i), f.name, human_size(size), str(f.parent).replace(str(folder), "."))
        console.print(table)

    if choice in ["2","4"]:
        console.print("\n[bold]📂 Subfolder breakdown...[/bold]")
        subfolders = [d for d in folder.iterdir() if d.is_dir()]
        sizes = []
        for d in track(subfolders, description="Calculating..."):
            s = get_size(d)
            sizes.append((d.name, s))
        sizes.sort(key=lambda x: x[1], reverse=True)

        total = sum(s for _, s in sizes)
        table = Table(title="Subfolder Sizes", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Folder", style="cyan")
        table.add_column("Size", style="yellow", justify="right")
        table.add_column("% of Total", style="green", justify="right")
        table.add_column("Bar")

        for name, size in sizes[:15]:
            pct = (size/total*100) if total else 0
            bar = "█" * int(pct / 5)
            table.add_row(name, human_size(size), f"{pct:.1f}%", f"[cyan]{bar}[/cyan]")
        console.print(table)

    if choice in ["3","4"]:
        console.print("\n[bold]📊 File type distribution...[/bold]")
        ext_sizes = {}
        for f in folder.rglob("*"):
            try:
                if f.is_file():
                    ext = f.suffix.lower() or "(no ext)"
                    ext_sizes[ext] = ext_sizes.get(ext, 0) + f.stat().st_size
            except:
                pass
        
        sorted_exts = sorted(ext_sizes.items(), key=lambda x: x[1], reverse=True)
        table = Table(title="File Types by Size", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("Extension", style="cyan")
        table.add_column("Total Size", style="yellow", justify="right")
        table.add_column("Count", style="dim", justify="right")

        ext_counts = {}
        for f in folder.rglob("*"):
            if f.is_file():
                e = f.suffix.lower() or "(no ext)"
                ext_counts[e] = ext_counts.get(e, 0) + 1

        for ext, size in sorted_exts[:15]:
            table.add_row(ext, human_size(size), str(ext_counts.get(ext,0)))
        console.print(table)

if __name__ == "__main__":
    disk_analyzer()
