"""
Tool 04 - PDF Toolkit
Merge, split, compress, or extract text from PDF files.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

def check_deps():
    try:
        import PyPDF2
        return PyPDF2
    except ImportError:
        console.print("[red]Install PyPDF2: pip install PyPDF2[/red]")
        sys.exit(1)

def merge_pdfs(PyPDF2):
    files_input = Prompt.ask("Enter PDF paths separated by commas")
    files = [Path(f.strip()) for f in files_input.split(",")]
    output = Prompt.ask("Output filename", default="merged_output.pdf")

    merger = PyPDF2.PdfMerger()
    for f in files:
        if f.exists():
            merger.append(str(f))
            console.print(f"[green]Added: {f.name}[/green]")
        else:
            console.print(f"[red]Not found: {f}[/red]")
    
    merger.write(output)
    merger.close()
    console.print(f"\n[bold green]✅ Merged PDF saved as: {output}[/bold green]")

def split_pdf(PyPDF2):
    filepath = Path(Prompt.ask("PDF to split"))
    if not filepath.exists():
        console.print("[red]File not found![/red]")
        return
    
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        total = len(reader.pages)
        console.print(f"[cyan]Total pages: {total}[/cyan]")
        
        mode = Prompt.ask("Split mode", choices=["each", "range"])
        
        if mode == "each":
            for i, page in enumerate(reader.pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(page)
                out = filepath.stem + f"_page_{i+1}.pdf"
                with open(out, "wb") as out_f:
                    writer.write(out_f)
            console.print(f"[bold green]✅ Split into {total} PDFs![/bold green]")
        
        elif mode == "range":
            start = int(Prompt.ask("Start page (1-indexed)")) - 1
            end = int(Prompt.ask("End page (inclusive)"))
            writer = PyPDF2.PdfWriter()
            for page in reader.pages[start:end]:
                writer.add_page(page)
            out = filepath.stem + f"_p{start+1}-{end}.pdf"
            with open(out, "wb") as out_f:
                writer.write(out_f)
            console.print(f"[bold green]✅ Extracted pages {start+1}-{end} → {out}[/bold green]")

def extract_text(PyPDF2):
    filepath = Path(Prompt.ask("PDF to extract text from"))
    if not filepath.exists():
        console.print("[red]File not found![/red]")
        return
    
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        all_text = ""
        for i, page in enumerate(reader.pages):
            all_text += f"\n--- Page {i+1} ---\n"
            all_text += page.extract_text() or ""
    
    out = filepath.stem + "_text.txt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(all_text)
    console.print(f"[bold green]✅ Text saved to: {out} ({len(all_text)} chars)[/bold green]")

def pdf_toolkit():
    PyPDF2 = check_deps()
    console.print("\n[bold cyan]📄 PDF TOOLKIT[/bold cyan]", justify="center")
    console.print("[dim]Merge • Split • Extract Text[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - Merge multiple PDFs")
    console.print("[cyan]2[/cyan] - Split PDF by page")
    console.print("[cyan]3[/cyan] - Extract text to .txt")

    choice = Prompt.ask("Choose", choices=["1","2","3"])
    
    if choice == "1":
        merge_pdfs(PyPDF2)
    elif choice == "2":
        split_pdf(PyPDF2)
    elif choice == "3":
        extract_text(PyPDF2)

if __name__ == "__main__":
    pdf_toolkit()
