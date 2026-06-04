"""
Tool 13 - Markdown to HTML Converter
Convert Markdown files to beautiful, styled HTML pages.
"""

import re
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def md_to_html(md: str, title: str = "Document") -> str:
    # Basic MD parsing
    html_body = md
    # Headers
    for i in range(6, 0, -1):
        html_body = re.sub(r'^' + '#'*i + r' (.+)$', rf'<h{i}>\1</h{i}>', html_body, flags=re.MULTILINE)
    # Bold and Italic
    html_body = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html_body)
    html_body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_body)
    html_body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_body)
    # Code blocks
    html_body = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html_body, flags=re.DOTALL)
    html_body = re.sub(r'`(.+?)`', r'<code>\1</code>', html_body)
    # Links
    html_body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html_body)
    # Images
    html_body = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', html_body)
    # Horizontal rule
    html_body = re.sub(r'^---$', '<hr>', html_body, flags=re.MULTILINE)
    # Blockquotes
    html_body = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html_body, flags=re.MULTILINE)
    # Unordered lists
    html_body = re.sub(r'^- (.+)$', r'<li>\1</li>', html_body, flags=re.MULTILINE)
    html_body = re.sub(r'(<li>.*?</li>\n)+', lambda m: '<ul>\n' + m.group(0) + '</ul>\n', html_body, flags=re.DOTALL)
    # Paragraphs
    paragraphs = html_body.split('\n\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        processed.append(p)
    html_body = '\n'.join(processed)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #0d1117; color: #e6edf3; line-height: 1.7; }}
    h1,h2,h3,h4,h5,h6 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
    a {{ color: #58a6ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ background: #161b22; padding: 2px 6px; border-radius: 4px; font-family: 'Fira Code', monospace; color: #ff7b72; }}
    pre {{ background: #161b22; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #30363d; }}
    pre code {{ background: none; color: #e6edf3; }}
    blockquote {{ border-left: 4px solid #58a6ff; margin: 0; padding: 8px 20px; background: #161b22; border-radius: 0 8px 8px 0; }}
    img {{ max-width: 100%; border-radius: 8px; }}
    hr {{ border: none; border-top: 1px solid #30363d; }}
    ul,ol {{ padding-left: 20px; }}
    li {{ margin: 4px 0; }}
  </style>
</head>
<body>
{html_body}
</body>
</html>"""

def markdown_converter():
    console.print("\n[bold cyan]📝 MARKDOWN → HTML CONVERTER[/bold cyan]", justify="center")
    console.print("[dim]Convert MD files to beautiful dark-themed HTML[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - Convert a file")
    console.print("[cyan]2[/cyan] - Type/paste markdown text")
    choice = Prompt.ask("Choose", choices=["1","2"])

    if choice == "1":
        filepath = Path(Prompt.ask("Markdown file path"))
        if not filepath.exists():
            console.print("[red]File not found![/red]")
            return
        md_text = filepath.read_text(encoding="utf-8")
        title = filepath.stem
        out = filepath.with_suffix(".html")
    else:
        console.print("[dim]Paste your markdown (type END on new line when done):[/dim]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        md_text = "\n".join(lines)
        title = Prompt.ask("Document title", default="My Document")
        out = Path(title.replace(" ", "_") + ".html")

    html = md_to_html(md_text, title)
    out.write_text(html, encoding="utf-8")
    console.print(f"\n[bold green]✅ HTML saved to: {out}[/bold green]")
    console.print(f"[dim]Size: {len(html)} bytes[/dim]")

if __name__ == "__main__":
    markdown_converter()
