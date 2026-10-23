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