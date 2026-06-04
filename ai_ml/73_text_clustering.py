"""
Tool 73 - Text Clustering
Cluster short sentences or keywords using TF-IDF + KMeans.
"""
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def main():
    console.print("\n[bold white]🗂️  TEXT CLUSTERING TOOL[/bold white]\n")
    
    default_texts = [
        "Python automation scripting is fun",
        "Deep learning and AI are changing the world",
        "How to build a web scraper in Python",
        "Machine learning algorithms for classification",
        "Simple script to automate files on desktop",
        "Neural networks for computer vision applications",
        "Data science and statistical analysis using pandas",
        "Automating tasks with windows powershell script"
    ]
    
    console.print("[dim]Sample Texts to Cluster:[/dim]")
    for i, t in enumerate(default_texts, 1):
        console.print(f"  {i}. {t}")
        
    k = int(Prompt.ask("\nEnter number of clusters (K)", default="2"))
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(default_texts)
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        kmeans.fit(X)
        labels = kmeans.labels_
        
        table = Table(title="Clustering Results")
        table.add_column("Cluster ID", style="bold yellow", justify="center")
        table.add_column("Sentences", style="cyan")
        
        clusters = {i: [] for i in range(k)}
        for txt, label in zip(default_texts, labels):
            clusters[label].append(txt)
            
        for cid, items in clusters.items():
            table.add_row(str(cid), "\n".join(f"- {x}" for x in items))
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Clustering requires scikit-learn. Error: {e}[/red]")
        # Mock group fallback
        console.print("\n[yellow]Fallback grouping:[/yellow]")
        for i, text in enumerate(default_texts):
            grp = "Cluster A" if "Python" in text or "automate" in text or "script" in text else "Cluster B"
            console.print(f"  {text} -> [bold green]{grp}[/bold green]")

if __name__ == "__main__":
    main()
