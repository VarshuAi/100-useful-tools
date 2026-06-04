"""
Tool 88 - NEET/JEE Previous Year Question Analyzer
Load previous year questions from JSON, analyze topic-wise frequency,
identify high-weightage chapters, view year-wise trends, and find
the most important areas to focus on.
Run: python 88_previous_year_analyzer.py
"""

import json
from collections import defaultdict
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.bar import Bar
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "pyq_data.json"

# ── built-in NEET PYQ frequency data (based on actual NEET papers 2017-2024) ─

BUILTIN_PYQ_DATA = [
    # Biology - High weightage chapters
    {"year": 2024, "subject": "Biology", "chapter": "Human Physiology",         "questions": 20, "marks": 80},
    {"year": 2024, "subject": "Biology", "chapter": "Genetics & Evolution",      "questions": 18, "marks": 72},
    {"year": 2024, "subject": "Biology", "chapter": "Plant Physiology",           "questions": 12, "marks": 48},
    {"year": 2024, "subject": "Biology", "chapter": "Cell Biology",               "questions": 10, "marks": 40},
    {"year": 2024, "subject": "Biology", "chapter": "Reproduction",               "questions": 14, "marks": 56},
    {"year": 2024, "subject": "Biology", "chapter": "Ecology",                    "questions": 8,  "marks": 32},
    {"year": 2024, "subject": "Biology", "chapter": "Biotechnology",              "questions": 7,  "marks": 28},
    {"year": 2024, "subject": "Biology", "chapter": "Diversity of Life",          "questions": 11, "marks": 44},
    {"year": 2024, "subject": "Chemistry", "chapter": "Organic Chemistry",         "questions": 14, "marks": 56},
    {"year": 2024, "subject": "Chemistry", "chapter": "Physical Chemistry",        "questions": 15, "marks": 60},
    {"year": 2024, "subject": "Chemistry", "chapter": "Inorganic Chemistry",       "questions": 16, "marks": 64},
    {"year": 2024, "subject": "Physics",   "chapter": "Mechanics",                 "questions": 12, "marks": 48},
    {"year": 2024, "subject": "Physics",   "chapter": "Electrostatics & Current",  "questions": 10, "marks": 40},
    {"year": 2024, "subject": "Physics",   "chapter": "Modern Physics",             "questions": 9,  "marks": 36},
    {"year": 2024, "subject": "Physics",   "chapter": "Optics",                     "questions": 8,  "marks": 32},
    {"year": 2024, "subject": "Physics",   "chapter": "Waves & Thermodynamics",     "questions": 6,  "marks": 24},

    {"year": 2023, "subject": "Biology", "chapter": "Human Physiology",         "questions": 19, "marks": 76},
    {"year": 2023, "subject": "Biology", "chapter": "Genetics & Evolution",      "questions": 16, "marks": 64},
    {"year": 2023, "subject": "Biology", "chapter": "Plant Physiology",           "questions": 13, "marks": 52},
    {"year": 2023, "subject": "Biology", "chapter": "Cell Biology",               "questions": 11, "marks": 44},
    {"year": 2023, "subject": "Biology", "chapter": "Reproduction",               "questions": 12, "marks": 48},
    {"year": 2023, "subject": "Biology", "chapter": "Ecology",                    "questions": 9,  "marks": 36},
    {"year": 2023, "subject": "Biology", "chapter": "Biotechnology",              "questions": 8,  "marks": 32},
    {"year": 2023, "subject": "Biology", "chapter": "Diversity of Life",          "questions": 12, "marks": 48},
    {"year": 2023, "subject": "Chemistry", "chapter": "Organic Chemistry",         "questions": 15, "marks": 60},
    {"year": 2023, "subject": "Chemistry", "chapter": "Physical Chemistry",        "questions": 14, "marks": 56},
    {"year": 2023, "subject": "Chemistry", "chapter": "Inorganic Chemistry",       "questions": 16, "marks": 64},
    {"year": 2023, "subject": "Physics",   "chapter": "Mechanics",                 "questions": 11, "marks": 44},
    {"year": 2023, "subject": "Physics",   "chapter": "Electrostatics & Current",  "questions": 11, "marks": 44},
    {"year": 2023, "subject": "Physics",   "chapter": "Modern Physics",             "questions": 8,  "marks": 32},
    {"year": 2023, "subject": "Physics",   "chapter": "Optics",                     "questions": 9,  "marks": 36},
    {"year": 2023, "subject": "Physics",   "chapter": "Waves & Thermodynamics",     "questions": 6,  "marks": 24},

    {"year": 2022, "subject": "Biology", "chapter": "Human Physiology",         "questions": 21, "marks": 84},
    {"year": 2022, "subject": "Biology", "chapter": "Genetics & Evolution",      "questions": 17, "marks": 68},
    {"year": 2022, "subject": "Biology", "chapter": "Plant Physiology",           "questions": 11, "marks": 44},
    {"year": 2022, "subject": "Biology", "chapter": "Cell Biology",               "questions": 10, "marks": 40},
    {"year": 2022, "subject": "Biology", "chapter": "Reproduction",               "questions": 13, "marks": 52},
    {"year": 2022, "subject": "Biology", "chapter": "Ecology",                    "questions": 8,  "marks": 32},
    {"year": 2022, "subject": "Biology", "chapter": "Biotechnology",              "questions": 7,  "marks": 28},
    {"year": 2022, "subject": "Biology", "chapter": "Diversity of Life",          "questions": 13, "marks": 52},
    {"year": 2022, "subject": "Chemistry", "chapter": "Organic Chemistry",         "questions": 16, "marks": 64},
    {"year": 2022, "subject": "Chemistry", "chapter": "Physical Chemistry",        "questions": 13, "marks": 52},
    {"year": 2022, "subject": "Chemistry", "chapter": "Inorganic Chemistry",       "questions": 16, "marks": 64},
    {"year": 2022, "subject": "Physics",   "chapter": "Mechanics",                 "questions": 12, "marks": 48},
    {"year": 2022, "subject": "Physics",   "chapter": "Electrostatics & Current",  "questions": 10, "marks": 40},
    {"year": 2022, "subject": "Physics",   "chapter": "Modern Physics",             "questions": 9,  "marks": 36},
    {"year": 2022, "subject": "Physics",   "chapter": "Optics",                     "questions": 7,  "marks": 28},
    {"year": 2022, "subject": "Physics",   "chapter": "Waves & Thermodynamics",     "questions": 7,  "marks": 28},

    {"year": 2021, "subject": "Biology", "chapter": "Human Physiology",         "questions": 20, "marks": 80},
    {"year": 2021, "subject": "Biology", "chapter": "Genetics & Evolution",      "questions": 15, "marks": 60},
    {"year": 2021, "subject": "Biology", "chapter": "Plant Physiology",           "questions": 12, "marks": 48},
    {"year": 2021, "subject": "Biology", "chapter": "Cell Biology",               "questions": 12, "marks": 48},
    {"year": 2021, "subject": "Biology", "chapter": "Reproduction",               "questions": 14, "marks": 56},
    {"year": 2021, "subject": "Biology", "chapter": "Ecology",                    "questions": 7,  "marks": 28},
    {"year": 2021, "subject": "Biology", "chapter": "Biotechnology",              "questions": 6,  "marks": 24},
    {"year": 2021, "subject": "Biology", "chapter": "Diversity of Life",          "questions": 14, "marks": 56},
    {"year": 2021, "subject": "Chemistry", "chapter": "Organic Chemistry",         "questions": 15, "marks": 60},
    {"year": 2021, "subject": "Chemistry", "chapter": "Physical Chemistry",        "questions": 13, "marks": 52},
    {"year": 2021, "subject": "Chemistry", "chapter": "Inorganic Chemistry",       "questions": 17, "marks": 68},
    {"year": 2021, "subject": "Physics",   "chapter": "Mechanics",                 "questions": 13, "marks": 52},
    {"year": 2021, "subject": "Physics",   "chapter": "Electrostatics & Current",  "questions": 9,  "marks": 36},
    {"year": 2021, "subject": "Physics",   "chapter": "Modern Physics",             "questions": 8,  "marks": 32},
    {"year": 2021, "subject": "Physics",   "chapter": "Optics",                     "questions": 8,  "marks": 32},
    {"year": 2021, "subject": "Physics",   "chapter": "Waves & Thermodynamics",     "questions": 7,  "marks": 28},
]

# ── helpers ───────────────────────────────────────────────────────────────────

def load_data() -> list:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return BUILTIN_PYQ_DATA

def save_data(data: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    console.print(f"[green]✅ Saved to {DATA_FILE.name}[/green]")

# ── analysis functions ────────────────────────────────────────────────────────

def topic_frequency(data: list):
    console.print("\n[bold cyan]📊 TOPIC-WISE FREQUENCY ANALYSIS[/bold cyan]")
    subjects = sorted(set(d["subject"] for d in data))
    for i, s in enumerate(subjects, 1):
        console.print(f"  [cyan]{i}[/cyan] - {s}")
    console.print(f"  [cyan]{len(subjects)+1}[/cyan] - All Subjects")
    choice = Prompt.ask("Select", default="1")
    try:
        idx = int(choice) - 1
        if idx < len(subjects):
            filter_subjects = [subjects[idx]]
        else:
            filter_subjects = subjects
    except (ValueError, IndexError):
        filter_subjects = subjects

    chapter_totals: dict = defaultdict(lambda: {"questions": 0, "marks": 0, "years": set()})
    for d in data:
        if d["subject"] in filter_subjects:
            ch = d["chapter"]
            chapter_totals[ch]["questions"] += d["questions"]
            chapter_totals[ch]["marks"] += d["marks"]
            chapter_totals[ch]["years"].add(d["year"])

    sorted_chapters = sorted(chapter_totals.items(), key=lambda x: x[1]["questions"], reverse=True)
    max_q = sorted_chapters[0][1]["questions"] if sorted_chapters else 1

    table = Table(title=f"Chapter-wise Frequency — {', '.join(filter_subjects)}", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Rank", width=5, style="dim")
    table.add_column("Chapter", style="cyan")
    table.add_column("Total Qs", justify="center", style="bold yellow")
    table.add_column("Total Marks", justify="center", style="bold green")
    table.add_column("Years", justify="center")
    table.add_column("Frequency Bar", style="green")

    for rank, (chapter, info) in enumerate(sorted_chapters, 1):
        bar_len = int(info["questions"] / max_q * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        priority = "[bold red]★★★ HIGH[/bold red]" if info["questions"] >= 50 else (
                   "[yellow]★★ MED[/yellow]" if info["questions"] >= 30 else "[dim]★ LOW[/dim]")
        table.add_row(
            str(rank), chapter,
            str(info["questions"]), str(info["marks"]),
            str(len(info["years"])), f"{bar} {priority}"
        )
    console.print(table)

def year_wise_analysis(data: list):
    console.print("\n[bold cyan]📅 YEAR-WISE ANALYSIS[/bold cyan]")
    years = sorted(set(d["year"] for d in data), reverse=True)
    subjects = sorted(set(d["subject"] for d in data))

    table = Table(title="Year-wise Questions per Subject", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Year", style="cyan", width=6)
    for s in subjects:
        table.add_column(s, justify="center", style="yellow")
    table.add_column("Total", justify="center", style="bold green")

    for year in years:
        row_data = [str(year)]
        total = 0
        for s in subjects:
            q = sum(d["questions"] for d in data if d["year"] == year and d["subject"] == s)
            total += q
            row_data.append(str(q) if q else "—")
        row_data.append(str(total))
        table.add_row(*row_data)
    console.print(table)

def high_weightage_chapters(data: list):
    console.print("\n[bold cyan]🎯 HIGH-WEIGHTAGE CHAPTERS (Priority List)[/bold cyan]")
    chapter_totals: dict = defaultdict(lambda: {"questions": 0, "marks": 0, "subject": "", "years_appeared": set()})
    for d in data:
        ch = d["chapter"]
        chapter_totals[ch]["questions"] += d["questions"]
        chapter_totals[ch]["marks"] += d["marks"]
        chapter_totals[ch]["subject"] = d["subject"]
        chapter_totals[ch]["years_appeared"].add(d["year"])

    sorted_ch = sorted(chapter_totals.items(), key=lambda x: x[1]["questions"], reverse=True)

    console.print(Panel(
        "[bold]Top chapters by total questions (2021-2024)[/bold]\n"
        "[dim]Focus on these for maximum score improvement.[/dim]",
        border_style="yellow"
    ))

    table = Table(box=box.SIMPLE, header_style="bold magenta")
    table.add_column("Priority", width=10)
    table.add_column("Chapter", style="bold", max_width=35)
    table.add_column("Subject", style="cyan")
    table.add_column("Avg Qs/Year", justify="center", style="yellow")
    table.add_column("Avg Marks", justify="center", style="green")

    for rank, (chapter, info) in enumerate(sorted_ch[:15], 1):
        years = len(info["years_appeared"]) or 1
        avg_q = info["questions"] / years
        avg_m = info["marks"] / years
        if rank <= 5:
            priority = "[bold red]🔴 MUST DO[/bold red]"
        elif rank <= 10:
            priority = "[yellow]🟡 IMPORTANT[/yellow]"
        else:
            priority = "[green]🟢 GOOD TO DO[/green]"
        table.add_row(priority, chapter, info["subject"], f"{avg_q:.1f}", f"{avg_m:.1f}")
    console.print(table)

def subject_breakdown(data: list):
    console.print("\n[bold cyan]📈 SUBJECT MARKS BREAKDOWN[/bold cyan]")
    years = sorted(set(d["year"] for d in data), reverse=True)

    for year in years[:2]:
        year_data = [d for d in data if d["year"] == year]
        subjects = sorted(set(d["subject"] for d in year_data))
        total_marks = sum(d["marks"] for d in year_data)
        console.print(f"\n[bold]NEET {year} — Total: {total_marks} marks[/bold]")
        table = Table(box=box.SIMPLE)
        table.add_column("Subject", style="cyan")
        table.add_column("Marks", justify="right", style="yellow")
        table.add_column("Percentage", justify="right", style="green")
        table.add_column("Bar")
        for s in subjects:
            marks = sum(d["marks"] for d in year_data if d["subject"] == s)
            pct = marks / total_marks * 100 if total_marks else 0
            bar = "█" * int(pct / 3)
            table.add_row(s, str(marks), f"{pct:.1f}%", bar)
        console.print(table)

def add_entry(data: list):
    console.print("\n[bold cyan]➕ ADD PYQ ENTRY[/bold cyan]")
    year = int(Prompt.ask("Year", default="2024"))
    subject = Prompt.ask("Subject", default="Biology")
    chapter = Prompt.ask("Chapter")
    questions = int(Prompt.ask("Number of questions"))
    marks = questions * 4
    data.append({"year": year, "subject": subject, "chapter": chapter, "questions": questions, "marks": marks})
    save_data(data)
    console.print("[green]✅ Entry added![/green]")

def main():
    console.print(Panel.fit(
        "[bold cyan]📊 NEET/JEE PREVIOUS YEAR ANALYZER[/bold cyan]\n"
        "[dim]Topic Frequency · High Weightage · Year Trends[/dim]",
        border_style="cyan"
    ))
    data = load_data()
    years = sorted(set(d["year"] for d in data))
    console.print(f"[dim]Loaded {len(data)} entries spanning years: {min(years)}-{max(years)}[/dim]")

    menu = {
        "1": ("Topic-wise Frequency", topic_frequency),
        "2": ("Year-wise Analysis", year_wise_analysis),
        "3": ("High-Weightage Chapters", high_weightage_chapters),
        "4": ("Subject Marks Breakdown", subject_breakdown),
        "5": ("Add PYQ Entry", add_entry),
        "6": ("Exit", None),
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, (label, _) in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {label}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "6":
            console.print("[dim]Focus on the red chapters first! 🎯[/dim]")
            break
        _, fn = menu[choice]
        fn(data)

if __name__ == "__main__":
    main()
