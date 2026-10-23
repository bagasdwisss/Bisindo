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