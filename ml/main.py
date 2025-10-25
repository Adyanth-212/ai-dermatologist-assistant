
import tensorflow as tf
import numpy as np
import cv2
import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from keras.models import load_model, Model
from keras.preprocessing.image import img_to_array
from PIL import Image
import os
from typing import Optional, Union
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "skin_cancer_model.h5")

# --- Configuration & Model Loading ---------------------------------------------

# Define the 7 classes your model was trained on (from the Hugging Face card)
# This order is CRITICAL.
CLASS_NAMES = [
    'Actinic Keratoses (akiec)',
    'Basal Cell Carcinoma (bcc)',
    'Benign Keratosis (bkl)',
    'Dermatofibroma (df)',
    'Melanocytic Nevus (nv)',
    'Vascular Lesions (vasc)',
    'Melanoma (mel)'
]
print("Health Check: CLASS_NAMES loaded.")
# Load your pre-trained Keras model
model: Optional[Model] = None
try:
    loaded_model = load_model(MODEL_PATH)
    if isinstance(loaded_model, Model):
        model = loaded_model
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
    else:
        print(f"❌ ERROR: Loaded object is not a Keras Model")
        model = None
except Exception as e:
    print(f"❌ ERROR loading model: {e}")
    print(f"👉 Make sure '{MODEL_PATH}' exists.")
    model = None

# Initialize the FastAPI app
app = FastAPI(title="Skin Cancer AI Brain (3060)")

# --- Helper Functions ----------------------------------------------------------

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Loads image from bytes, resizes to 224x224, and preprocesses
    for the `syaha/skin_cancer_detection_model`.
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    img = img.resize((224, 224))
    
    img_array = img_to_array(img)
    img_array = img_array / 255.0  # Simple rescale
    img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
    
    return img_array

def find_last_conv_layer(model: Model) -> str:
    """
    Finds the name of the last convolutional layer in the model.
    """
    for layer in reversed(model.layers):
        if "conv2d" in layer.name:
            print(f"Found last conv layer: {layer.name}")
            return layer.name
    
    # Fallback if no "conv2d" found
    # You may need to manually find this by printing model.summary()
    # For this specific model, a good guess is one of the last conv layers.
    # We'll guess a common name. If this fails, we'll need model.summary().
    print("Warning: Could not auto-find 'conv2d' layer. Guessing 'conv2d_9'.")
    return "conv2d_9" 

# Find the layer name ONCE at startup
LAST_CONV_LAYER = find_last_conv_layer(model) if model else None

def get_grad_cam(model: Model, img_array: np.ndarray, last_conv_layer_name: str, pred_index: int) -> np.ndarray:
    """
    Generates the Grad-CAM heatmap.
    """
    grad_model = Model(
        [model.inputs], 
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    last_conv_layer_output = last_conv_layer_output[0]
    
    heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
    heatmap = heatmap.numpy()
    
    return heatmap

def overlay_heatmap(image_bytes: bytes, heatmap: np.ndarray, alpha=0.4) -> bytes:
    """
    Overlays the heatmap on the original image and returns bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
    img = img_to_array(img)

    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    heatmap_uint8 = (255 * heatmap_resized).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    superimposed_img = (heatmap_colored * alpha) + img
    superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)

    is_success, buffer = cv2.imencode(".jpg", superimposed_img)
    if not is_success:
        raise HTTPException(status_code=500, detail="Failed to encode heatmap image.")
        
    return buffer.tobytes()

# --- API Endpoints -------------------------------------------------------------

@app.get("/")
def read_root():
    return {"status": "AI Brain Server (3060) is running."}


@app.post("/generate_report")
async def generate_report(file: UploadFile = File(...)):
    """
    Receives an image, performs prediction, and generates a Grad-CAM report.
    This is the "Big/Slow" endpoint.
    """
    if not model:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    if not LAST_CONV_LAYER:
        raise HTTPException(status_code=500, detail="Could not find conv layer for Grad-CAM.")

    image_bytes = await file.read()
    try:
        processed_image = preprocess_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file. Error: {e}")

    # Get model prediction
    preds = model.predict(processed_image)[0]
    pred_index = int(np.argmax(preds))
    prediction = CLASS_NAMES[pred_index]
    confidence = float(np.max(preds))

    # Generate Grad-CAM heatmap
    try:
        heatmap = get_grad_cam(model, processed_image, LAST_CONV_LAYER, pred_index)
        heatmap_overlay_bytes = overlay_heatmap(image_bytes, heatmap)
        heatmap_base64 = base64.b64encode(heatmap_overlay_bytes).decode('utf-8')
        
    except Exception as e:
        print(f"❌ Grad-CAM Error: {e}")
        heatmap_base64 = None

    # Send the final JSON response
    return {
        "prediction": prediction,
        "confidence": confidence,
        "heatmap_image": f"data:image/jpeg;base64,{heatmap_base64}"
    }
