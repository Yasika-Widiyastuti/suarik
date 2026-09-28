# app.py — Aplikasi Flask utama Suarik
# Platform refleksi dan perencanaan aksi mikro untuk mahasiswa tingkat akhir.

import os
import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, g, abort, jsonify
)

# ---------------------------------------------------------------------------
# Konfigurasi aplikasi
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "suarik.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SUARIK_SECRET_KEY",
    "suarik-dev-secret-key-ganti-di-produksi"
)
app.config["DATABASE"] = DATABASE_PATH
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB cukup untuk form teks


# ---------------------------------------------------------------------------
# Koneksi database
# ---------------------------------------------------------------------------
def get_db():
    """Kembalikan koneksi SQLite untuk request saat ini."""
    if "db" not in g:
        g.db = sqlite3.connect(
            app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """Tutup koneksi database di akhir request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Buat tabel dan seed data jika database belum ada."""
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emotion TEXT NOT NULL,
            stress_level INTEGER NOT NULL,
            academic_score INTEGER DEFAULT 0,
            career_score INTEGER DEFAULT 0,
            financial_score INTEGER DEFAULT 0,
            relationship_score INTEGER DEFAULT 0,
            burnout_score INTEGER DEFAULT 0,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            duration INTEGER NOT NULL,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            topic TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            detail TEXT NOT NULL,
            reading_time INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    db.commit()
    seed_data(db)
    db.close()


def seed_data(db):
    """Isi awal untuk tabel resources bila masih kosong."""
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM resources;")
    if cur.fetchone()["n"] > 0:
        return

    resources = [
        (
            "Akademik",
            "Memecah skripsi menjadi tugas kecil",
            "Ubah bab besar menjadi daftar tugas 25 menit yang bisa dimulai hari ini.",
            "Skripsi terasa berat karena kita melihatnya sebagai satu bongkahan besar. "
            "Coba tuliskan bab yang sedang dikerjakan, lalu pecah menjadi tiga sampai lima "
            "tugas kecil berdurasi 25 menit. Pilih satu tugas paling mudah untuk dimulai. "
            "Selesai satu tugas kecil sudah cukup untuk hari ini.",
            4,
        ),
        (
            "Akademik",
            "Membuat sesi fokus yang realistis",
            "Sesi fokus pendek yang konsisten lebih berkelanjutan daripada maraton semalam.",
            "Coba pola 25 menit fokus dan 5 menit istirahat. Sebelum mulai, tulis satu "
            "kalimat tentang apa yang akan dikerjakan pada sesi tersebut. Setelah sesi "
            "selesai, catat satu kemajuan kecil, sekecil apa pun. Jangan menuntut hasil "
            "sempurna dalam satu sesi.",
            3,
        ),
        (
            "Karier",
            "Memetakan skill yang sudah dimiliki",
            "Tulis apa yang sudah kamu bisa sebelum memikirkan apa yang belum kamu miliki.",
            "Ambil selembar catatan dan tuliskan minimal lima skill yang kamu miliki, baik "
            "teknis maupun non-teknis. Tambahkan satu contoh proyek atau pengalaman untuk "
            "setiap skill. Peta ini akan membantumu memilih lowongan yang sesuai tanpa "
            "membandingkan diri secara berlebihan.",
            4,
        ),
        (
            "Karier",
            "Memulai portofolio tanpa menunggu sempurna",
            "Portofolio bertumbuh seiring waktu. Mulai dari satu karya kecil hari ini.",
            "Pilih satu proyek, tugas kuliah, atau eksperimen kecil yang pernah kamu "
            "kerjakan. Tulis satu paragraf singkat berisi tujuan, peran, dan hasilnya. "
            "Simpan sebagai draft. Kamu bisa memperbarui dan menambah karya lain nanti "
            "tanpa harus menunggu portofolio benar-benar lengkap.",
            5,
        ),
        (
            "Finansial",
            "Mencatat pengeluaran tanpa menghakimi diri",
            "Catat dulu, evaluasi kemudian. Tujuannya melihat pola, bukan menghukum diri.",
            "Selama tujuh hari, catat pengeluaran harianmu di catatan sederhana. Belum "
            "perlu kategori rumit atau aplikasi khusus. Setelah tujuh hari, baca ulang "
            "catatanmu dengan netral. Fokus pada pola, bukan pada rasa bersalah.",
            3,
        ),
        (
            "Finansial",
            "Membedakan kebutuhan dan keinginan",
            "Latihan sederhana untuk memilih pengeluaran yang lebih selaras dengan prioritasmu.",
            "Buat dua kolom: kebutuhan dan keinginan. Tuliskan pengeluaran minggu lalu di "
            "kolom yang sesuai. Untuk keinginan, tanyakan apakah kamu masih menginginkannya "
            "setelah 24 jam. Latihan ini membantu memilah tanpa harus melarang diri sendiri.",
            4,
        ),
        (
            "Burnout",
            "Mengenali tanda tubuh membutuhkan jeda",
            "Sinyal tubuh sering muncul lebih dulu daripada kesadaran pikiran.",
            "Perhatikan tanda seperti bahu tegang, pernapasan dangkal, sulit fokus, atau "
            "mudah tersinggung. Bila muncul, beri jeda 5–10 menit untuk berdiri, minum air, "
            "atau melihat ke kejauhan. Jeda kecil membantu mencegah kelelahan yang menumpuk.",
            3,
        ),
        (
            "Burnout",
            "Membuat batas sederhana dalam rutinitas",
            "Batas bukan penolakan; batas adalah cara menjaga energi agar bertahan lebih lama.",
            "Pilih satu batas kecil untuk minggu ini. Misalnya, tidak membuka pesan kerja "
            "setelah pukul 21.00, atau menutup laptop 30 menit sebelum tidur. Sampaikan "
            "kepada orang yang perlu tahu, lalu jalankan tanpa merasa bersalah.",
            4,
        ),
        (
            "Relasi",
            "Menyampaikan perasaan dengan kalimat aku",
            "Kalimat aku membantu menyampaikan perasaan tanpa membuat orang lain defensif.",
            "Struktur sederhana: aku merasa (perasaan) ketika (situasi) karena (alasan). "
            "Contoh: aku merasa kewalahan ketika permintaan datang mendadak karena aku "
            "butuh waktu untuk menyusun prioritas. Coba tulis satu kalimat aku hari ini "
            "untuk situasi yang sedang mengganggumu.",
            3,
        ),
        (
            "Relasi",
            "Meminta bantuan tanpa merasa menjadi beban",
            "Meminta bantuan adalah bagian sehat dari relasi, bukan tanda kelemahan.",
            "Mulailah dari permintaan kecil yang jelas. Sebutkan apa yang kamu butuhkan, "
            "kapan, dan seberapa lama. Contoh: bolehkah kamu menemaniku menulis selama "
            "30 menit besok pagi. Permintaan yang spesifik lebih mudah dijawab dan "
            "mengurangi rasa segan.",
            3,
        ),
    ]

    cur.executemany(
        """
        INSERT INTO resources (category, title, summary, detail, reading_time)
        VALUES (?, ?, ?, ?, ?);
        """,
        resources,
    )
    db.commit()


# ---------------------------------------------------------------------------
# Konstanta domain
# ---------------------------------------------------------------------------
EMOTIONS = ["Tenang", "Bersemangat", "Cemas", "Kewalahan", "Lelah", "Sedih"]

AREA_CHOICES = [
    ("Akademik dan skripsi", "academic_score", "Akademik"),
    ("Karier dan masa depan", "career_score", "Karier"),
    ("Finansial", "financial_score", "Finansial"),
    ("Relasi dan keluarga", "relationship_score", "Relasi"),
    ("Kelelahan atau burnout", "burnout_score", "Burnout"),
]

# Prioritas untuk memutuskan seri (tie-breaker).
FOCUS_PRIORITY = ["Burnout", "Akademik", "Karier", "Finansial", "Relasi"]

CATEGORY_LABELS = {
    "academic_score": "Akademik",
    "career_score": "Karier",
    "financial_score": "Finansial",
    "relationship_score": "Relasi",
    "burnout_score": "Burnout",
}

TASK_CATEGORIES = ["Akademik", "Karier", "Finansial", "Relasi", "Burnout", "Personal"]
TASK_DURATIONS = [10, 15, 25, 30]
JOURNAL_TOPICS = ["Akademik", "Karier", "Finansial", "Relasi", "Burnout", "Lainnya"]
RESOURCE_CATEGORIES = ["Akademik", "Karier", "Finansial", "Burnout", "Relasi"]

RECOMMENDATIONS = {
    "Akademik": [
        {
            "title": "Tulis tiga poin kecil untuk skripsi",
            "duration": 10,
            "reason": "Menurunkan hambatan awal dengan memecah pekerjaan menjadi bagian yang jelas.",
        },
        {
            "title": "Sesi fokus 25 menit tanpa distraksi",
            "duration": 25,
            "reason": "Sesi pendek yang konsisten membantu menjaga momentum tanpa kelelahan.",
        },
        {
            "title": "Susun satu pertanyaan spesifik untuk teman atau dosen",
            "duration": 15,
            "reason": "Pertanyaan spesifik memudahkan mendapat bantuan yang tepat.",
        },
    ],
    "Karier": [
        {
            "title": "Catat tiga kemampuan yang sudah dimiliki",
            "duration": 10,
            "reason": "Memulai dari kekuatan membantu menyeimbangkan pikiran soal kekurangan.",
        },
        {
            "title": "Pelajari satu lowongan tanpa langsung melamar",
            "duration": 15,
            "reason": "Membaca untuk memahami kebutuhan pasar, bukan menekan diri untuk melamar.",
        },
        {
            "title": "Perbarui satu bagian kecil di CV atau portofolio",
            "duration": 25,
            "reason": "Perubahan kecil lebih mudah dituntaskan dan menjaga dokumen tetap segar.",
        },
    ],
    "Finansial": [
        {
            "title": "Catat pengeluaran hari ini tanpa menghakimi",
            "duration": 10,
            "reason": "Melihat data lebih membantu daripada menebak-nebak dengan rasa cemas.",
        },
        {
            "title": "Tentukan satu pengeluaran untuk ditinjau minggu ini",
            "duration": 10,
            "reason": "Perubahan bertahap lebih berkelanjutan daripada memangkas besar sekaligus.",
        },
        {
            "title": "Buat daftar kebutuhan dan keinginan tujuh hari ke depan",
            "duration": 15,
            "reason": "Rencana singkat membantu menentukan prioritas dengan tenang.",
        },
    ],
    "Relasi": [
        {
            "title": "Kirim pesan sederhana ke orang yang kamu percaya",
            "duration": 10,
            "reason": "Kontak singkat menjaga hubungan tanpa harus menunggu momen sempurna.",
        },
        {
            "title": "Tulis satu hal yang ingin kamu sampaikan dengan tenang",
            "duration": 15,
            "reason": "Menuliskan lebih dulu membantu memilih kata yang lebih jujur.",
        },
        {
            "title": "Ambil jeda sebelum merespons konflik",
            "duration": 10,
            "reason": "Jeda singkat memberi ruang untuk merespons, bukan bereaksi.",
        },
    ],
    "Burnout": [
        {
            "title": "Ambil jeda 10 menit tanpa layar",
            "duration": 10,
            "reason": "Mata dan pikiran butuh jeda dari input digital yang terus mengalir.",
        },
        {
            "title": "Minum air dan lakukan peregangan ringan",
            "duration": 10,
            "reason": "Tubuh yang bergerak membantu mereset ketegangan pikiran.",
        },
        {
            "title": "Pilih satu tugas paling penting, izinkan sisanya menunggu",
            "duration": 15,
            "reason": "Fokus pada satu hal mengurangi rasa kewalahan.",
        },
    ],
    "Personal": [
        {
            "title": "Rapikan satu area kecil di sekitarmu",
            "duration": 10,
            "reason": "Ruang yang lebih ringan sering membantu pikiran ikut terasa lebih ringan.",
        },
        {
            "title": "Tulis satu hal yang ingin kamu beri ruang hari ini",
            "duration": 10,
            "reason": "Menuliskan niat kecil membantu memilih hal yang benar-benar penting.",
        },
        {
            "title": "Pilih aktivitas sederhana untuk lebih hadir",
            "duration": 15,
            "reason": "Aktivitas yang disadari membantu mengurangi mode autopilot.",
        },
    ],
}


# ---------------------------------------------------------------------------
# Helper logika
# ---------------------------------------------------------------------------
def calculate_scores(stress_level, selected_areas):
    """Petakan pilihan area menjadi skor per kategori."""
    scores = {
        "academic_score": 0,
        "career_score": 0,
        "financial_score": 0,
        "relationship_score": 0,
        "burnout_score": 0,
    }
    for area_label, field, _display in AREA_CHOICES:
        if area_label in selected_areas:
            scores[field] = stress_level
    return scores


def get_focus_category(scores):
    """Tentukan kategori fokus utama dari skor terbesar dengan tie-breaker."""
    max_score = max(scores.values()) if scores else 0
    if max_score <= 0:
        return "Personal"
    top = [CATEGORY_LABELS[f] for f, v in scores.items() if v == max_score]
    for name in FOCUS_PRIORITY:
        if name in top:
            return name
    return top[0]


def get_recommendations(focus):
    """Kembalikan hingga tiga rekomendasi untuk kategori fokus."""
    return RECOMMENDATIONS.get(focus, RECOMMENDATIONS["Personal"])[:3]


def empathetic_greeting(emotion):
    """Sapaan lembut berdasarkan emosi yang dipilih."""
    greetings = {
        "Tenang": "Senang mendengar hari ini terasa cukup tenang untukmu.",
        "Bersemangat": "Bagus, energimu sedang tersedia hari ini.",
        "Cemas": "Rasa cemas boleh hadir. Kita coba pelan-pelan menyusunnya.",
        "Kewalahan": "Ketika terlalu banyak yang terasa bersamaan, satu langkah kecil sudah cukup.",
        "Lelah": "Lelah adalah sinyal tubuh yang layak didengarkan.",
        "Sedih": "Rasa sedih boleh diberi ruang. Kamu tidak sendirian.",
    }
    return greetings.get(emotion, "Terima kasih sudah menyempatkan diri untuk check-in.")


def stress_label(level):
    """Label teks untuk tingkat tekanan agar tidak hanya bergantung pada warna."""
    if level <= 3:
        return "Ringan"
    if level <= 6:
        return "Sedang"
    if level <= 8:
        return "Berat"
    return "Sangat berat"


def needs_support_alert(emotion, stress_level, selected_areas):
    """Tentukan apakah perlu menampilkan alert dukungan."""
    if stress_level >= 9:
        return True
    if emotion == "Sedih" and len(selected_areas) > 2:
        return True
    return False


# ---------------------------------------------------------------------------
# Context processor
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "brand_name": "Suarik",
        "brand_tagline": "Dengarkan dirimu, temukan langkahmu.",
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", active="beranda")


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "POST":
        emotion = (request.form.get("emotion") or "").strip()
        stress_raw = (request.form.get("stress_level") or "").strip()
        areas = request.form.getlist("areas")
        note = (request.form.get("note") or "").strip()

        # Validasi server-side
        errors = []
        if emotion not in EMOTIONS:
            errors.append("Silakan pilih satu emosi yang paling menggambarkan hari ini.")
        try:
            stress_level = int(stress_raw)
            if stress_level < 1 or stress_level > 10:
                raise ValueError
        except (TypeError, ValueError):
            errors.append("Tingkat tekanan wajib diisi antara 1 sampai 10.")
            stress_level = 0

        valid_area_labels = [label for label, _, _ in AREA_CHOICES]
        selected_areas = [a for a in areas if a in valid_area_labels]
        if not selected_areas:
            errors.append("Pilih minimal satu area yang paling memenuhi pikiranmu.")

        if len(note) > 500:
            note = note[:500]

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "checkin.html",
                active="checkin",
                emotions=EMOTIONS,
                area_choices=AREA_CHOICES,
                form_data={
                    "emotion": emotion,
                    "stress_level": stress_raw,
                    "areas": selected_areas,
                    "note": note,
                },
            )

        scores = calculate_scores(stress_level, selected_areas)
        db = get_db()
        cur = db.execute(
            """
            INSERT INTO checkins (
                emotion, stress_level,
                academic_score, career_score, financial_score,
                relationship_score, burnout_score, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                emotion,
                stress_level,
                scores["academic_score"],
                scores["career_score"],
                scores["financial_score"],
                scores["relationship_score"],
                scores["burnout_score"],
                note or None,
            ),
        )
        db.commit()
        new_id = cur.lastrowid
        return redirect(url_for("hasil", checkin_id=new_id))

    return render_template(
        "checkin.html",
        active="checkin",
        emotions=EMOTIONS,
        area_choices=AREA_CHOICES,
        form_data={"emotion": "", "stress_level": "5", "areas": [], "note": ""},
    )


@app.route("/hasil/<int:checkin_id>")
def hasil(checkin_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM checkins WHERE id = ?;", (checkin_id,)
    ).fetchone()
    if row is None:
        abort(404)

    scores = {
        "academic_score": row["academic_score"],
        "career_score": row["career_score"],
        "financial_score": row["financial_score"],
        "relationship_score": row["relationship_score"],
        "burnout_score": row["burnout_score"],
    }
    focus = get_focus_category(scores)
    recs = get_recommendations(focus)

    selected_areas = [
        CATEGORY_LABELS[f] for f, v in scores.items() if v > 0
    ]
    alert = needs_support_alert(row["emotion"], row["stress_level"], selected_areas)

    focus_explanations = {
        "Akademik": "Sepertinya area akademik sedang mengambil banyak ruang di pikiranmu. Kamu tidak perlu menyelesaikan semuanya sekaligus.",
        "Karier": "Pikiran tentang karier bisa terasa besar. Kita coba mulai dari satu langkah yang cukup dekat untuk dijangkau.",
        "Finansial": "Beban finansial sering terasa berat karena banyak faktor di luar kendali. Fokus pada satu bagian yang bisa kamu atur hari ini.",
        "Relasi": "Relasi memerlukan energi, dan tidak apa-apa jika kamu butuh jeda. Satu percakapan kecil yang jujur sudah cukup.",
        "Burnout": "Tubuh dan pikiranmu sedang meminta jeda. Beri ruang untuk memulihkan energi lebih dulu.",
        "Personal": "Beri dirimu waktu untuk hadir sejenak sebelum melangkah.",
    }

    return render_template(
        "result.html",
        active="checkin",
        checkin=row,
        focus=focus,
        focus_explanation=focus_explanations.get(focus, ""),
        recommendations=recs,
        greeting=empathetic_greeting(row["emotion"]),
        stress_text=stress_label(row["stress_level"]),
        show_alert=alert,
    )


@app.route("/dashboard")
def dashboard():
    db = get_db()
    checkins = db.execute(
        "SELECT * FROM checkins ORDER BY created_at ASC;"
    ).fetchall()
    tasks_completed = db.execute(
        "SELECT COUNT(*) AS n FROM tasks WHERE completed = 1;"
    ).fetchone()["n"]
    tasks_total = db.execute(
        "SELECT COUNT(*) AS n FROM tasks;"
    ).fetchone()["n"]

    summary = {
        "total_checkins": len(checkins),
        "avg_stress": 0,
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "top_focus": "-",
    }

    latest_scores = {
        "Akademik": 0, "Karier": 0, "Finansial": 0, "Relasi": 0, "Burnout": 0,
    }
    trend_labels = []
    trend_values = []
    focus_counter = {}

    if checkins:
        summary["avg_stress"] = round(
            sum(c["stress_level"] for c in checkins) / len(checkins), 1
        )

        last = checkins[-1]
        latest_scores = {
            "Akademik": last["academic_score"],
            "Karier": last["career_score"],
            "Finansial": last["financial_score"],
            "Relasi": last["relationship_score"],
            "Burnout": last["burnout_score"],
        }

        for c in checkins:
            s = {
                "academic_score": c["academic_score"],
                "career_score": c["career_score"],
                "financial_score": c["financial_score"],
                "relationship_score": c["relationship_score"],
                "burnout_score": c["burnout_score"],
            }
            focus = get_focus_category(s)
            focus_counter[focus] = focus_counter.get(focus, 0) + 1

            created = c["created_at"]
            if isinstance(created, datetime):
                label = created.strftime("%d %b")
            else:
                label = str(created)[5:10]
            trend_labels.append(label)
            trend_values.append(c["stress_level"])

        if focus_counter:
            summary["top_focus"] = max(focus_counter.items(), key=lambda kv: kv[1])[0]

    weekly_reflection = ""
    if summary["total_checkins"] == 0:
        weekly_reflection = "Belum ada cukup data untuk membaca pola. Mulai dari satu check-in hari ini."
    else:
        weekly_reflection = (
            f"Rata-rata tingkat tekananmu berada di {summary['avg_stress']}/10. "
            f"Area yang paling sering muncul adalah {summary['top_focus']}. "
            "Data ini hanya cerminan pola, bukan penilaian atas dirimu."
        )

    return render_template(
        "dashboard.html",
        active="dashboard",
        summary=summary,
        latest_scores=latest_scores,
        trend_labels=trend_labels,
        trend_values=trend_values,
        weekly_reflection=weekly_reflection,
        has_data=summary["total_checkins"] > 0,
    )


@app.route("/planner")
def planner():
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks ORDER BY completed ASC, created_at DESC;"
    ).fetchall()
    total = len(tasks)
    done = sum(1 for t in tasks if t["completed"])
    percent = int((done / total) * 100) if total else 0
    return render_template(
        "planner.html",
        active="planner",
        tasks=tasks,
        categories=TASK_CATEGORIES,
        durations=TASK_DURATIONS,
        percent=percent,
        total=total,
        done=done,
    )


@app.route("/planner/add", methods=["POST"])
def planner_add():
    title = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    duration_raw = (request.form.get("duration") or "").strip()
    due_date = (request.form.get("due_date") or "").strip()

    errors = []
    if not title or len(title) > 120:
        errors.append("Judul langkah wajib diisi dan maksimal 120 karakter.")
    if category not in TASK_CATEGORIES:
        errors.append("Kategori tidak valid.")
    try:
        duration = int(duration_raw)
        if duration not in TASK_DURATIONS:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Estimasi waktu tidak valid.")
        duration = 10

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Format tanggal tidak valid.")
            due_date = ""

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("planner"))

    db = get_db()
    db.execute(
        "INSERT INTO tasks (title, category, duration, due_date) VALUES (?, ?, ?, ?);",
        (title, category, duration, due_date or None),
    )
    db.commit()
    flash("Langkah baru berhasil disimpan.", "success")
    return redirect(url_for("planner"))


@app.route("/planner/<int:task_id>/toggle", methods=["POST"])
def planner_toggle(task_id):
    db = get_db()
    row = db.execute("SELECT completed FROM tasks WHERE id = ?;", (task_id,)).fetchone()
    if row is None:
        abort(404)
    new_val = 0 if row["completed"] else 1
    db.execute("UPDATE tasks SET completed = ? WHERE id = ?;", (new_val, task_id))
    db.commit()
    flash("Status langkah diperbarui.", "success")
    return redirect(url_for("planner"))


@app.route("/planner/<int:task_id>/edit", methods=["POST"])
def planner_edit(task_id):
    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,)).fetchone()
    if row is None:
        abort(404)

    title = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    duration_raw = (request.form.get("duration") or "").strip()
    due_date = (request.form.get("due_date") or "").strip()

    errors = []
    if not title or len(title) > 120:
        errors.append("Judul langkah wajib diisi dan maksimal 120 karakter.")
    if category not in TASK_CATEGORIES:
        errors.append("Kategori tidak valid.")
    try:
        duration = int(duration_raw)
        if duration not in TASK_DURATIONS:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Estimasi waktu tidak valid.")
        duration = row["duration"]
    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Format tanggal tidak valid.")
            due_date = ""

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("planner"))

    db.execute(
        """
        UPDATE tasks
        SET title = ?, category = ?, duration = ?, due_date = ?
        WHERE id = ?;
        """,
        (title, category, duration, due_date or None, task_id),
    )
    db.commit()
    flash("Langkah berhasil diperbarui.", "success")
    return redirect(url_for("planner"))


@app.route("/planner/<int:task_id>/delete", methods=["POST"])
def planner_delete(task_id):
    db = get_db()
    row = db.execute("SELECT id FROM tasks WHERE id = ?;", (task_id,)).fetchone()
    if row is None:
        abort(404)
    db.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
    db.commit()
    flash("Langkah dihapus.", "success")
    return redirect(url_for("planner"))


# Endpoint tambahan agar tombol dari halaman hasil dapat menambah rekomendasi
@app.route("/planner/add-from-result", methods=["POST"])
def planner_add_from_result():
    title = (request.form.get("title") or "").strip()
    category = (request.form.get("category") or "").strip()
    duration_raw = (request.form.get("duration") or "").strip()

    if not title or category not in TASK_CATEGORIES:
        flash("Rekomendasi tidak dapat disimpan.", "error")
        return redirect(request.referrer or url_for("planner"))
    try:
        duration = int(duration_raw)
        if duration not in TASK_DURATIONS:
            duration = 10
    except (TypeError, ValueError):
        duration = 10

    db = get_db()
    # Hindari duplikasi untuk kombinasi title + category yang belum selesai
    existing = db.execute(
        "SELECT id FROM tasks WHERE title = ? AND category = ? AND completed = 0;",
        (title, category),
    ).fetchone()
    if existing:
        flash("Rekomendasi ini sudah ada di Langkah Kecilku.", "success")
        return redirect(url_for("planner"))

    db.execute(
        "INSERT INTO tasks (title, category, duration) VALUES (?, ?, ?);",
        (title, category, duration),
    )
    db.commit()
    flash("Rekomendasi ditambahkan ke Langkah Kecilku.", "success")
    return redirect(url_for("planner"))


@app.route("/journal", methods=["GET", "POST"])
def journal():
    if request.method == "POST":
        return journal_add_inline()
    db = get_db()
    journals = db.execute(
        "SELECT * FROM journals ORDER BY created_at DESC;"
    ).fetchall()

    topic_counter = {}
    for j in journals:
        topic_counter[j["topic"]] = topic_counter.get(j["topic"], 0) + 1

    insight = ""
    if journals:
        top_topic = max(topic_counter.items(), key=lambda kv: kv[1])[0]
        insight = (
            f"Belakangan ini kamu cukup sering menulis tentang {top_topic}. "
            "Coba beri ruang untuk satu langkah kecil hari ini."
        )
    else:
        insight = "Belum ada cerita. Kamu bisa mulai dari satu paragraf singkat."

    return render_template(
        "journal.html",
        active="journal",
        journals=journals,
        topics=JOURNAL_TOPICS,
        insight=insight,
    )


def journal_add_inline():
    """Dipakai bila form dikirim langsung ke /journal."""
    return _journal_save(redirect_endpoint="journal")


@app.route("/journal/add", methods=["POST"])
def journal_add():
    return _journal_save(redirect_endpoint="journal")


def _journal_save(redirect_endpoint):
    title = (request.form.get("title") or "").strip()
    content = (request.form.get("content") or "").strip()
    topic = (request.form.get("topic") or "").strip()

    errors = []
    if len(title) > 120:
        errors.append("Judul maksimal 120 karakter.")
    if not content:
        errors.append("Isi cerita wajib diisi.")
    if len(content) > 1500:
        errors.append("Isi cerita maksimal 1500 karakter.")
    if topic not in JOURNAL_TOPICS:
        errors.append("Topik tidak valid.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for(redirect_endpoint))

    db = get_db()
    db.execute(
        "INSERT INTO journals (title, content, topic) VALUES (?, ?, ?);",
        (title or None, content, topic),
    )
    db.commit()
    flash("Cerita berhasil disimpan.", "success")
    return redirect(url_for(redirect_endpoint))


@app.route("/journal/<int:journal_id>/delete", methods=["POST"])
def journal_delete(journal_id):
    db = get_db()
    row = db.execute("SELECT id FROM journals WHERE id = ?;", (journal_id,)).fetchone()
    if row is None:
        abort(404)
    db.execute("DELETE FROM journals WHERE id = ?;", (journal_id,))
    db.commit()
    flash("Cerita dihapus.", "success")
    return redirect(url_for("journal"))


@app.route("/resources")
def resources():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM resources ORDER BY category ASC, id ASC;"
    ).fetchall()
    return render_template(
        "resources.html",
        active="resources",
        resources=rows,
        categories=RESOURCE_CATEGORIES,
    )


@app.route("/help")
def help_page():
    return render_template("help.html", active="help")


@app.route("/about")
def about():
    return render_template("about.html", active="about")


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
