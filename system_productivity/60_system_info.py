"""
Tool 60 - System Info Report
Generates a complete OS, CPU, Memory, Disk and Python environment report.
"""
import os
import platform
import psutil
import sys
from rich.console import Console
from rich.table import Table

console = Console()

def get_size(bytes_val, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes_val < factor:
            return f"{bytes_val:.2f}{unit}{suffix}"
        bytes_val /= factor

def main():
    console.print("\n[bold magenta]🖥️  SYSTEM INFORMATION REPORT[/bold magenta]\n")
    
    table = Table(title="System & Hardware Specifications")
    table.add_column("Component", style="cyan")
    table.add_column("Details", style="yellow")
    
    # OS Info
    table.add_row("Operating System", f"{platform.system()} {platform.release()} ({platform.version()})")
    table.add_row("Machine / Arch", f"{platform.machine()} ({platform.architecture()[0]})")
    table.add_row("Node Name", platform.node())
    
    # CPU
    table.add_row("CPU Model", platform.processor() or "Unknown")
    table.add_row("CPU Cores (Logical)", str(psutil.cpu_count(logical=True)))
    table.add_row("CPU Cores (Physical)", str(psutil.cpu_count(logical=False)))
    
    # RAM
    svmem = psutil.virtual_memory()
    table.add_row("Total RAM", get_size(svmem.total))
    table.add_row("Available RAM", get_size(svmem.available))
    table.add_row("RAM Usage", f"{svmem.percent}%")
    
    # Disks
    partitions = psutil.disk_partitions()
    for partition in partitions[:2]: # show first 2 partitions max
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            table.add_row(f"Disk ({partition.device})", 
                          f"Total: {get_size(usage.total)} | Free: {get_size(usage.free)} | Used: {usage.percent}%")
        except Exception:
            pass
            
    # Python Env
    table.add_row("Python Executable", sys.executable)
    table.add_row("Python Version", sys.version.split()[0])
    
    console.print(table)

if __name__ == "__main__":
    main()
