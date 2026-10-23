# PROPOSAL TUGAS AKHIR

---

## A. RENCANA JUDUL

**"Penerjemah Bahasa Isyarat Indonesia (BISINDO) Real-Time Berbasis Deteksi Landmark Tangan Menggunakan MediaPipe dan Deep Learning"**

---

## B. BIDANG ILMU

- Kecerdasan Buatan (*Artificial Intelligence*)
- Pemrosesan Citra Digital (*Computer Vision*)
- Interaksi Manusia-Komputer (*Human-Computer Interaction*)

---

## C. LATAR BELAKANG

Bahasa Isyarat Indonesia (BISINDO) merupakan bahasa alami yang digunakan oleh komunitas Tuli di Indonesia. Berbeda dengan Sistem Isyarat Bahasa Indonesia (SIBI) yang merupakan isyarat buatan berbasis bahasa lisan, BISINDO tumbuh secara organik dalam komunitas Tuli dan memiliki tata bahasa yang mandiri. Meskipun demikian, kesenjangan komunikasi antara pengguna BISINDO dan masyarakat umum masih sangat lebar, dikarenakan terbatasnya jumlah interpreter profesional serta rendahnya literasi isyarat di masyarakat.

Perkembangan teknologi *computer vision* dan *deep learning* membuka peluang untuk membangun sistem penerjemah otomatis berbasis kamera yang dapat menjembatani kesenjangan komunikasi tersebut. Salah satu pendekatan yang populer adalah menggunakan deteksi *keypoint* atau titik-titik landmark pada tangan secara real-time, sehingga sistem tidak bergantung pada piksel gambar mentah melainkan pada representasi geometris postur tangan yang lebih ringkas dan invariant terhadap perubahan pencahayaan.

MediaPipe Hands, sebuah framework dari Google, mampu mendeteksi 21 landmark per tangan secara real-time pada perangkat komputasi biasa. Dengan memanfaatkan 21 landmark × 3 dimensi (x, y, z) per tangan, setiap gestur dapat direpresentasikan sebagai vektor fitur berdimensi 126 (untuk dua tangan). Vektor fitur ini kemudian dapat dilatih menggunakan model jaringan saraf tiruan (*Artificial Neural Network*) untuk mengklasifikasikan gestur menjadi abjad (A–Z) maupun kosakata BISINDO tertentu.

Penelitian ini mengusulkan pembangunan sistem penerjemah BISINDO dua moda, yaitu **Mode Abjad** (penerjemahan huruf demi huruf) dan **Mode Kosakata** (penerjemahan kata/frasa tertentu), yang dapat dijalankan langsung di browser melalui antarmuka web interaktif.

---

## D. RUMUSAN MASALAH

Berdasarkan latar belakang di atas, rumusan masalah pada penelitian ini adalah:

1. Bagaimana membangun pipeline ekstraksi fitur landmark tangan secara real-time menggunakan MediaPipe yang dapat merepresentasikan gestur BISINDO dua tangan?
2. Bagaimana merancang dan melatih model *deep learning* yang mampu mengklasifikasikan gestur abjad (A–Z) dan kosakata BISINDO dengan tingkat akurasi yang memadai?
3. Bagaimana mengimplementasikan mekanisme stabilisasi prediksi (*confidence thresholding* dan *majority voting*) untuk meminimalkan prediksi palsu (*false positive*) pada inferensi real-time?
4. Bagaimana membangun antarmuka aplikasi web yang intuitif sehingga pengguna umum dapat menggunakan sistem tanpa keahlian teknis?

---

## E. BATASAN MASALAH

Agar penelitian lebih terfokus, ditetapkan batasan-batasan sebagai berikut:

1. Sistem hanya menerjemahkan gestur **statis** (diam di posisi tertentu), bukan gestur dinamis/bergerak.
2. Input berupa **kamera webcam** yang terhubung ke komputer; tidak mendukung input video pra-rekam.
3. **Mode Abjad** mencakup 26 huruf alfabet (A–Z) sesuai representasi BISINDO.
4. **Mode Kosakata** dibatasi pada sejumlah kosakata tertentu yang telah dikumpulkan dalam dataset pelatihan.
5. Sistem dirancang untuk kondisi **satu atau dua tangan** terdeteksi; gestur yang membutuhkan lebih dari dua tangan tidak didukung.
6. Lingkungan penggunaan diasumsikan memiliki **pencahayaan yang cukup** dan **latar belakang yang relatif bersih**.
7. Platform aplikasi adalah **desktop web browser** menggunakan Streamlit; tidak mencakup aplikasi mobile native.
8. Bahasa isyarat yang diacu adalah **BISINDO**, bukan SIBI atau bahasa isyarat internasional lainnya.

---

## F. TUJUAN PENELITIAN

Penelitian ini bertujuan untuk:

1. Membangun pipeline ekstraksi landmark tangan secara real-time menggunakan MediaPipe Hands yang menghasilkan vektor fitur 126 dimensi (dua tangan).
2. Melatih model *Artificial Neural Network* (ANN) dengan arsitektur *fully-connected* bertingkat untuk klasifikasi gestur BISINDO pada dua moda: abjad dan kosakata.
3. Mengimplementasikan mekanisme stabilisasi prediksi berbasis *confidence threshold* (≥ 0,85 untuk abjad; ≥ 0,75 untuk kosakata) dan *majority voting* (histori 5 frame) untuk meningkatkan keandalan inferensi real-time.
4. Membangun aplikasi web real-time berbasis Streamlit yang menampilkan hasil terjemahan gestur BISINDO secara langsung dari kamera webcam.

---

## G. MANFAAT PENELITIAN

### Manfaat Teoritis
- Memberikan kontribusi pada kajian penerapan *computer vision* dan *deep learning* untuk pengenalan bahasa isyarat Indonesia.
- Menjadi referensi bagi penelitian selanjutnya dalam pengembangan sistem penerjemah BISINDO yang lebih komprehensif (gestur dinamis, kalimat lengkap, dll.).

### Manfaat Praktis
- **Bagi komunitas Tuli**: Memberikan alat bantu komunikasi yang mudah diakses untuk menjembatani interaksi dengan masyarakat umum yang tidak memahami BISINDO.
- **Bagi masyarakat umum**: Memudahkan belajar dan memahami dasar-dasar BISINDO secara interaktif.
- **Bagi institusi pendidikan**: Dapat digunakan sebagai media pembelajaran isyarat berbasis teknologi di sekolah luar biasa (SLB) maupun kelas inklusi.
- **Bagi pengembang**: Kode sumber terbuka dan pipeline modular yang dapat dikembangkan lebih lanjut untuk gestur dan bahasa isyarat lainnya.

---

## H. METODOLOGI PENELITIAN

Penelitian ini menggunakan pendekatan *Research and Development* (R&D) dengan tahapan sebagai berikut:

### 1. Studi Literatur
- Kajian bahasa isyarat Indonesia (BISINDO) dan strukturnya.
- Telaah penelitian terdahulu tentang pengenalan bahasa isyarat berbasis *computer vision*.
- Studi teknologi: MediaPipe Hands, TensorFlow/Keras, Streamlit.

### 2. Pengumpulan Dataset
- **Dataset Abjad**: Pengambilan sampel gestur abjad A–Z, masing-masing beberapa ratus sampel per kelas, menggunakan skrip ekstraksi landmark (`extract_landmarks.py`).
- **Dataset Kosakata**: Pengambilan sampel gestur kosakata BISINDO menggunakan skrip (`extract_kosakata.py`) yang menghasilkan file CSV fitur per video/sesi rekaman.
- Setiap sampel direpresentasikan sebagai vektor 126 fitur (koordinat x, y, z dari 21 landmark tangan kiri + 21 landmark tangan kanan).

### 3. Pra-pemrosesan Data
- Normalisasi koordinat landmark relatif terhadap pergelangan tangan (wrist) agar posisi tangan di frame tidak memengaruhi klasifikasi.
- Pengisian nilai nol (zero-padding) jika hanya satu tangan yang terdeteksi.
- Pembagian data menjadi data latih (80%) dan data validasi (20%) dengan stratifikasi kelas.

### 4. Perancangan dan Pelatihan Model
- **Arsitektur**: *Fully-connected ANN* dengan lapisan `Dense`, `BatchNormalization`, dan `Dropout`.
  - **Model Abjad**: Input 126 → Dense(512) → BN → Dropout(0.35) → Dense(256) → BN → Dropout(0.30) → Dense(128) → BN → Dense(N_kelas, softmax).
  - **Model Kosakata**: Input 126 → BN → Dense(256) → BN → Dropout(0.5) → Dense(128) → BN → Dropout(0.4) → Dense(64) → BN → Dropout(0.3) → Dense(N_kelas, softmax).
- **Fungsi kerugian**: *Sparse Categorical Crossentropy*.
- **Optimizer**: Adam (lr = 0,001).
- **Regularisasi**: L2 weight decay, Dropout, EarlyStopping, dan ReduceLROnPlateau.
- **Framework**: TensorFlow 2.15 / Keras.

### 5. Evaluasi Model
- Metrik: Akurasi, Loss (train & validasi).
- Pengujian pada data validasi yang dipisahkan sejak awal.
- Analisis *confusion matrix* untuk mengidentifikasi kelas yang sulit dibedakan.

### 6. Implementasi Aplikasi
- Pembangunan antarmuka web menggunakan **Streamlit**.
- Integrasi MediaPipe Hands untuk deteksi landmark secara real-time dari webcam.
- Implementasi mekanisme stabilisasi: *confidence threshold* dan *majority voting* berbasis histori frame.
- Pengujian fungsional aplikasi pada berbagai kondisi pencahayaan dan pengguna.

### 7. Pengujian dan Evaluasi Sistem
- **Pengujian unit**: Akurasi model pada test set.
- **Pengujian sistem**: Pengujian end-to-end aplikasi oleh beberapa pengguna (termasuk pengguna BISINDO jika memungkinkan).
- Pencatatan hasil dan analisis kendala yang ditemukan.

---

## I. TINJAUAN PUSTAKA

| No | Referensi | Relevansi |
|----|-----------|-----------|
| 1 | Luqman, H., et al. (2019). "Isolated Arabic Sign Language Recognition Using a Discriminative Sequence Feature Extraction Approach." *IEEE Access*. | Pendekatan ekstraksi fitur untuk pengenalan bahasa isyarat statis. |
| 2 | Zhang, F., et al. (2020). "MediaPipe Hands: On-device Real-time Hand Tracking." *arXiv:2006.10214*. | Landasan teknis framework MediaPipe Hands yang digunakan dalam penelitian ini. |
| 3 | Bantupalli, K., & Xie, Y. (2018). "American Sign Language Recognition Using Deep Learning and Computer Vision." *IEEE Big Data*. | Studi kasus pengenalan ASL menggunakan deep learning, menjadi acuan arsitektur model. |
| 4 | Parelli, M., et al. (2022). "CLIP-guided Vision-Language Pre-training for Sign Language Recognition." *CVPR Workshops*. | Perkembangan terkini dalam pengenalan bahasa isyarat berbasis visi. |
| 5 | Koller, O., et al. (2020). "Quantitative Survey of the State of the Art in Sign Language Recognition." *arXiv:2008.09918*. | Survei komprehensif metode-metode pengenalan bahasa isyarat. |
| 6 | Abdi, M. H., et al. (2022). "BISINDO Sign Language Recognition Using MediaPipe and CNN." *Jurnal Informatika*. | Penelitian terkait yang secara spesifik membahas BISINDO. |
| 7 | Ioffe, S., & Szegedy, C. (2015). "Batch Normalization: Accelerating Deep Network Training." *ICML*. | Landasan teoritis Batch Normalization yang digunakan dalam arsitektur model. |
| 8 | Srivastava, N., et al. (2014). "Dropout: A Simple Way to Prevent Neural Networks from Overfitting." *JMLR*. | Landasan teoritis teknik regularisasi Dropout. |

> **Catatan**: Daftar referensi di atas bersifat indikatif dan perlu dilengkapi/diverifikasi dengan literatur yang tersedia secara aktual.

---

## J. RENCANA KEGIATAN

| No | Kegiatan | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 | Bulan 5 | Bulan 6 |
|----|----------|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| 1 | Studi Literatur & Pengumpulan Referensi | ✓ | ✓ | | | | |
| 2 | Pengumpulan & Anotasi Dataset Abjad | ✓ | ✓ | | | | |
| 3 | Pengumpulan & Anotasi Dataset Kosakata | | ✓ | ✓ | | | |
| 4 | Pra-pemrosesan & Ekstraksi Fitur | | ✓ | ✓ | | | |
| 5 | Perancangan Arsitektur Model | | | ✓ | | | |
| 6 | Pelatihan & Evaluasi Model Abjad | | | ✓ | ✓ | | |
| 7 | Pelatihan & Evaluasi Model Kosakata | | | | ✓ | | |
| 8 | Pengembangan Aplikasi Web (Streamlit) | | | | ✓ | ✓ | |
| 9 | Pengujian & Perbaikan Sistem | | | | | ✓ | |
| 10 | Penulisan Laporan Tugas Akhir | | ✓ | ✓ | ✓ | ✓ | ✓ |
| 11 | Sidang / Presentasi Akhir | | | | | | ✓ |

---

*Dokumen ini merupakan rancangan awal proposal Tugas Akhir dan dapat diperbarui sesuai perkembangan penelitian.*
