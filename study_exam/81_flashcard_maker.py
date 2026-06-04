"""
Tool 81 - Flashcard Maker & Spaced Repetition Quiz
Create Q&A flashcard decks stored in JSON, quiz yourself with spaced
repetition logic (SM-2 algorithm), and track your scores over time.
Run: python 81_flashcard_maker.py
"""

import json
import os
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "flashcards_data.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def load_data() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"decks": {}}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def new_card_meta() -> dict:
    """SM-2 spaced repetition initial metadata."""
    return {
        "interval": 1,       # days until next review
        "ease": 2.5,         # ease factor
        "reps": 0,           # number of successful reps
        "next_review": datetime.now().isoformat(),
        "times_seen": 0,
        "times_correct": 0,
    }

def update_sm2(meta: dict, quality: int) -> dict:
    """Apply SM-2 algorithm. quality: 0=blackout, 1=wrong, 2=hard, 3=ok, 4=easy, 5=perfect."""
    if quality < 3:
        meta["reps"] = 0
        meta["interval"] = 1
    else:
        if meta["reps"] == 0:
            meta["interval"] = 1
        elif meta["reps"] == 1:
            meta["interval"] = 6
        else:
            meta["interval"] = math.ceil(meta["interval"] * meta["ease"])
        meta["reps"] += 1
    meta["ease"] = max(1.3, meta["ease"] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    meta["next_review"] = (datetime.now() + timedelta(days=meta["interval"])).isoformat()
    return meta

# ── deck management ───────────────────────────────────────────────────────────

def create_deck(data: dict):
    console.print("\n[bold cyan]📚 CREATE NEW DECK[/bold cyan]")
    name = Prompt.ask("Deck name (e.g. 'Biology - Cell')")
    if name in data["decks"]:
        console.print("[red]Deck already exists![/red]")
        return
    data["decks"][name] = {"cards": [], "created": datetime.now().isoformat()}
    save_data(data)
    console.print(f"[green]✅ Deck '[bold]{name}[/bold]' created![/green]")

def add_cards(data: dict):
    console.print("\n[bold cyan]➕ ADD FLASHCARDS[/bold cyan]")
    if not data["decks"]:
        console.print("[red]No decks found. Create one first.[/red]")
        return
    deck_name = _choose_deck(data)
    if not deck_name:
        return
    deck = data["decks"][deck_name]
    console.print(f"[dim]Adding cards to '[bold]{deck_name}[/bold]'. Type 'done' as question to stop.[/dim]\n")
    count = 0
    while True:
        q = Prompt.ask("[yellow]Question[/yellow]")
        if q.strip().lower() == "done":
            break
        a = Prompt.ask("[green]Answer[/green]")
        hint = Prompt.ask("[dim]Hint (optional, press Enter to skip)[/dim]", default="")
        card = {"id": len(deck["cards"]) + 1, "question": q, "answer": a, "hint": hint}
        card.update(new_card_meta())
        deck["cards"].append(card)
        count += 1
        console.print(f"[dim]Card #{card['id']} added.[/dim]\n")
    save_data(data)
    console.print(f"[green]✅ {count} card(s) added to '{deck_name}'.[/green]")

def list_decks(data: dict):
    if not data["decks"]:
        console.print("[yellow]No decks yet. Create one first.[/yellow]")
        return
    table = Table(title="📚 Your Flashcard Decks", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Deck Name", style="cyan")
    table.add_column("Cards", justify="center")
    table.add_column("Due Today", justify="center", style="yellow")
    table.add_column("Avg Accuracy", justify="center", style="green")
    for name, deck in data["decks"].items():
        cards = deck["cards"]
        now = datetime.now()
        due = sum(1 for c in cards if datetime.fromisoformat(c.get("next_review", now.isoformat())) <= now)
        seen = [c for c in cards if c.get("times_seen", 0) > 0]
        if seen:
            acc = sum(c["times_correct"] / c["times_seen"] for c in seen) / len(seen) * 100
            acc_str = f"{acc:.0f}%"
        else:
            acc_str = "—"
        table.add_row(name, str(len(cards)), str(due), acc_str)
    console.print(table)

def _choose_deck(data: dict) -> str | None:
    names = list(data["decks"].keys())
    for i, n in enumerate(names, 1):
        console.print(f"  [cyan]{i}[/cyan] - {n}")
    choice = Prompt.ask("Select deck number", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            return names[idx]
    except ValueError:
        pass
    console.print("[red]Invalid choice.[/red]")
    return None

# ── quiz ─────────────────────────────────────────────────────────────────────

def quiz_deck(data: dict):
    console.print("\n[bold cyan]🎯 QUIZ MODE[/bold cyan]")
    if not data["decks"]:
        console.print("[red]No decks found.[/red]")
        return
    deck_name = _choose_deck(data)
    if not deck_name:
        return
    mode = Prompt.ask("Mode", choices=["spaced", "random", "all"], default="spaced",
                      show_choices=True)
    deck = data["decks"][deck_name]
    cards = deck["cards"]
    now = datetime.now()

    if mode == "spaced":
        pool = [c for c in cards if datetime.fromisoformat(c.get("next_review", now.isoformat())) <= now]
        if not pool:
            console.print("[green]🎉 No cards due for review today! Great job.[/green]")
            return
    elif mode == "random":
        n = int(Prompt.ask("How many cards to practice?", default=str(min(10, len(cards)))))
        pool = random.sample(cards, min(n, len(cards)))
    else:
        pool = list(cards)

    random.shuffle(pool)
    console.print(f"\n[bold]Starting quiz: [cyan]{len(pool)}[/cyan] cards from '[bold]{deck_name}[/bold]'[/bold]\n")

    correct = 0
    for i, card in enumerate(pool, 1):
        console.print(Panel(f"[bold yellow]Q {i}/{len(pool)}:[/bold yellow]  {card['question']}",
                            border_style="yellow", title=deck_name))
        if card.get("hint"):
            show_hint = Confirm.ask("   Show hint?", default=False)
            if show_hint:
                console.print(f"   [dim]💡 Hint: {card['hint']}[/dim]")
        input("   [Press Enter to reveal answer]")
        console.print(Panel(f"[bold green]{card['answer']}[/bold green]", border_style="green", title="Answer"))
        console.print("[dim]Rate yourself: [bold]0[/bold]=Blackout  [bold]1[/bold]=Wrong  [bold]2[/bold]=Hard  [bold]3[/bold]=OK  [bold]4[/bold]=Easy  [bold]5[/bold]=Perfect[/dim]")
        q_str = Prompt.ask("Your score", choices=["0","1","2","3","4","5"], default="3")
        quality = int(q_str)
        card["times_seen"] = card.get("times_seen", 0) + 1
        if quality >= 3:
            card["times_correct"] = card.get("times_correct", 0) + 1
            correct += 1
        update_sm2(card, quality)
        console.print()

    save_data(data)
    acc = correct / len(pool) * 100
    color = "green" if acc >= 70 else "yellow" if acc >= 50 else "red"
    console.print(Panel(
        f"[bold]Score: [{color}]{correct}/{len(pool)} ({acc:.0f}%)[/{color}][/bold]\n"
        f"[dim]Cards updated with spaced repetition schedule.[/dim]",
        title="📊 Quiz Complete", border_style=color
    ))

def view_deck_cards(data: dict):
    console.print("\n[bold cyan]📋 VIEW DECK CARDS[/bold cyan]")
    if not data["decks"]:
        console.print("[yellow]No decks yet.[/yellow]")
        return
    deck_name = _choose_deck(data)
    if not deck_name:
        return
    cards = data["decks"][deck_name]["cards"]
    if not cards:
        console.print("[yellow]No cards in this deck.[/yellow]")
        return
    table = Table(title=f"Cards in '{deck_name}'", box=box.SIMPLE, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Question", style="bold", max_width=40)
    table.add_column("Answer", max_width=35)
    table.add_column("Accuracy", justify="center")
    table.add_column("Next Review", justify="center", style="yellow")
    for c in cards:
        seen = c.get("times_seen", 0)
        acc = f"{c.get('times_correct',0)/seen*100:.0f}%" if seen else "—"
        nr = datetime.fromisoformat(c.get("next_review", datetime.now().isoformat())).strftime("%d %b")
        table.add_row(str(c["id"]), c["question"][:40], c["answer"][:35], acc, nr)
    console.print(table)

# ── main ──────────────────────────────────────────────────────────────────────

def main():
    console.print(Panel.fit(
        "[bold cyan]🃏 FLASHCARD MAKER & SPACED REPETITION[/bold cyan]\n"
        "[dim]Create decks, add cards, quiz with SM-2 algorithm[/dim]",
        border_style="cyan"
    ))
    data = load_data()

    menu = {
        "1": ("Create new deck", create_deck),
        "2": ("Add cards to deck", add_cards),
        "3": ("Quiz yourself", quiz_deck),
        "4": ("List all decks", list_decks),
        "5": ("View cards in deck", view_deck_cards),
        "6": ("Exit", None),
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, (label, _) in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {label}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "6":
            console.print("[dim]Goodbye! Keep studying! 📖[/dim]")
            break
        _, fn = menu[choice]
        fn(data)

if __name__ == "__main__":
    main()
