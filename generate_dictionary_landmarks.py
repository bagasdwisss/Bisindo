import os
import json
import numpy as np
import pandas as pd

def extract_clean_landmarks():
    dictionary_data = {
        "abjad": {},
        "kosakata": {}
    }

    # 1. Process Abjad (A-Z) from dataset/
    print("Processing Abjad (filtering valid non-zero frames)...")
    letters = sorted(os.listdir("dataset"))
    for letter in letters:
        dir_path = os.path.join("dataset", letter)
        if not os.path.isdir(dir_path):
            continue

        npy_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".npy")]
        valid_samples = []

        for f in npy_files:
            try:
                arr = np.load(f)
                if arr.shape == (126,) and np.count_nonzero(arr[:63]) > 20:
                    valid_samples.append(arr)
            except Exception:
                pass

        if valid_samples:
            median_coords = np.median(valid_samples, axis=0)
            h1 = median_coords[:63].reshape(21, 3).tolist()
            h2 = median_coords[63:].reshape(21, 3).tolist()
            has_h2 = bool(np.count_nonzero(median_coords[63:]) > 20 and np.max(np.abs(median_coords[63:])) > 0.05)

            dictionary_data["abjad"][letter] = {
                "name": letter,
                "type": "abjad",
                "twoHands": has_h2,
                "hand1": [[round(float(v), 4) for v in pt] for pt in h1],
                "hand2": [[round(float(v), 4) for v in pt] for pt in h2] if has_h2 else None
            }
            print(f"  [OK] Abjad {letter}: {len(valid_samples)} samples, 2-Hands: {has_h2}")
        else:
            print(f"  [WARN] Abjad {letter} has no valid samples!")

    # 2. Process Kosakata from features_kosakata/train_kosakata.csv
    print("\nProcessing Kosakata from features_kosakata/train_kosakata.csv...")
    csv_path = "features_kosakata/train_kosakata.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        labels = sorted(df["label"].unique())

        for label in labels:
            df_label = df[df["label"] == label].drop("label", axis=1)
            coords_arr = df_label.values
            valid_samples = [row for row in coords_arr if np.count_nonzero(row[:63]) > 20]

            if valid_samples:
                median_coords = np.median(valid_samples, axis=0)
                h1 = median_coords[:63].reshape(21, 3).tolist()
                h2 = median_coords[63:].reshape(21, 3).tolist()
                has_h2 = bool(np.count_nonzero(median_coords[63:]) > 20 and np.max(np.abs(median_coords[63:])) > 0.05)

                dictionary_data["kosakata"][label] = {
                    "name": label,
                    "type": "kata",
                    "twoHands": has_h2,
                    "hand1": [[round(float(v), 4) for v in pt] for pt in h1],
                    "hand2": [[round(float(v), 4) for v in pt] for pt in h2] if has_h2 else None
                }
                print(f"  [OK] Kosakata {label}: {len(valid_samples)} samples, 2-Hands: {has_h2}")

    out_path = "models/web/landmarks_dictionary.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(dictionary_data, f, indent=2)

    print(f"\nGenerated {out_path} with {len(dictionary_data['abjad'])} abjad and {len(dictionary_data['kosakata'])} kosakata!")

if __name__ == "__main__":
    extract_clean_landmarks()
