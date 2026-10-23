import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model

def clean_config(obj):
    if isinstance(obj, dict):
        keys_to_remove = ["module", "registered_name", "date_saved", "build_config"]
        cleaned = {}
        for k, v in obj.items():
            if k in keys_to_remove:
                continue
            if k.endswith("_regularizer") or k.endswith("_constraint"):
                cleaned[k] = None
            else:
                cleaned[k] = clean_config(v)
        return cleaned
    elif isinstance(obj, list):
        return [clean_config(item) for item in obj]
    return obj

def convert_keras_to_tfjs(model_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading {model_path}...")
    model = load_model(model_path)
    
    # 1. Prepare weights
    weights_spec = []
    binary_data = bytearray()
    
    for weight in model.weights:
        name = weight.name
        if name.endswith(":0"):
            name = name[:-2]
            
        data = weight.numpy().astype(np.float32)
        shape = list(data.shape)
        
        weights_spec.append({
            "name": name,
            "shape": shape,
            "dtype": "float32"
        })
        binary_data.extend(data.tobytes())
        
    bin_path = os.path.join(output_dir, "weights.bin")
    with open(bin_path, "wb") as f:
        f.write(binary_data)
    print(f"Wrote {len(weights_spec)} weights ({len(binary_data):,} bytes) to {bin_path}")
    
    # 2. Prepare topology and manifest
    raw_config = json.loads(model.to_json())
    model_config = clean_config(raw_config)
    
    model_json = {
        "format": "layers-model",
        "generatedBy": f"keras v{tf.__version__}",
        "convertedBy": "Antigravity Custom Converter",
        "modelTopology": {
            "keras_version": tf.__version__,
            "backend": "tensorflow",
            "model_config": model_config
        },
        "weightsManifest": [
            {
                "paths": ["weights.bin"],
                "weights": weights_spec
            }
        ]
    }
    
    json_path = os.path.join(output_dir, "model.json")
    with open(json_path, "w") as f:
        json.dump(model_json, f, indent=2)
    print(f"Wrote {json_path}")

def export_labels():
    # Abjad labels (A-Z)
    abjad_labels = sorted(os.listdir("raw_dataset"))
    os.makedirs("models/web", exist_ok=True)
    with open("models/web/labels_abjad.json", "w") as f:
        json.dump(abjad_labels, f, indent=2)
    print(f"Exported {len(abjad_labels)} abjad labels.")
    
    # Kosakata labels
    with open("models/labels_kosakata.txt", "r") as f:
        kosakata_labels = [line.strip() for line in f.readlines() if line.strip()]
    with open("models/web/labels_kosakata.json", "w") as f:
        json.dump(kosakata_labels, f, indent=2)
    print(f"Exported {len(kosakata_labels)} kosakata labels.")

if __name__ == "__main__":
    export_labels()
    convert_keras_to_tfjs("models/model_bisindo_2hands.h5", "models/web/abjad")
    convert_keras_to_tfjs("models/model_kosakata_2hands.h5", "models/web/kosakata")
    print("All models and labels successfully converted!")
