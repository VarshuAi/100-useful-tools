"""
Tool 38 - HTTP Load Tester
Send concurrent requests to test server load capacity.
"""
import time
import requests
import threading
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress

console = Console()

def send_request(url, stats):
    start = time.time()
    try:
        r = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        stats['codes'].append(r.status_code)
        stats['latencies'].append(latency)
        if r.status_code == 200:
            stats['success'] += 1
        else:
            stats['failed'] += 1
    except Exception:
        stats['failed'] += 1

def main():
    console.print("\n[bold red]💥 HTTP LOAD TESTER[/bold red]\n")
    url = Prompt.ask("URL to test")
    num_reqs = int(Prompt.ask("Total number of requests", default="50"))
    concurrency = int(Prompt.ask("Concurrency (concurrent threads)", default="5"))
    
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    console.print(f"[cyan]Testing load on {url}...[/cyan]")
    
    stats = {
        'success': 0,
        'failed': 0,
        'latencies': [],
        'codes': []
    }
    
    threads = []
    start_time = time.time()
    
    with Progress() as progress:
        task = progress.add_task("[yellow]Sending requests...", total=num_reqs)
        
        for _ in range(0, num_reqs, concurrency):
            batch = []
            for _ in range(min(concurrency, num_reqs - progress.completed)):
                t = threading.Thread(target=send_request, args=(url, stats))
                batch.append(t)
                t.start()
                
            for t in batch:
                t.join()
                progress.advance(task)
                
    elapsed = time.time() - start_time
    
    # Calculate stats
    total = stats['success'] + stats['failed']
    avg_lat = sum(stats['latencies']) / len(stats['latencies']) if stats['latencies'] else 0
    rps = total / elapsed if elapsed > 0 else total
    
    console.print(f"\n[bold green]Load Test Completed![/bold green]")
    console.print(f"Total Requests: [yellow]{total}[/yellow]")
    console.print(f"Successful (200 OK): [green]{stats['success']}[/green]")
    console.print(f"Failed/Other: [red]{stats['failed']}[/red]")
    console.print(f"Average Latency: [cyan]{avg_lat:.1f} ms[/cyan]")
    console.print(f"Requests/Sec (RPS): [cyan]{rps:.2f}[/cyan]")
    console.print(f"Total Duration: [cyan]{elapsed:.2f} s[/cyan]")

if __name__ == "__main__":
    main()
