"""
Tool 55 - ASCII Art Generator
Convert text to ASCII art using pyfiglet, or convert an image.
"""
import pyfiglet
from rich.console import Console
from rich.prompt import Prompt
from PIL import Image

console = Console()

def text_to_ascii():
    text = Prompt.ask("Enter text to convert")
    fonts = ['standard', 'slant', 'banner', 'isometric1', 'block']
    console.print("\nAvailable Fonts: " + ", ".join(fonts))
    font = Prompt.ask("Select font", choices=fonts, default="standard")
    
    try:
        result = pyfiglet.figlet_format(text, font=font)
        console.print(f"\n[green]{result}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

def image_to_ascii():
    img_path = Prompt.ask("Enter path to image file")
    try:
        img = Image.open(img_path)
        # resize for aspect ratio correction
        width, height = img.size
        aspect_ratio = height / width
        new_width = 80
        new_height = int(aspect_ratio * new_width * 0.5)
        img = img.resize((new_width, new_height)).convert('L')
        
        chars = "@%#*+=-:. "
        pixels = img.getdata()
        ascii_str = ""
        for i, pix in enumerate(pixels):
            if i % new_width == 0 and i > 0:
                ascii_str += "\n"
            ascii_str += chars[pix * len(chars) // 256]
            
        console.print(f"\n[cyan]{ascii_str}[/cyan]")
    except Exception as e:
        console.print(f"[red]Error opening or processing image: {e}[/red]")

def main():
    console.print("\n[bold magenta]🎭 ASCII ART GENERATOR[/bold magenta]\n")
    console.print("[1] Convert Text to ASCII Art")
    console.print("[2] Convert Image to ASCII Art")
    choice = Prompt.ask("Choose mode", choices=["1", "2"], default="1")
    
    if choice == "1":
        text_to_ascii()
    else:
        image_to_ascii()

if __name__ == "__main__":
    main()
