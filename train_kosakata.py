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