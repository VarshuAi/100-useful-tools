"""
Tool 07 - File Encryption & Decryption
Encrypt or decrypt files using AES-256 (password-based).
"""

import os
import hashlib
import struct
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm

console = Console()

def get_key(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()

def encrypt_file(filepath: Path, password: str):
    key = get_key(password)
    iv = os.urandom(16)
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
    except ImportError:
        console.print("[red]Install pycryptodome: pip install pycryptodome[/red]")
        return

    with open(filepath, "rb") as f:
        data = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    
    out = filepath.with_suffix(filepath.suffix + ".enc")
    with open(out, "wb") as f:
        f.write(iv + encrypted)
    
    console.print(f"[bold green]✅ Encrypted → {out}[/bold green]")

def decrypt_file(filepath: Path, password: str):
    key = get_key(password)
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import unpad
    except ImportError:
        console.print("[red]Install pycryptodome: pip install pycryptodome[/red]")
        return

    with open(filepath, "rb") as f:
        iv = f.read(16)
        encrypted = f.read()

    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = unpad(cipher.decrypt(encrypted), AES.block_size)
    except Exception:
        console.print("[bold red]❌ Wrong password or corrupted file![/bold red]")
        return
    
    # Remove .enc suffix
    out_name = filepath.name.replace(".enc", "")
    if out_name == filepath.name:
        out_name = "decrypted_" + filepath.name
    out = filepath.parent / out_name
    
    with open(out, "wb") as f:
        f.write(data)
    console.print(f"[bold green]✅ Decrypted → {out}[/bold green]")

def file_encryption():
    console.print("\n[bold cyan]🔒 FILE ENCRYPTION TOOL[/bold cyan]", justify="center")
    console.print("[dim]AES-256 password-based encryption[/dim]\n", justify="center")

    action = Prompt.ask("Action", choices=["encrypt","decrypt"])
    filepath = Path(Prompt.ask("File path"))
    
    if not filepath.exists():
        console.print("[red]File not found![/red]")
        return
    
    password = Prompt.ask("Password", password=True)
    if action == "encrypt":
        confirm = Prompt.ask("Confirm password", password=True)
        if password != confirm:
            console.print("[red]Passwords do not match![/red]")
            return
        encrypt_file(filepath, password)
    else:
        decrypt_file(filepath, password)

if __name__ == "__main__":
    file_encryption()
