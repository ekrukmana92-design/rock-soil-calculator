# Calculator Estimasi Penyelesaian Pengujian Mekanika Batuan & Tanah

Aplikasi Android internal untuk memperkirakan waktu penyelesaian pekerjaan
pengujian laboratorium mekanika batuan dan tanah.

**Versi 1.0** · Offline · Smartphone + Tablet

---

## 1. Ringkasan

Aplikasi menjawab satu pertanyaan:

> "Jika ada X sampel yang harus diuji, kapan pekerjaan diperkirakan selesai?"

Rumus inti (PRD Bab 10 & 10.1):

```
Batch          = CEILING(Jumlah Sampel / Jumlah Maks)
Estimasi Hari  = Batch × Durasi Hari
Estimasi Selesai = tanggal mulai + estimasi hari (kalender kerja)
```

Contoh PRD Bab 37: 25 sampel UCS (maks 15/batch, 1 hari/batch)
→ 2 batch → 2 hari kerja.

---

## 2. Cara Menjalankan

### Coba cepat di Windows (tanpa setup)

Klik dua kali salah satu file berikut di folder project:

| File | Kegunaan |
|---|---|
| `JALANKAN.bat` | Jendela default, menyerupai smartphone (420 x 860) |
| `JALANKAN_SMARTPHONE.bat` | Simulasi smartphone (600 x 1000) |
| `JALANKAN_TABLET.bat` | Simulasi tablet (1230 x 800) — layout dua kolom |

Ketiganya memakai Python Kivy yang sudah terpasang di mesin ini:
`C:\Users\Win11\.workbuddy-ai\binaries\python\envs\kivy-test\Scripts\python.exe`

> **Catatan:** file `.bat` ini menunjuk ke path Python di atas. Bila project
> dipindah ke komputer lain, ubah variabel `PY` di dalamnya (atau buat
> environment sendiri sesuai langkah di bawah).

### Desktop (Windows / macOS / Linux) — dengan environment sendiri

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Mengubah ukuran jendela (uji tampilan responsif)

```bash
python main.py --size=420x860      # smartphone portrait (default)
python main.py --size=1000x600     # smartphone landscape
python main.py --size=800x1230     # tablet portrait
python main.py --size=1230x800     # tablet landscape -> layout dua kolom
```

Breakpoint layout dua kolom aktif pada lebar **>= 900dp** (PRD Bab 24).

Database SQLite dibuat otomatis di `data/rock_soil.db` dan langsung terisi
11 pengujian mekanika batuan + 22 pengujian mekanika tanah.

### Test & verifikasi

```bash
python -m unittest discover -s tests -v   # 49 unit test calculation engine
python tools/verify_layout.py             # verifikasi UI & responsive layout
python tools/screenshot_check.py          # screenshot tiap screen
```

---

## 3. Struktur Project

```
rock_soil_calculator/
├── main.py                     # entry point + navigasi + toast
├── buildozer.spec              # konfigurasi build APK
├── requirements.txt
│
├── screens/                    # LAYER UI
│   ├── base.py                 # BaseScreen, TopBar, NavDrawer
│   ├── home.py                 # Home / Dashboard
│   ├── calculator.py           # Modul Calculator (fungsi utama)
│   ├── database.py             # Database pengujian + CRUD
│   ├── history.py              # Riwayat perhitungan
│   └── settings.py             # Kalender kerja, backup, PIN
│
├── widgets/                    # WIDGET REUSABLE
│   ├── theme.py                # Palet & tipografi (Modern Engineering)
│   ├── layout.py               # Helper teks & format tanggal/angka
│   ├── result_card.py          # SummaryCard, ResultCard, Card
│   ├── test_selector.py        # CategoryTabs, SimpleDropdown, TestSelector
│   └── numeric_input.py        # NumericInput, DatePickerField
│
├── database/                   # LAYER DATABASE
│   ├── database.py             # Database SQLite + CRUD + backup
│   ├── models.py               # TestType, CalculationInput/Result, History
│   └── seed_data.py            # Data awal PRD Bab 15 & 16
│
├── calculation/                # LAYER ENGINE (tanpa dependensi UI)
│   ├── estimator.py            # Rumus batch, kalender kerja, Mode Advanced
│   └── calculator.py           # Facade API untuk screen
│
├── tools/                      # Alat QA (bukan bagian aplikasi)
└── tests/                      # Unit test
```

Arsitektur berlapis sesuai PRD Bab 30 — formula perhitungan tidak menyentuh UI:

```
UI  →  Calculator  →  Estimator  →  Database  →  SQLite
```

---

## 4. Fitur

### Calculator
- Pilih kategori: Mekanika Batuan / Mekanika Tanah
- Pilih jenis pengujian dari database
- Input jumlah sampel (keyboard angka, 1–9999)
- Pilih tanggal mulai (default hari ini)
- **Mode Standard** — rumus PRD Bab 10
- **Mode Advanced** — estimasi paralel dengan jalur kritis
- Kartu hasil rinci + kartu ringkasan besar (tanggal selesai ditampilkan
  sangat besar, PRD Bab 13)

### Database Pengujian
- 11 pengujian mekanika batuan (PRD Bab 15)
- 22 pengujian mekanika tanah (PRD Bab 16)
- Tambah / edit / aktif-nonaktifkan / hapus
- Semua parameter dapat diubah tanpa mengubah program
- Tombol "Reset ke Default" untuk memuat ulang data PRD

### Riwayat
- Setiap perhitungan menyimpan **snapshot parameter** (PRD Bab 28)
- Perubahan database **tidak mengubah riwayat lama** (PRD Bab 27)
- Filter kategori, pencarian nama project, detail snapshot untuk audit

### Settings
- Hari kerja per minggu (5 / 6 / 7 hari)
- Export backup database (.db atau .json)
- PIN opsional untuk menu Database
- Reset database pengujian

---

## 5. Catatan Penting: Kalender Kerja

PRD Bab 10.1 menyebut "aturan kalender yang ditetapkan aplikasi". Aplikasi ini
memakai **kalender kerja murni** (sesuai keputusan pemilik produk):

| Parameter | Default | Dapat diubah di |
|---|---|---|
| Hari kerja per minggu | 6 (Senin–Sabtu) | Settings |
| Hari mulai dihitung sebagai hari ke-1 | Tidak | Settings |

**Tanggal selesai selalu jatuh pada hari kerja** — hari Minggu dilewati.

Contoh: 25 sampel UCS, mulai Jumat 02 Okt 2026, 2 hari kerja
→ Sabtu 03 (hari-1), Minggu 04 libur, **Senin 05 Okt 2026 (selesai)**.

> **Perhatian.** Contoh di PRD Bab 12 menuliskan selesai 03 Okt 2026 untuk
> kasus yang sama. Tanggal itu hanya tercapai bila hari mulai dihitung sebagai
> hari ke-1 **dan** Sabtu tetap dihitung sebagai hari kerja tanpa jeda. Karena
> pemilik produk memilih kalender kerja murni, angka di PRD Bab 12 akan tampak
> berbeda. Logika batch dan durasi tetap persis sesuai PRD.

---

## 6. Mode Advanced (PRD Bab 11)

Mode Advanced memerlukan metadata tambahan pada tiap pengujian —
`phase` (Preparasi / Pengujian / Pelaporan), `depends_on` (prasyarat), dan
`is_parallel`. Metadata ini ada di `database/seed_data.py` dan tidak
mengganggu Mode Standard.

Alur yang dimodelkan:

```
Preparasi Sampel
      ↓
Physical Properties
      ↓
┌─────┴──────┬────────────┐
UCS      Point Load    Brazilian     ← berjalan paralel
└─────┬──────┴────────────┘
      ↓
Input, analisa dan pelaporan
```

Uji sefase dengan prasyarat sama digabung menjadi satu *blok paralel*;
durasi blok = durasi maksimum anggotanya, bukan jumlahnya. Aplikasi juga
menampilkan **jalur kritis** — rantai pengujian yang menentukan total durasi.

---

## 7. Validasi & Stabilitas

Sesuai PRD Bab 26 & 29, aplikasi menampilkan pesan yang jelas (bukan crash)
untuk:

- nama project kosong
- jumlah sampel kosong / 0 / bukan angka / di atas 9999
- pengujian belum dipilih
- pengujian berstatus non-aktif
- parameter durasi tidak tersedia di database
- kapasitas maksimum 0 atau negatif
- tanggal tidak valid pada pemilih tanggal

---

## 8. Status Implementasi terhadap PRD

| Prioritas | Fitur | Status |
|---|---|---|
| P0 | Calculator | ✅ |
| P0 | Database Rock (11 uji) | ✅ |
| P0 | Database Soil (22 uji) | ✅ |
| P0 | Edit Database | ✅ |
| P0 | Perhitungan Batch | ✅ |
| P0 | Estimasi Durasi | ✅ |
| P0 | Estimasi Tanggal Selesai | ✅ |
| P0 | Responsive Smartphone/Tablet | ✅ |
| P1 | History + snapshot | ✅ |
| P1 | Export Database | ✅ |
| P1 | PIN Database | ✅ |
| P2 | Advanced Parallel Calculation | ✅ (dasar) |
| P2 | Multi-test Project | ◻︎ v1.1 |
| P2 | Resource Planning | ◻︎ v1.1 |
| P2 | Dashboard Monitoring | ◻︎ v2.0 |

Import database (.db) sudah tersedia di layer database
(`Database.import_backup`) namun belum diekspos ke UI Settings.

---

## 9. Build APK Android

Build APK **wajib memakai Linux** — buildozer menolak berjalan di Windows
(`NotImplementedError: Windows platform not yet working for Android`).

**Cara tercepat tanpa install Linux: pakai GitHub Actions.** Workflow sudah
disiapkan, tinggal upload project ke GitHub:

| Dokumen | Isi |
|---|---|
| **[PANDUAN_BUILD_APK.md](PANDUAN_BUILD_APK.md)** | Panduan langkah demi langkah (upload ke GitHub → unduh APK → install) |
| **[README_BUILD_ANDROID.md](README_BUILD_ANDROID.md)** | Referensi teknis: konfigurasi, signing, penelusuran masalah |

File pendukung yang sudah ada di project:

| File | Fungsi |
|---|---|
| `.github/workflows/build-apk.yml` | Perintah build yang dijalankan server Linux GitHub |
| `buildozer.spec` | Konfigurasi aplikasi Android |
| `.gitignore` | Mencegah file besar ikut terunggah |
