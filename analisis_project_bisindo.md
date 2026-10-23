# 📋 Analisis Lengkap Project: BISINDO Translator

> **Judul Resmi:** Penerjemah Bahasa Isyarat Indonesia (BISINDO) Real-Time Berbasis Deteksi Landmark Tangan Menggunakan MediaPipe dan Deep Learning
> **Jenis Dokumen:** Laporan Analisis Teknis — Tugas Akhir

---

## 1. 🎯 Tujuan Program

### Apa ini?
**BISINDO Translator** adalah aplikasi web **real-time** yang mampu menerjemahkan gerakan tangan (bahasa isyarat) menjadi teks tertulis, langsung dari kamera webcam. Program ini dibuat sebagai **Tugas Akhir (Skripsi)** di bidang Kecerdasan Buatan dan Computer Vision.

### Masalah yang Diselesaikan
Komunitas Tuli di Indonesia menggunakan **BISINDO (Bahasa Isyarat Indonesia)** sebagai bahasa sehari-hari. Namun, mayoritas masyarakat umum tidak memahaminya, sehingga terjadi **kesenjangan komunikasi** yang lebar. Program ini menjadi **jembatan digital** antara pengguna BISINDO dan masyarakat umum, tanpa memerlukan interpreter manusia.

### Jenis Aplikasi
- **Jenis:** Aplikasi Web Desktop (berjalan di browser)
- **Domain:** AI / Machine Learning / Computer Vision
- **Platform:** Streamlit (Python Web Framework)
- **Input:** Kamera Webcam real-time
- **Output:** Teks terjemahan isyarat tangan

---

## 2. 🛠️ Teknologi yang Digunakan

### Bahasa Pemrograman
| Bahasa | Penggunaan |
|--------|-----------|
| **Python 3.x** | Seluruh kodebase (100%) |

### Library & Framework Utama

| Library | Versi | Fungsi |
|---------|-------|--------|
| **Streamlit** | 1.32.0 | Framework UI aplikasi web |
| **TensorFlow/Keras** | 2.15.0 | Training & inferensi model deep learning |
| **MediaPipe** | 0.10.9 | Deteksi 21 landmark titik tangan |
| **OpenCV** | 4.9.0.80 | Capture & pemrosesan frame kamera |
| **NumPy** | 1.24.3 | Operasi numerik & array fitur |
| **scikit-learn** | 1.3.2 | Split data, LabelEncoder, evaluasi model |
| **Pandas** | 2.1.4 | Manipulasi data CSV fitur kosakata |
| **PyYAML** | 6.0.1 | Parsing file `data.yaml` YOLO dataset |
| **Matplotlib/Seaborn** | — | Visualisasi grafik training & confusion matrix |

### Tidak Ada Database
Project ini **tidak menggunakan database** (SQL/NoSQL). Data disimpan sebagai:
- File `.npy` (NumPy binary) → fitur landmark abjad
- File `.csv` → fitur landmark kosakata
- File `.h5` → model Keras yang sudah terlatih
- File `.txt` → daftar label kelas kosakata

### Arsitektur Sistem
```
Webcam → OpenCV → MediaPipe → [126 Fitur] → Model ANN → Prediksi → Streamlit UI
```

---

## 3. 📁 Struktur Folder dan File

```
bisindo-translatorgg/
│
├── 📄 app.py                    ← ENTRY POINT — Aplikasi Streamlit utama
├── 📄 utils.py                  ← Fungsi shared: ekstraksi & normalisasi landmark
├── 📄 dataset_loader.py         ← Loader dataset abjad (.npy) untuk training
├── 📄 extract_landmarks.py      ← Pipeline ekstraksi fitur abjad dari raw_dataset
├── 📄 extract_kosakata.py       ← Pipeline ekstraksi fitur kosakata dari YOLO dataset
├── 📄 train_model.py            ← Script training Model Abjad (A–Z)
├── 📄 train_kosakata.py         ← Script training Model Kosakata (38 kata)
├── 📄 requirements.txt          ← Daftar dependency Python
├── 📄 proposal_ta.md            ← Proposal Tugas Akhir (dokumentasi akademik)
├── 📄 BRIEF_LAPORAN_TA.md       ← Ringkasan laporan TA
│
├── 📁 raw_dataset/              ← Dataset mentah gambar abjad (A–Z, per huruf)
│   ├── A/ (ratusan gambar .jpg)
│   ├── B/ ...
│   └── Z/
│
├── 📁 dataset/                  ← Hasil ekstraksi fitur abjad dalam format .npy
│   ├── A/ (file .npy, satu per gambar)
│   ├── B/ ...
│   └── Z/
│
├── 📁 yolo_dataset/             ← Dataset kosakata berformat YOLO (dari Roboflow)
│   ├── data.yaml                ← Konfigurasi kelas (38 kosakata)
│   ├── train/
│   │   ├── images/              ← Gambar training kosakata
│   │   └── labels/              ← Anotasi YOLO (.txt) per gambar
│   ├── valid/
│   └── test/
│
├── 📁 features_kosakata/        ← Hasil ekstraksi fitur kosakata dalam format .csv
│   └── train_kosakata.csv       ← ~3.5 MB, dataset utama training kosakata
│
├── 📁 models/                   ← Model terlatih & label
│   ├── model_bisindo_2hands.h5  ← Model Abjad (A–Z), ~774 KB
│   ├── model_kosakata_2hands.h5 ← Model Kosakata (38 kata), ~984 KB
│   ├── model_bisindo.h5         ← Model abjad versi lama (1 tangan)
│   └── labels_kosakata.txt      ← 38 label kelas kosakata
│
├── 📁 training_results_abjad/   ← Artefak hasil training model abjad
│   ├── accuracy_graph.png
│   ├── loss_graph.png
│   ├── confusion_matrix.png
│   ├── classification_report.txt
│   ├── final_validation_result.txt
│   ├── model_architecture_summary.txt
│   ├── dataset_sample.csv
│   ├── sample_prediction_result.csv
│   └── training_log_epoch.csv
│
├── 📁 training_results/         ← Artefak hasil training model kosakata
│   └── (sama seperti di atas)
│
└── 📁 venv/                     ← Virtual environment Python (tidak di-commit)
```

### File Paling Penting
| File | Peran |
|------|-------|
| `app.py` | **Entry point** — menjalankan seluruh aplikasi |
| `utils.py` | **Jantung sistem** — normalisasi landmark, dipakai di semua script |
| `models/model_bisindo_2hands.h5` | Model terlatih untuk inferensi abjad |
| `models/model_kosakata_2hands.h5` | Model terlatih untuk inferensi kosakata |

---

## 4. ✨ Fitur Program

### Fitur 1: Mode Abjad (A–Z)
- **Apa:** Menerjemahkan gestur isyarat huruf demi huruf (26 kelas: A–Z)
- **Cara kerja:** User menunjukkan satu huruf BISINDO → model memprediksi huruf tersebut → huruf ditambahkan ke kalimat yang sedang dibangun
- **Threshold:** Confidence ≥ 0.85

### Fitur 2: Mode Kosakata (38 Kata)
- **Apa:** Menerjemahkan gestur satu kata/frasa sekaligus (38 kelas)
- **Daftar kata:** ambil, apa, bantu, berdoa, berhenti, berjalan, berpikir, betul, bisindo, buat, hati-hati, ingat, jangan, janji, kamu, keren, maaf, melihat, membaca, menggambar, menulis, minta, mulai, nama, paham, perkenalkan, sabar, salah, sama-sama, saya, semangat, siapa, terima kasih, terlambat, tolong, tunggu, waktu, ya
- **Threshold:** Confidence ≥ 0.75

### Fitur 3: Smart Spacing (Penggabungan Teks Cerdas)
- Huruf dari Mode Abjad digabung langsung (tanpa spasi) → membentuk kata
- Kata dari Mode Kosakata ditambahkan dengan spasi
- Peralihan dari Mode Kata ke Mode Abjad → ada spasi otomatis
- Contoh output: `"saya B-I-S-A"` → `"saya BISA"`

### Fitur 4: Stabilisasi Prediksi Anti-Flicker
Dua mekanisme mencegah prediksi yang tidak stabil:
1. **Confidence Thresholding** — prediksi hanya diterima jika kepercayaan model ≥ ambang batas
2. **Majority Voting** — menyimpan histori 5 frame terakhir; prediksi diterima jika muncul ≥ 4 kali

### Fitur 5: Logika Jeda 0.6 Detik
- Gestur yang sama harus dipertahankan selama **0.6 detik** sebelum ditambahkan ke kalimat
- Mencegah karakter terduplikasi akibat tangan bergerak lambat
- Jika kata yang sama sudah ada terakhir, harus menunggu **1.5 detik** sebelum bisa ditambahkan lagi

### Fitur 6: Kontrol Pengguna
- **Tombol "Hapus Kata Terakhir"** — menghapus token terakhir
- **Tombol "Reset Kalimat"** — mengosongkan seluruh kalimat
- **Toggle Kamera** — ON/OFF kamera via checkbox; hardware kamera dibebaskan saat OFF

### Fitur 7: Visualisasi Landmark Tangan
- Menggambar 21 titik landmark dan koneksi antar titik pada preview kamera secara real-time

---

## 5. 🔄 Alur Program

### Alur Utama (Real-Time Inference)

```
START
  │
  ▼
[Streamlit App Launch] → Load kedua model (.h5) ke memori (cached)
  │
  ▼
[User klik "Mulai Kamera"] → OpenCV buka VideoCapture(0)
  │
  ▼
[Loop Frame]
  ├── Baca frame webcam → Resize 640×480 → Flip horizontal
  ├── Convert BGR → RGB
  ├── MediaPipe deteksi landmark tangan (maks. 2 tangan)
  │
  ├── [Tangan Terdeteksi?]
  │     YES → process_landmarks() → vektor 126 fitur (normalized)
  │           → Pilih model aktif (abjad/kosakata)
  │           → model.predict(keypoints)
  │           → Ambil label dengan argmax
  │           → Cek confidence threshold
  │
  │           [confidence ≥ threshold?]
  │                YES → final_word = label langsung
  │                NO  → Tambah ke history (majority voting)
  │                       Jika muncul ≥ 4x dari 5 frame → final_word
  │
  │           [final_word ada?]
  │                YES → Cek pending (harus sama ≥ 0.6 detik)
  │                       → Tambah ke history_items
  │                       → Update UI Output
  │
  ├── Draw landmark di frame
  └── Tampilkan frame ke FRAME_WINDOW

[User klik mode/tombol di sidebar]
  └── Update session_state → Efek langsung pada loop berikutnya
```

### Alur Pipeline Training (Offline)

```
[Tahap 1] Kumpul Gambar
  raw_dataset/{A-Z}/*.jpg     ← abjad
  yolo_dataset/train/images/  ← kosakata (dari Roboflow)

[Tahap 2] Ekstraksi Fitur
  extract_landmarks.py  → dataset/{A-Z}/*.npy    (126 fitur per gambar)
  extract_kosakata.py   → features_kosakata/train_kosakata.csv

[Tahap 3] Training
  train_model.py    → models/model_bisindo_2hands.h5
  train_kosakata.py → models/model_kosakata_2hands.h5

[Tahap 4] Inferensi
  app.py → memuat kedua model → siap digunakan
```

---

## 6. 🔬 Analisis Kode

### Coding Style
- **Prosedural** (bukan OOP) — semua kode ditulis sebagai script/fungsi
- Komentar berbahasa Indonesia
- Menggunakan `st.session_state` untuk state management di Streamlit
- Modularitas sedang: fungsi `process_landmarks()` di-share via `utils.py`

### Pola Desain
| Aspek | Implementasi |
|-------|-------------|
| Arsitektur | **Pipeline Pattern** (data mengalir dari kamera → fitur → model → UI) |
| State Management | **Streamlit Session State** (pengganti global state) |
| Caching | `@st.cache_resource` untuk load model sekali saja |
| Model | **Fully-Connected ANN** (bukan CNN, bukan RNN) |

### Kelebihan Kode
- ✅ Modular: `utils.py` dapat dipakai oleh semua script (extract, train, infer)
- ✅ Efisien: model di-cache, kamera tidak di-restart setiap rerun Streamlit
- ✅ Dual-model: dua model spesialis lebih akurat daripada satu model umum
- ✅ Anti-flicker: mekanisme stabilisasi berlapis (threshold + voting + jeda)
- ✅ Hasil training lengkap: grafik, laporan, confusion matrix otomatis disimpan
- ✅ Support 2 tangan: padding zero untuk tangan yang tidak terdeteksi

### Kekurangan Kode
- ⚠️ **Tidak ada unit test** — tidak ada pengujian otomatis
- ⚠️ **Hardcoded paths** — path model dan dataset di-hardcode, tidak menggunakan config file
- ⚠️ **Tidak ada logging** — tidak ada sistem log untuk debugging runtime
- ⚠️ **Model lama tidak dihapus** — `model_bisindo.h5` (versi 1-tangan lama) masih ada
- ⚠️ **Tidak ada error handling** kamera yang robust (hanya `st.error` sederhana)
- ⚠️ **Gestur statis saja** — tidak mendukung gestur dinamis (gerakan)

### Potensi Bug / Masalah
| Issue | Lokasi | Dampak |
|-------|--------|--------|
| Indeks model tidak sinkron dengan label | `app.py` L143 | Jika urutan label berubah, prediksi salah |
| Race condition kamera | `app.py` L121 | Kamera bisa gagal diinisialisasi di multithread |
| `history` tidak direset saat ganti mode | `app.py` | Voting residual dari mode sebelumnya |

---

## 7. 🏗️ Arsitektur Model Neural Network

### Model Abjad (`model_bisindo_2hands.h5`)

```
Input: 126 fitur (21 titik × 3D × 2 tangan)
  ↓
Dense(512, ReLU) + L2 regularization
  ↓
BatchNormalization + Dropout(0.35)
  ↓
Dense(256, ReLU) + L2 regularization
  ↓
BatchNormalization + Dropout(0.30)
  ↓
Dense(128, ReLU)
  ↓
BatchNormalization
  ↓
Dense(26, Softmax)   ← Output 26 kelas (A–Z)

Total Parameter: 236,186 (~922 KB)
```

### Model Kosakata (`model_kosakata_2hands.h5`)

```
Input: 126 fitur
  ↓
BatchNormalization   ← Normalisasi input tambahan
  ↓
Dense(256, ReLU) + L2
  ↓
BatchNormalization + Dropout(0.5)
  ↓
Dense(128, ReLU) + L2
  ↓
BatchNormalization + Dropout(0.4)
  ↓
Dense(64, ReLU)
  ↓
BatchNormalization + Dropout(0.3)
  ↓
Dense(38, Softmax)   ← Output 38 kelas kosakata

Total Parameter: 78,430 (~306 KB)
```

---

## 8. 📊 Performa Model (Hasil Aktual)

### Model Abjad

| Metrik | Nilai |
|--------|-------|
| Total Epoch Berjalan | 31 epoch |
| Train Accuracy | 77.29% |
| **Validation Accuracy** | **76.61%** |
| Train Loss | 0.8347 |
| Validation Loss | 0.8773 |

**Catatan Penting:** Huruf **A** memiliki precision sangat rendah (0.15) karena gesturnya paling mirip dengan huruf lain. Huruf dengan performa terbaik: **O** (F1: 0.95), **M** dan **N** (F1: 0.92–0.93).

### Model Kosakata

| Metrik | Nilai |
|--------|-------|
| Total Epoch Berjalan | 114 epoch |
| Train Accuracy | 82.83% |
| **Validation Accuracy** | **85.49%** |
| Train Loss | 0.7969 |
| Validation Loss | 0.6783 |

**Catatan:** Model kosakata lebih akurat (85.49%) dari model abjad (76.61%), kemungkinan karena kosakata memiliki gestur yang lebih berbeda antar kelas. Kata dengan F1 sempurna (1.00): **keren**, **maaf**, **tunggu**.

---

## 9. ⚙️ Cara Menjalankan Program

### Prasyarat
- Python 3.9–3.11 (disarankan)
- Webcam/kamera yang terhubung
- OS: Windows / Linux / macOS

### Langkah Instalasi

```bash
# 1. Clone/buka project
cd "d:\Tugas Akhir\code\bisindo-translatorgg"

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
# Windows:
.\venv\Scripts\Activate
# Linux/Mac:
source venv/bin/activate

# 4. Install semua dependency
pip install -r requirements.txt
```

### Menjalankan Aplikasi

```bash
# Jalankan aplikasi Streamlit
streamlit run app.py
```
Buka browser ke `http://localhost:8501`

### Menjalankan Pipeline Training (Jika Ingin Melatih Ulang)

```bash
# Langkah 1: Ekstraksi fitur abjad dari raw_dataset/
python extract_landmarks.py

# Langkah 2: Ekstraksi fitur kosakata dari yolo_dataset/
python extract_kosakata.py

# Langkah 3: Training model abjad
python train_model.py
# → Menghasilkan: models/model_bisindo_2hands.h5

# Langkah 4: Training model kosakata
python train_kosakata.py
# → Menghasilkan: models/model_kosakata_2hands.h5
```

### Environment yang Dibutuhkan
- RAM: min. 4 GB (8 GB disarankan untuk training)
- GPU: Opsional (training akan otomatis pakai GPU jika ada)
- Disk: ~500 MB (termasuk dataset dan model)

---

## 10. 🗄️ Struktur Data (Bukan Database Relasional)

### Representasi Fitur (126 Dimensi)

```
Tangan 1 (Kanan/Kiri):
  [x1,y1,z1, x2,y2,z2, ..., x21,y21,z21]  → 63 nilai
  (sudah dinormalisasi relatif terhadap wrist/pergelangan)

Tangan 2 (atau padding 0 jika tidak ada):
  [x1,y1,z1, ..., x21,y21,z21]              → 63 nilai

Total: 126 nilai float per frame/sampel
```

### Format File Dataset

| Jenis | Format | Lokasi |
|-------|--------|--------|
| Abjad (raw) | JPEG/PNG gambar | `raw_dataset/{A-Z}/` |
| Abjad (fitur) | `.npy` NumPy array [126,] | `dataset/{A-Z}/` |
| Kosakata (raw) | JPEG + Label YOLO `.txt` | `yolo_dataset/train/` |
| Kosakata (fitur) | CSV dengan kolom `label, f1..f126` | `features_kosakata/` |

### Skema CSV Kosakata (`train_kosakata.csv`)

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `label` | string | Nama kelas (misal: "maaf") |
| `f1` – `f126` | float32 | 126 nilai koordinat landmark ternormalisasi |

---

## 11. 🌐 Tidak Ada API Eksternal

Project ini **tidak mengekspos API** dan **tidak memanggil API eksternal** saat runtime. Semua proses berjalan secara lokal:

- MediaPipe berjalan **on-device** (tidak butuh internet)
- Model inference berjalan **lokal** di mesin pengguna
- Streamlit membuat server lokal (`localhost:8501`)

**Satu-satunya integrasi eksternal (offline):**
- Dataset kosakata diunduh dari **Roboflow** (saat pengumpulan data awal, bukan saat runtime)
  - URL: `https://universe.roboflow.com/ta-workspace/bisindo-kosakata-0mulz-ygrpa`

---

## 12. 🗺️ Diagram Alur Sistem

```
╔══════════════════════════════════════════════════════════════╗
║              PIPELINE BISINDO TRANSLATOR                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [FASE OFFLINE — Training]                                   ║
║                                                              ║
║  raw_dataset/         yolo_dataset/                          ║
║  (gambar A-Z)         (gambar kosakata)                      ║
║       │                     │                                ║
║       ▼                     ▼                                ║
║  extract_            extract_kosakata.py                     ║
║  landmarks.py        (MediaPipe + YOLO labels)               ║
║       │                     │                                ║
║       ▼                     ▼                                ║
║  dataset/*.npy       features_kosakata/*.csv                 ║
║  (126 fitur)         (label + 126 fitur)                     ║
║       │                     │                                ║
║       ▼                     ▼                                ║
║  train_model.py      train_kosakata.py                       ║
║  (ANN 512-256-128)   (ANN 256-128-64)                        ║
║       │                     │                                ║
║       ▼                     ▼                                ║
║  model_bisindo_      model_kosakata_                         ║
║  2hands.h5           2hands.h5                               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  [FASE ONLINE — Inferensi Real-Time]                         ║
║                                                              ║
║  Webcam                                                      ║
║    │ (frame 640×480)                                         ║
║    ▼                                                         ║
║  OpenCV → MediaPipe Hands                                    ║
║              │ (21 landmark × 2 tangan)                      ║
║              ▼                                               ║
║          utils.process_landmarks()                           ║
║              │ (normalisasi, padding → [126])                ║
║              ▼                                               ║
║      ┌───────────────────────┐                               ║
║      │  Mode Abjad?          │  Mode Kosakata?               ║
║      │  model_bisindo.h5     │  model_kosakata.h5            ║
║      │  threshold ≥ 0.85     │  threshold ≥ 0.75             ║
║      └───────────┬───────────┘                               ║
║                  │                                           ║
║                  ▼                                           ║
║      Stabilisasi Prediksi                                    ║
║      (Confidence + Majority Voting + Delay 0.6s)             ║
║                  │                                           ║
║                  ▼                                           ║
║      Streamlit UI → Tampilan Teks Kalimat                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 13. 📝 Kesimpulan

### Ringkasan
BISINDO Translator adalah proyek Tugas Akhir yang membangun sistem penerjemah bahasa isyarat Indonesia (BISINDO) berbasis computer vision secara real-time. Sistem menggunakan MediaPipe untuk ekstraksi landmark tangan (126 fitur dari dua tangan), kemudian mengklasifikasikan gestur menggunakan dua model ANN terpisah: satu untuk 26 abjad dan satu untuk 38 kosakata.

### Tingkat Kompleksitas
**Menengah-Tinggi** — melibatkan:
- Pipeline machine learning end-to-end (collect → extract → train → deploy)
- Integrasi beberapa library besar (TF, MediaPipe, OpenCV, Streamlit)
- Mekanisme stabilisasi prediksi yang cukup sophistocated
- Dua model spesialis dengan arsitektur berbeda

### Saran Pengembangan Selanjutnya

| Prioritas | Saran | Dampak |
|-----------|-------|--------|
| 🔴 Tinggi | Tambah lebih banyak data abjad → akurasi abjad masih 76% | Akurasi naik signifikan |
| 🔴 Tinggi | Data augmentation (rotasi, brightness) untuk robustness | Tahan kondisi cahaya berbeda |
| 🟡 Sedang | Gunakan LSTM/GRU untuk gestur dinamis (gerakan) | Fitur baru |
| 🟡 Sedang | Tambah Text-to-Speech (TTS) sebagai output suara | UX lebih baik |
| 🟡 Sedang | Buat config file (`config.yaml`) untuk path & hyperparameter | Maintainability |
| 🟢 Rendah | Deploy ke cloud (Streamlit Cloud / Hugging Face Spaces) | Akses publik |
| 🟢 Rendah | Tambah fitur ekspor kalimat (copy to clipboard / download) | UX lebih lengkap |
| 🟢 Rendah | Tambah unit test untuk fungsi `process_landmarks` | Kualitas kode |

---

*Dokumen ini dibuat secara otomatis melalui analisis kode sumber. Terakhir diperbarui: 15 Mei 2026.*
