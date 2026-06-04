"""
Tool 53 - Startup Manager
List Windows Registry startup items.
"""
import sys
from rich.console import Console
from rich.table import Table

console = Console()

def main():
    console.print("\n[bold cyan]🚀 WINDOWS STARTUP MANAGER[/bold cyan]\n")
    
    if sys.platform != "win32":
        console.print("[red]This tool only supports Windows systems.[/red]")
        return
        
    import winreg
    
    run_paths = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "Current User Startup"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "System-Wide Startup (Read-Only)")
    ]
    
    table = Table(title="Registered Startup Apps")
    table.add_column("Source", style="cyan")
    table.add_column("App Name", style="bold yellow")
    table.add_column("Command Path", style="green")
    
    for hkey, path, source_name in run_paths:
        try:
            key = winreg.OpenKey(hkey, path, 0, winreg.KEY_READ)
            info = winreg.QueryInfoKey(key)
            for i in range(info[1]):
                name, val, _ = winreg.EnumValue(key, i)
                table.add_row(source_name, name, str(val))
            winreg.CloseKey(key)
        except PermissionError:
            table.add_row(source_name, "[red]Access Denied[/red]", "Run as administrator to inspect HKLM")
        except Exception as e:
            pass
            
    console.print(table)

if __name__ == "__main__":
    main()
