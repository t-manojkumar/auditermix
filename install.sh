#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════
#  auditermix — macOS / Linux one-time installer
#  Auto-installs: Python 3.11+, ffmpeg, yt-dlp
#  Generates: .venv/, run.sh, macOS .command launcher
# ════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────────────────
if [ -t 1 ]; then
    OR="\033[38;5;214m" GR="\033[38;5;120m" RE="\033[38;5;203m"
    SM="\033[38;5;245m" GH="\033[38;5;238m" YL="\033[38;5;228m"
    BO="\033[1m" RS="\033[0m"
else
    OR="" GR="" RE="" SM="" GH="" YL="" BO="" RS=""
fi

ok()   { echo -e "  ${GR}✓${RS}  $*"; }
fail() { echo -e "  ${RE}✗${RS}  $*"; exit 1; }
info() { echo -e "  ${SM}·${RS}  $*"; }
step() { echo -e "  ${GH}checking $*...${RS}"; }
warn() { echo -e "  ${YL}◆${RS}  $*"; }

# ── Detect OS + package manager ───────────────────────────────────────────────
OS="unknown"
case "$(uname -s)" in
    Darwin) OS="macos" ;;
    Linux)
        if   grep -qi ubuntu  /etc/os-release 2>/dev/null; then OS="ubuntu"
        elif grep -qi debian  /etc/os-release 2>/dev/null; then OS="debian"
        elif grep -qi fedora  /etc/os-release 2>/dev/null; then OS="fedora"
        elif grep -qi arch    /etc/os-release 2>/dev/null; then OS="arch"
        elif grep -qi alpine  /etc/os-release 2>/dev/null; then OS="alpine"
        else OS="linux"
        fi ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "  ${OR}╔══════════════════════════════════════════════╗${RS}"
echo -e "  ${OR}║${RS}  auditermix  |  one-time setup              ${OR}║${RS}"
echo -e "  ${OR}╚══════════════════════════════════════════════╝${RS}"
echo ""
info "platform: $OS"
echo ""


# ── Package installer helper ──────────────────────────────────────────────────
install_pkg() {
    local pkg="$1"
    case "$OS" in
        macos)
            command -v brew &>/dev/null || fail "Homebrew not found.
  Install: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            brew install "$pkg" ;;
        ubuntu|debian) sudo apt-get update -qq && sudo apt-get install -y "$pkg" ;;
        fedora)        sudo dnf install -y "$pkg" ;;
        arch)          sudo pacman -Sy --noconfirm "$pkg" ;;
        alpine)        sudo apk add --no-cache "$pkg" ;;
        *)             fail "Cannot auto-install on $OS — install $pkg manually." ;;
    esac
}


# ── 1. PYTHON ─────────────────────────────────────────────────────────────────
step "python"
PYTHON_BIN=""

for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        maj="${ver%%.*}"; min="${ver##*.}"
        if [[ $maj -ge 3 && $min -ge 11 ]]; then
            PYTHON_BIN="$candidate"
            ok "Python $ver  ($candidate)"
            break
        fi
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    warn "Python 3.11+ not found — installing..."
    case "$OS" in
        macos)
            install_pkg python@3.11
            PYTHON_BIN="$(brew --prefix python@3.11)/bin/python3.11" ;;
        ubuntu|debian)
            sudo apt-get install -y software-properties-common
            sudo add-apt-repository -y ppa:deadsnakes/ppa
            sudo apt-get update -qq
            sudo apt-get install -y python3.11 python3.11-venv python3.11-distutils
            PYTHON_BIN="python3.11" ;;
        fedora) install_pkg python3.11 ; PYTHON_BIN="python3.11" ;;
        arch)   install_pkg python     ; PYTHON_BIN="python3" ;;
        alpine) install_pkg python3    ; PYTHON_BIN="python3" ;;
        *) fail "Cannot auto-install Python on $OS. Download from https://python.org" ;;
    esac
    ok "Python 3.11 installed"
fi


# ── 2. FFMPEG ─────────────────────────────────────────────────────────────────
step "ffmpeg"

if command -v ffmpeg &>/dev/null; then
    FFVER=$(ffmpeg -version 2>&1 | awk 'NR==1{print $3}')
    ok "ffmpeg $FFVER"
else
    warn "ffmpeg not found — installing..."
    case "$OS" in
        macos) install_pkg ffmpeg ;;
        ubuntu|debian) install_pkg ffmpeg ;;
        fedora)
            sudo dnf install -y \
              https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm \
              2>/dev/null || true
            sudo dnf install -y ffmpeg ;;
        arch)   install_pkg ffmpeg ;;
        alpine) install_pkg ffmpeg ;;
        *) fail "Cannot auto-install ffmpeg. See https://ffmpeg.org/download.html" ;;
    esac
    ok "ffmpeg installed"
fi


# ── 3. VIRTUAL ENVIRONMENT ────────────────────────────────────────────────────
step "virtual environment"

if [[ -d .venv ]]; then
    ok ".venv exists — skipping"
else
    "$PYTHON_BIN" -m venv .venv
    ok ".venv created"
fi


# ── 4. YT-DLP ─────────────────────────────────────────────────────────────────
step "yt-dlp"
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/pip install --quiet --upgrade yt-dlp
ok "yt-dlp ready"


# ── 5. LAUNCHERS ─────────────────────────────────────────────────────────────
step "launchers"

cat > run.sh << 'RUN'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
.venv/bin/python auditermix.py "$@"
RUN
chmod +x run.sh
ok "run.sh"

# macOS double-clickable launcher in Finder
if [[ "$OS" == "macos" ]]; then
    cat > "auditermix.command" << 'CMD'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
.venv/bin/python auditermix.py
CMD
    chmod +x "auditermix.command"
    xattr -d com.apple.quarantine "auditermix.command" 2>/dev/null || true
    ok "auditermix.command (Finder double-click)"
fi


# ── DONE ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${OR}╔══════════════════════════════════════════════╗${RS}"
echo -e "  ${OR}║${RS}  ${GR}✓${RS}  Setup complete!                        ${OR}║${RS}"
echo -e "  ${OR}╚══════════════════════════════════════════════╝${RS}"
echo ""
echo -e "  Launch anytime:"
echo -e "    ${SM}bash run.sh${RS}                       terminal"
[[ "$OS" == "macos" ]] && \
echo -e "    ${SM}double-click auditermix.command${RS}   Finder"
echo ""
