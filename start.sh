#!/usr/bin/env bash
# MY-OSINT 95 Launcher Script (Backend + Astro UI)

echo "=========================================================="
echo " [★] MEMULAI MY-OSINT RETRO WINDOWS 95/98 SUITE..."
echo "=========================================================="

# 1. Jalankan Backend Python di latar belakang pada port 8080
if command -v python3 &> /dev/null; then
    echo "  > [1/2] Menyalakan Backend Python (Port 8080)..."
    python3 backend/server.py 8080 &
    BACKEND_PID=$!
fi

# 2. Jalankan Frontend Astro
echo "  > [2/2] Menyalakan Astro UI..."
cd astro-ui && npm run dev

# Trap untuk mematikan backend jika user menekan CTRL+C
trap "kill $BACKEND_PID 2> /dev/null; exit" INT TERM
