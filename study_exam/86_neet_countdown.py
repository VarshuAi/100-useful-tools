"""
Tool 86 - NEET Exam Countdown & Daily Motivation Dashboard
Real-time countdown to NEET 2026 (June 21, 2026).
Daily motivation quote, study streak tracker, and today's focus areas.
Run: python 86_neet_countdown.py
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "neet_tracker.json"

NEET_DATE = datetime(2026, 6, 21, 10, 0, 0)  # NEET 2026 — June 21, 2026

# ── curated content ───────────────────────────────────────────────────────────

QUOTES = [
    ("Every expert was once a beginner.", "Helen Hayes"),
    ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("Medicine is not only a science; it is also an art.", "Paracelsus"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("The more that you read, the more things you will know.", "Dr. Seuss"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Study hard what interests you the most in the most undisciplined, irreverent and original manner possible.", "Richard Feynman"),
    ("Hard work beats talent when talent doesn't work hard.", "Tim Notke"),
    ("Your only limit is your mind.", "Anonymous"),
    ("The beautiful thing about learning is that no one can take it away from you.", "B.B. King"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Dream big, work hard, stay focused, and surround yourself with good people.", "Anonymous"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("Do not be embarrassed by your failures, learn from them and start again.", "Richard Branson"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Education is the passport to the future, for tomorrow belongs to those who prepare for it today.", "Malcolm X"),
    ("I am not a product of my circumstances. I am a product of my decisions.", "Stephen Covey"),
    ("The mind is not a vessel to be filled but a fire to be kindled.", "Plutarch"),
    ("A doctor saves lives, NEET saves your dream.", "Anonymous Aspirant"),
    ("Biology is the study of complicated things that give the appearance of having been designed for a purpose.", "Richard Dawkins"),
    ("Failure is the opportunity to begin again more intelligently.", "Henry Ford"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
    ("Life is 10% what happens to you and 90% how you react to it.", "Charles Swindoll"),
    ("The harder you work for something, the greater you'll feel when you achieve it.", "Anonymous"),
    ("Push yourself, because no one else is going to do it for you.", "Anonymous"),
    ("Wake up with determination. Go to bed with satisfaction.", "Anonymous"),
    ("It's not about having time, it's about making time.", "Anonymous"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ("NEET is not about intelligence alone, it's about discipline and consistency.", "Anonymous"),
]

STUDY_TIPS = [
    "🧬 Biology: Use diagrams and flowcharts for processes like cell division and respiration.",
    "⚗️ Chemistry: Balance all equations before attempting numerical problems.",
    "⚡ Physics: Master the concept first, then tackle numericals.",
    "📖 Read NCERT word-for-word for Biology — NEET follows it closely.",
    "🔁 Revise each chapter at least 3 times with increasing intervals.",
    "✍️ Write out formulas daily to reinforce memory through muscle memory.",
    "🎯 Attempt previous year NEET papers under timed conditions every weekend.",
    "💤 Sleep 7-8 hours — memory consolidation happens during sleep.",
    "🥗 Eat brain foods: nuts, fish, blueberries, dark chocolate in moderation.",
    "🧘 Take 5-minute breaks every 45 minutes (Pomodoro technique).",
    "📊 Track your weak areas; spend 60% time on weaknesses, 40% on strengths.",
    "🔖 Make short notes for each chapter after first reading.",
    "❓ Attempt at least 100 MCQs per day across subjects.",
    "🧪 For Organic Chemistry: master named reactions and mechanisms.",
    "🌿 Memorise plant families and their characteristics for NEET taxonomy.",
    "🔬 Know all diagrams in NCERT Biology — they appear directly in NEET.",
    "📐 For Physics, units and dimensions analysis helps verify answers.",
    "🔢 Learn periodic table trends — they appear every year in Chemistry.",
    "📝 Write mock tests in the same time slot as the actual exam (morning).",
    "💡 Teach what you learn — explaining concepts deepens understanding.",
]

DAILY_FOCUS = {
    0: ("Monday",    "Physics",   "Mechanics + Optics"),
    1: ("Tuesday",   "Chemistry", "Physical Chemistry + Equilibrium"),
    2: ("Wednesday", "Biology",   "Cell Biology + Genetics"),
    3: ("Thursday",  "Physics",   "Electrostatics + Modern Physics"),
    4: ("Friday",    "Chemistry", "Organic Chemistry + Reaction Mechanisms"),
    5: ("Saturday",  "Biology",   "Human Physiology + Plant Biology"),
    6: ("Sunday",    "Revision",  "Mock Test + All Subjects"),
}

AFFIRMATIONS = [
    "I am capable of achieving my dream of becoming a doctor.",
    "Every hour I study today brings me closer to MBBS.",
    "I understand Biology, Chemistry and Physics with clarity.",
    "I remain calm and focused during my exam.",
    "I am disciplined, consistent, and unstoppable.",
    "My preparation is thorough and I am ready to succeed.",
    "I have the intelligence, the will, and the dedication.",
    "I choose progress over perfection every single day.",
    "Setbacks are temporary; my goal is permanent.",
    "I believe in myself and my ability to crack NEET.",
]

# ── data helpers ──────────────────────────────────────────────────────────────

def load_tracker() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"streak": 0, "last_checkin": None, "hours_today": 0,
            "total_hours": 0, "checkins": [], "targets_done": 0}

def save_tracker(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_streak(data: dict):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if data["last_checkin"] == today:
        return  # already checked in today
    if data["last_checkin"] == yesterday:
        data["streak"] += 1
    elif data["last_checkin"] != today:
        data["streak"] = 1
    data["last_checkin"] = today
    if today not in data.get("checkins", []):
        data.setdefault("checkins", []).append(today)

# ── display ───────────────────────────────────────────────────────────────────

def show_dashboard(data: dict):
    now = datetime.now()
    delta = NEET_DATE - now
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    # Countdown panel
    countdown_text = (
        f"[bold red]🩺 NEET 2026 — June 21, 2026[/bold red]\n\n"
        f"[bold yellow]{'':>5}{days:>4}[/bold yellow] [dim]days[/dim]  "
        f"[bold yellow]{hours:02d}[/bold yellow] [dim]hrs[/dim]  "
        f"[bold yellow]{minutes:02d}[/bold yellow] [dim]min[/dim]  "
        f"[bold yellow]{seconds:02d}[/bold yellow] [dim]sec[/dim]"
    )

    # Quote
    today_seed = int(now.strftime("%j%Y"))
    quote, author = QUOTES[today_seed % len(QUOTES)]
    quote_text = f'[italic]"{quote}"[/italic]\n[dim]— {author}[/dim]'

    # Streak & stats
    streak_bar = "🔥" * min(data["streak"], 20)
    stats_text = (
        f"[bold]Study Streak:[/bold] [yellow]{data['streak']} day(s)[/yellow]  {streak_bar}\n"
        f"[bold]Hours Today:[/bold]  [cyan]{data.get('hours_today', 0):.1f}h[/cyan]\n"
        f"[bold]Total Hours:[/bold]  [green]{data.get('total_hours', 0):.1f}h[/green]"
    )

    # Daily focus
    weekday = now.weekday()
    day_name, focus_subject, focus_topics = DAILY_FOCUS[weekday]
    focus_text = (
        f"[bold]{day_name}'s Focus:[/bold]\n"
        f"[bold cyan]{focus_subject}[/bold cyan] — {focus_topics}"
    )

    # Tip and affirmation
    tip = STUDY_TIPS[today_seed % len(STUDY_TIPS)]
    affirmation = AFFIRMATIONS[today_seed % len(AFFIRMATIONS)]

    console.print()
    console.print(Panel(countdown_text, title="⏰ COUNTDOWN TO NEET 2026", border_style="red", padding=(1, 4)))
    console.print()

    col1 = Panel(quote_text, title="📣 Today's Quote", border_style="yellow", padding=(1, 2))
    col2 = Panel(stats_text, title="📊 Your Stats", border_style="green", padding=(1, 2))
    console.print(Columns([col1, col2]))
    console.print()

    console.print(Panel(focus_text, title="🎯 Today's Focus", border_style="cyan"))
    console.print(Panel(tip, title="💡 Study Tip", border_style="blue"))
    console.print(Panel(f"[bold green]{affirmation}[/bold green]", title="🌟 Daily Affirmation", border_style="magenta"))

def checkin(data: dict):
    console.print("\n[bold cyan]✅ DAILY CHECK-IN[/bold cyan]")
    update_streak(data)
    hours = float(Prompt.ask("Hours studied today", default="0"))
    data["hours_today"] = hours
    data["total_hours"] = data.get("total_hours", 0) + hours
    topics = Prompt.ask("Topics covered (brief note)", default="")
    if topics:
        today = datetime.now().strftime("%Y-%m-%d")
        data.setdefault("notes", {})[today] = topics
    save_tracker(data)
    console.print(f"[green]✅ Check-in saved! Streak: {data['streak']} day(s) 🔥[/green]")

def show_weekly_plan():
    console.print("\n[bold cyan]📅 WEEKLY STUDY PLAN[/bold cyan]\n")
    table = Table(box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Day", style="cyan", width=12)
    table.add_column("Subject", style="bold yellow", width=12)
    table.add_column("Focus Topics", style="white")
    for day_idx, (day_name, subject, topics) in DAILY_FOCUS.items():
        style = "on dark_green" if datetime.now().weekday() == day_idx else ""
        table.add_row(day_name, subject, topics, style=style)
    console.print(table)
    console.print("[dim]Today's row is highlighted in green.[/dim]")

def main():
    console.print(Panel.fit(
        "[bold red]🩺 NEET 2026 COUNTDOWN DASHBOARD[/bold red]\n"
        "[dim]Motivation · Streak · Daily Focus · Countdown[/dim]",
        border_style="red"
    ))
    data = load_tracker()

    menu = {
        "1": "Show Dashboard",
        "2": "Daily Check-In",
        "3": "Weekly Study Plan",
        "4": "Random Motivation Boost",
        "5": "Exit",
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, v in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {v}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "1":
            show_dashboard(data)
        elif choice == "2":
            checkin(data)
        elif choice == "3":
            show_weekly_plan()
        elif choice == "4":
            q, a = random.choice(QUOTES)
            tip = random.choice(STUDY_TIPS)
            aff = random.choice(AFFIRMATIONS)
            console.print(Panel(f'[italic]"{q}"[/italic]\n[dim]— {a}[/dim]', title="💬 Quote", border_style="yellow"))
            console.print(Panel(tip, title="💡 Tip", border_style="blue"))
            console.print(Panel(f"[green]{aff}[/green]", title="🌟 Affirmation", border_style="magenta"))
        elif choice == "5":
            console.print("[dim]You've got this! 🩺✨[/dim]")
            break

if __name__ == "__main__":
    main()
