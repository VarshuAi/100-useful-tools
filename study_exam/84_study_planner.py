"""
Tool 84 - Study Planner for Competitive Exams
Input exam date, subjects, daily hours. Generate a day-by-day study
schedule with topic assignments. Track daily completion and view progress.
Run: python 84_study_planner.py
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "study_plan.json"

# ── predefined NEET syllabus ──────────────────────────────────────────────────

NEET_SYLLABUS = {
    "Biology": [
        "Cell: Structure and Functions",
        "Cell Cycle and Cell Division",
        "Transport in Plants",
        "Mineral Nutrition",
        "Photosynthesis in Higher Plants",
        "Respiration in Plants",
        "Plant Growth and Development",
        "Digestion and Absorption",
        "Breathing and Exchange of Gases",
        "Body Fluids and Circulation",
        "Excretory Products and their Elimination",
        "Locomotion and Movement",
        "Neural Control and Coordination",
        "Chemical Coordination and Integration",
        "Sexual Reproduction in Flowering Plants",
        "Human Reproduction",
        "Reproductive Health",
        "Principles of Inheritance and Variation",
        "Molecular Basis of Inheritance",
        "Evolution",
        "Human Health and Disease",
        "Strategies for Enhancement in Food Production",
        "Microbes in Human Welfare",
        "Biotechnology: Principles and Processes",
        "Biotechnology and its Applications",
        "Organisms and Populations",
        "Ecosystem",
        "Biodiversity and Conservation",
        "Environmental Issues",
        "The Living World",
        "Biological Classification",
        "Plant Kingdom",
        "Animal Kingdom",
        "Morphology of Flowering Plants",
        "Anatomy of Flowering Plants",
        "Structural Organisation in Animals",
    ],
    "Physics": [
        "Physical World and Measurement",
        "Kinematics",
        "Laws of Motion",
        "Work, Energy and Power",
        "Motion of System of Particles and Rigid Body",
        "Gravitation",
        "Properties of Bulk Matter",
        "Thermodynamics",
        "Behaviour of Perfect Gas and Kinetic Theory",
        "Oscillations and Waves",
        "Electrostatics",
        "Current Electricity",
        "Magnetic Effects of Current and Magnetism",
        "Electromagnetic Induction and Alternating Currents",
        "Electromagnetic Waves",
        "Optics",
        "Dual Nature of Matter and Radiation",
        "Atoms and Nuclei",
        "Electronic Devices",
    ],
    "Chemistry": [
        "Some Basic Concepts of Chemistry",
        "Structure of Atom",
        "Classification of Elements and Periodicity in Properties",
        "Chemical Bonding and Molecular Structure",
        "States of Matter: Gases and Liquids",
        "Thermodynamics",
        "Equilibrium",
        "Redox Reactions",
        "Hydrogen",
        "s-Block Elements",
        "p-Block Elements (Group 13 & 14)",
        "Organic Chemistry: Basic Principles",
        "Hydrocarbons",
        "Environmental Chemistry",
        "Solid State",
        "Solutions",
        "Electrochemistry",
        "Chemical Kinetics",
        "Surface Chemistry",
        "General Principles and Processes of Isolation of Elements",
        "p-Block Elements (Group 15, 16, 17, 18)",
        "d and f Block Elements",
        "Coordination Compounds",
        "Haloalkanes and Haloarenes",
        "Alcohols, Phenols and Ethers",
        "Aldehydes, Ketones and Carboxylic Acids",
        "Organic Compounds Containing Nitrogen",
        "Biomolecules",
        "Polymers",
        "Chemistry in Everyday Life",
    ],
}

JEE_SYLLABUS = {
    "Mathematics": [
        "Sets, Relations and Functions",
        "Complex Numbers and Quadratic Equations",
        "Matrices and Determinants",
        "Permutations and Combinations",
        "Mathematical Induction",
        "Binomial Theorem",
        "Sequences and Series",
        "Limits, Continuity and Differentiability",
        "Integral Calculus",
        "Differential Equations",
        "Coordinate Geometry",
        "3D Geometry",
        "Vector Algebra",
        "Statistics and Probability",
        "Trigonometry",
        "Mathematical Reasoning",
    ],
    "Physics": NEET_SYLLABUS["Physics"],
    "Chemistry": NEET_SYLLABUS["Chemistry"],
}

# ── helpers ───────────────────────────────────────────────────────────────────

def load_plan() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_plan(plan: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

def create_plan(plan: dict):
    console.print("\n[bold cyan]📅 CREATE STUDY PLAN[/bold cyan]")
    plan_name = Prompt.ask("Plan name (e.g. 'NEET 2026')", default="NEET 2026")
    exam_type = Prompt.ask("Exam type", choices=["NEET", "JEE", "Custom"], default="NEET")
    exam_date_str = Prompt.ask("Exam date (DD/MM/YYYY)", default="21/06/2026")
    try:
        exam_date = datetime.strptime(exam_date_str, "%d/%m/%Y")
    except ValueError:
        console.print("[red]Invalid date format.[/red]")
        return
    daily_hours = float(Prompt.ask("Study hours per day", default="8"))
    rest_day = Prompt.ask("Weekly rest day", choices=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], default="Sunday")

    days_left = (exam_date - datetime.now()).days
    if days_left <= 0:
        console.print("[red]Exam date is in the past![/red]")
        return

    syllabus = NEET_SYLLABUS if exam_type == "NEET" else (JEE_SYLLABUS if exam_type == "JEE" else {})
    if exam_type == "Custom":
        subjects_input = Prompt.ask("Subjects (comma separated)")
        syllabus = {s.strip(): ["General Study"] for s in subjects_input.split(",")}

    # Distribute topics across study days
    study_days = []
    current = datetime.now() + timedelta(days=1)
    for _ in range(days_left):
        if current.strftime("%A") != rest_day:
            study_days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    all_topics = []
    for subject, topics in syllabus.items():
        for topic in topics:
            all_topics.append({"subject": subject, "topic": topic})

    schedule = {}
    topic_idx = 0
    topics_per_day = max(1, len(all_topics) // len(study_days)) if study_days else 1

    for day in study_days:
        day_topics = []
        for _ in range(topics_per_day):
            if topic_idx < len(all_topics):
                day_topics.append({**all_topics[topic_idx], "completed": False})
                topic_idx += 1
        if day_topics:
            schedule[day] = {"topics": day_topics, "hours_target": daily_hours, "hours_done": 0, "notes": ""}

    plan[plan_name] = {
        "exam": exam_type, "exam_date": exam_date.strftime("%Y-%m-%d"),
        "daily_hours": daily_hours, "rest_day": rest_day,
        "created": datetime.now().isoformat(), "schedule": schedule,
    }
    save_plan(plan)
    console.print(f"\n[green]✅ Plan '{plan_name}' created![/green]")
    console.print(f"   📅 {len(study_days)} study days | 📚 {len(all_topics)} topics | ⏱ {daily_hours}h/day")

def view_today(plan: dict):
    console.print("\n[bold cyan]📅 TODAY'S STUDY PLAN[/bold cyan]")
    if not plan:
        console.print("[yellow]No plans found. Create one first.[/yellow]")
        return
    plan_name = _choose_plan(plan)
    if not plan_name:
        return
    p = plan[plan_name]
    today = datetime.now().strftime("%Y-%m-%d")
    schedule = p["schedule"]
    if today not in schedule:
        console.print(f"[yellow]No study scheduled for today ({today}).[/yellow]")
        days = sorted(schedule.keys())
        if days:
            next_day = next((d for d in days if d >= today), None)
            if next_day:
                console.print(f"[dim]Next study day: {next_day}[/dim]")
        return
    day_data = schedule[today]
    exam_date = datetime.strptime(p["exam_date"], "%Y-%m-%d")
    days_left = (exam_date - datetime.now()).days
    done = sum(1 for t in day_data["topics"] if t["completed"])
    total = len(day_data["topics"])

    console.print(Panel(
        f"[bold yellow]📆 {today}[/bold yellow]  |  [red]{days_left} days to exam[/red]  |  "
        f"[cyan]Target: {day_data['hours_target']}h[/cyan]  |  "
        f"[green]Done: {day_data['hours_done']}h[/green]",
        title=plan_name, border_style="cyan"
    ))

    table = Table(box=box.SIMPLE, header_style="bold magenta")
    table.add_column("#", width=3, style="dim")
    table.add_column("Subject", style="cyan", width=12)
    table.add_column("Topic", style="bold", max_width=45)
    table.add_column("Status", justify="center", width=10)
    for i, t in enumerate(day_data["topics"], 1):
        status = "[green]✅ Done[/green]" if t["completed"] else "[yellow]⏳ Pending[/yellow]"
        table.add_row(str(i), t["subject"], t["topic"], status)
    console.print(table)
    console.print(f"[dim]Progress: {done}/{total} topics completed today.[/dim]")

def mark_complete(plan: dict):
    console.print("\n[bold cyan]✅ MARK TOPICS COMPLETE[/bold cyan]")
    if not plan:
        console.print("[yellow]No plans found.[/yellow]")
        return
    plan_name = _choose_plan(plan)
    if not plan_name:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    schedule = plan[plan_name]["schedule"]
    if today not in schedule:
        console.print("[yellow]No study scheduled for today.[/yellow]")
        return
    day_data = schedule[today]
    for i, t in enumerate(day_data["topics"], 1):
        status = "✅" if t["completed"] else "⏳"
        console.print(f"  [cyan]{i}[/cyan] {status} [{t['subject']}] {t['topic']}")
    nums = Prompt.ask("Mark numbers as done (comma separated, e.g. 1,2,3)")
    hours = float(Prompt.ask("Hours studied today so far", default=str(day_data.get("hours_done", 0))))
    for n in nums.split(","):
        try:
            idx = int(n.strip()) - 1
            if 0 <= idx < len(day_data["topics"]):
                day_data["topics"][idx]["completed"] = True
        except (ValueError, IndexError):
            pass
    day_data["hours_done"] = hours
    save_plan(plan)
    done = sum(1 for t in day_data["topics"] if t["completed"])
    console.print(f"[green]✅ Updated! {done}/{len(day_data['topics'])} topics complete for today.[/green]")

def view_progress(plan: dict):
    console.print("\n[bold cyan]📊 OVERALL PROGRESS[/bold cyan]")
    if not plan:
        console.print("[yellow]No plans found.[/yellow]")
        return
    plan_name = _choose_plan(plan)
    if not plan_name:
        return
    p = plan[plan_name]
    schedule = p["schedule"]
    exam_date = datetime.strptime(p["exam_date"], "%Y-%m-%d")
    today = datetime.now()
    days_left = (exam_date - today).days

    total_topics = sum(len(d["topics"]) for d in schedule.values())
    done_topics = sum(sum(1 for t in d["topics"] if t["completed"]) for d in schedule.values())
    total_hours_target = sum(d["hours_target"] for d in schedule.values())
    total_hours_done = sum(d.get("hours_done", 0) for d in schedule.values())

    pct_topics = done_topics / total_topics * 100 if total_topics else 0
    pct_hours = total_hours_done / total_hours_target * 100 if total_hours_target else 0

    # Subject-wise breakdown
    subject_data: dict = {}
    for day_data in schedule.values():
        for t in day_data["topics"]:
            s = t["subject"]
            if s not in subject_data:
                subject_data[s] = {"total": 0, "done": 0}
            subject_data[s]["total"] += 1
            if t["completed"]:
                subject_data[s]["done"] += 1

    console.print(Panel(
        f"[bold]Plan:[/bold] {plan_name}  |  [bold]Exam:[/bold] {p['exam_date']}  |  "
        f"[red bold]{days_left} days left[/red bold]\n\n"
        f"Topics: [{('green' if pct_topics >= 70 else 'yellow')}]{done_topics}/{total_topics} ({pct_topics:.0f}%)[/]\n"
        f"Hours:  [{('green' if pct_hours >= 70 else 'yellow')}]{total_hours_done:.0f}h/{total_hours_target:.0f}h ({pct_hours:.0f}%)[/]",
        title="📊 Progress Report", border_style="cyan"
    ))

    table = Table(title="Subject-wise Progress", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Subject", style="cyan")
    table.add_column("Topics Done", justify="center")
    table.add_column("Progress", justify="center")
    table.add_column("Bar", style="green")
    for subject, info in subject_data.items():
        pct = info["done"] / info["total"] * 100 if info["total"] else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        color = "green" if pct >= 70 else "yellow" if pct >= 40 else "red"
        table.add_row(subject, f"{info['done']}/{info['total']}", f"[{color}]{pct:.0f}%[/{color}]", bar)
    console.print(table)

def _choose_plan(plan: dict) -> str | None:
    names = list(plan.keys())
    if len(names) == 1:
        return names[0]
    for i, n in enumerate(names, 1):
        console.print(f"  [cyan]{i}[/cyan] - {n}")
    choice = Prompt.ask("Select plan", default="1")
    try:
        return names[int(choice) - 1]
    except (ValueError, IndexError):
        return None

def main():
    console.print(Panel.fit(
        "[bold cyan]📅 STUDY PLANNER — NEET / JEE[/bold cyan]\n"
        "[dim]Plan · Schedule · Track · Progress[/dim]",
        border_style="cyan"
    ))
    plan = load_plan()

    menu = {
        "1": ("Create New Plan", create_plan),
        "2": ("View Today's Schedule", view_today),
        "3": ("Mark Topics Complete", mark_complete),
        "4": ("View Overall Progress", view_progress),
        "5": ("Exit", None),
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, (label, _) in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {label}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "5":
            console.print("[dim]Stay consistent! 🎯[/dim]")
            break
        _, fn = menu[choice]
        fn(plan)

if __name__ == "__main__":
    main()
