"""
Tool 15 - Smart Note Taker with Tags
Create, search, and organize notes with tags and timestamps.
"""

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()
NOTES_FILE = Path.home() / ".smart_notes.json"

def load_notes():
    if NOTES_FILE.exists():
        return json.loads(NOTES_FILE.read_text())
    return []

def save_notes(notes):
    NOTES_FILE.write_text(json.dumps(notes, indent=2))

def note_taker():
    notes = load_notes()
    
    while True:
        console.print("\n[bold cyan]📓 SMART NOTE TAKER[/bold cyan]", justify="center")
        console.print(f"[dim]{len(notes)} notes stored[/dim]\n", justify="center")

        console.print("[cyan]1[/cyan] - Add new note")
        console.print("[cyan]2[/cyan] - View all notes")
        console.print("[cyan]3[/cyan] - Search by keyword or tag")
        console.print("[cyan]4[/cyan] - Delete note")
        console.print("[cyan]5[/cyan] - Export to markdown")
        console.print("[cyan]0[/cyan] - Exit")

        choice = Prompt.ask("Choice", choices=["0","1","2","3","4","5"])

        if choice == "0":
            break

        elif choice == "1":
            title = Prompt.ask("📌 Title")
            console.print("[dim]Enter note content (type END on new line to finish):[/dim]")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            content = "\n".join(lines)
            tags_input = Prompt.ask("🏷️  Tags (comma separated)", default="")
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            
            note = {
                "id": len(notes) + 1,
                "title": title,
                "content": content,
                "tags": tags,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }
            notes.append(note)
            save_notes(notes)
            console.print(f"[bold green]✅ Note saved! ID: {note['id']}[/bold green]")

        elif choice == "2":
            if not notes:
                console.print("[yellow]No notes yet![/yellow]")
                continue
            table = Table(title="All Notes", box=box.ROUNDED, header_style="bold magenta")
            table.add_column("ID", style="dim", width=5)
            table.add_column("Title", style="cyan")
            table.add_column("Tags", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Preview", style="white", max_width=35)
            for n in notes:
                table.add_row(
                    str(n["id"]), n["title"],
                    ", ".join(n["tags"]) if n["tags"] else "-",
                    n["created"][:10],
                    n["content"][:35].replace("\n"," ")
                )
            console.print(table)
            
            view = Prompt.ask("View full note? (ID or blank)", default="")
            if view.strip():
                note = next((n for n in notes if str(n["id"]) == view), None)
                if note:
                    console.print(f"\n[bold cyan]# {note['title']}[/bold cyan]")
                    console.print(f"[dim]Tags: {', '.join(note['tags'])} | Created: {note['created'][:16]}[/dim]\n")
                    console.print(note["content"])

        elif choice == "3":
            query = Prompt.ask("🔍 Search keyword or #tag")
            is_tag = query.startswith("#")
            results = []
            for n in notes:
                if is_tag:
                    if query[1:].lower() in [t.lower() for t in n["tags"]]:
                        results.append(n)
                else:
                    if query.lower() in n["title"].lower() or query.lower() in n["content"].lower():
                        results.append(n)
            console.print(f"[green]Found {len(results)} notes[/green]")
            for n in results:
                console.print(f"\n[bold cyan]{n['id']}: {n['title']}[/bold cyan] [{', '.join(n['tags'])}]")
                console.print(f"  {n['content'][:100]}...")

        elif choice == "4":
            nid = Prompt.ask("Delete note ID")
            notes = [n for n in notes if str(n["id"]) != nid]
            save_notes(notes)
            console.print("[green]Note deleted![/green]")

        elif choice == "5":
            out = "my_notes.md"
            md = "# My Notes\n\n"
            for n in notes:
                md += f"## {n['title']}\n"
                md += f"> Tags: {', '.join(n['tags'])} | {n['created'][:10]}\n\n"
                md += n["content"] + "\n\n---\n\n"
            Path(out).write_text(md, encoding="utf-8")
            console.print(f"[bold green]✅ Exported to {out}![/bold green]")

if __name__ == "__main__":
    note_taker()
