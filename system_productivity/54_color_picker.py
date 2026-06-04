"""
Tool 54 - Color Picker
Convert, display, and analyze color codes.
"""
import re
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def rgb_to_hsl(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    h = 0
    if df != 0:
        if mx == r:
            h = ((g - b) / df) % 6
        elif mx == g:
            h = (b - r) / df + 2
        elif mx == b:
            h = (r - g) / df + 4
        h = round(h * 60)
        if h < 0:
            h += 360
    l = (mx + mn) / 2
    s = 0
    if df != 0:
        s = df / (1 - abs(2 * l - 1))
    return h, round(s * 100), round(l * 100)

def main():
    console.print("\n[bold magenta]🎨 COLOR CODE CONVERTER[/bold magenta]\n")
    
    color_in = Prompt.ask("Enter hex color code (e.g. #3498db or 3498db)")
    color_in = color_in.strip()
    if not color_in.startswith('#'):
        color_in = '#' + color_in
        
    if not re.match(r"^#[0-9a-fA-F]{6}$", color_in):
        console.print("[red]Invalid hex code! Must be 6-digit hex.[/red]")
        return
        
    r, g, b = hex_to_rgb(color_in)
    h, s, l = rgb_to_hsl(r, g, b)
    
    # Complementary
    comp_r, comp_g, comp_b = 255 - r, 255 - g, 255 - b
    comp_hex = rgb_to_hex(comp_r, comp_g, comp_b)
    
    console.print(f"\n[bold]Input Color: {color_in}[/bold]")
    console.print(f"  RGB: [cyan]rgb({r}, {g}, {b})[/cyan]")
    console.print(f"  HSL: [cyan]hsl({h}, {s}%, {l}%)[/cyan]")
    
    console.print(f"\n[bold]Complementary Color: {comp_hex}[/bold]")
    console.print(f"  RGB: [cyan]rgb({comp_r}, {comp_g}, {comp_b})[/cyan]")
    
    # Render blocks of colors
    console.print(f"\nPreview: [on {color_in}]      [/on]  Complementary: [on {comp_hex}]      [/on]\n")

if __name__ == "__main__":
    main()
