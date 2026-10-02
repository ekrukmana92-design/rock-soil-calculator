[app]

title = Calculator Estimasi Pengujian
package.name = rocksoilcalc
package.domain = com.lab.rocksoil

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf

# Versi aplikasi (PRD Bab 40)
version = 1.0.0

# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
# PRD Bab 30: Python 3.x + Kivy. KivyMD opsional (tidak dipakai).
#
# PENTING — kenapa memakai URL, bukan `kivy==2.3.1`:
# Buildozer/p4a punya "recipe" Kivy internal. Bila menemukan recipe tersebut,
# p4a bisa memakai versi bawaan recipe (atau cache lama) dan MENGABAIKAN
# versi di baris requirements. Akibatnya build mengompilasi Kivy lama dan
# gagal dengan error seperti:
#     kivy/weakproxy.pyx: undeclared name not builtin: long
# Menunjuk langsung ke URL rilis memaksa p4a memakai sumber yang benar.
#
# Cython 3.0.x wajib untuk Kivy 2.3.x. Bila dibiarkan default (0.29.x),
# kompilasi weakproxy.pyx dapat gagal.
requirements = python3,kivy==https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip,cython==3.0.11

# Pakai branch p4a yang mendukung Python 3.13 (stable branch tertinggal).
# Bila build gagal karena resep Python, ini titik pertama yang perlu diubah.
p4a.branch = develop

# ---------------------------------------------------------------------------
# Orientasi & tampilan
# ---------------------------------------------------------------------------
# Portrait + landscape keduanya didukung (PRD Bab 24 — responsive).
# Aplikasi menyesuaikan layout sendiri lewat breakpoint 900dp,
# jadi tidak perlu dipaksa satu orientasi.
orientation = all
fullscreen = 0

# Kivy memerlukan konfigurasi ini agar berjalan benar di Android
android.entrypoint = org.kivy.android.PythonActivity
android.allow_backup = True

# ---------------------------------------------------------------------------
# Izin aplikasi
# ---------------------------------------------------------------------------
# Aplikasi berjalan offline, tetapi menyimpan backup .db/.json sehingga
# memerlukan akses penyimpanan. Pada API 33+ (target 34) izin WRITE/READ
# _EXTERNAL_STORAGE sudah tidak berlaku, sehingga perlu izin media.
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_DOCUMENTS

# ---------------------------------------------------------------------------
# Android API
# ---------------------------------------------------------------------------
# api 34 wajib untuk sideload di Android 14+.
# minapi 24 (Android 7.0) — Kivy 2.3.x butuh minimal API 21,
# tetapi 24 memberi kompatibilitas lebih baik untuk perangkat modern.
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# ---------------------------------------------------------------------------
# Presplash / ikon (opsional)
# ---------------------------------------------------------------------------
# Letakkan file berikut di assets/ bila sudah tersedia:
# android.presplash.light = assets/presplash.png
# icon.filename = %(source.dir)s/assets/icon.png

# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------
android.release_artifact = rocksoilcalc-1.0.0-release.apk
android.debug_artifact = rocksoilcalc-1.0.0-debug.apk

# Tingkatkan log saat debugging
log_level = 2
