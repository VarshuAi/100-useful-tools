"""
Tool 85 - AI Subject Tutor (Powered by Gemini)
Ask any Physics / Chemistry / Biology / Math question.
Get detailed explanations, step-by-step solutions, related concepts,
mnemonics, and practice problems — all from Gemini AI.
Run: python 85_ai_tutor.py
"""

import os
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich import box

console = Console()

HISTORY_FILE = Path(__file__).parent / "ai_tutor_history.json"

SUBJECTS = {
    "1": "Physics",
    "2": "Chemistry",
    "3": "Biology",
    "4": "Mathematics",
    "5": "General Science",
}

QUESTION_TYPES = {
    "1": ("Explain Concept",    "Explain in detail with examples, diagrams (ASCII if helpful), and real-world applications."),
    "2": ("Solve Problem",      "Solve step-by-step showing all working. Highlight the key formula used. Give the final answer clearly."),
    "3": ("Practice Problems",  "Generate 5 practice problems of varying difficulty on this topic. Include answers at the end."),
    "4": ("Mnemonics / Tips",   "Give memory tricks, mnemonics, acronyms, and quick recall tips for this topic."),
    "5": ("Quick Summary",      "Give a concise bullet-point summary of all key points, formulas, and facts."),
    "6": ("Free Question",      "Answer the question thoroughly as an expert NEET/JEE tutor."),
}

# ── Gemini setup ──────────────────────────────────────────────────────────────

def get_gemini_client():
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            console.print(Panel(
                "[yellow]No GEMINI_API_KEY found in environment.\n"
                "Set it with: [bold]set GEMINI_API_KEY=your_key_here[/bold] (Windows)\n"
                "or export GEMINI_API_KEY=your_key_here (Linux/Mac)[/yellow]",
                title="⚠️ API Key Missing", border_style="yellow"
            ))
            return None
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    except ImportError:
        console.print("[red]google-generativeai not installed. Run: pip install google-generativeai[/red]")
        return None

def ask_gemini(model, prompt: str, subject: str) -> str:
    system_context = (
        f"You are an expert {subject} tutor specializing in NEET and JEE preparation for Indian students. "
        "Provide clear, accurate, and engaging explanations. "
        "Use proper scientific notation, equations (text-based), and step-by-step reasoning. "
        "Keep the language friendly but precise. Format output with markdown headings and bullet points."
    )
    full_prompt = f"{system_context}\n\n{prompt}"
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"[Error communicating with Gemini: {e}]"

# ── history ───────────────────────────────────────────────────────────────────

def load_history() -> list:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_to_history(history: list, subject: str, question: str, answer: str):
    history.append({
        "timestamp": datetime.now().isoformat(),
        "subject": subject,
        "question": question,
        "answer": answer,
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-50:], f, indent=2, ensure_ascii=False)  # keep last 50

# ── main flows ────────────────────────────────────────────────────────────────

def ask_question(model, history: list):
    console.print("\n[bold cyan]📚 SUBJECT TUTOR — SELECT SUBJECT[/bold cyan]")
    for k, v in SUBJECTS.items():
        console.print(f"  [cyan]{k}[/cyan] - {v}")
    s_choice = Prompt.ask("Subject", choices=list(SUBJECTS.keys()), default="1")
    subject = SUBJECTS[s_choice]

    console.print(f"\n[bold]Question type for [cyan]{subject}[/cyan]:[/bold]")
    for k, (label, _) in QUESTION_TYPES.items():
        console.print(f"  [cyan]{k}[/cyan] - {label}")
    q_choice = Prompt.ask("Type", choices=list(QUESTION_TYPES.keys()), default="1")
    q_label, q_instruction = QUESTION_TYPES[q_choice]

    console.print(f"\n[bold yellow]📝 Enter your {subject} question / topic:[/bold yellow]")
    user_input = Prompt.ask("❓")

    prompt = f"{q_instruction}\n\nSubject: {subject}\n\nQuestion/Topic: {user_input}"

    console.print()
    with Live(Spinner("dots", text="[cyan]Gemini is thinking...[/cyan]"), refresh_per_second=10):
        answer = ask_gemini(model, prompt, subject)

    console.print(Panel(
        Markdown(answer),
        title=f"[bold cyan]🤖 Gemini Tutor — {subject} / {q_label}[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

    save = Confirm.ask("Save this to history?", default=True)
    if save:
        save_to_history(history, subject, user_input, answer)
        console.print("[dim]Saved to tutor history.[/dim]")

def view_history(history: list):
    if not history:
        console.print("[yellow]No history yet.[/yellow]")
        return
    console.print(f"\n[bold cyan]📜 TUTOR HISTORY ({len(history)} sessions)[/bold cyan]\n")
    for i, h in enumerate(reversed(history[-10:]), 1):
        ts = datetime.fromisoformat(h["timestamp"]).strftime("%d %b %H:%M")
        console.print(f"[dim]{i}. [{ts}] [{h['subject']}][/dim] [bold]{h['question'][:70]}[/bold]")
    idx_str = Prompt.ask("View full answer (number) or Enter to skip", default="")
    if idx_str.strip():
        try:
            idx = int(idx_str) - 1
            h = list(reversed(history[-10:]))[idx]
            console.print(Panel(Markdown(h["answer"]), title=h["question"], border_style="cyan"))
        except (ValueError, IndexError):
            console.print("[red]Invalid.[/red]")

def quick_concepts():
    """Offline mode with curated concept summaries."""
    concepts = {
        "Photosynthesis": "Light-dependent reactions occur in thylakoid membranes; Calvin cycle in stroma. Equation: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. PS-I (700nm, P700) and PS-II (680nm, P680).",
        "Newton's Laws": "1st: Inertia (no net force → no change in motion). 2nd: F=ma. 3rd: Action-Reaction pairs are equal and opposite.",
        "DNA Structure": "Double helix by Watson & Crick (1953). A-T (2H bonds), G-C (3H bonds). Sugar-phosphate backbone. 3' to 5' antiparallel strands.",
        "Acid-Base (Arrhenius)": "Acid: produces H⁺ in water. Base: produces OH⁻ in water. Brønsted-Lowry: acid=proton donor, base=proton acceptor. Lewis: electron pair concepts.",
        "Bohr's Atomic Model": "Electrons in fixed orbits. E_n = -13.6/n² eV. Angular momentum = nh/2π. Explains hydrogen spectrum.",
        "Mendel's Laws": "Law of Segregation: two alleles separate during gamete formation. Law of Independent Assortment: genes on different chromosomes assort independently.",
    }
    console.print("\n[bold cyan]💡 QUICK CONCEPT CARDS (Offline)[/bold cyan]\n")
    for i, (topic, desc) in enumerate(concepts.items(), 1):
        console.print(f"  [cyan]{i}[/cyan] - {topic}")
    choice = Prompt.ask("Select concept", default="1")
    try:
        topic = list(concepts.keys())[int(choice) - 1]
        console.print(Panel(f"[bold]{topic}[/bold]\n\n{concepts[topic]}", border_style="green"))
    except (ValueError, IndexError):
        console.print("[red]Invalid choice.[/red]")

def main():
    console.print(Panel.fit(
        "[bold cyan]🤖 AI SUBJECT TUTOR — Powered by Gemini[/bold cyan]\n"
        "[dim]Physics · Chemistry · Biology · Math · NEET/JEE Ready[/dim]",
        border_style="cyan"
    ))
    model = get_gemini_client()
    history = load_history()

    if model:
        console.print("[green]✅ Gemini AI connected.[/green]")
    else:
        console.print("[yellow]⚠️  Running in offline mode (quick concepts only).[/yellow]")

    menu = {
        "1": "Ask AI Tutor",
        "2": "View History",
        "3": "Quick Concept Cards (Offline)",
        "4": "Exit",
    }

    while True:
        console.print("\n[bold]MENU:[/bold]")
        for k, v in menu.items():
            console.print(f"  [cyan]{k}[/cyan] - {v}")
        choice = Prompt.ask("Choose", choices=list(menu.keys()))
        if choice == "1":
            if not model:
                console.print("[red]No API key. Using offline mode.[/red]")
                quick_concepts()
            else:
                ask_question(model, history)
        elif choice == "2":
            view_history(history)
        elif choice == "3":
            quick_concepts()
        elif choice == "4":
            console.print("[dim]Keep asking questions! Curiosity is the key. 🧠[/dim]")
            break

if __name__ == "__main__":
    main()
