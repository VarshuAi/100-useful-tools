"""
Tool 11 - YouTube Downloader (Video/Audio)
Download YouTube videos or extract audio using yt-dlp.
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def yt_download():
    console.print("\n[bold cyan]📺 YOUTUBE DOWNLOADER[/bold cyan]", justify="center")
    console.print("[dim]Download videos or extract MP3 audio[/dim]\n", justify="center")

    try:
        import yt_dlp
    except ImportError:
        console.print("[red]Install yt-dlp: pip install yt-dlp[/red]")
        return

    url = Prompt.ask("🔗 YouTube URL (video or playlist)")
    
    console.print("\n[cyan]1[/cyan] - Best quality video (MP4)")
    console.print("[cyan]2[/cyan] - Audio only (MP3)")
    console.print("[cyan]3[/cyan] - Custom quality")
    console.print("[cyan]4[/cyan] - Playlist download")
    choice = Prompt.ask("Format", choices=["1","2","3","4"])

    output_dir = Prompt.ask("💾 Save to folder", default=str(Path.home() / "Downloads"))
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'outtmpl': str(Path(output_dir) / '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: console.print(f"[green]{d.get('_percent_str','').strip()}[/green] {d.get('filename','').split('/')[-1][:50]}", end="\r") if d['status'] == 'downloading' else None],
    }

    if choice == "1":
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    elif choice == "2":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}]
    elif choice == "3":
        quality = Prompt.ask("Quality (e.g. 720, 1080, 480)", default="720")
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    elif choice == "4":
        ydl_opts['format'] = 'best'
        console.print("[yellow]Downloading entire playlist...[/yellow]")

    # Show video info first
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            console.print(f"\n[bold]📹 {title}[/bold]")
            console.print(f"[dim]Duration: {duration//60}:{duration%60:02d}[/dim]")
        except:
            console.print("[yellow]Could not fetch info, proceeding...[/yellow]")

    console.print("\n[bold green]⬇️  Downloading...[/bold green]")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    console.print(f"\n\n[bold green]✅ Download complete! Saved to: {output_dir}[/bold green]")

if __name__ == "__main__":
    yt_download()
