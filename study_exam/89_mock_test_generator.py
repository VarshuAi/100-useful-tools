"""
Tool 89 - AI Mock Test Generator
Generates mock NEET/competitive test MCQs using Gemini AI.
"""
import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

def generate_test(subject, topic):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return f"""[bold yellow]Mock test questions for: {subject} - {topic}[/bold yellow] (Provide GEMINI_API_KEY for dynamic AI tests)

Q1. Which of the following is the powerhouse of the cell?
A) Nucleus
B) Mitochondria
C) Golgi body
D) Ribosome
Correct Option: B
Explanation: Mitochondria are responsible for ATP generation.

Q2. What is the SI unit of electric current?
A) Volt
B) Ohm
C) Ampere
D) Watt
Correct Option: C
Explanation: Electric current is measured in Amperes (A).
"""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Generate a 3-question MCQ quiz for {subject} on the topic '{topic}' in the style of NEET. Each question must have 4 options, the correct answer, and a short explanation."
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        return f"[red]Error generating mock test: {e}[/red]"

def main():
    console.print("\n[bold magenta]📝 AI MOCK TEST GENERATOR[/bold magenta]\n")
    subject = Prompt.ask("Select Subject", choices=["Physics", "Chemistry", "Biology"], default="Biology")
    topic = Prompt.ask("Topic name (e.g. Genetics, Thermodynamics)", default="Genetics")
    
    console.print(f"[cyan]Generating timed mock test for {subject}: {topic}...[/cyan]")
    test_content = generate_test(subject, topic)
    console.print("\n", Panel(test_content, title=f"Mock Test: {subject} - {topic}", expand=False))

if __name__ == "__main__":
    main()
