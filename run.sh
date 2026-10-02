#!/usr/bin/env bash
# ===================================================================
#  Jalankan aplikasi Calculator Estimasi Pengujian Mekanika Batuan
#  & Tanah dari terminal (Git Bash / WSL / Linux / macOS).
#
#  Pemakaian:
#      ./run.sh                      # ukuran default (420x860)
#      ./run.sh --size=1230x800      # tablet landscape
#      ./run.sh --size=600x1000      # smartphone
# ===================================================================

set -u

cd "$(dirname "$0")"

# Cari interpreter Python yang punya Kivy.
CANDIDATES=(
    "C:/Users/Win11/.workbuddy-ai/binaries/python/envs/kivy-test/Scripts/python.exe"
    ".venv/Scripts/python.exe"
    ".venv/bin/python"
    "python"
)

PY=""
for c in "${CANDIDATES[@]}"; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then
        if "$c" -c "import kivy" >/dev/null 2>&1; then
            PY="$c"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "[X] Tidak menemukan Python dengan Kivy terpasang."
    echo
    echo "    Buat environment dulu:"
    echo "        python -m venv .venv"
    echo "        .venv/Scripts/activate    # Windows"
    echo "        pip install -r requirements.txt"
    exit 1
fi

echo "Python : $PY"
echo "Menjalankan aplikasi..."
echo

exec "$PY" main.py "$@"
