# Suarik

**Tagline:** Dengarkan dirimu, temukan langkahmu.

Suarik adalah platform refleksi dan perencanaan aksi mikro berbasis web untuk mahasiswa tingkat akhir. Aplikasi ini membantu pengguna menyuarakan keresahan, mengenali sumber tekanan, menentukan prioritas, dan memulai langkah kecil yang realistis.

> Suarik bukan aplikasi diagnosis kesehatan mental, bukan pengganti psikolog, dan bukan layanan darurat.

## Teknologi

- Backend: **Python Flask**
- Database: **SQLite** (bawaan Python, dibuat otomatis)
- Frontend: HTML, CSS murni, JavaScript murni
- Grafik: **Chart.js** via CDN
- Font: **Plus Jakarta Sans** via Google Fonts CDN

## Struktur Proyek

```
suarik/
├── app.py                 # Aplikasi Flask utama (route, DB, logika rekomendasi)
├── requirements.txt       # Dependensi Python
├── README.md
├── suarik.db              # Dibuat otomatis saat pertama kali dijalankan
├── templates/             # Template Jinja2
│   ├── base.html
│   ├── index.html
│   ├── checkin.html
│   ├── result.html
│   ├── dashboard.html
│   ├── planner.html
│   ├── journal.html
│   ├── resources.html
│   ├── help.html
│   ├── about.html
│   └── 404.html
└── static/
    ├── css/style.css
    ├── js/{main,checkin,planner,dashboard}.js
    └── images/.gitkeep
```

## Cara Menjalankan

```bash
# 1. Buat virtual environment
python -m venv venv

# 2. Aktifkan environment
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependensi
pip install -r requirements.txt

# 4. Jalankan aplikasi
python app.py
```

Kemudian buka: <http://127.0.0.1:5000>

Database `suarik.db` akan dibuat otomatis pada saat pertama kali dijalankan, lengkap dengan seed data untuk halaman **Bekal Suarik**.

## Variabel Environment (opsional)

- `SUARIK_SECRET_KEY` — secret key Flask. Jika tidak diset, digunakan fallback untuk development lokal.

## Halaman

| Route | Nama tampilan | Fungsi |
|-------|--------------|--------|
| `/` | Beranda | Landing page dan CTA. |
| `/checkin` | Suara Hari Ini | Form check-in 4 langkah. |
| `/hasil/<id>` | Yang Sedang Berbicara | Ringkasan check-in + rekomendasi. |
| `/dashboard` | Jejak Suarik | Grafik dan refleksi mingguan. |
| `/planner` | Langkah Kecilku | CRUD daftar aksi mikro. |
| `/journal` | Ruang Cerita | Jurnal dengan insight ringan. |
| `/resources` | Bekal Suarik | Bacaan edukatif dengan filter. |
| `/help` | Suarakan Butuhmu | Panduan mencari dukungan. |
| `/about` | Tentang | Latar belakang produk. |

## Disclaimer

Data disimpan lokal pada `suarik.db` dan hanya digunakan untuk demo. Suarik tidak memberikan diagnosis atau saran medis. Bila kamu berada dalam bahaya langsung, hubungi layanan darurat setempat.
