"""
Tool 17 - Password Generator & Strength Checker
Generate secure passwords and evaluate password strength.
"""

import random
import string
import re
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import pyperclip

console = Console()

def check_strength(password: str) -> dict:
    score = 0
    feedback = []

    if len(password) >= 8: score += 1
    else: feedback.append("❌ Too short (min 8)")
    if len(password) >= 12: score += 1
    if len(password) >= 16: score += 1

    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))

    if has_lower: score += 1
    else: feedback.append("❌ Add lowercase letters")
    if has_upper: score += 1
    else: feedback.append("❌ Add uppercase letters")
    if has_digit: score += 1
    else: feedback.append("❌ Add numbers")
    if has_special: score += 2
    else: feedback.append("❌ Add special characters")

    # Common patterns
    common = ["password","123456","qwerty","abc123","letmein","admin","welcome"]
    if any(c in password.lower() for c in common):
        score -= 2
        feedback.append("❌ Contains common pattern")

    if score >= 7: strength = "💚 VERY STRONG"
    elif score >= 5: strength = "🟡 STRONG"
    elif score >= 3: strength = "🟠 MEDIUM"
    else: strength = "🔴 WEAK"

    return {"score": score, "strength": strength, "feedback": feedback}

def generate_password(length=16, use_upper=True, use_digits=True, use_special=True, exclude=""):
    chars = string.ascii_lowercase
    if use_upper: chars += string.ascii_uppercase
    if use_digits: chars += string.digits
    if use_special: chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    chars = "".join(c for c in chars if c not in exclude)
    
    # Ensure at least one of each
    password = []
    if use_upper: password.append(random.choice(string.ascii_uppercase))
    if use_digits: password.append(random.choice(string.digits))
    if use_special: password.append(random.choice("!@#$%^&*"))
    
    remaining = length - len(password)
    password.extend(random.choices(chars, k=remaining))
    random.shuffle(password)
    return "".join(password)

def password_tool():
    console.print("\n[bold cyan]🔑 PASSWORD GENERATOR & CHECKER[/bold cyan]", justify="center")
    console.print("[dim]Generate secure passwords & evaluate strength[/dim]\n", justify="center")

    console.print("[cyan]1[/cyan] - Generate password(s)")
    console.print("[cyan]2[/cyan] - Check password strength")
    console.print("[cyan]3[/cyan] - Memorable passphrase generator")
    choice = Prompt.ask("Choose", choices=["1","2","3"])

    if choice == "1":
        length = int(Prompt.ask("Length", default="16"))
        count = int(Prompt.ask("How many to generate?", default="5"))
        use_special = Confirm.ask("Include special chars?", default=True)
        exclude = Prompt.ask("Exclude characters (optional)", default="")

        console.print("\n[bold]Generated Passwords:[/bold]")
        passwords = []
        for i in range(count):
            p = generate_password(length, use_special=use_special, exclude=exclude)
            result = check_strength(p)
            passwords.append(p)
            console.print(f"  [cyan]{i+1}[/cyan] [bold]{p}[/bold]  {result['strength']}")
        
        pick = Prompt.ask(f"\nCopy which to clipboard? (1-{count} or blank)")
        if pick.strip() and pick.isdigit():
            idx = int(pick) - 1
            if 0 <= idx < len(passwords):
                try:
                    pyperclip.copy(passwords[idx])
                    console.print(f"[green]✅ Password #{int(pick)} copied to clipboard![/green]")
                except:
                    console.print(f"[yellow]Password: {passwords[idx]}[/yellow]")

    elif choice == "2":
        password = Prompt.ask("Enter password to check", password=True)
        result = check_strength(password)
        console.print(Panel(
            f"[bold]Strength: {result['strength']}[/bold]\nScore: {result['score']}/9\n" +
            ("\n".join(result['feedback']) if result['feedback'] else "✅ No issues found!"),
            title="Password Analysis", border_style="cyan"
        ))

    elif choice == "3":
        words = ["correct","horse","battery","staple","mountain","ocean","thunder","crystal",
                 "shadow","falcon","quantum","neural","cyber","delta","sigma","omega"]
        count = int(Prompt.ask("Words in passphrase", default="4"))
        separator = Prompt.ask("Separator", default="-")
        passphrases = []
        for _ in range(5):
            phrase = separator.join(random.choices(words, k=count))
            num = random.randint(10,99)
            phrase += f"{separator}{num}"
            passphrases.append(phrase)
            console.print(f"  [bold cyan]{phrase}[/bold cyan]")
        
        pick = Prompt.ask("Copy which? (1-5 or blank)")
        if pick.strip() and pick.isdigit():
            try:
                pyperclip.copy(passphrases[int(pick)-1])
                console.print("[green]✅ Copied to clipboard![/green]")
            except:
                pass

if __name__ == "__main__":
    password_tool()
