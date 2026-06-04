"""
Tool 06 - QR Code Generator
Generate QR codes for URLs, text, contact info, WiFi credentials.
"""

import qrcode
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def generate_qr():
    console.print("\n[bold cyan]📲 QR CODE GENERATOR[/bold cyan]", justify="center")
    console.print("[dim]Generate QR codes for anything[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - URL / Website")
    console.print("[cyan]2[/cyan] - Plain text")
    console.print("[cyan]3[/cyan] - WiFi credentials")
    console.print("[cyan]4[/cyan] - Contact vCard")
    console.print("[cyan]5[/cyan] - Email")

    choice = Prompt.ask("Choose type", choices=["1","2","3","4","5"])
    
    data = ""
    filename = "qrcode.png"

    if choice == "1":
        url = Prompt.ask("Enter URL")
        data = url
        filename = "qr_url.png"
    
    elif choice == "2":
        data = Prompt.ask("Enter text")
        filename = "qr_text.png"
    
    elif choice == "3":
        ssid = Prompt.ask("WiFi SSID (network name)")
        password = Prompt.ask("Password")
        security = Prompt.ask("Security type", choices=["WPA","WEP","nopass"], default="WPA")
        data = f"WIFI:T:{security};S:{ssid};P:{password};;"
        filename = f"qr_wifi_{ssid}.png"
    
    elif choice == "4":
        name = Prompt.ask("Full name")
        phone = Prompt.ask("Phone")
        email = Prompt.ask("Email")
        org = Prompt.ask("Organization (optional)", default="")
        data = f"BEGIN:VCARD\nVERSION:3.0\nFN:{name}\nTEL:{phone}\nEMAIL:{email}\nORG:{org}\nEND:VCARD"
        filename = f"qr_contact_{name.replace(' ','_')}.png"
    
    elif choice == "5":
        to = Prompt.ask("To email")
        subject = Prompt.ask("Subject")
        body = Prompt.ask("Body (optional)", default="")
        data = f"mailto:{to}?subject={subject}&body={body}"
        filename = "qr_email.png"

    # QR settings
    fill = Prompt.ask("QR color (e.g. black, navy, #1a1a2e)", default="black")
    bg = Prompt.ask("Background color", default="white")
    size = int(Prompt.ask("Size (box size, 5-20)", default="10"))

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=size, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color=bg)
    img.save(filename)

    console.print(f"\n[bold green]✅ QR Code saved as: {filename}[/bold green]")
    console.print(f"[dim]Data: {data[:80]}{'...' if len(data)>80 else ''}[/dim]")

if __name__ == "__main__":
    generate_qr()
