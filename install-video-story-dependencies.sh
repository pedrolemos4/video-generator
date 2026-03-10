#!/usr/bin/env bash
# =============================================================================
# install_dependencies.sh
# Installs all dependencies required for the Video Story Pipeline
# Supports: Ubuntu 20.04, 22.04, 24.04 — also works on Raspberry Pi (Ubuntu)
# =============================================================================

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

log()     { echo -e "${BLUE}▶  $1${NC}"; }
success() { echo -e "${GREEN}✅  $1${NC}"; }
warn()    { echo -e "${YELLOW}⚠️   $1${NC}"; }
error()   { echo -e "${RED}❌  $1${NC}"; exit 1; }

# ── Root check ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    error "Please run as root: sudo bash install_dependencies.sh"
fi

echo ""
echo "============================================="
echo "   Video Story Pipeline — Dependency Setup  "
echo "============================================="
echo ""

# ── 1. System update ──────────────────────────────────────────────────────────
log "Updating apt package list..."
apt-get update -qq
success "Package list updated"

# ── 2. ffmpeg ─────────────────────────────────────────────────────────────────
log "Installing ffmpeg (video processing, encoding, subtitles, thumbnails)..."
apt-get install -y ffmpeg > /dev/null
success "ffmpeg installed: $(ffmpeg -version 2>&1 | head -1)"

# ── 3. Python3 + pip ──────────────────────────────────────────────────────────
log "Installing Python3 and pip..."
apt-get install -y python3 python3-pip > /dev/null
success "Python3 installed: $(python3 --version)"

log "Installing python3-venv (required to create virtual environments)..."
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
apt-get install -y "python${PYTHON_VERSION}-venv" > /dev/null 2>&1 || \
apt-get install -y python3-venv > /dev/null
success "python${PYTHON_VERSION}-venv installed"

log "Upgrading pip to latest version..."
python3 -m pip install --upgrade pip --break-system-packages --quiet
success "pip upgraded: $(pip3 --version)"

# ── 4. curl ───────────────────────────────────────────────────────────────────
log "Installing curl (for cloud API calls)..."
apt-get install -y curl > /dev/null
success "curl installed: $(curl --version | head -1)"

# ── 5. yt-dlp ────────────────────────────────────────────────────────────────
log "Installing yt-dlp (video downloader)..."
pip3 install --break-system-packages --quiet yt-dlp
success "yt-dlp installed: $(yt-dlp --version)"

# ── 6. openai-whisper ─────────────────────────────────────────────────────────
log "Installing openai-whisper (local audio transcription)..."
warn "This may take a few minutes — it includes PyTorch as a dependency"
pip3 install --break-system-packages --quiet openai-whisper
success "openai-whisper installed"

# ── 7. whisper-ctranslate2 ────────────────────────────────────────────────────
log "Installing whisper-ctranslate2 (faster CPU-optimised Whisper)..."
pip3 install --break-system-packages --ignore-installed whisper-ctranslate2
success "whisper-ctranslate2 installed"

# ── 8. edge-tts ───────────────────────────────────────────────────────────────
log "Installing edge-tts (free text-to-speech, no API key needed)..."
pip3 install --break-system-packages --quiet edge-tts
success "edge-tts installed"

# ── 9. Verification ───────────────────────────────────────────────────────────
echo ""
echo "============================================="
echo "   Verification"
echo "============================================="

check() {
    local name=$1
    local cmd=$2
    if eval "$cmd" &> /dev/null; then
        success "$name — OK"
    else
        warn "$name — could not verify (may still work)"
    fi
}

check "ffmpeg"              "ffmpeg -version"
check "ffprobe"             "ffprobe -version"
check "yt-dlp"              "yt-dlp --version"
check "whisper"             "whisper --help"
check "whisper-ctranslate2" "whisper-ctranslate2 --help"
check "edge-tts"            "python3 -c 'import edge_tts'"
check "Python asyncio"      "python3 -c 'import asyncio'"

# ── 10. Whisper model download (optional) ────────────────────────────────────
echo ""
echo "============================================="
echo "   Optional: Pre-download Whisper model"
echo "============================================="
echo ""
echo "  Whisper downloads the model on first use."
echo "  You can pre-download it now to avoid waiting later."
echo ""
echo "  Recommended models:"
echo "    small    — best balance of speed/quality (default, ~244MB)"
echo "    base     — faster, decent quality (~74MB)"
echo "    large-v3 — best quality, slow on CPU (~1.5GB)"
echo ""
read -r -p "  Download 'small' model now? [y/N] " response
if [[ "$response" =~ ^[Yy]$ ]]; then
    log "Downloading Whisper 'small' model..."
    python3 -c "import whisper; whisper.load_model('small')"
    success "Whisper 'small' model downloaded"
else
    warn "Skipped — model will download automatically on first run"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "============================================="
echo -e "${GREEN}   All dependencies installed successfully!${NC}"
echo "============================================="
echo ""
echo "  Next steps:"
echo "  1. Edit VIDEO_LIST in video_story_pipeline.py"
echo "     to point to your video files"
echo ""
echo "  2. Run the pipeline:"
echo '     python3 video_story_pipeline.py --story "Your story here"'
echo ""
echo "  3. List available TTS voices:"
echo '     python3 video_story_pipeline.py --list-voices'
echo ""
