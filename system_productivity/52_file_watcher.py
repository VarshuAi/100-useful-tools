"""
Tool 52 - File Watcher
Monitor directories and run commands on detection of file changes.
"""
import os
import time
import sys
import subprocess
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def get_dir_state(path):
    state = {}
    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                fpath = os.path.join(root, file)
                try:
                    state[fpath] = os.stat(fpath).st_mtime
                except Exception:
                    pass
    except Exception:
        pass
    return state

def main():
    console.print("\n[bold cyan]👁️  FILE WATCHER[/bold cyan]\n")
    path = Prompt.ask("Folder path to watch", default=".")
    cmd = Prompt.ask("Command to run on change (leave blank for log only)", default="")
    
    if not os.path.exists(path):
        console.print(f"[red]Path does not exist: {path}[/red]")
        return
        
    console.print(f"[green]Watching '{os.path.abspath(path)}' for changes. Press Ctrl+C to exit...[/green]")
    
    old_state = get_dir_state(path)
    
    try:
        while True:
            time.sleep(1.5)
            new_state = get_dir_state(path)
            
            added = [f for f in new_state if f not in old_state]
            removed = [f for f in old_state if f not in new_state]
            modified = [f for f in new_state if f in old_state and new_state[f] != old_state[f]]
            
            if added or removed or modified:
                for f in added:
                    console.print(f"[green][+] File Created:[/green] {f}")
                for f in removed:
                    console.print(f"[red][-] File Deleted:[/red] {f}")
                for f in modified:
                    console.print(f"[yellow][*] File Modified:[/yellow] {f}")
                    
                if cmd:
                    console.print(f"[cyan]Running command: {cmd}...[/cyan]")
                    subprocess.run(cmd, shell=True)
                    
                old_state = new_state
    except KeyboardInterrupt:
        console.print("\n[yellow]File watcher stopped.[/yellow]")

if __name__ == "__main__":
    main()
