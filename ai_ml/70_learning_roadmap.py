"""
Tool 70 - AI Learning Roadmap Generator
Generates structured learning roadmaps for any topic using Gemini AI.
"""
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def generate_roadmap(topic, level):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Mock/Fallback roadmap
        return f"""[bold yellow]Mock Roadmap for: {topic} ({level})[/bold yellow] (Set GEMINI_API_KEY env var for full AI gen)

Week 1: Foundations & Core Concepts
- Research basic terminology, watch introductory video lectures.
- Complete 2 basic exercises.

Week 2: Intermediate Syntax & Tools
- Dive into advanced details and standard workflows.
- Set up local development environment and run sample scripts.

Week 3: Build & Experiment
- Work on a small personal project.
- Integrate 2 different concepts.

Week 4: Review & Deploy
- Optimize performance and debug errors.
- Publish work and seek review from online forums.
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Create a structured weekly 4-week learning roadmap for a {level} learning {topic}. Outline topics, exercises, and recommended resources for each week."
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Failed to generate roadmap using Gemini API: {e}[/red]"

def main():
    console.print("\n[bold magenta]🗺️  AI LEARNING ROADMAP GENERATOR[/bold magenta]\n")
    topic = Prompt.ask("What topic/skill do you want to learn?")
    level = Prompt.ask("Your current experience level", choices=["Beginner", "Intermediate", "Advanced"], default="Beginner")
    
    console.print(f"[cyan]Generating roadmap for '{topic}'...[/cyan]")
    roadmap = generate_roadmap(topic, level)
    
    console.print("\n", Panel(roadmap, title=f"Learning Roadmap: {topic} ({level})", expand=False))

if __name__ == "__main__":
    main()
