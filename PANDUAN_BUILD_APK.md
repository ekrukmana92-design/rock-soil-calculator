# Panduan Membuat APK Android

Panduan lengkap dari nol sampai APK ter-install di smartphone/tablet.

---

## 1. Kenapa tidak bisa dibuat di PC Windows ini?

Membangun APK Python/Kivy **wajib memakai Linux**. Ini bukan keterbatasan
aplikasi kita, melainkan batasan resmi dari toolchain-nya.

Bukti dari buildozer sendiri — saat dijalankan di Windows, ia langsung menolak:

```
NotImplementedError: Windows platform not yet working for Android
```

Dokumentasi resmi python-for-android juga menyatakan hal yang sama:

> "Windows users should create a virtual machine with an GNU Linux os
> installed, and then you can follow the described instructions from within
> your virtual machine."

Dan di PC ini, jalur alternatifnya juga tidak tersedia:

| Alternatif | Status di PC ini |
|---|---|
| WSL (Linux di dalam Windows) | Tidak terpasang + diblokir Security Policy |
| Docker (image Linux) | Tidak terpasang |
| Linux VM | Tidak tersedia |

**Solusinya:** memakai komputer Linux milik orang lain secara gratis —
server GitHub. Caranya lewat GitHub Actions (bagian berikutnya).

---

## 2. Cara Tercepat: GitHub Actions

GitHub menyediakan server Linux **gratis** untuk membangun project open source
dan publik. Kita manfaatkan itu. Tidak perlu install apa pun di PC Anda.

Waktu yang dibutuhkan: **20-35 menit** untuk build pertama (mayoritas untuk
mengunduh Android SDK/NDK ~2-3 GB). Build berikutnya lebih cepat karena
komponen di-cache.

### Langkah 1 — Buat akun GitHub

Kalau belum punya, daftar gratis di <https://github.com/signup>.

### Langkah 2 — Buat repository baru

1. Buka <https://github.com/new>
2. **Repository name:** `rock-soil-calculator` (atau nama lain)
3. Pilih **Public** (wajib agar build gratis tanpa batas menit)
4. **Jangan** centang "Add a README file"
5. Klik **Create repository**

### Langkah 3 — Upload project

**Cara A — lewat halaman web (tanpa install Git):**

1. Di halaman repository yang baru dibuat, klik **"uploading an existing file"**
2. Seret **seluruh isi** folder `rock_soil_calculator` ke halaman itu
   (semua file & subfolder: `.github`, `calculation`, `database`,
   `screens`, `widgets`, `tests`, `tools`, `main.py`, `buildozer.spec`, dst.)
3. Di kolom pesan tulis: `Versi awal aplikasi`
4. Klik **Commit changes**

> **Penting:** folder `.github` harus ikut ter-upload, karena di dalamnya ada
> file workflow yang mengatur proses build. Bila tersembunyi di Windows,
> aktifkan dulu "Hidden items" di tab View pada File Explorer.

**Cara B — lewat Git (kalau Git sudah terpasang):**

```bash
cd "rock_soil_calculator"
git init
git add .
git commit -m "Versi awal aplikasi"
git branch -M main
git remote add origin https://github.com/USERNAME/rock-soil-calculator.git
git push -u origin main
```

Ganti `USERNAME` dengan nama akun GitHub Anda.

### Langkah 4 — Jalankan build

Setelah upload, build **langsung berjalan otomatis** (karena ada trigger `push`).

Untuk menjalankannya manual:

1. Buka tab **Actions** di halaman repository
2. Di panel kiri klik **Build APK Android**
3. Klik tombol **Run workflow** → **Run workflow**
4. (Opsional) pilih jenis build: `debug` (untuk uji coba) atau `release`

### Langkah 5 — Unduh APK

1. Tunggu sampai tanda centang hijau muncul (20-35 menit)
2. Klik pada nama workflow run yang sedang/sudah selesai
3. Scroll ke bagian bawah, cari kotak **Artifacts**
4. Klik **apk-rocksoilcalc-debug** untuk mengunduh
5. File yang terunduh berupa `.zip` — ekstrak untuk mendapat file `.apk`

---

## 3. Memasang APK di Smartphone / Tablet

1. Pindahkan file `.apk` ke perangkat (kabel USB, Google Drive, WhatsApp
   "pesan ke diri sendiri", atau Bluetooth)
2. Buka **File Manager** di perangkat, ketuk file `.apk`
3. Android akan meminta izin **"Install unknown apps"** —
   buka pengaturan itu dan aktifkan untuk aplikasi File Manager
4. Ketuk **Install**
5. Setelah selesai, aplikasi **"Calculator Estimasi Pengujian"** muncul di
   daftar aplikasi

### Persyaratan perangkat

| Item | Minimum |
|---|---|
| Android | 7.0 (API 24) atau lebih baru |
| Arsitektur | arm64-v8a (mayoritas HP modern) atau armeabi-v7a |
| Ruang penyimpanan | ~60 MB |

---

## 4. Kalau Build Gagal

### Melihat penyebabnya

1. Buka tab **Actions** → klik run yang gagal (tanda silang merah)
2. Klik langkah yang bergaris merah untuk melihat log-nya
3. Workflow juga otomatis mengunggah artifact **build-log-gagal** berisi log
   lengkap

### Masalah yang paling sering muncul

**A. `undeclared name not builtin: long`** saat kompilasi `kivy/weakproxy.pyx`

Buildozer memakai recipe Kivy internal yang sudah usang. `buildozer.spec`
di project ini **sudah** mengatasinya dengan menunjuk langsung ke URL rilis:

```ini
requirements = python3,kivy==https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip,cython==3.0.11
```

Bila tetap terjadi, hapus cache lama dengan menambahkan langkah ini **sebelum**
langkah build di `.github/workflows/build-apk.yml`:

```yaml
      - name: Bersihkan cache buildozer
        run: |
          buildozer android clean || true
          rm -rf .buildozer/android/platform/python-for-android || true
```

**B. Build gagal karena versi Python tidak didukung**

Ganti branch p4a di `buildozer.spec`. Coba `develop` (saat ini dipakai),
atau tangga versi berikut bila masih gagal:

```ini
p4a.branch = develop
# alternatif:
# p4a.branch = master
# p4a.branch = release
```

**C. Build berhenti tanpa pesan jelas / kehabisan waktu**

Runner GitHub punya batas 6 jam, sedangkan kita set `timeout-minutes: 90`.
Kalau terasa terlalu lama, kurangi arsitektur menjadi satu saja di
`buildozer.spec` agar build lebih cepat:

```ini
android.archs = arm64-v8a
```

> Hampir semua HP dan tablet yang dijual setelah 2018 memakai `arm64-v8a`.
> Mengurangi ke satu arsitektur memotong waktu build hampir setengahnya.

**D. Ingin memastikan versi Kivy yang benar-benar dipakai**

Lihat log pada tahap `# Compiling Kivy`. Akan terlihat URL atau folder sumber.
Setelah build, sumbernya ada di:
`.buildozer/android/platform/build-*/build/other_builds/kivy/`

---

## 5. Build Alternatif

### Google Colab (tanpa GitHub)

Kalau Anda lebih suka jalur manual:

1. Buka <https://colab.research.google.com>
2. Buat notebook baru
3. Upload folder project (ikon folder di kiri → unggah)
4. Jalankan di sel:

```bash
!sudo apt-get install -y git zip unzip openjdk-17-jdk autoconf libtool \
     pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo6 \
     cmake libffi-dev libssl-dev
!pip install buildozer cython==3.0.11
%cd /content/rock_soil_calculator
!buildozer -v android debug
```

5. Unduh APK:

```python
from google.colab import files
import glob
for f in glob.glob('/content/rock_soil_calculator/bin/*.apk'):
    files.download(f)
```

> Catatan: Colab membatasi waktu sesi (sekitar 12 jam untuk akun gratis) dan
> bisa terputus. Untuk sesi yang lebih andal, jalankan bertahap dan simpan
> `.buildozer` ke Google Drive.

### Linux lokal (Ubuntu 22.04 / 24.04)

Cara paling cepat karena tidak ada batas waktu:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip \
     python3-venv autoconf libtool pkg-config zlib1g-dev \
     libncurses5-dev libncursesw5-dev libtinfo6 cmake \
     libffi-dev libssl-dev

pip install --user buildozer cython==3.0.11

cd rock_soil_calculator
buildozer -v android debug
```

APK muncul di folder `bin/`.

---

## 6. Catatan Penting tentang Versi APK

| Jenis | Kegunaan | Bisa dibagikan? |
|---|---|---|
| `debug` | Uji coba, bisa langsung di-install | Ya, tapi ditandai debug |
| `release` | Untuk dibagikan / Play Store | Perlu signing key |

APK **debug** sudah cukup untuk dipasang di HP/tablet sendiri dan
dibagikan ke rekan kerja. Untuk mengunggah ke Google Play Store, APK perlu
di-*sign* dengan keystore — beri tahu saya kalau Anda ingin sampai tahap itu.

---

## 7. Ringkasan Alur

```
PC Windows                 GitHub (Linux, gratis)            HP/Tablet
─────────────             ──────────────────────             ─────────
upload project   ───────►  build APK otomatis
                           (~20-35 menit)
                                     │
                           unduh dari Artifacts  ──────────►  install .apk
```

Tiga file yang menyiapkan otomasi ini:

| File | Fungsi |
|---|---|
| `.github/workflows/build-apk.yml` | Perintah build yang dijalankan GitHub |
| `buildozer.spec` | Konfigurasi aplikasi Android (nama, versi, API, izin) |
| `.gitignore` | Mencegah file besar/tidak perlu ikut terunggah |
