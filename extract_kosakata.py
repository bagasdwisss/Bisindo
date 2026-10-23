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