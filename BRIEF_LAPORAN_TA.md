# BRIEFING LAPORAN TUGAS AKHIR — BISINDO TRANSLATOR
> Dokumen ini berisi seluruh konteks teknis project yang sudah selesai dikerjakan.
> Gunakan dokumen ini sebagai acuan untuk membantu menulis laporan Tugas Akhir.

---

## IDENTITAS PROJECT

| Item | Detail |
|---|---|
| **Judul** | Penerjemah Bahasa Isyarat Indonesia (BISINDO) Real-Time Berbasis Deteksi Landmark Tangan Menggunakan MediaPipe dan Deep Learning |
| **Platform Aplikasi** | Web Browser (Streamlit) |
| **Status** | ✅ Selesai — Semua fitur telah diimplementasikan |
| **Bahasa Pemrograman** | Python |

---

## DESKRIPSI SINGKAT PROJECT

Sistem ini adalah aplikasi web real-time yang menerjemahkan gestur tangan Bahasa Isyarat Indonesia (BISINDO) menggunakan kamera webcam. Sistem memiliki **dua model klasifikasi** yang berjalan bersamaan:

1. **Model Abjad** — Mengenali 26 huruf (A–Z) BISINDO
2. **Model Kosakata** — Mengenali sejumlah kosakata/kata tertentu dalam BISINDO

Pengguna dapat berpindah mode secara real-time. Hasil terjemahan huruf-per-huruf maupun kata dapat digabungkan menjadi kalimat utuh dengan logika *smart spacing* otomatis.

---

## STACK TEKNOLOGI

```
streamlit==1.32.0
opencv-python==4.9.0.80
mediapipe==0.10.9
numpy==1.24.3
tensorflow==2.15.0
scikit-learn==1.3.2
pandas==2.1.4
pyyaml==6.0.1
matplotlib (untuk visualisasi training)
seaborn (untuk confusion matrix)
```

---

## ARSITEKTUR SISTEM (PIPELINE LENGKAP)

```
[Webcam Input]
      |
      v
[OpenCV — Frame Capture & Preprocessing]
  - Resize ke 640x480
  - Flip horizontal (mirror)
  - Konversi BGR → RGB
      |
      v
[MediaPipe Hands — Deteksi Landmark]
  - max_num_hands = 2
  - min_detection_confidence = 0.5
  - min_tracking_confidence = 0.5
  - Output: 21 titik landmark per tangan (x, y, z)
      |
      v
[Feature Extraction — utils.py: process_landmarks()]
  - Total fitur: 126 (21 titik × 3 koordinat × 2 tangan)
  - Normalisasi: Koordinat dikurangi dengan koordinat wrist (titik 0)
  - Zero-padding: Jika hanya 1 tangan terdeteksi, 63 fitur sisa = 0.0
      |
      v
[Klasifikasi — ANN Model (TensorFlow/Keras)]
  - Model Abjad: model_bisindo_2hands.h5 (≈2.8 MB)
  - Model Kosakata: model_kosakata_2hands.h5 (≈1.0 MB)
  - Output: Probabilitas untuk setiap kelas (softmax)
      |
      v
[Stabilisasi Prediksi — Confidence Threshold + Majority Voting]
  - Confidence Threshold: 0.85 (abjad), 0.75 (kosakata)
  - Jika di bawah threshold: Majority voting dari histori 5 frame terakhir
  - Syarat majority: confidence > 0.60 DAN ≥ 4 dari 5 frame sama
  - Jeda minimum antar kata: 0.6 detik
  - Anti-duplikasi: Kata sama tidak ditambah ulang dalam 1.5 detik
      |
      v
[Antarmuka Web — Streamlit]
  - Tampilan split: Kanan kamera, Kiri hasil terjemahan
  - Smart spacing: Kata + spasi, Abjad disambung langsung
  - Tombol: "Hapus Kata Terakhir" dan "Reset Kalimat"
```

---

## STRUKTUR FILE PROJECT

```
bisindo-translatorgg/
│
├── app.py                  # Aplikasi utama Streamlit (196 baris)
├── utils.py                # Fungsi process_landmarks() — ekstraksi & normalisasi fitur
├── dataset_loader.py       # Loader dataset abjad dari folder .npy
│
├── extract_landmarks.py    # Script ekstraksi landmark dari raw_dataset/ → dataset/
├── extract_kosakata.py     # Script ekstraksi landmark dari yolo_dataset/ → features_kosakata/
│
├── train_model.py          # Script training Model Abjad (193 baris)
├── train_kosakata.py       # Script training Model Kosakata
│
├── raw_dataset/            # Dataset gambar mentah abjad (A-Z, tiap folder = 1 huruf)
├── dataset/                # Dataset .npy abjad hasil ekstraksi (A-Z)
├── yolo_dataset/           # Dataset gambar kosakata dalam format YOLO
│   ├── train/images/
│   ├── train/labels/
│   ├── val/images/
│   ├── val/labels/
│   └── data.yaml
├── features_kosakata/      # Fitur kosakata dalam format CSV
│   └── train_kosakata.csv
│
├── models/
│   ├── model_bisindo_2hands.h5     # Model abjad terlatih (2.8 MB)
│   ├── model_kosakata_2hands.h5    # Model kosakata terlatih (1.0 MB)
│   └── labels_kosakata.txt         # Daftar label kosakata (satu per baris)
│
├── training_results_abjad/     # Output evaluasi training model abjad
│   ├── accuracy_graph.png
│   ├── loss_graph.png
│   ├── confusion_matrix.png
│   ├── classification_report.txt
│   ├── final_validation_result.txt
│   ├── training_log_epoch.csv
│   ├── sample_prediction_result.csv
│   └── model_architecture_summary.txt
│
├── training_results/            # Output evaluasi training model kosakata
│   └── (file yang sama seperti di atas)
│
├── requirements.txt
└── proposal_ta.md              # Draft proposal TA
```

---

## DETAIL KODE INTI

### 1. `utils.py` — Fungsi Ekstraksi & Normalisasi Fitur

```python
def process_landmarks(results):
    keypoints = np.zeros(126)  # 2 tangan × 21 titik × 3 koordinat
    
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i >= 2: break
            
            hand_pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
            wrist = hand_pts[0]
            normalized_hand = hand_pts - wrist  # Normalisasi relatif terhadap wrist
            
            start_idx = i * 63
            keypoints[start_idx:start_idx+63] = normalized_hand.flatten()
    
    return keypoints  # Array 126 elemen
```

**Penjelasan teknis:**
- MediaPipe menghasilkan koordinat dalam rentang [0, 1] relatif terhadap ukuran frame
- Normalisasi wrist dilakukan agar posisi tangan di frame tidak mempengaruhi klasifikasi (model fokus pada *bentuk* gestur, bukan *posisi* tangan)
- Zero-padding memungkinkan model tetap berjalan meski hanya 1 tangan terdeteksi

---

### 2. `train_model.py` — Arsitektur Model Abjad

```python
model = Sequential([
    InputLayer(input_shape=(126,)),
    
    Dense(512, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
    BatchNormalization(),
    Dropout(0.35),

    Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
    BatchNormalization(),
    Dropout(0.30),

    Dense(128, activation="relu"),
    BatchNormalization(),

    Dense(26, activation="softmax")  # 26 kelas = A-Z
])
```

**Konfigurasi training:**
- Optimizer: Adam (lr = 0.001)
- Loss: Sparse Categorical Crossentropy
- Max Epochs: 100
- Batch Size: 64
- Early Stopping: monitor=val_accuracy, patience=10
- ReduceLROnPlateau: monitor=val_loss, factor=0.5, patience=5, min_lr=1e-6
- Data Split: 80% train / 20% validasi (stratified)
- Regularisasi: L2 weight decay + Dropout + BatchNormalization

---

### 3. `train_kosakata.py` — Arsitektur Model Kosakata

```python
model = Sequential([
    InputLayer(input_shape=(126,)),
    BatchNormalization(),   # Normalisasi di pintu masuk
    
    Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    BatchNormalization(),
    Dropout(0.5),

    Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    BatchNormalization(),
    Dropout(0.4),

    Dense(64, activation="relu"),
    BatchNormalization(),
    Dropout(0.3),

    Dense(N_kelas, activation="softmax")  # Jumlah kelas kosakata
])
```

**Perbedaan desain dari model abjad:**
- Lebih ramping (256 → 128 → 64 vs 512 → 256 → 128) karena kosakata lebih sedikit kelasnya
- Dropout lebih besar (0.5, 0.4, 0.3) untuk mencegah overfitting pada dataset yang lebih kecil
- BatchNormalization di lapisan pertama untuk stabilisasi skala koordinat
- Penalti L2 lebih besar (0.001 vs 0.0001)
- Max Epochs: 150, Batch Size: 32 (lebih kecil agar belajar lebih detail)
- Early Stopping: monitor=val_accuracy, patience=15

---

### 4. `app.py` — Logika Stabilisasi Prediksi Real-Time

```python
# Tahap 1: Confidence Threshold
if confidence > threshold:  # 0.85 abjad / 0.75 kosakata
    final_word = active_labels[label_index]
    st.session_state.history.clear()
    
# Tahap 2: Majority Voting (jika confidence rendah)
else:
    st.session_state.history.append(label_index)
    if len(st.session_state.history) > 5:
        st.session_state.history.pop(0)
    
    final_index = max(set(st.session_state.history), key=st.session_state.history.count)
    if confidence > 0.60 and st.session_state.history.count(final_index) >= 4:
        final_word = active_labels[final_index]

# Tahap 3: Jeda Temporal (Anti-Duplicate)
if final_word:
    if final_word != st.session_state.pending_word:
        st.session_state.pending_word = final_word
        st.session_state.pending_time = time.time()
    else:
        if time.time() - st.session_state.pending_time > 0.6:
            last_word = history_items[-1][0] if history_items else ""
            if final_word != last_word or (time.time() - last_add_time > 1.5):
                st.session_state.history_items.append((final_word, current_type))
```

---

### 5. `app.py` — Smart Spacing Logic

```python
def get_display_text():
    display_text = ""
    for i, (word, mode_type) in enumerate(st.session_state.history_items):
        if i == 0:
            display_text += word
        else:
            prev_word, prev_type = st.session_state.history_items[i-1]
            if mode_type == "kata":
                display_text += " " + word      # Kata selalu dapat spasi
            elif mode_type == "abjad":
                if prev_type == "kata":
                    display_text += " " + word  # Abjad setelah kata dapat spasi
                else:
                    display_text += word         # Abjad setelah abjad disambung
    return display_text
```

---

## DATASET

### Dataset Abjad
- **Sumber**: Foto tangan yang diambil sendiri, terorganisir dalam folder per huruf
- **Lokasi mentah**: `raw_dataset/` → 26 subfolder (A-Z)
- **Format setelah ekstraksi**: File `.npy` per gambar di `dataset/` → 26 subfolder (A-Z)
- **Isi setiap .npy**: Array numpy ukuran 126 (sudah dinormalisasi)
- **Proses**: `extract_landmarks.py` memproses setiap gambar dengan MediaPipe, mengekstrak landmark, menormalisasi, dan menyimpan ke `.npy`

### Dataset Kosakata
- **Format sumber**: YOLO dataset (memiliki folder `images/` dan `labels/` berformat `.txt`)
- **Lokasi**: `yolo_dataset/train/` dan `yolo_dataset/val/`
- **File konfigurasi**: `yolo_dataset/data.yaml` → berisi daftar nama kelas
- **Proses**: `extract_kosakata.py` membaca setiap gambar, mencocokkannya dengan file `.txt` (yang berisi `class_id`), mengekstrak landmark, dan menyimpan ke CSV
- **Output**: `features_kosakata/train_kosakata.csv` (kolom: `label, f1, f2, ..., f126`)
- **Jumlah kelas kosakata**: Sesuai isi `models/labels_kosakata.txt`

---

## FITUR APLIKASI (app.py)

| Fitur | Detail |
|---|---|
| **Dual Model** | Kedua model (abjad + kosakata) dimuat sekaligus saat startup menggunakan `@st.cache_resource` |
| **Mode Switching** | Radio button untuk beralih antara Mode Abjad dan Mode Kosakata real-time |
| **Kamera Anti-Refresh** | Objek `cv2.VideoCapture` disimpan di `st.session_state` agar tidak dibuat ulang setiap rerun |
| **Smart Spacing** | Logika penggabungan teks otomatis antara abjad dan kata |
| **Hapus Kata Terakhir** | Tombol untuk menghapus kata/huruf terakhir dari kalimat |
| **Reset Kalimat** | Tombol untuk mengosongkan seluruh kalimat |
| **Stabilisasi Prediksi** | 3 lapisan: Confidence Threshold → Majority Voting → Temporal Delay |
| **Skeleton Tangan** | Landmark dan koneksi tulang tangan digambar di atas frame kamera |

---

## OUTPUT TRAINING (File yang Dihasilkan)

Kedua script training (`train_model.py` dan `train_kosakata.py`) menghasilkan:

| File | Deskripsi |
|---|---|
| `accuracy_graph.png` | Grafik akurasi train vs validasi per epoch |
| `loss_graph.png` | Grafik loss train vs validasi per epoch |
| `confusion_matrix.png` | Heatmap confusion matrix pada data validasi |
| `classification_report.txt` | Precision, Recall, F1-Score per kelas |
| `final_validation_result.txt` | Akurasi dan loss akhir (train & validasi) |
| `training_log_epoch.csv` | Log lengkap semua metrik per epoch |
| `sample_prediction_result.csv` | 25 sampel prediksi acak + status BENAR/SALAH |
| `model_architecture_summary.txt` | Ringkasan arsitektur model (teks) |
| `dataset_sample.csv` | 20 baris sampel dataset mentah |

Untuk model abjad: folder `training_results_abjad/`
Untuk model kosakata: folder `training_results/`

---

## METODOLOGI PENELITIAN (RINGKASAN)

1. **Akuisisi Data** — Pengambilan foto tangan untuk abjad A-Z; dataset kosakata dalam format YOLO
2. **Ekstraksi Fitur** — MediaPipe Hands mendeteksi 21 landmark per tangan → normalisasi wrist → vektor 126 dimensi
3. **Pembangunan Model** — ANN fully-connected dengan BatchNorm, Dropout, dan regularisasi L2
4. **Training & Evaluasi** — 80/20 split, EarlyStopping, ReduceLROnPlateau, confusion matrix, classification report
5. **Implementasi Inferensi** — 3-layer stabilization: confidence threshold + majority voting + temporal delay
6. **Aplikasi Web** — Streamlit dengan dual-model, smart spacing, dan kamera anti-refresh

---

## STATUS PROGRESS

| Komponen | Status |
|---|---|
| Ekstraksi landmark abjad (`extract_landmarks.py`) | ✅ Selesai |
| Ekstraksi landmark kosakata (`extract_kosakata.py`) | ✅ Selesai |
| Training model abjad (`train_model.py`) | ✅ Selesai + Output evaluasi |
| Training model kosakata (`train_kosakata.py`) | ✅ Selesai + Output evaluasi |
| Aplikasi web real-time (`app.py`) | ✅ Selesai |
| Model abjad tersimpan | ✅ `models/model_bisindo_2hands.h5` (2.8 MB) |
| Model kosakata tersimpan | ✅ `models/model_kosakata_2hands.h5` (1.0 MB) |
| Penulisan laporan TA | 🔄 Sedang dikerjakan |

---

## CATATAN PENTING UNTUK PENULISAN LAPORAN

### Terminologi yang Perlu Dijelaskan di Laporan
- **BISINDO** = Bahasa Isyarat Indonesia (bahasa alami komunitas Tuli di Indonesia, berbeda dari SIBI)
- **SIBI** = Sistem Isyarat Bahasa Indonesia (sistem buatan berbasis bahasa lisan)
- **Landmark** = Titik-titik kunci pada anatomi tangan yang dideteksi MediaPipe
- **Confidence Score** = Nilai probabilitas tertinggi dari output softmax model
- **Majority Voting** = Mekanisme pengambilan keputusan berdasarkan suara terbanyak dari beberapa frame
- **Zero-padding** = Mengisi nilai 0 pada fitur tangan yang tidak terdeteksi
- **Batch Normalization** = Normalisasi output setiap lapisan untuk mempercepat dan menstabilkan training
- **Dropout** = Teknik regularisasi dengan "mematikan" neuron secara acak saat training
- **L2 Regularization** = Penalti pada bobot yang terlalu besar untuk mencegah overfitting
- **EarlyStopping** = Menghentikan training otomatis saat metrik validasi tidak membaik

### Poin Keunggulan Pendekatan Ini
1. **Tidak bergantung piksel** — Menggunakan landmark geometris, bukan raw image, sehingga robust terhadap perubahan pencahayaan dan warna kulit
2. **Ringan & efisien** — Model ANN dengan input 126 fitur jauh lebih ringan dari CNN berbasis gambar
3. **Real-time** — Latensi sangat rendah karena inferensi hanya pada vektor 126 angka
4. **Dua tangan** — Mendukung gestur BISINDO yang membutuhkan kedua tangan
5. **Dual-mode** — Satu aplikasi untuk abjad dan kosakata

### Keterbatasan Sistem
1. Hanya mengenali gestur **statis** (posisi diam), bukan gestur dinamis/bergerak
2. Membutuhkan **pencahayaan yang cukup** untuk deteksi landmark yang akurat
3. Performa menurun jika tangan **terhalang** (oklusi) sebagian
4. Dataset kosakata terbatas pada kelas yang sudah dilatih
5. Berjalan di **desktop** (webcam), belum mendukung mobile

---

## ROADMAP & SARAN PENGEMBANGAN SISTEM (BAB V & MATERI SIDANG SKRIPSI)

Berikut adalah 4 pilar peningkatan strategis yang dapat dicantumkan pada **BAB V (Saran)** serta disiapkan sebagai bahan argumentasi unggulan pada **Tanya-Jawab Sidang Skripsi**:

### 1. Peningkatan Model AI & Computer Vision (Paling Krusial)
* **Peralihan ke Model Sekuensial Temporal (LSTM / GRU / 1D-CNN)**:
  * *Konteks Akademik*: Model saat ini bekerja berbasis *single-frame classification* (frame demi frame terpisah). Padahal, banyak kosakata BISINDO yang merupakan gestur dinamis berkesinambungan (gerakan dari detik awal ke detik akhir).
  * *Solusi Pengembangan*: Menerapkan metode *sliding window* (misal 20–30 frame time-steps) yang diumpankan ke jaringan **LSTM (Long Short-Term Memory)** atau **Bi-directional GRU**. Model akan mampu mengenali gestur berdasarkan trayektori lintasan koordinat tangan sepanjang waktu.
* **Integrasi Titik Tubuh & Pose (MediaPipe Holistic / Pose Fusion)**:
  * *Konteks Akademik*: Normalisasi koordinat saat ini murni relatif terhadap pergelangan tangan (`wrist = landmark[0]`). Akibatnya, sistem memiliki kelemahan dalam membedakan gestur yang memiliki formasi jari serupa namun posisi anatomisnya berbeda (misal tangan di dahi vs tangan di dada).
  * *Solusi Pengembangan*: Mengintegrasikan landmark wajah/tubuh (hidung, bahu kiri, bahu kanan) sebagai titik jangkar (*anchor point*) sehingga model memiliki konteks spasial terhadap tubuh pengguna.

### 2. Peningkatan Pengolahan Bahasa (NLP & Grammar Smoothing)
* **Rekonstruksi Tata Bahasa Isyarat ke Bahasa Lisan Baku**:
  * *Konteks Akademik*: Bahasa Isyarat Indonesia (BISINDO) memiliki tata bahasa alami yang berbeda dengan Bahasa Indonesia lisan (kerap kali tanpa imbuhan *me-*, *di-*, *-kan* serta pola urutan kata topik-komentar atau Subjek-Objek-Predikat).
  * *Solusi Pengembangan*: Menambahkan modul *NLP Post-Processing* (berbasis aturan linguistik atau model sekuens kecil) untuk menerjemahkan rangkaian isyarat mentah (misal: `"saya buku baca"`) menjadi kalimat bahasa Indonesia formal yang mengalir (misal: `"Saya sedang membaca buku."`).
* **Ambang Batas Adaptif (Dynamic Confidence Filtering)**:
  * Menyediakan fitur penyesuaian nilai ambang batas (*confidence threshold*) dan durasi tahan isyarat (*hold time*) secara dinamis agar pengguna pemula maupun mahir dapat berinteraksi dengan nyaman.

### 3. Peningkatan Aksesibilitas & UI/UX
* **Komunikasi Dua Arah (Bidirectional Translator: Dengar ⇄ Tuli)**:
  * Mengubah sistem dari translator satu arah menjadi platform dialog inklusif. Teman Dengar dapat berbicara melalui mikrofon (ditranskripsi via *Speech-to-Text* secara real-time), dan sistem menampilkan kata kunci serta kartu isyarat visual untuk teman Tuli.
* **Progressive Web App (PWA) & Offline Inference**:
  * Menerapkan arsitektur PWA (*Service Worker* dan *Web App Manifest*) sehingga aplikasi dapat di-install langsung di layar utama smartphone (Android & iOS) layaknya aplikasi native tanpa Google Play Store, serta dapat memuat model secara instan melalui cache lokal.
* **Kamus Referensi Isyarat Visual Terintegrasi**:
  * Menyediakan katalog panduan visual interaktif untuk 26 abjad dan seluruh kosakata langsung di antarmuka web, memudahkan proses belajar bagi pengguna umum.

### 4. Poin Penguatan untuk Laporan / Sidang Skripsi (Nilai Tambah A+)
* **Evaluasi Performa Komputasi & Latensi (Edge AI vs Cloud)**:
  * Mencantumkan tabel komparasi teknis antara eksekusi di server cloud vs eksekusi lokal di browser (*Client-side WebGL*):
    - Waktu inferensi per frame: **< 15 ms** (setara 30–60 FPS).
    - Biaya komputasi server: **0% (Serverless)**, tanpa risiko *server crash / Out of Memory*.
* **Pengujian Ketahanan Sistem (Robustness Testing)**:
  * Menguji performa deteksi pada 3 skenario lingkungan berbeda:
    - Variasi intensitas pencahayaan (Terang ~300 lux, Redup ~50 lux, Backlight).
    - Variasi jarak kamera ke pengguna (50 cm, 100 cm, 150 cm).
    - Kompleksitas latar belakang (polos vs latar bergerak/ramai).
* **Pengujian Pengguna Riil (System Usability Scale - SUS)**:
  * Melibatkan responden dari komunitas Tuli / Gerkatin / SLB untuk mengisi kuesioner baku SUS (skala 0–100) sebagai bukti validasi empiris bahwa aplikasi layak dan mudah digunakan oleh target pengguna sesungguhnya.

---

## INSTRUKSI PENGGUNAAN UNTUK CLAUDE WEB

Ketika meminta bantuan penulisan laporan ke Claude Web, sertakan konteks ini dan instruksikan:

> "Saya sedang menulis laporan Tugas Akhir tentang sistem penerjemah BISINDO real-time. 
> Berikut adalah detail lengkap project saya yang sudah selesai. 
> Tolong bantu saya menulis [BAB/BAGIAN YANG INGIN DITULIS] berdasarkan informasi di atas.
> Gunakan bahasa Indonesia akademis yang formal."

**Bagian laporan yang perlu ditulis:**
- [ ] BAB I — Pendahuluan (Latar Belakang, Rumusan Masalah, Tujuan, Manfaat, Batasan)
- [ ] BAB II — Tinjauan Pustaka (BISINDO, MediaPipe, ANN, dll.)
- [ ] BAB III — Metodologi Penelitian
- [ ] BAB IV — Hasil dan Pembahasan
- [ ] BAB V — Kesimpulan dan Saran
- [ ] Abstrak
- [ ] Daftar Pustaka
