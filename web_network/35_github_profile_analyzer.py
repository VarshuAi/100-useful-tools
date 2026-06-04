"""
Tool 35 - GitHub Profile Analyzer
Analyze public repositories, languages, stars, and details of any GitHub user.
"""
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from collections import Counter

console = Console()

def main():
    console.print("\n[bold white]🐙 GITHUB PROFILE ANALYZER[/bold white]\n")
    username = Prompt.ask("Enter GitHub username")
    
    console.print(f"[dim]Analyzing user: {username}...[/dim]")
    
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    
    try:
        user_resp = requests.get(user_url, timeout=10)
        if user_resp.status_code == 404:
            console.print("[red]User not found.[/red]")
            return
        elif user_resp.status_code != 200:
            console.print(f"[red]GitHub API Error: {user_resp.status_code}[/red]")
            return
            
        u = user_resp.json()
        repos_resp = requests.get(repos_url, timeout=10)
        repos = repos_resp.json() if repos_resp.status_code == 200 else []
        
        # Calculate stats
        total_stars = sum(r.get('stargazers_count', 0) for r in repos)
        total_forks = sum(r.get('forks_count', 0) for r in repos)
        languages = [r.get('language') for r in repos if r.get('language')]
        lang_counts = Counter(languages).most_common(3)
        
        panel_content = (
            f"[bold cyan]Name:[/bold cyan] {u.get('name', 'N/A')} (@{u.get('login')})\n"
            f"[bold cyan]Bio:[/bold cyan] {u.get('bio', 'No bio')}\n"
            f"[bold cyan]Public Repos:[/bold cyan] {u.get('public_repos')} | "
            f"[bold cyan]Followers:[/bold cyan] {u.get('followers')} | "
            f"[bold cyan]Following:[/bold cyan] {u.get('following')}\n"
            f"[bold cyan]Stars Received:[/bold cyan] ⭐ {total_stars} | "
            f"[bold cyan]Forks:[/bold cyan] 🍴 {total_forks}\n"
        )
        if lang_counts:
            langs = ", ".join(f"{l} ({c})" for l, c in lang_counts)
            panel_content += f"[bold cyan]Top Languages:[/bold cyan] {langs}"
            
        console.print(Panel(panel_content, title=f"GitHub Stats for {username}", expand=False))
        
        if repos:
            table = Table(title="Top Public Repositories (by Stars)")
            table.add_column("Repository", style="bold yellow")
            table.add_column("Language", style="cyan")
            table.add_column("Stars", justify="right", style="green")
            table.add_column("Forks", justify="right", style="magenta")
            
            sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:5]
            for r in sorted_repos:
                table.add_row(r['name'], r['language'] or 'None', str(r['stargazers_count']), str(r['forks_count']))
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error analyzing GitHub profile: {e}[/red]")

if __name__ == "__main__":
    main()
