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