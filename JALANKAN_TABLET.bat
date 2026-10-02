@echo off
REM ===================================================================
REM  Jalankan aplikasi dalam mode TABLET (1230 x 800)
REM  Untuk menguji layout dua kolom (responsive breakpoint 900dp).
REM ===================================================================

cd /d "%~dp0"

set PY=C:\Users\Win11\.workbuddy-ai\binaries\python\envs\kivy-test\Scripts\python.exe

if not exist "%PY%" (
    echo [X] Python Kivy tidak ditemukan: %PY%
    pause
    exit /b 1
)

echo Menjalankan dalam mode TABLET (1230 x 800) - layout dua kolom...
"%PY%" main.py --size=1230x800
