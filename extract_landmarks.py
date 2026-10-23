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