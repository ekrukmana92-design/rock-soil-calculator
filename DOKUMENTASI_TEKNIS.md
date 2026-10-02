# Dokumentasi Teknis

Catatan implementasi untuk pengembang yang akan melanjutkan aplikasi ini.

---

## 0. Menjalankan di Desktop untuk Pengujian Cepat

Karena APK Android belum dibangun, pengujian fungsional dilakukan di desktop.
Tersedia tiga cara:

| Cara | Perintah |
|---|---|
| Klik dua kali (Windows) | `JALANKAN.bat` / `JALANKAN_SMARTPHONE.bat` / `JALANKAN_TABLET.bat` |
| Terminal (bash) | `./run.sh --size=1230x800` |
| Manual | `python main.py --size=1230x800` |

### Ukuran jendela

Ukuran diatur lewat `--size=LEBARxTINGGI`. Argumen ini **diproses manual**
di `_configure_kivy()` (`main.py`) lalu diteruskan sebagai `KIVY_WINDOW_SIZE`,
karena `KIVY_NO_ARGS=1` mematikan parser argumen bawaan Kivy sehingga
`--size` milik Kivy tidak akan berfungsi bila ditangani Kivy sendiri.

| Argumen | Simulasi |
|---|---|
| `--size=420x860` | smartphone portrait (default) |
| `--size=1000x600` | smartphone landscape |
| `--size=800x1230` | tablet portrait |
| `--size=1230x800` | tablet landscape → layout dua kolom |

Breakpoint dua kolom: lebar ≥ 900dp (`BREAKPOINT_TWO_COLUMN` di `widgets/theme.py`).

> Jendela Kivy harus dijalankan di terminal milik pengguna. Proses latar yang
> dijalankan lewat alat otomasi akan dimatikan begitu perintah selesai,
> sehingga tidak bisa dipakai untuk memeriksa tampilan secara interaktif.

---

## 1. Prinsip Arsitektur

Empat lapisan dengan arah ketergantungan satu arah (PRD Bab 30):

```
┌─────────────────────────────────────────┐
│  screens/ + widgets/      (UI)          │  Kivy
│  ↓ memanggil                            │
│  calculation/Calculator   (App Logic)   │  ← facade
│  ↓ memanggil                            │
│  calculation/Estimator    (Engine)      │  ← PURE, tanpa Kivy
│  ↓ memanggil                            │
│  database/Database        (Data)        │  ← satu-satunya penulis SQL
│  ↓                                      │
│  SQLite                                 │
└─────────────────────────────────────────┘
```

**Aturan yang harus dijaga:**

1. `calculation/estimator.py` **tidak boleh** mengimpor Kivy. Ini yang membuat
   engine bisa diuji tanpa GUI dan dipakai ulang oleh sistem monitoring
   laboratorium di masa depan (PRD Bab 38).
2. `screens/` **tidak boleh** menulis SQL. Semua lewat `Database`.
3. Rumus hanya hidup di `estimator.py`. UI hanya menampilkan.

---

## 2. Alur Satu Perhitungan

```
User menekan HITUNG ESTIMASI
        ↓
CalculatorScreen._on_calculate()
        ↓  validasi UI (field kosong, pengujian belum dipilih)
        ↓
Calculator.build_input(...)        ← menyisipkan preferensi dari Settings
        ↓
Estimator.run(CalculationInput)
        ↓  validasi ulang (juga melindungi bila dipanggil headless)
        ↓  _resolve_test() → TestType dari database
        ↓  cek is_active, cek parameter lengkap
        ↓
   mode STANDARD ──→ calculate_standard() ──→ batch, days, hours
   mode ADVANCED ──→ AdvancedEstimator.estimate() ──→ total_days, jalur kritis
        ↓
   add_working_days()               ← kalender kerja
        ↓
   _snapshot()                      ← PRD Bab 28
        ↓
CalculationResult
        ↓
CalculatorScreen._render_result()   ← SummaryCard + ResultCard
        ↓
User menekan SIMPAN → Database.save_calculation()
```

---

## 3. Rumus & Kalender Kerja

### Batch (PRD Bab 10)

```python
batch = math.ceil(samples / max_quantity)
```

### Durasi (PRD Bab 10.1)

```python
days  = batch * duration_days
hours = batch * effective_hours
```

### Tanggal selesai

`add_working_days(start, days, working_days_per_week, count_start_day)`

```python
_allowed_weekdays(n)   # n=6 → {0,1,2,3,4,5} = Senin..Sabtu (Minggu libur)
```

Algoritma:

1. Tentukan himpunan hari kerja yang diperbolehkan.
2. Bila `count_start_day` dan tanggal mulai bukan hari kerja → geser maju.
3. Iterasi: maju satu hari, tambah penghitung hanya bila hari itu hari kerja,
   sampai penghitung mencapai `needed`.

Properti yang dijaga (diuji di `tests/test_calculation.py`):
setiap tanggal selesai **tidak pernah** jatuh pada hari Minggu.

### Mode Advanced

Menggunakan **blok paralel**, bukan per-fase:

```python
_build_blocks(order)
```

Blok paralel = deretan bersambung uji `is_parallel` pada fase yang sama
**dan dengan himpunan prasyarat identik**. Ini yang menjamin
`UCS` / `Point Load` / `Brazilian` mulai bersamaan *setelah*
`Physical Properties` selesai, bukan sebelumnya.

```
untuk setiap blok:
    ready = max(selesai prasyarat semua anggota, gerbang fase sebelumnya)
    durasi_blok = max(durasi anggota)      # bukan dijumlahkan
    setiap anggota selesai pada akhir blok
```

`_critical_path()` melacak mundur dari uji terakhir yang selesai paling lambat.

---

## 4. Skema Database

### `test_types`

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `category` | TEXT | `ROCK` / `SOIL` |
| `test_name` | TEXT | |
| `max_quantity` | INTEGER | kapasitas maksimum per batch |
| `effective_hours` | REAL | jam efektif per batch |
| `duration_days` | REAL | hari kalender per batch |
| `phase` | TEXT | `PREPARATION` / `TESTING` / `REPORTING` |
| `depends_on` | TEXT | CSV nama uji prasyarat |
| `is_parallel` | INTEGER | 0/1 — boleh paralel |
| `is_active` | INTEGER | 0/1 — PRD Bab 17 |
| `sort_order` | INTEGER | urutan tampil |
| `created_at` / `updated_at` | TEXT | ISO timestamp |

Kolom `phase`, `depends_on`, `is_parallel` **melampaui PRD Bab 18** — hanya
dipakai Mode Advanced. Mode Standard mengabaikannya.

### `calculation_history`

| Kolom | Keterangan |
|---|---|
| `project_name`, `category`, `test_name` | identitas |
| `sample_quantity`, `batch_quantity` | hasil |
| `estimated_hours`, `estimated_days` | hasil |
| `start_date`, `estimated_finish_date` | tanggal |
| `created_at` | waktu simpan |
| `mode` | `STANDARD` / `ADVANCED` |
| `snapshot_json` | **snapshot parameter penuh** (PRD Bab 28) |

### `app_settings`

Key-value: `working_days_per_week`, `count_start_day`,
`database_pin_enabled`, `database_pin_value`.

---

## 5. Jaminan Audit Trail (PRD Bab 27)

`update_test()` **hanya** menyentuh baris `test_types`. Riwayat tidak pernah
di-`UPDATE`. Setiap baris riwayat menyimpan `snapshot_json`, sehingga hasil
lama tetap dapat dipertanggungjawabkan walau parameter berubah.

Diuji oleh `test_history_snapshot_tidak_berubah`:
simpan hasil dengan maks=15/hari=1 → ubah database jadi maks=100/hari=4 →
riwayat lama tetap mencatat 2 batch / 2 hari, sementara perhitungan **baru**
memakai 100 / 4 hari.

---

## 6. Lapisan UI

### `BaseScreen`

Menyediakan top bar, `ScrollView`, dan hook responsive:

```python
def build(self): ...                    # isi self.content
def refresh(self): ...                  # muat ulang data
def apply_layout(self, two_column): ... # atur ulang saat breakpoint berubah
```

Poin kritis — lebar konten:

```python
self.scroll.bind(width=self._sync_content_width)
```

Tanpa ini, `BoxLayout` menyimpulkan lebarnya dari *minimum_width* anak,
sehingga `GridLayout` / `Card` dengan `size_hint_x=1` akan **melebar keluar
layar**. Ini pernah menjadi bug nyata dan sekarang dijaga oleh
`tools/verify_layout.py`.

### Breakpoint

`BREAKPOINT_TWO_COLUMN = 900dp`

| Lebar | Home | Calculator |
|---|---|---|
| < 900dp | 1 kolom | form di atas, hasil di bawah |
| ≥ 900dp | 2 kolom | form kiri, hasil kanan (PRD Bab 23) |

### Jebakan Kivy yang sudah dihindari

| Jebakan | Akibat | Solusi |
|---|---|---|
| `self._label = "..."` pada widget turunan `Label` | Menimpa atribut internal `Label._label` → `'str' object has no attribute 'text'` | Gunakan nama lain (`_header_label`) |
| `label.bind(size=lambda w,s: setattr(w,"text_size",(s[0],s[1])))` | Loop tak stabil, teks tidak membungkus | `label.bind(width=...)` + `text_size=(v, None)` |
| `BoxLayout` di dalam `ScrollView` tanpa `size_hint_x=1` | Konten melebar keluar layar | Kunci `content.width` ke lebar viewport |
| `Window.size` di-set sebelum `build()` | Ukuran tidak diterapkan | Set setelah app berjalan |

---

## 7. Menambah Jenis Pengujian

Cara yang benar: **lewat UI** (Database → Tambah Pengujian) — perubahan
langsung tersimpan tanpa mengubah program, persis maksud PRD.

Bila perlu menambah ke data default (misal laboratorium punya uji baru tetap),
edit `database/seed_data.py` lalu tekan "Reset ke Default", atau tambahkan
baris pada `ROCK_TESTS` / `SOIL_TESTS` dengan format:

```python
(no, nama, max_quantity, effective_hours, duration_days,
 phase, [prasyarat], is_parallel)
```

---

## 8. Menambah Screen Baru

1. Buat `screens/nama_screen.py` dengan subclass `BaseScreen`.
2. Implementasikan `build()` (dan `refresh()` bila perlu data).
3. Daftarkan di `screens/__init__.py` → `SCREEN_REGISTRY`.
4. Tambahkan tombol di `NavDrawer._add_item` (`screens/base.py`).

---

## 9. Test

```bash
python -m unittest discover -s tests -v     # 49 test engine
python tools/verify_layout.py               # 13 pemeriksaan UI
```

`verify_layout.py` memeriksa:

- kelima screen dapat dibangun di 4 konfigurasi layar
- **tidak ada widget melewati tepi viewport** pada semua kombinasi
- breakpoint responsive menghasilkan jumlah kolom yang benar
- alur perhitungan UI: 25 sampel UCS → 2 batch / 2 hari / selesai 2026-10-05
- validasi input memunculkan banner saat jumlah sampel kosong

skrip ini sengaja **tidak** memakai screenshot untuk menilai kebenaran layout,
karena framebuffer pada lingkungan headless dapat bergeser dan menghasilkan
gambar yang menyesatkan. Pengukuran widget jauh lebih andal.

### 9.1 Regresi seed ganda

Ditemukan dan diperbaiki: basis data bawaan sempat berisi **66 baris
(33 uji × 2)** karena `seed_default_tests()` tidak idempoten.

Perbaikan:

- `seed_default_tests(skip_existing=True)` melewati baris yang sudah ada
  berdasarkan pasangan `(category, test_name)` → aman dipanggil berulang.
- `deduplicate_tests()` menghapus duplikat dan menyisakan `id` terkecil.
- `repair_if_needed()` memperbaiki basis data yang sudah terlanjur rusak.
- `initialize()` (dipanggil `main.py` saat start) kini menjalankan
  deduplikasi otomatis, sehingga basis data lama sembuh sendiri saat aplikasi
  dibuka.

**Riwayat perhitungan tidak tersentuh** oleh proses perbaikan ini, sesuai
PRD Bab 27 & 28. Hal ini dijamin oleh test
`test_riwayat_tidak_terpengaruh_repair`.

---

## 10. Yang Belum Dikerjakan

- **Import database lewat UI** — `Database.import_backup()` sudah ada, belum
  ada tombolnya di Settings.
- **Multi-test dalam satu project** (PRD Bab 38, v1.1) — saat ini satu
  perhitungan = satu pengujian. Mode Advanced sudah mendekati, tetapi belum
  menjumlahkan estimasi total project.
- **Resource/personnel capacity** — Mode Advanced mengasumsikan kapasitas
  personel tidak terbatas.
- **Multi-user / sinkronisasi** — v1.0 sepenuhnya offline dan single-user.
