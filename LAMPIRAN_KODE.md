# Lampiran Kode Program - Penerjemah BISINDO (BISINDO Translator)

Dokumen ini berisi lampiran kode program utama yang digunakan dalam pengembangan sistem Penerjemah Bahasa Isyarat Indonesia (BISINDO). Sistem ini dikembangkan menggunakan Python dengan framework Streamlit untuk antarmuka pengguna, MediaPipe untuk estimasi pose tangan, dan TensorFlow/Keras untuk pelatihan model klasifikasi.

---

## Daftar Berkas Kode Program

Berikut adalah daftar berkas penting yang dilampirkan:

1. **[app.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/app.py)** - Aplikasi utama antarmuka pengguna (Streamlit), penangkapan kamera real-time, prediksi isyarat, dan fitur Text-to-Speech.
2. **[utils.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/utils.py)** - Modul utilitas untuk pemrosesan dan normalisasi koordinat hand landmarks.
3. **[dataset_loader.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/dataset_loader.py)** - Modul pemuat dataset untuk model abjad dari file numpy (.npy).
4. **[extract_landmarks.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/extract_landmarks.py)** - Script untuk mengekstrak hand landmarks dari citra mentah dataset abjad.
5. **[extract_kosakata.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/extract_kosakata.py)** - Script untuk mengekstrak hand landmarks dari dataset kosakata berbasis anotasi YOLO.
6. **[train_model.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/train_model.py)** - Script pelatihan model neural network untuk klasifikasi abjad.
7. **[train_kosakata.py](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/train_kosakata.py)** - Script pelatihan model neural network untuk klasifikasi kosakata.
8. **[requirements.txt](file:///d:/Tugas%20Akhir/code/bisindo-translatorgg/requirements.txt)** - Daftar ketergantungan library/package Python yang digunakan.

---

## 1. Antarmuka Aplikasi Utama (`app.py`)

Berkas ini mengimplementasikan antarmuka grafis berbasis web menggunakan Streamlit. Alur kerja berkas ini meliputi pembacaan input kamera secara real-time menggunakan OpenCV, deteksi landmark tangan dengan MediaPipe, normalisasi fitur, prediksi menggunakan model TensorFlow (.h5), pengelolaan logika transisi kata/abjad, serta fitur pengucapan suara (Text-to-Speech) menggunakan gTTS.

```python
import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import os
import time
from tensorflow.keras.models import load_model
from utils import process_landmarks

# pyrefly: ignore [missing-import]
from gtts import gTTS
# pyrefly: ignore [missing-import]
import pygame
import tempfile

def speak_text(text):
    """Mengubah teks menjadi suara menggunakan gTTS dan memutar dengan pygame."""
    if not text.strip():
        return
    try:
        tts = gTTS(text=text, lang="id")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_path = tmp_file.name
        tts.save(tmp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        os.remove(tmp_path)
    except Exception as e:
        st.warning(f"TTS Error: {e}")

st.set_page_config(page_title="BISINDO Translator", layout="wide")
st.title("BISINDO Translator")

@st.cache_resource
def load_all_models():
    model_abjad = load_model("models/model_bisindo_2hands.h5")
    labels_abjad = sorted(os.listdir("raw_dataset"))
    
    model_kosa = load_model("models/model_kosakata_2hands.h5")
    labels_kosa = []
    with open("models/labels_kosakata.txt", "r") as f:
        labels_kosa = [line.strip() for line in f.readlines()]
        
    return model_abjad, labels_abjad, model_kosa, labels_kosa

model_abjad, labels_abjad, model_kosa, labels_kosa = load_all_models()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

if "history_items" not in st.session_state:
    st.session_state.history_items = []
if "history" not in st.session_state:
    st.session_state.history = []
if "last_index" not in st.session_state:
    st.session_state.last_index = None

if "pending_word" not in st.session_state:
    st.session_state.pending_word = ""
if "pending_time" not in st.session_state:
    st.session_state.pending_time = 0
if "last_add_time" not in st.session_state:
    st.session_state.last_add_time = 0

if "auto_speak" not in st.session_state:
    st.session_state.auto_speak = False

if "cap" not in st.session_state:
    st.session_state.cap = None

def get_display_text():
    display_text = ""
    for i, (word, mode_type) in enumerate(st.session_state.history_items):
        if i == 0:
            display_text += word
        else:
            prev_word, prev_type = st.session_state.history_items[i-1]
            if mode_type == "kata":
                display_text += " " + word
            elif mode_type == "abjad":
                if prev_type == "kata":
                    display_text += " " + word
                else:
                    display_text += word 
    return display_text

col1, col2 = st.columns([2, 1])

with col1:
    run = st.checkbox("Mulai Kamera", key="start_cam")
    FRAME_WINDOW = st.image([])

with col2:
    st.markdown("### Hasil Terjemahan:")
    OUTPUT = st.empty()
    
    OUTPUT.markdown(
        f"<div style='padding:20px; border-radius:10px; background-color:#1e1e1e; min-height:150px;'>"
        f"<h2 style='text-align:left; color:#4CAF50;'>{get_display_text()}</h2>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### Kontrol Sistem")
    
    mode_pilihan = st.radio("Pilih Mode:", ["Mode Kata", "Mode Abjad"], horizontal=True)
    st.session_state.is_mode_abjad = (mode_pilihan == "Mode Abjad")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Hapus Kata Terakhir", use_container_width=True):
            if len(st.session_state.history_items) > 0:
                st.session_state.history_items.pop()
                
    with col_btn2:
        if st.button("Reset Kalimat", use_container_width=True):
            st.session_state.history_items = []

    st.markdown("---")
    st.markdown("### 🔊 Text-to-Speech")

    col_tts1, col_tts2 = st.columns(2)
    with col_tts1:
        if st.button("🔊 Ucapkan Kalimat", use_container_width=True):
            speak_text(get_display_text())
    with col_tts2:
        st.session_state.auto_speak = st.toggle(
            "Auto-Ucap Kata Baru", value=st.session_state.auto_speak
        )

if run:
    if st.session_state.cap is None or not st.session_state.cap.isOpened():
        st.session_state.cap = cv2.VideoCapture(0)
    
    while run:
        ret, frame = st.session_state.cap.read()
        if not ret:
            st.error("Kamera tidak terdeteksi.")
            break

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            keypoints = process_landmarks(results)
            active_model = model_abjad if st.session_state.is_mode_abjad else model_kosa
            active_labels = labels_abjad if st.session_state.is_mode_abjad else labels_kosa
            threshold = 0.85 if st.session_state.is_mode_abjad else 0.75
            current_type = "abjad" if st.session_state.is_mode_abjad else "kata"

            prediction = active_model.predict(np.array([keypoints]), verbose=0)
            label_index = np.argmax(prediction)
            confidence = float(np.max(prediction))

            final_word = None

            if confidence > threshold:
                final_word = active_labels[label_index]
                st.session_state.history.clear()
                st.session_state.last_index = label_index
            else:
                if st.session_state.last_index is not None and label_index != st.session_state.last_index:
                    st.session_state.history.clear()

                st.session_state.history.append(label_index)
                if len(st.session_state.history) > 5:
                    st.session_state.history.pop(0)

                final_index = max(set(st.session_state.history), key=st.session_state.history.count)
                if confidence > 0.60 and st.session_state.history.count(final_index) >= 4:
                    final_word = active_labels[final_index]

            if final_word:
                if final_word != st.session_state.pending_word:
                    st.session_state.pending_word = final_word
                    st.session_state.pending_time = time.time()
                else:
                    if time.time() - st.session_state.pending_time > 0.6:
                        last_word = st.session_state.history_items[-1][0] if len(st.session_state.history_items) > 0 else ""
                        
                        if final_word != last_word or (time.time() - st.session_state.last_add_time > 1.5):
                            st.session_state.history_items.append((final_word, current_type))
                            st.session_state.last_add_time = time.time()
                            st.session_state.pending_word = ""
                            if st.session_state.auto_speak:
                                speak_text(final_word)
            else:
                st.session_state.pending_word = ""

            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        FRAME_WINDOW.image(rgb)

        OUTPUT.markdown(
            f"<div style='padding:20px; border-radius:10px; background-color:#1e1e1e; min-height:150px;'>"
            f"<h2 style='text-align:left; color:#4CAF50;'>{get_display_text()}</h2>"
            f"</div>",
            unsafe_allow_html=True
        )

else:
    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None
```

---

## 2. Pemrosesan & Normalisasi Koordinat (`utils.py`)

Fungsi ini bertanggung jawab untuk mengekstrak posisi koordinat $X, Y, Z$ dari landmark tangan MediaPipe, melakukan normalisasi posisi relatif terhadap pergelangan tangan (wrist), meratakan (flattening) array tersebut ke dalam format vektor satu dimensi dengan ukuran 126 elemen (2 tangan $\times$ 21 landmark $\times$ 3 koordinat), dan mengisi nilai 0 (zero-padding) jika tangan yang terdeteksi kurang dari dua.

```python
import numpy as np

def process_landmarks(results):
    keypoints = np.zeros(126)
    
    if results.multi_hand_landmarks:
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            if i >= 2: 
                break

            hand_pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])

            wrist = hand_pts[0]
            normalized_hand = hand_pts - wrist
            start_idx = i * 63
            end_idx = start_idx + 63
            keypoints[start_idx:end_idx] = normalized_hand.flatten()
            
    return keypoints
```

---

## 3. Utilitas Pemuat Dataset Abjad (`dataset_loader.py`)

Modul ini memuat dataset abjad berformat NumPy (.npy), menyusun label target, serta membagi dataset menjadi data latih (train) dan data validasi (validation) dengan rasio 80:20 serta pemisahan tersatifikasi (stratified split).

```python
import os
import numpy as np
from sklearn.model_selection import train_test_split

DATASET_PATH = "dataset"

def load_data():
    X, y = [], []
    labels = sorted(os.listdir(DATASET_PATH))
    label_map = {label:i for i,label in enumerate(labels)}

    for label in labels:
        folder = os.path.join(DATASET_PATH, label)
        for file in os.listdir(folder):
            data = np.load(os.path.join(folder, file))
            X.append(data)
            y.append(label_map[label])

    X = np.array(X)
    y = np.array(y)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    return X_train, X_val, y_train, y_val, label_map
```

---

## 4. Ekstraksi Fitur Citra Abjad (`extract_landmarks.py`)

Script ini berjalan secara offline untuk memproses citra mentah dari folder dataset abjad (`raw_dataset`), menggunakan MediaPipe Hands untuk mendeteksi koordinat landmark tangan, menormalisasinya menggunakan `utils.py`, dan menyimpannya ke bentuk file biner `.npy` pada folder target (`dataset`).

```python
import cv2
import mediapipe as mp
import numpy as np
import os
from utils import process_landmarks

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)

SOURCE = "raw_dataset"
DEST = "dataset"

for label in os.listdir(SOURCE):
    os.makedirs(os.path.join(DEST, label), exist_ok=True)

    for img_file in os.listdir(os.path.join(SOURCE, label)):
        img_path = os.path.join(SOURCE, label, img_file)
        img = cv2.imread(img_path)

        if img is None:
            continue

        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        keypoints = process_landmarks(results)

        np.save(
            os.path.join(DEST, label, img_file.split(".")[0] + ".npy"),
            keypoints
        )

print("Landmark ekstraksi 2 tangan selesai!")
```

---

## 5. Ekstraksi Fitur Kosakata Berdasarkan Dataset YOLO (`extract_kosakata.py`)

Berkas ini memproses gambar berlabel format YOLO (`yolo_dataset`), membaca label anotasi dari berkas teks, mencocokkannya dengan peta nama kelas dari `data.yaml`, mengekstrak fitur landmark tangan untuk pembagian data `train` dan `val`, lalu menyimpannya dalam format terstruktur CSV (`features_kosakata`).

```python
import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import yaml
from utils import process_landmarks

YOLO_DIR = "yolo_dataset"
OUT_DIR = "features_kosakata"
YAML_PATH = os.path.join(YOLO_DIR, "data.yaml")

os.makedirs(OUT_DIR, exist_ok=True)

with open(YAML_PATH, 'r') as file:
    data_yaml = yaml.safe_load(file)

class_names = data_yaml['names']
print(f"Ditemukan {len(class_names)} kelas di data.yaml: {class_names}\n")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2)

def extract_split(split_name):
    print(f"=== Memproses dataset: {split_name} ===")
    
    img_dir = os.path.join(YOLO_DIR, split_name, "images")
    lbl_dir = os.path.join(YOLO_DIR, split_name, "labels")
    
    if not os.path.exists(img_dir) or not os.path.exists(lbl_dir):
        print(f"Folder {split_name} tidak lengkap, dilewati.")
        return

    all_features = []
    
    img_files = [f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    for img_file in img_files:
        txt_file = os.path.splitext(img_file)[0] + ".txt"
        lbl_path = os.path.join(lbl_dir, txt_file)
        
        if not os.path.exists(lbl_path):
            continue
            
        with open(lbl_path, 'r') as f:
            content = f.readline().strip()
            if not content:
                continue
            class_id = int(content.split()[0])
            
            label_name = class_names[class_id]

        img_path = os.path.join(img_dir, img_file)
        img = cv2.imread(img_path)
        
        if img is None:
            continue
            
        results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        if results.multi_hand_landmarks:
            keypoints = process_landmarks(results)
            
            row_data = [label_name] + keypoints.tolist()
            all_features.append(row_data)

    if all_features:
        cols = ['label'] + [f'f{i}' for i in range(1, 127)]
        df = pd.DataFrame(all_features, columns=cols)
        
        csv_out_path = os.path.join(OUT_DIR, f"{split_name}_kosakata.csv")
        df.to_csv(csv_out_path, index=False)
        print(f"Berhasil menyimpan {len(df)} baris ke {csv_out_path}\n")
    else:
        print(f"Tidak ada tangan yang terdeteksi di dataset {split_name}.\n")

extract_split("train")
extract_split("val")

print("Proses ekstraksi kosakata selesai!")
```

---

## 6. Pelatihan Model Klasifikasi Abjad (`train_model.py`)

Script ini melatih model Deep Neural Network (DNN) untuk mengenali kelas abjad (huruf) isyarat. Memiliki struktur 3 hidden layer dengan Batch Normalization, Dropout untuk regulasi overfitting, callback EarlyStopping, dan ReduceLROnPlateau. Hasil evaluasi mencakup confusion matrix, grafik metrik akurasi/loss per epoch, serta klasifikasi report secara otomatis di-export.

```python
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, InputLayer
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
# pyrefly: ignore [missing-import]
from tensorflow.keras.utils import plot_model
from sklearn.metrics import classification_report, confusion_matrix
from dataset_loader import load_data

RESULTS_DIR = "training_results_abjad"
os.makedirs(RESULTS_DIR, exist_ok=True)
print(f"Folder {RESULTS_DIR} disiapkan untuk menyimpan hasil evaluasi.")

print("Memuat dataset abjad...")
X_train, X_val, y_train, y_val, label_map = load_data()

class_names = [k for k, v in sorted(label_map.items(), key=lambda item: item[1])]

print(f"Berhasil memuat dataset. Total kelas: {len(class_names)}")

sample_df = pd.DataFrame(X_train[:20])
sample_df['label'] = [class_names[i] for i in y_train[:20]]
cols = ['label'] + [col for col in sample_df.columns if col != 'label']
sample_df = sample_df[cols]
sample_df.to_csv(f"{RESULTS_DIR}/dataset_sample.csv", index=False)

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

    Dense(len(class_names), activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

try:
    plot_model(model, to_file=f"{RESULTS_DIR}/model_architecture.png", show_shapes=True, show_layer_names=True)
except Exception as e:
    print("Graphviz tidak terdeteksi, menyimpan arsitektur ke format teks sebagai cadangan.")
with open(f"{RESULTS_DIR}/model_architecture_summary.txt", 'w') as f:
    model.summary(print_fn=lambda x: f.write(x + '\n'))

early_stop = EarlyStopping(
    monitor="val_accuracy",
    patience=10,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor="val_loss",
    factor=0.5,
    patience=5,
    min_lr=1e-6,
    verbose=1
)

print("\nMulai proses training...\n")
history = model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=64,
    validation_data=(X_val, y_val),
    callbacks=[early_stop, reduce_lr]
)

os.makedirs("models", exist_ok=True)
model_out_path = "models/model_bisindo_2hands.h5"
model.save(model_out_path)
print(f"\nTraining selesai! Model berhasil disimpan di {model_out_path}")

print("\nMenyusun laporan dan grafik hasil training...")

hist_df = pd.DataFrame(history.history)
hist_df.to_csv(f"{RESULTS_DIR}/training_log_epoch.csv", index=False)

plt.figure(figsize=(10, 6))
plt.plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
plt.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
plt.title('Model Accuracy over Epochs (Abjad)')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.grid(True)
plt.savefig(f"{RESULTS_DIR}/accuracy_graph.png")
plt.close()

plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Train Loss', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
plt.title('Model Loss over Epochs (Abjad)')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.grid(True)
plt.savefig(f"{RESULTS_DIR}/loss_graph.png")
plt.close()

y_pred_prob = model.predict(X_val, verbose=0)
y_pred = np.argmax(y_pred_prob, axis=1)

cm = confusion_matrix(y_val, y_pred)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix (Abjad)')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig(f"{RESULTS_DIR}/confusion_matrix.png")
plt.close()

report = classification_report(y_val, y_pred, target_names=class_names)
with open(f"{RESULTS_DIR}/classification_report.txt", "w") as f:
    f.write("=== CLASSIFICATION REPORT (ABJAD) ===\n\n")
    f.write(report)

final_train_acc = history.history['accuracy'][-1]
final_val_acc = history.history['val_accuracy'][-1]
final_train_loss = history.history['loss'][-1]
final_val_loss = history.history['val_loss'][-1]

with open(f"{RESULTS_DIR}/final_validation_result.txt", "w") as f:
    f.write("=== FINAL TRAINING & VALIDATION RESULT (ABJAD) ===\n")
    f.write(f"Total Epochs Run: {len(history.history['accuracy'])}\n")
    f.write(f"Final Train Accuracy: {final_train_acc:.4f}\n")
    f.write(f"Final Train Loss: {final_train_loss:.4f}\n")
    f.write(f"Best / Final Validation Accuracy: {final_val_acc:.4f}\n")
    f.write(f"Best / Final Validation Loss: {final_val_loss:.4f}\n")

sample_indices = np.random.choice(len(X_val), min(25, len(X_val)), replace=False)
sample_true = [class_names[i] for i in y_val[sample_indices]]
sample_pred = [class_names[i] for i in y_pred[sample_indices]]
sample_conf = np.max(y_pred_prob[sample_indices], axis=1)

sample_df = pd.DataFrame({
    'True_Label': sample_true,
    'Predicted_Label': sample_pred,
    'Confidence_Score': sample_conf,
    'Status': ['BENAR' if t == p else 'SALAH' for t, p in zip(sample_true, sample_pred)]
})
sample_df.to_csv(f"{RESULTS_DIR}/sample_prediction_result.csv", index=False)

print(f"\nSemua grafik dan laporan berhasil di-generate dan disimpan ke folder '{RESULTS_DIR}/'!")
```

---

## 7. Pelatihan Model Klasifikasi Kosakata (`train_kosakata.py`)

Serupa dengan model abjad, berkas ini melatih DNN menggunakan data input berupa CSV (`features_kosakata/train_kosakata.csv`). Model ditujukan untuk mengenali kata-kata isyarat BISINDO yang lebih kompleks secara semantik.

```python
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, InputLayer
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
# pyrefly: ignore [missing-import]
from tensorflow.keras.utils import plot_model
import matplotlib.pyplot as plt
import seaborn as sns
import os

RESULTS_DIR = "training_results"
os.makedirs(RESULTS_DIR, exist_ok=True)
print(f"Folder {RESULTS_DIR} disiapkan untuk menyimpan hasil evaluasi.")

CSV_PATH = "features_kosakata/train_kosakata.csv"
print(f"Membaca data dari {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)

df.head(20).to_csv(f"{RESULTS_DIR}/dataset_sample.csv", index=False)

X = df.drop("label", axis=1).values.astype(np.float32)
y_raw = df["label"].values

le = LabelEncoder()
y = le.fit_transform(y_raw)

os.makedirs("models", exist_ok=True)
labels_path = "models/labels_kosakata.txt"
with open(labels_path, "w") as f:
    for cls in le.classes_:
        f.write(f"{cls}\n")

X_train, X_val, y_train, y_val = train_test_split(
    X, y, 
    test_size=0.2, 
    stratify=y, 
    random_state=42
)

model = Sequential([
    InputLayer(input_shape=(126,)),
    BatchNormalization(), 
    
    Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    BatchNormalization(),
    Dropout(0.5),

    Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.001)),
    BatchNormalization(),
    Dropout(0.4),

    Dense(64, activation="relu"),
    BatchNormalization(),
    Dropout(0.3),

    Dense(len(le.classes_), activation="softmax")
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

try:
    plot_model(model, to_file=f"{RESULTS_DIR}/model_architecture.png", show_shapes=True, show_layer_names=True)
except Exception as e:
    print("Graphviz tidak terdeteksi, menyimpan arsitektur ke format teks sebagai cadangan.")
with open(f"{RESULTS_DIR}/model_architecture_summary.txt", 'w') as f:
    model.summary(print_fn=lambda x: f.write(x + '\n'))

early_stop = EarlyStopping(
    monitor="val_accuracy", 
    patience=15, 
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor="val_loss", 
    factor=0.5, 
    patience=5, 
    min_lr=1e-6,
    verbose=1
)

print("\nMulai proses training...\n")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=150, 
    batch_size=32, 
    callbacks=[early_stop, reduce_lr]
)

model_out_path = "models/model_kosakata_2hands.h5"
model.save(model_out_path)
print(f"\nTraining selesai! Model disimpan di {model_out_path}")

print("\nMenyusun laporan dan grafik hasil training...")

hist_df = pd.DataFrame(history.history)
hist_df.to_csv(f"{RESULTS_DIR}/training_log_epoch.csv", index=False)

plt.figure(figsize=(10, 6))
plt.plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
plt.plot(history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
plt.title('Model Accuracy over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.grid(True)
plt.savefig(f"{RESULTS_DIR}/accuracy_graph.png")
plt.close()

plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Train Loss', linewidth=2)
plt.plot(history.history['val_loss'], label='Validation Loss', linewidth=2)
plt.title('Model Loss over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')
plt.grid(True)
plt.savefig(f"{RESULTS_DIR}/loss_graph.png")
plt.close()

y_pred_prob = model.predict(X_val, verbose=0)
y_pred = np.argmax(y_pred_prob, axis=1)

cm = confusion_matrix(y_val, y_pred)
plt.figure(figsize=(16, 12))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.xticks(rotation=90)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{RESULTS_DIR}/confusion_matrix.png")
plt.close()

report = classification_report(y_val, y_pred, target_names=le.classes_)
with open(f"{RESULTS_DIR}/classification_report.txt", "w") as f:
    f.write("=== CLASSIFICATION REPORT ===\n\n")
    f.write(report)

final_train_acc = history.history['accuracy'][-1]
final_val_acc = history.history['val_accuracy'][-1]
final_train_loss = history.history['loss'][-1]
final_val_loss = history.history['val_loss'][-1]

with open(f"{RESULTS_DIR}/final_validation_result.txt", "w") as f:
    f.write("=== FINAL TRAINING & VALIDATION RESULT ===\n")
    f.write(f"Total Epochs Run: {len(history.history['accuracy'])}\n")
    f.write(f"Final Train Accuracy: {final_train_acc:.4f}\n")
    f.write(f"Final Train Loss: {final_train_loss:.4f}\n")
    f.write(f"Best / Final Validation Accuracy: {final_val_acc:.4f}\n")
    f.write(f"Best / Final Validation Loss: {final_val_loss:.4f}\n")

sample_indices = np.random.choice(len(X_val), 25, replace=False)
sample_true = le.inverse_transform(y_val[sample_indices])
sample_pred = le.inverse_transform(y_pred[sample_indices])
sample_conf = np.max(y_pred_prob[sample_indices], axis=1)

sample_df = pd.DataFrame({
    'True_Label': sample_true,
    'Predicted_Label': sample_pred,
    'Confidence_Score': sample_conf,
    'Status': ['BENAR' if t == p else 'SALAH' for t, p in zip(sample_true, sample_pred)]
})
sample_df.to_csv(f"{RESULTS_DIR}/sample_prediction_result.csv", index=False)

print(f"\nSemua grafik dan laporan berhasil di-generate dan disimpan ke folder '{RESULTS_DIR}/'!")
```

---

## 8. Kebutuhan Pustaka (`requirements.txt`)

Daftar pustaka Python yang wajib diinstal agar seluruh sistem dapat beroperasi dengan baik.

```text
streamlit==1.32.0
opencv-python==4.9.0.80
mediapipe==0.10.9
numpy==1.24.3
tensorflow==2.15.0
scikit-learn==1.3.2
pandas==2.1.4
pyyaml==6.0.1
```
