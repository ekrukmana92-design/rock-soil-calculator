@echo off
REM ===================================================================
REM  Calculator Estimasi Penyelesaian Pengujian Mekanika Batuan & Tanah
REM  Launcher untuk Windows - klik dua kali file ini untuk menjalankan.
REM ===================================================================

cd /d "%~dp0"

set PY=C:\Users\Win11\.workbuddy-ai\binaries\python\envs\kivy-test\Scripts\python.exe

echo.
echo  =========================================================
echo   CALCULATOR ESTIMASI PENYELESAIAN PENGUJIAN
echo   Mekanika Batuan ^& Tanah
echo  =========================================================
echo.

if not exist "%PY%" (
    echo  [X] Python Kivy tidak ditemukan di:
    echo      %PY%
    echo.
    echo  Buat environment dulu:
    echo      python -m venv .venv
    echo      .venv\Scripts\activate
    echo      pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo  Menjalankan aplikasi...
echo  (tutup jendela aplikasi untuk keluar)
echo.

"%PY%" main.py

if errorlevel 1 (
    echo.
    echo  [!] Aplikasi berhenti dengan kode error %errorlevel%
    echo      Periksa pesan di atas.
    pause
)
