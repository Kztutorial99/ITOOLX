#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║          ITOOLX — Auto Setup Termux Edition             ║
# ╚══════════════════════════════════════════════════════════╝

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'

banner() {
  clear
  echo -e "${CYAN}"
  echo "  ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗"
  echo "  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ╚██╗██╔╝"
  echo "  ██║   ██║   ██║   ██║██║   ██║██║      ╚███╔╝ "
  echo "  ██║   ██║   ██║   ██║██║   ██║██║      ██╔██╗ "
  echo "  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██╔╝ ██╗"
  echo "  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝"
  echo -e "${RESET}"
  echo -e "  ${BOLD}Auto Setup — Termux Edition${RESET}"
  echo -e "  ${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""
}

ok()   { echo -e "  ${GREEN}✓${RESET}  $1"; }
info() { echo -e "  ${CYAN}→${RESET}  $1"; }
warn() { echo -e "  ${YELLOW}!${RESET}  $1"; }
fail() { echo -e "  ${RED}✗${RESET}  $1"; exit 1; }
step() { echo -e "\n  ${BOLD}${CYAN}[$1]${RESET} $2"; }

banner

# ── [1] Update & upgrade
step "1/6" "Update Termux packages"
info "pkg update + upgrade (mungkin butuh beberapa menit)..."
pkg update -y -o Dpkg::Options::="--force-confold" 2>/dev/null || true
pkg upgrade -y -o Dpkg::Options::="--force-confold" 2>/dev/null || true
ok "Packages updated"

# ── [2] Install deps sistem
step "2/6" "Install dependencies"
PKGS="python git curl jq"
for p in $PKGS; do
  if ! command -v $p &>/dev/null; then
    info "Installing $p..."
    pkg install -y $p 2>/dev/null || warn "Gagal install $p, lanjut..."
  else
    ok "$p sudah ada"
  fi
done

# ── [3] Clone / pull repo
step "3/6" "Ambil kode ITOOLX"
REPO_URL="https://github.com/Kztutorial99/ITOOLX.git"
INSTALL_DIR="$HOME/ITOOLX"

if [ -d "$INSTALL_DIR/.git" ]; then
  info "Repo sudah ada, pull update..."
  cd "$INSTALL_DIR" && git pull --rebase 2>/dev/null && ok "Updated ke versi terbaru" || warn "Git pull gagal, pakai versi lokal"
else
  info "Clone dari GitHub..."
  git clone "$REPO_URL" "$INSTALL_DIR" 2>/dev/null || fail "Gagal clone repo. Cek koneksi internet."
  ok "Repo berhasil di-clone ke $INSTALL_DIR"
fi
cd "$INSTALL_DIR"

# ── [4] Install Python packages
step "4/6" "Install Python dependencies"
PYLIBS="requests rich cloudscraper"
info "pip install $PYLIBS"
pip install --quiet --upgrade $PYLIBS 2>/dev/null || pip install $PYLIBS || warn "pip install partial gagal, coba manual: pip install $PYLIBS"
ok "Python packages siap"

# ── [5] Setup env (OLSERA_EMAIL & OLSERA_PASSWORD)
step "5/6" "Konfigurasi akun Olsera (auto-refresh token)"
ENV_FILE="$HOME/.itoolx_env"

# Cek apakah env sudah ada
OLS_EMAIL_EXISTING=""
OLS_PASS_EXISTING=""
if [ -f "$ENV_FILE" ]; then
  source "$ENV_FILE" 2>/dev/null
  OLS_EMAIL_EXISTING="$OLSERA_EMAIL"
  OLS_PASS_EXISTING="$OLSERA_PASSWORD"
fi

if [ -n "$OLS_EMAIL_EXISTING" ]; then
  warn "Akun Olsera sudah tersimpan: ${OLS_EMAIL_EXISTING}"
  echo -ne "  ${CYAN}→${RESET}  Mau ganti? (y/N): "
  read -r CHANGE_CREDS
  CHANGE_CREDS="${CHANGE_CREDS:-n}"
else
  CHANGE_CREDS="y"
fi

if [[ "$CHANGE_CREDS" =~ ^[Yy]$ ]]; then
  echo ""
  echo -ne "  ${CYAN}→${RESET}  Email Olsera   : "
  read -r INPUT_EMAIL
  echo -ne "  ${CYAN}→${RESET}  Password Olsera: "
  read -rs INPUT_PASS
  echo ""

  if [ -n "$INPUT_EMAIL" ] && [ -n "$INPUT_PASS" ]; then
    cat > "$ENV_FILE" <<ENVEOF
export OLSERA_EMAIL="$INPUT_EMAIL"
export OLSERA_PASSWORD="$INPUT_PASS"
ENVEOF
    chmod 600 "$ENV_FILE"
    ok "Credentials disimpan di $ENV_FILE"
  else
    warn "Email/password kosong, skip. Olesera tidak akan auto-refresh token."
  fi
else
  ok "Pakai credentials yang sudah ada"
fi

# Tambah source ke bashrc / bash_profile kalau belum ada
PROFILE="$HOME/.bashrc"
[ -f "$HOME/.bash_profile" ] && PROFILE="$HOME/.bash_profile"
if ! grep -q "itoolx_env" "$PROFILE" 2>/dev/null; then
  echo "" >> "$PROFILE"
  echo "# ITOOLX env" >> "$PROFILE"
  echo "[ -f \"\$HOME/.itoolx_env\" ] && source \"\$HOME/.itoolx_env\"" >> "$PROFILE"
  ok "Auto-load credentials ditambahkan ke $PROFILE"
fi

# ── [6] Buat alias / launcher
step "6/6" "Buat launcher 'itoolx'"
LAUNCHER="$PREFIX/bin/itoolx"
cat > "$LAUNCHER" <<'LAUNCHEOF'
#!/data/data/com.termux/files/usr/bin/bash
[ -f "$HOME/.itoolx_env" ] && source "$HOME/.itoolx_env"
cd "$HOME/ITOOLX"
# Pull update diam-diam di background
git pull --quiet --rebase 2>/dev/null &
python ITOOLX.py "$@"
LAUNCHEOF
chmod +x "$LAUNCHER"
ok "Launcher dibuat → ketik: ${BOLD}itoolx${RESET} untuk jalankan"

# ── Done
echo ""
echo -e "  ${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  ${GREEN}${BOLD}✓  Setup selesai!${RESET}"
echo ""
echo -e "  ${BOLD}Cara pakai:${RESET}"
echo -e "  ${CYAN}itoolx${RESET}            → jalankan ITOOLX"
echo -e "  ${CYAN}cd ~/ITOOLX${RESET}       → masuk folder"
echo -e "  ${CYAN}git pull${RESET}          → update manual"
echo ""
echo -e "  ${YELLOW}Note:${RESET} Tutup & buka ulang Termux agar env aktif,"
echo -e "  atau jalankan: ${CYAN}source ~/.bashrc${RESET}"
echo ""
