"""
Tool 05 - Image Batch Converter & Resizer
Convert image formats, resize batches, add watermarks, compress.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import track

console = Console()

def check_pil():
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
    except ImportError:
        console.print("[red]Install Pillow: pip install Pillow[/red]")
        sys.exit(1)

def image_batch():
    Image, ImageDraw, ImageFont = check_pil()
    console.print("\n[bold cyan]🖼️  IMAGE BATCH PROCESSOR[/bold cyan]", justify="center")
    console.print("[dim]Convert • Resize • Watermark • Compress[/dim]\n", justify="center")

    folder = Prompt.ask("📁 Image folder", default=".")
    folder = Path(folder)
    supported = [".jpg",".jpeg",".png",".bmp",".gif",".tiff",".webp"]
    images = [f for f in folder.iterdir() if f.suffix.lower() in supported]

    if not images:
        console.print("[red]No images found![/red]")
        return

    console.print(f"[green]Found {len(images)} images[/green]\n")
    console.print("[cyan]1[/cyan] - Convert format")
    console.print("[cyan]2[/cyan] - Resize all")
    console.print("[cyan]3[/cyan] - Add watermark text")
    console.print("[cyan]4[/cyan] - Compress (reduce quality)")

    choice = Prompt.ask("Choose", choices=["1","2","3","4"])
    output_dir = folder / "processed"
    output_dir.mkdir(exist_ok=True)

    if choice == "1":
        fmt = Prompt.ask("Target format", choices=["png","jpg","webp","bmp"], default="png")
        for img_path in track(images, description="Converting..."):
            with Image.open(img_path) as img:
                if fmt == "jpg" and img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                out = output_dir / (img_path.stem + "." + fmt)
                img.save(str(out))
        console.print(f"[bold green]✅ Converted {len(images)} images → {output_dir}[/bold green]")

    elif choice == "2":
        width = int(Prompt.ask("Width (px)", default="800"))
        height = int(Prompt.ask("Height (px, 0=auto)", default="0"))
        for img_path in track(images, description="Resizing..."):
            with Image.open(img_path) as img:
                if height == 0:
                    ratio = width / img.width
                    new_size = (width, int(img.height * ratio))
                else:
                    new_size = (width, height)
                resized = img.resize(new_size, Image.LANCZOS)
                out = output_dir / img_path.name
                resized.save(str(out))
        console.print(f"[bold green]✅ Resized {len(images)} images → {output_dir}[/bold green]")

    elif choice == "3":
        watermark = Prompt.ask("Watermark text", default="© Varshan")
        for img_path in track(images, description="Watermarking..."):
            with Image.open(img_path).convert("RGBA") as img:
                overlay = Image.new("RGBA", img.size, (255,255,255,0))
                draw = ImageDraw.Draw(overlay)
                font_size = max(20, img.width // 20)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                bbox = draw.textbbox((0,0), watermark, font=font)
                x = img.width - (bbox[2]-bbox[0]) - 10
                y = img.height - (bbox[3]-bbox[1]) - 10
                draw.text((x, y), watermark, font=font, fill=(255,255,255,128))
                combined = Image.alpha_composite(img, overlay)
                out = output_dir / img_path.name
                combined.convert("RGB").save(str(out))
        console.print(f"[bold green]✅ Watermarked {len(images)} images → {output_dir}[/bold green]")

    elif choice == "4":
        quality = int(Prompt.ask("Quality (1-95, lower=smaller)", default="60"))
        for img_path in track(images, description="Compressing..."):
            with Image.open(img_path) as img:
                if img.mode in ("RGBA","P"):
                    img = img.convert("RGB")
                out = output_dir / (img_path.stem + "_compressed.jpg")
                img.save(str(out), "JPEG", quality=quality, optimize=True)
        console.print(f"[bold green]✅ Compressed {len(images)} images → {output_dir}[/bold green]")

if __name__ == "__main__":
    image_batch()
