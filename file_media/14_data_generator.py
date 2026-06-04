"""
Tool 14 - Random Data Generator
Generate fake but realistic test data: names, emails, addresses, IPs, etc.
"""

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import json, csv, random, string
from pathlib import Path

console = Console()

def random_name():
    first = ["Aarav","Arjun","Riya","Priya","Dev","Ananya","Rahul","Sanya","Karan","Diya",
             "James","Emma","Liam","Olivia","Noah","Ava","Elijah","Sophia","Lucas","Mia"]
    last = ["Sharma","Patel","Kumar","Singh","Gupta","Reddy","Smith","Johnson","Williams","Brown"]
    return f"{random.choice(first)} {random.choice(last)}"

def random_email(name):
    domains = ["gmail.com","yahoo.com","outlook.com","proton.me","example.com"]
    slug = name.lower().replace(" ",".")
    return f"{slug}{random.randint(1,999)}@{random.choice(domains)}"

def random_phone():
    return f"+91 {random.randint(70000,99999):05d} {random.randint(10000,99999):05d}"

def random_ip():
    return ".".join(str(random.randint(1,255)) for _ in range(4))

def random_address():
    streets = ["MG Road","Park Street","Gandhi Nagar","Nehru Colony","Tech Park Avenue"]
    cities = ["Bangalore","Mumbai","Delhi","Chennai","Hyderabad","Pune","Kolkata"]
    states = ["Karnataka","Maharashtra","Tamil Nadu","Telangana","West Bengal"]
    return f"{random.randint(1,999)}, {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)}"

def random_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(length))

def random_uuid():
    import uuid
    return str(uuid.uuid4())

def generate_records(n):
    records = []
    for _ in range(n):
        name = random_name()
        records.append({
            "id": random_uuid(),
            "name": name,
            "email": random_email(name),
            "phone": random_phone(),
            "ip": random_ip(),
            "address": random_address(),
            "password": random_password(),
            "age": random.randint(18, 65),
            "score": round(random.uniform(0, 100), 2)
        })
    return records

def data_generator():
    console.print("\n[bold cyan]🎲 RANDOM DATA GENERATOR[/bold cyan]", justify="center")
    console.print("[dim]Generate realistic test data for development[/dim]\n", justify="center")

    n = int(Prompt.ask("How many records?", default="10"))
    records = generate_records(n)

    # Preview table
    table = Table(title=f"Generated {n} Records (preview: first 5)", header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Email", style="green")
    table.add_column("Phone", style="yellow")
    table.add_column("Age", style="dim")
    table.add_column("IP", style="dim")

    for r in records[:5]:
        table.add_row(r["name"], r["email"], r["phone"], str(r["age"]), r["ip"])
    console.print(table)

    fmt = Prompt.ask("Export format", choices=["json","csv","none"], default="json")
    
    if fmt == "json":
        out = f"fake_data_{n}.json"
        with open(out, "w") as f:
            json.dump(records, f, indent=2)
        console.print(f"[bold green]✅ Saved {n} records to {out}[/bold green]")
    elif fmt == "csv":
        out = f"fake_data_{n}.csv"
        with open(out, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        console.print(f"[bold green]✅ Saved {n} records to {out}[/bold green]")

if __name__ == "__main__":
    data_generator()
