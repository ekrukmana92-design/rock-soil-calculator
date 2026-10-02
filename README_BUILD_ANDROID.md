# Panduan Build APK Android — Referensi Teknis

Dokumen ini adalah **referensi teknis** untuk proses build.
Untuk panduan langkah demi langkah yang lebih mudah diikuti, lihat
**[PANDUAN_BUILD_APK.md](PANDUAN_BUILD_APK.md)**.

Aplikasi ini memakai **Python 3 + Kivy**, dipaketkan ke APK dengan
**Buildozer** + **python-for-android (p4a)**.

> **Build APK wajib dilakukan di Linux.** Buildozer/p4a tidak didukung secara
> native di Windows. Bila dijalankan di Windows, buildozer langsung menolak
> dengan pesan:
>
> ```
> NotImplementedError: Windows platform not yet working for Android
> ```
>
> Dokumentasi resmi p4a juga menyatakan: *"Windows users should create a
> virtual machine with an GNU Linux os installed."*
>
> **Jalan tercepat tanpa install Linux:** gunakan **GitHub Actions** —
> workflow sudah disiapkan di `.github/workflows/build-apk.yml`.

---

## 1. Tiga Jalur Build

| Jalur | Kelebihan | Kekurangan |
|---|---|---|
| **GitHub Actions** (disarankan) | Gratis, tanpa install, otomatis | Perlu upload ke GitHub; 20-35 menit |
| **Google Colab** | Tanpa GitHub | Manual, sesi bisa terputus |
| **Linux lokal / VM** | Tercepat, tanpa batas waktu | Perlu mesin Linux |

---

## 2. Prasyarat (untuk jalur Linux lokal)

- Ubuntu 20.04 / 22.04 / 24.04
- Python 3.9 – 3.13 *(p4a branch `develop` mendukung 3.13; branch `stable`
  tertinggal)*
- OpenJDK 17
- Minimal 10 GB ruang disk (Android SDK + NDK)
- Koneksi internet saat build pertama

---

## 3. Instalasi Buildozer

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
    autoconf automake libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo6 cmake libffi-dev libssl-dev libltdl-dev

pip3 install --user buildozer cython==3.0.11
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

> **Cython 3.0.11**, bukan 0.29.x. Kivy 2.3.x memerlukan Cython 3.0.x; dengan
> 0.29.x kompilasi `kivy/weakproxy.pyx` bisa gagal.

---

## 4. Build

```bash
cd rock_soil_calculator

# APK debug — paling cepat untuk uji coba
buildozer -v android debug

# APK release (perlu signing, lihat bagian 7)
buildozer -v android release
```

Hasil ada di folder `bin/`:

```
bin/rocksoilcalc-1.0.0-debug.apk
```

Build pertama **15–40 menit** (mengunduh SDK/NDK, mengompilasi dependensi
untuk ARM). Build berikutnya jauh lebih cepat karena cache di `.buildozer/`.

---

## 5. Konfigurasi Penting di `buildozer.spec`

### Kivy harus ditunjuk lewat URL, bukan nomor versi

```ini
requirements = python3,kivy==https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip,cython==3.0.11
```

**Kenapa?** Buildozer/p4a punya *recipe* Kivy internal. Bila recipe itu
ditemukan, p4a dapat memakai versi bawaan recipe (atau cache lama) dan
**mengabaikan** versi di baris `requirements`. Akibatnya build mengompilasi
Kivy lama dan gagal dengan:

```
kivy/weakproxy.pyx:257:15: undeclared name not builtin: long
```

Menunjuk URL rilis langsung memaksa p4a memakai sumber yang benar.

### Branch p4a

```ini
p4a.branch = develop
```

Branch `stable` tertinggal dalam dukungan resep Python terbaru. Bila build
gagal karena resep Python, ini titik pertama yang perlu diubah.

### API & arsitektur

```ini
android.api = 34          # wajib untuk Android 14+
android.minapi = 24       # Android 7.0
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
```

**Mempercepat build** — batasi ke satu arsitektur:

```ini
android.archs = arm64-v8a
```

Hampir semua perangkat pasca-2018 memakai `arm64-v8a`; ini memotong waktu
build hampir setengahnya.

### Orientasi

```ini
orientation = all     # portrait + landscape (PRD Bab 24)
fullscreen = 0
```

### KivyMD (opsional)

Kode UI **tidak bergantung pada KivyMD** — semua widget dibuat dari Kivy murni,
sehingga aplikasi berjalan penuh tanpanya. Bila ingin mencoba KivyMD:

```ini
requirements = python3,kivy==https://github.com/kivy/kivy/archive/refs/tags/2.3.1.zip,kivymd==1.2.0,pillow,cython==3.0.11
```

---

## 6. Instal ke Perangkat

### Lewat kabel USB

Aktifkan **Opsi Pengembang → Debug USB**, lalu:

```bash
adb devices
buildozer android deploy run
```

### Lewat file APK

Salin `bin/rocksoilcalc-1.0.0-debug.apk` ke perangkat, buka file tersebut,
izinkan "Instal dari sumber tidak dikenal".

### Lihat log aplikasi

```bash
buildozer android logcat
# atau
adb logcat | grep -i python
```

---

## 7. Build Release & Signing

### 7.1 Buat keystore (sekali saja)

```bash
keytool -genkey -v -keystore rocksoil.keystore -alias rocksoil \
    -keyalg RSA -keysize 2048 -validity 10000
```

Simpan file ini baik-baik — tanpanya Anda tidak bisa merilis update untuk
aplikasi yang sama.

> **Untuk GitHub Actions:** simpan isi keystore sebagai *Repository Secret*
> (Settings → Secrets and variables → Actions), **jangan** commit ke
> repository.

### 7.2 Tambahkan ke `buildozer.spec`

```ini
android.release_artifact = rocksoilcalc-1.0.0-release.apk
android.debug_artifact = rocksoilcalc-1.0.0-debug.apk

android.keystore = /path/ke rocksoil.keystore
android.keyalias = rocksoil
android.keystore_password = <password>
android.keyalias_password = <password>
```

### 7.3 Build

```bash
buildozer -v android release
```

> Untuk pemakaian internal, APK debug sudah cukup dan dapat didistribusikan
> langsung ke perangkat laboratorium.

---

## 8. Penyesuaian Umum

### Ganti nama paket / versi

```ini
title = Calculator Estimasi Pengujian
package.name = rocksoilcalc
package.domain = com.lab.rocksoil
version = 1.0.0
```

`package.domain` + `package.name` menjadi ID aplikasi (`com.lab.rocksoil`).
**Ubah ke domain milik laboratorium Anda sebelum rilis** — ID ini tidak dapat
diubah setelah aplikasi dipasang, dan mengubahnya membuat Android menganggapnya
aplikasi berbeda.

---

## 9. Lokasi Database di Android

Saat berjalan di Android, aplikasi menyimpan SQLite di direktori privat
aplikasi:

```
/data/data/com.lab.rocksoil/files/data/rock_soil.db
```

Direktori ini **tidak dapat diakses aplikasi lain** tanpa root, sehingga data
laboratorium tetap terlindungi (PRD Bab 32).

Gunakan **Settings → Export Backup** untuk menghasilkan salinan database yang
dapat disalin ke penyimpanan eksternal.

---

## 10. Pemecahan Masalah

| Gejala | Penyebab & solusi |
|---|---|
| `buildozer: command not found` | `~/.local/bin` belum ada di `PATH` |
| `NotImplementedError: Windows platform not yet working` | Build dijalankan di Windows — pindah ke Linux/WSL2/VM, atau pakai GitHub Actions |
| `undeclared name not builtin: long` | p4a memakai recipe Kivy usang — pastikan `requirements` memakai URL seperti bagian 5 |
| `Cython` error | Pakai `cython==3.0.11` (bukan 0.29.x) |
| Build gagal karena resep Python | Ubah `p4a.branch` → `develop` |
| Build memakai Kivy lama walau versi sudah dipatok | Bersihkan cache: `buildozer android clean` lalu `rm -rf .buildozer/android/platform/python-for-android` |
| Build gagal saat unduh SDK | Koneksi/blocker; ulangi `buildozer android debug` |
| Build terlalu lama | Batasi `android.archs = arm64-v8a` |
| Aplikasi langsung tertutup | Lihat `buildozer android logcat`; biasanya import bermasalah |
| Database tidak tersimpan | Terjadi bila `ANDROID_PRIVATE` tidak terdeteksi; `Database` menanganinya otomatis |
| Teks terpotong di layar kecil | Uji dengan `python tools/verify_layout.py`, atau sesuaikan ukuran di `widgets/theme.py` |

---

## 11. Checklist Rilis Internal

- [ ] Ubah `package.domain` ke domain laboratorium
- [ ] Naikkan `version` di `buildozer.spec`
- [ ] Isi ikon: `assets/icon.png` (512×512) + `android.presplash.light`
- [ ] Jalankan `python -m unittest discover -s tests` — semua harus lulus
- [ ] Jalankan `python tools/verify_layout.py` — 0 masalah
- [ ] Uji di 1 smartphone dan 1 tablet (portrait + landscape)
- [ ] Uji alur: hitung → simpan → buka riwayat → edit database → hitung ulang
- [ ] Pastikan riwayat lama tidak berubah setelah edit database
- [ ] Export backup dan verifikasi file terbentuk
