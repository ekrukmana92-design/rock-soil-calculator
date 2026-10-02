@echo off
REM ===================================================================
REM  Jalankan aplikasi dalam mode SMARTPHONE (600 x 1000)
REM  Berguna untuk melihat tampilan portrait di layar PC.
REM ===================================================================

cd /d "%~dp0"

set PY=C:\Users\Win11\.workbuddy-ai\binaries\python\envs\kivy-test\Scripts\python.exe

if not exist "%PY%" (
    echo [X] Python Kivy tidak ditemukan: %PY%
    pause
    exit /b 1
)

echo Menjalankan dalam mode SMARTPHONE (600 x 1000)...
"%PY%" main.py --size=600x1000
