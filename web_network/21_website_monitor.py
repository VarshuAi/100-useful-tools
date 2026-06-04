"""
Tool 21 - Website Health Monitor
Check uptime, response time, SSL, headers for multiple URLs.
"""

import time
import ssl
import socket
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

def check_ssl(hostname):
    try:
        ctx = ssl.create_default_context()
        conn = ctx.wrap_socket(socket.socket(), server_hostname=hostname)
        conn.settimeout(5)
        conn.connect((hostname, 443))
        cert = conn.getpeercert()
        expires = cert['notAfter']
        conn.close()
        return True, expires
    except:
        return False, None

def check_url(url: str) -> dict:
    try:
        import requests
        if not url.startswith(("http://","https://")):
            url = "https://" + url
        
        start = time.time()
        resp = requests.get(url, timeout=10, allow_redirects=True,
                           headers={"User-Agent": "HealthMonitor/1.0"})
        elapsed = (time.time() - start) * 1000  # ms
        
        # SSL check
        from urllib.parse import urlparse
        parsed = urlparse(url)
        ssl_ok, ssl_expires = (False, None)
        if url.startswith("https://"):
            ssl_ok, ssl_expires = check_ssl(parsed.hostname)
        
        return {
            "url": url,
            "status": resp.status_code,
            "ok": 200 <= resp.status_code < 400,
            "time_ms": round(elapsed, 1),
            "ssl": ssl_ok,
            "ssl_expires": ssl_expires,
            "server": resp.headers.get("Server", "?"),
            "content_type": resp.headers.get("Content-Type", "?").split(";")[0],
            "size_kb": round(len(resp.content) / 1024, 1),
            "redirects": len(resp.history),
        }
    except Exception as e:
        return {"url": url, "status": 0, "ok": False, "error": str(e), "time_ms": 0}

def website_monitor():
    console.print("\n[bold cyan]🌐 WEBSITE HEALTH MONITOR[/bold cyan]", justify="center")
    console.print("[dim]Check uptime, SSL, response time for URLs[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - Check single URL")
    console.print("[cyan]2[/cyan] - Check multiple URLs")
    console.print("[cyan]3[/cyan] - Continuous monitoring (ping every N seconds)")
    choice = Prompt.ask("Choose", choices=["1","2","3"])

    if choice == "1":
        url = Prompt.ask("🔗 URL to check")
        console.print(f"[dim]Checking {url}...[/dim]")
        r = check_url(url)
        
        table = Table(title=f"Health Report: {url}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")
        
        status_color = "green" if r.get("ok") else "red"
        table.add_row("Status", f"[{status_color}]{r.get('status', 'ERROR')}[/{status_color}]")
        if r.get("ok"):
            table.add_row("Response Time", f"{r['time_ms']} ms" + (" 🐢" if r['time_ms'] > 2000 else " ⚡"))
            table.add_row("SSL Valid", "✅ Yes" if r.get('ssl') else "❌ No")
            if r.get("ssl_expires"):
                table.add_row("SSL Expires", r["ssl_expires"])
            table.add_row("Server", r.get("server","?"))
            table.add_row("Content Type", r.get("content_type","?"))
            table.add_row("Page Size", f"{r.get('size_kb',0)} KB")
            table.add_row("Redirects", str(r.get("redirects",0)))
        else:
            table.add_row("Error", str(r.get("error","Unknown")))
        console.print(table)

    elif choice == "2":
        urls_input = Prompt.ask("URLs (comma separated)")
        urls = [u.strip() for u in urls_input.split(",")]
        
        table = Table(title="Batch Health Check", box=box.ROUNDED, header_style="bold magenta")
        table.add_column("URL", style="cyan", max_width=35)
        table.add_column("Status", justify="center")
        table.add_column("Time (ms)", style="yellow", justify="right")
        table.add_column("SSL", justify="center")
        table.add_column("Size", justify="right")

        for url in urls:
            console.print(f"[dim]Checking {url}...[/dim]", end="\r")
            r = check_url(url)
            status = f"[green]{r['status']}[/green]" if r.get('ok') else f"[red]{r.get('status','ERR')}[/red]"
            ssl = "✅" if r.get('ssl') else ("N/A" if not url.startswith("https") else "❌")
            table.add_row(url[:35], status, str(r.get('time_ms','-')), ssl, f"{r.get('size_kb','-')} KB")
        
        console.print(table)

    elif choice == "3":
        url = Prompt.ask("🔗 URL to monitor")
        interval = int(Prompt.ask("Check interval (seconds)", default="30"))
        console.print(f"\n[bold yellow]Monitoring {url} every {interval}s (Ctrl+C to stop)[/bold yellow]\n")
        
        results = []
        try:
            while True:
                r = check_url(url)
                ts = datetime.now().strftime("%H:%M:%S")
                status = "✅" if r.get("ok") else "❌"
                color = "green" if r.get("ok") else "red"
                console.print(f"[dim]{ts}[/dim] {status} [{color}]{r.get('status','ERR')}[/{color}] - {r.get('time_ms','-')}ms")
                results.append(r)
                time.sleep(interval)
        except KeyboardInterrupt:
            if results:
                ok_count = sum(1 for r in results if r.get("ok"))
                avg_time = sum(r.get("time_ms",0) for r in results) / len(results)
                uptime = ok_count / len(results) * 100
                console.print(f"\n[bold]📊 Session Stats:[/bold]")
                console.print(f"Uptime: [green]{uptime:.1f}%[/green] | Avg Response: {avg_time:.0f}ms | Checks: {len(results)}")

if __name__ == "__main__":
    website_monitor()
