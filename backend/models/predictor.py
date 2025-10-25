
# Predictor helpers for loading huggingface or local TensorFlow models.
# This file contains utilities to download a pre-trained model (from HF) and load it.

from huggingface_hub import hf_hub_download
import tensorflow as tf
import os

def download_model_from_hf(repo_id: str, filename: str, dest_dir="ml/trained_models/hf"):
    os.makedirs(dest_dir, exist_ok=True)
    local_path = hf_hub_download(repo_id=repo_id, filename=filename, repo_type='model')
    # Move or copy to dest_dir as needed
    return local_path

def load_keras_model(path):
    return tf.keras.models.load_model(path)
