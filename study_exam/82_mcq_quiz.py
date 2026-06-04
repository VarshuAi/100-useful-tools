"""
Tool 82 - MCQ Quiz Engine (NEET/JEE Style)
Load multiple-choice questions from a JSON file, run a timed quiz with
shuffled questions & options, score at the end, and explain wrong answers.
Run: python 82_mcq_quiz.py
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

console = Console()

DATA_FILE = Path(__file__).parent / "mcq_questions.json"

# ── built-in sample questions ─────────────────────────────────────────────────

SAMPLE_QUESTIONS = [
    {
        "subject": "Biology",
        "chapter": "Cell Biology",
        "question": "Which organelle is known as the 'powerhouse of the cell'?",
        "options": ["Ribosome", "Mitochondria", "Golgi apparatus", "Lysosome"],
        "answer": 1,
        "explanation": "Mitochondria produce ATP through oxidative phosphorylation, providing energy to the cell. They contain their own DNA and ribosomes, supporting the endosymbiotic theory."
    },
    {
        "subject": "Biology",
        "chapter": "Genetics",
        "question": "The process by which mRNA is synthesized from a DNA template is called:",
        "options": ["Translation", "Replication", "Transcription", "Transduction"],
        "answer": 2,
        "explanation": "Transcription is the synthesis of RNA from a DNA template, catalyzed by RNA polymerase. It occurs in the nucleus (in eukaryotes)."
    },
    {
        "subject": "Biology",
        "chapter": "Genetics",
        "question": "Which of the following is NOT a pyrimidine base?",
        "options": ["Thymine", "Cytosine", "Guanine", "Uracil"],
        "answer": 2,
        "explanation": "Guanine is a purine base (two-ring structure). Pyrimidines (single-ring) include Thymine, Cytosine, and Uracil."
    },
    {
        "subject": "Biology",
        "chapter": "Human Physiology",
        "question": "The enzyme responsible for the conversion of fibrinogen to fibrin during blood clotting is:",
        "options": ["Pepsin", "Thrombin", "Trypsin", "Lipase"],
        "answer": 1,
        "explanation": "Thrombin converts soluble fibrinogen into insoluble fibrin strands, forming the clot. Thrombin itself is activated from prothrombin."
    },
    {
        "subject": "Biology",
        "chapter": "Plant Biology",
        "question": "Photosystem I absorbs light maximally at:",
        "options": ["680 nm", "700 nm", "660 nm", "730 nm"],
        "answer": 1,
        "explanation": "Photosystem I (PS I) absorbs light at 700 nm (P700 reaction centre). Photosystem II absorbs at 680 nm (P680)."
    },
    {
        "subject": "Chemistry",
        "chapter": "Atomic Structure",
        "question": "The principal quantum number 'n' describes:",
        "options": ["Shape of orbital", "Energy level and size of orbital", "Orientation of orbital", "Spin of electron"],
        "answer": 1,
        "explanation": "Principal quantum number n = 1, 2, 3... determines the energy level and size of the orbital. Higher n means larger orbital and higher energy."
    },
    {
        "subject": "Chemistry",
        "chapter": "Chemical Bonding",
        "question": "Which molecule has a trigonal bipyramidal geometry?",
        "options": ["BF3", "PCl5", "SF6", "H2O"],
        "answer": 1,
        "explanation": "PCl5 has 5 bonding pairs and no lone pairs, giving it a trigonal bipyramidal shape. BF3 is trigonal planar, SF6 is octahedral."
    },
    {
        "subject": "Chemistry",
        "chapter": "Thermodynamics",
        "question": "Which of the following is true for a spontaneous process at constant T and P?",
        "options": ["ΔG > 0", "ΔG = 0", "ΔG < 0", "ΔH > 0"],
        "answer": 2,
        "explanation": "Gibbs free energy ΔG = ΔH - TΔS. A process is spontaneous when ΔG < 0, meaning it releases free energy."
    },
    {
        "subject": "Chemistry",
        "chapter": "Organic Chemistry",
        "question": "Markovnikov's rule applies to the addition of HX to:",
        "options": ["Alkanes", "Alkenes", "Alcohols", "Carboxylic acids"],
        "answer": 1,
        "explanation": "Markovnikov's rule: in addition of HX to an asymmetric alkene, H attaches to the carbon with more H atoms (more substituted carbon gets X)."
    },
    {
        "subject": "Chemistry",
        "chapter": "Equilibrium",
        "question": "Le Chatelier's principle predicts that increasing pressure will shift equilibrium toward:",
        "options": ["The side with more moles of gas", "The side with fewer moles of gas", "Products always", "Reactants always"],
        "answer": 1,
        "explanation": "Increased pressure favours the side with fewer moles of gas, reducing volume. For equal moles, pressure has no effect."
    },
    {
        "subject": "Physics",
        "chapter": "Mechanics",
        "question": "A body is thrown vertically upward. At the highest point:",
        "options": ["Velocity and acceleration are both zero", "Velocity is zero, acceleration is g downward", "Velocity is maximum, acceleration is zero", "Both are non-zero"],
        "answer": 1,
        "explanation": "At the highest point, instantaneous velocity = 0 (momentarily at rest), but acceleration due to gravity (g = 9.8 m/s²) acts downward throughout the motion."
    },
    {
        "subject": "Physics",
        "chapter": "Optics",
        "question": "Total internal reflection occurs when light travels from:",
        "options": ["Rarer to denser medium", "Denser to rarer medium at angle > critical angle", "Denser to rarer medium at any angle", "Rarer to denser at angle > critical angle"],
        "answer": 1,
        "explanation": "TIR occurs when light goes from a denser to a rarer medium AND the angle of incidence exceeds the critical angle (sin θc = n2/n1)."
    },
    {
        "subject": "Physics",
        "chapter": "Modern Physics",
        "question": "The photoelectric effect proves that light has:",
        "options": ["Wave nature only", "Particle nature (photons)", "No momentum", "Continuous energy"],
        "answer": 1,
        "explanation": "The photoelectric effect (Einstein, 1905) proved that light consists of discrete packets of energy called photons (E = hν), earning Einstein the Nobel Prize."
    },
    {
        "subject": "Physics",
        "chapter": "Thermodynamics",
        "question": "The efficiency of a Carnot engine operating between 500K and 300K is:",
        "options": ["60%", "40%", "50%", "30%"],
        "answer": 1,
        "explanation": "Carnot efficiency η = 1 - T_cold/T_hot = 1 - 300/500 = 1 - 0.6 = 0.4 = 40%."
    },
    {
        "subject": "Physics",
        "chapter": "Electrostatics",
        "question": "Electric field inside a conducting sphere is:",
        "options": ["Equal to surface field", "Zero", "Maximum at centre", "Depends on charge"],
        "answer": 1,
        "explanation": "Inside a conductor in electrostatic equilibrium, the electric field is zero. All excess charge resides on the surface."
    },
]

# ── helpers ───────────────────────────────────────────────────────────────────

def load_questions() -> list:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    return SAMPLE_QUESTIONS

def save_questions(questions: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✅ Saved {len(questions)} questions to {DATA_FILE.name}[/green]")

def filter_questions(questions: list) -> list:
    subjects = sorted(set(q.get("subject", "General") for q in questions))
    console.print("\n[bold]Available subjects:[/bold]")
    console.print("  [cyan]0[/cyan] - All subjects")
    for i, s in enumerate(subjects, 1):
        console.print(f"  [cyan]{i}[/cyan] - {s}")
    choice = Prompt.ask("Select subject", default="0")
    try:
        idx = int(choice)
        if idx == 0:
            return questions
        selected = subjects[idx - 1]
        return [q for q in questions if q.get("subject") == selected]
    except (ValueError, IndexError):
        return questions

# ── quiz engine ───────────────────────────────────────────────────────────────

def run_quiz(questions: list):
    console.print("\n[bold cyan]⚡ NEET/JEE MCQ QUIZ ENGINE[/bold cyan]\n")
    questions = filter_questions(questions)
    n = int(Prompt.ask(f"Number of questions (max {len(questions)})", default=str(min(10, len(questions)))))
    n = min(n, len(questions))
    timed = Confirm.ask("Enable timer per question?", default=True)
    time_limit = 0
    if timed:
        time_limit = int(Prompt.ask("Seconds per question", default="90"))
    shuffle_opts = Confirm.ask("Shuffle options?", default=True)

    pool = random.sample(questions, n)
    results = []

    console.print(f"\n[bold green]Starting {n}-question quiz. Good luck! 🍀[/bold green]\n")
    time.sleep(1)

    for i, q in enumerate(pool, 1):
        options = list(enumerate(q["options"]))
        correct_text = q["options"][q["answer"]]
        if shuffle_opts:
            random.shuffle(options)
        correct_shuffled = next(idx for idx, (_, text) in enumerate(options) if text == correct_text)

        console.print(Panel(
            f"[bold yellow]Q {i}/{n}  [{q.get('subject','?')} — {q.get('chapter','?')}][/bold yellow]\n\n"
            f"{q['question']}",
            border_style="yellow"
        ))
        labels = ["A", "B", "C", "D"]
        for j, (_, text) in enumerate(options):
            console.print(f"  [cyan]{labels[j]}[/cyan]) {text}")

        start = time.time()
        if timed:
            console.print(f"[dim]⏱  {time_limit}s to answer[/dim]")

        answer_label = Prompt.ask(f"\nYour answer", choices=["A","B","C","D","a","b","c","d"])
        elapsed = time.time() - start
        ans_idx = "abcd".index(answer_label.lower())

        if timed and elapsed > time_limit:
            console.print("[red]⏰ Time's up![/red]")
            is_correct = False
        else:
            is_correct = (ans_idx == correct_shuffled)

        if is_correct:
            console.print("[bold green]✅ Correct![/bold green]")
        else:
            console.print(f"[bold red]❌ Wrong! Correct answer: {labels[correct_shuffled]}) {correct_text}[/bold red]")

        results.append({
            "question": q["question"],
            "subject": q.get("subject","?"),
            "chapter": q.get("chapter","?"),
            "correct": is_correct,
            "your_answer": options[ans_idx][1],
            "correct_answer": correct_text,
            "explanation": q.get("explanation",""),
            "time_taken": round(elapsed, 1),
        })
        console.print()

    # ── results ───────────────────────────────────────────────────────────────
    score = sum(1 for r in results if r["correct"])
    pct = score / n * 100
    neet_marks = score * 4 - (n - score)  # NEET marking: +4/-1
    color = "green" if pct >= 70 else "yellow" if pct >= 50 else "red"

    console.print(Panel(
        f"[bold]Score: [{color}]{score}/{n} ({pct:.0f}%)[/{color}][/bold]\n"
        f"[bold]NEET Marks (4/-1): [{color}]{neet_marks}[/{color}][/bold]\n"
        f"[dim]Avg time per Q: {sum(r['time_taken'] for r in results)/n:.1f}s[/dim]",
        title="📊 QUIZ RESULTS", border_style=color
    ))

    show_wrong = Confirm.ask("Review wrong answers with explanations?", default=True)
    if show_wrong:
        wrong = [r for r in results if not r["correct"]]
        if not wrong:
            console.print("[green]🎉 Perfect score! No wrong answers.[/green]")
        for r in wrong:
            console.print(Panel(
                f"[bold red]Q: {r['question']}[/bold red]\n\n"
                f"[red]Your answer:[/red] {r['your_answer']}\n"
                f"[green]Correct:[/green] {r['correct_answer']}\n\n"
                f"[cyan]💡 Explanation:[/cyan] {r['explanation']}",
                border_style="red",
                title=f"❌ {r['subject']} — {r['chapter']}"
            ))

def add_question(questions: list):
    console.print("\n[bold cyan]➕ ADD NEW QUESTION[/bold cyan]")
    subject = Prompt.ask("Subject", default="Biology")
    chapter = Prompt.ask("Chapter")
    question = Prompt.ask("Question text")
    opts = []
    for label in ["A", "B", "C", "D"]:
        opts.append(Prompt.ask(f"Option {label}"))
    correct = Prompt.ask("Correct option", choices=["A","B","C","D"])
    ans_idx = "ABCD".index(correct)
    explanation = Prompt.ask("Explanation (why this is correct)")
    questions.append({
        "subject": subject, "chapter": chapter, "question": question,
        "options": opts, "answer": ans_idx, "explanation": explanation
    })
    save_questions(questions)
    console.print("[green]✅ Question added![/green]")

def stats_view(questions: list):
    table = Table(title="📊 Question Bank Stats", box=box.ROUNDED, header_style="bold magenta")
    table.add_column("Subject", style="cyan")
    table.add_column("Chapters", style="yellow")
    table.add_column("Questions", justify="right", style="bold green")
    from collections import defaultdict
    data: dict = defaultdict(lambda: {"chapters": set(), "count": 0})
    for q in questions:
        s = q.get("subject","General")
        data[s]["chapters"].add(q.get("chapter","?"))
        data[s]["count"] += 1
    for subject, info in sorted(data.items()):
        table.add_row(subject, str(len(info["chapters"])), str(info["count"]))
    table.add_row("[bold]TOTAL[/bold]", "—", f"[bold]{len(questions)}[/bold]")
    console.print(table)

def main():
    console.print(Panel.fit(
        "[bold cyan]📝 MCQ QUIZ ENGINE — NEET / JEE STYLE[/bold cyan]\n"
        "[dim]Timed quiz · Shuffle · Score · Explanations[/dim]",
        border_style="cyan"
    ))
    questions = load_questions()

    menu = {
        "1": "Start Quiz",
        "2": "Add Question",
        "3": "Question Bank Stats",
        "4": "Export Questions to JSON",
        "5": "Exit",
    }
    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, v in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {v}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "1":
            run_quiz(questions)
        elif choice == "2":
            add_question(questions)
        elif choice == "3":
            stats_view(questions)
        elif choice == "4":
            save_questions(questions)
        elif choice == "5":
            console.print("[dim]Keep practising! 💪[/dim]")
            break

if __name__ == "__main__":
    main()
