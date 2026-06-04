"""
50_battery_monitor.py
─────────────────────────────────────────────────────────────────────────────
Battery Monitor & Advisor
─────────────────────────────────────────────────────────────────────────────
Monitors your laptop battery with:
  • Current charge level with color-coded progress bar
  • Charging status and estimated time remaining
  • Battery health information
  • Alerts when battery is low (< 20%) or fully charged (> 95%)
  • Live auto-refresh mode
  • Desktop notifications via plyer

Usage:
    python 50_battery_monitor.py
    python 50_battery_monitor.py --watch        # Live refresh every 30s
    python 50_battery_monitor.py --alert 20     # Alert when below 20%
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import sys
import time
from datetime import datetime, timedelta

import psutil
from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


# ── helpers ───────────────────────────────────────────────────────────────────

def get_battery() -> psutil._common.sbattery | None:
    try:
        return psutil.sensors_battery()
    except Exception:
        return None


def notify_battery(title: str, message: str) -> None:
    try:
        from plyer import notification
        notification.notify(title=title, message=message,
                            app_name="Battery Monitor", timeout=10)
    except Exception:
        pass


def fmt_time_remaining(secs: int) -> str:
    if secs == psutil.POWER_TIME_UNLIMITED:
        return "∞  (plugged in)"
    if secs == psutil.POWER_TIME_UNKNOWN or secs < 0:
        return "Unknown"
    td = timedelta(seconds=secs)
    h = td.seconds // 3600
    m = (td.seconds % 3600) // 60
    return f"{h}h {m:02d}m"


def battery_color(pct: float) -> str:
    if pct >= 70:
        return "bold green"
    if pct >= 40:
        return "bold yellow"
    if pct >= 20:
        return "bold orange1"
    return "bold red"


def charging_icon(charging: bool) -> str:
    return "⚡ Charging" if charging else "🔋 Discharging"


def health_label(pct: float) -> tuple[str, str]:
    """Rough health estimate (psutil doesn't expose real health; we infer from current %."""
    # We can't get actual health from psutil on all platforms
    # Display a static placeholder with helpful message
    return "N/A (platform dependent)", "dim"


# ── display ───────────────────────────────────────────────────────────────────

def build_battery_panel(alert_low: int, alert_high: int,
                         _prev_alerted: set) -> Panel:
    batt = get_battery()

    if batt is None:
        return Panel(
            Align.center(Text(
                "\n❌  No battery detected\n\n"
                "This tool is intended for laptops.\n"
                "A desktop or VM may show no battery.\n",
                style="yellow"
            )),
            title="🔋  Battery Monitor",
            border_style="yellow",
        )

    pct = batt.percent
    charging = batt.power_plugged
    secs_left = batt.secsleft
    color = battery_color(pct)

    # Trigger alerts
    if pct <= alert_low and not charging and "low" not in _prev_alerted:
        notify_battery("⚠ Low Battery!", f"Battery at {pct:.0f}% — please plug in!")
        _prev_alerted.add("low")
    elif pct > alert_low + 5:
        _prev_alerted.discard("low")

    if pct >= alert_high and charging and "full" not in _prev_alerted:
        notify_battery("🔋 Battery Full", f"Battery at {pct:.0f}% — consider unplugging.")
        _prev_alerted.add("full")
    elif pct < alert_high - 5:
        _prev_alerted.discard("full")

    # Progress bar
    bar_width = 40
    filled = int(pct / 100 * bar_width)
    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (bar_width - filled)}[/dim]"

    # Status text
    charge_icon = charging_icon(charging)

    # Build table
    table = Table(show_header=False, box=box.SIMPLE, expand=False, padding=(0, 3))
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Charge Level",
                  f"[{color}]{pct:.1f}%[/{color}]  {bar}")
    table.add_row("Status", f"[bold]{charge_icon}[/bold]")
    table.add_row("Time Remaining", fmt_time_remaining(secs_left))
    table.add_row("Power Source", "🔌 AC Power" if charging else "🔋 Battery")
    table.add_row("Refreshed", datetime.now().strftime("%H:%M:%S"))

    # Low battery warning
    warning = ""
    if pct <= 10 and not charging:
        warning = "\n\n  [bold red blink]⚠  CRITICAL: Connect charger NOW![/bold red blink]"
    elif pct <= alert_low and not charging:
        warning = f"\n\n  [bold yellow]⚠  Low battery — please plug in![/bold yellow]"
    elif pct >= alert_high and charging:
        warning = f"\n\n  [bold green]✅  Battery full — you can unplug![/bold green]"

    content = Text.from_markup(str(table) + warning) if warning else None

    border = "red" if (pct <= alert_low and not charging) else \
             "green" if charging else "cyan"

    return Panel(
        table,
        title="[bold]🔋  Battery Monitor[/bold]",
        border_style=border,
        subtitle=warning.strip() if warning else None,
        padding=(1, 3),
    )


# ── tips ──────────────────────────────────────────────────────────────────────

BATTERY_TIPS = [
    "💡 Keep battery between 20–80% for longest lifespan.",
    "💡 Avoid full discharges — lithium batteries prefer partial cycles.",
    "💡 High screen brightness drains battery faster.",
    "💡 Disable Bluetooth and WiFi when not needed to save power.",
    "💡 Close unused background apps to extend battery life.",
    "💡 Cool temperatures extend battery runtime and lifespan.",
]


def show_tips() -> None:
    import random
    tip = random.choice(BATTERY_TIPS)
    console.print(Panel(f"[italic yellow]{tip}[/italic yellow]",
                        title="💡  Battery Tip", border_style="yellow"))


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Battery Monitor & Advisor")
    parser.add_argument("--watch", action="store_true",
                        help="Live auto-refresh mode")
    parser.add_argument("--interval", type=int, default=30,
                        help="Refresh interval in seconds for watch mode (default: 30)")
    parser.add_argument("--alert-low", type=int, default=20,
                        help="Alert when battery drops below this %% (default: 20)")
    parser.add_argument("--alert-high", type=int, default=95,
                        help="Alert when battery reaches this %% while charging (default: 95)")
    args = parser.parse_args()

    alerted: set = set()

    if args.watch:
        console.print(Panel(
            f"[bold cyan]Battery Monitor — Watch Mode[/bold cyan]\n"
            f"[dim]Refreshing every {args.interval}s | Press Ctrl+C to exit[/dim]",
            border_style="blue"
        ))
        try:
            with Live(build_battery_panel(args.alert_low, args.alert_high, alerted),
                      refresh_per_second=0.5, console=console) as live:
                while True:
                    time.sleep(args.interval)
                    live.update(build_battery_panel(args.alert_low, args.alert_high, alerted))
        except KeyboardInterrupt:
            console.print("\n[yellow]Battery monitor stopped.[/yellow]")
    else:
        console.print(build_battery_panel(args.alert_low, args.alert_high, alerted))
        show_tips()

        batt = get_battery()
        if batt:
            console.print(
                f"\n[dim]Tip: Run with [bold]--watch[/bold] for live monitoring, "
                f"or [bold]--alert-low 15[/bold] to customize alerts.[/dim]"
            )


if __name__ == "__main__":
    main()
