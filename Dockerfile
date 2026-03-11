# =============================================================================
# Dockerfile — Video Story Pipeline API
# =============================================================================

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# ── Pre-download Whisper model so it doesn't happen at runtime ────────────────
RUN python3 -c "import whisper; whisper.load_model('small')"

# ── Copy entire project maintaining the same structure ────────────────────────
COPY src/        ./src/
COPY stories/    ./stories/
COPY videos/     ./videos/
COPY output/     ./output/

# ── Expose API port ───────────────────────────────────────────────────────────
EXPOSE 8000

# ── Run the API from src/_api/main.py ─────────────────────────────────────────
WORKDIR /app/src
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
