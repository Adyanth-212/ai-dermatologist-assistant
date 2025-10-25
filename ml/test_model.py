import tensorflow as tf
import numpy as np
from keras.models import load_model, Model
from keras.preprocessing.image import img_to_array
from PIL import Image
import os
import sys
from typing import Optional

# --- CONFIG ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "skin_cancer_model.h5")

CLASS_NAMES = [
    'Actinic Keratoses (akiec)',
    'Basal Cell Carcinoma (bcc)',
    'Benign Keratosis (bkl)',
    'Dermatofibroma (df)',
    'Melanocytic Nevus (nv)',
    'Vascular Lesions (vasc)',
    'Melanoma (mel)'
]

def test_model_loading():
    """Test if the model loads correctly"""
    print("🔍 Testing model loading...")
    try:
        if not os.path.exists(MODEL_PATH):
            print(f"❌ Model file not found: {MODEL_PATH}")
            return None
        
        loaded_model = load_model(MODEL_PATH)
        if not isinstance(loaded_model, Model):
            print("❌ Loaded object is not a Keras Model")
            return None
            
        model = loaded_model
        print("✅ Model loaded successfully!")
        
        # Print model summary
        print("\n📊 Model Summary:")
        try:
            print(f"Input shape: {model.input_shape}")
            print(f"Output shape: {model.output_shape}")
            print(f"Total params: {model.count_params():,}")
        except:
            print("Model summary not available")
            print(f"Model layers: {len(model.layers)}")
        
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def create_test_image():
    """Create a dummy test image if no real image is provided"""
    print("🖼️ Creating dummy test image (224x224 random pixels)...")
    # Create a random RGB image
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    return Image.fromarray(test_img)

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess image for model prediction"""
    img = image.convert("RGB")
    img = img.resize((224, 224))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_image(model: Model, img_array: np.ndarray):
    """Make prediction on preprocessed image"""
    print("🧠 Making prediction...")
    preds = model.predict(img_array)[0]
    pred_index = int(np.argmax(preds))
    prediction = CLASS_NAMES[pred_index]
    confidence = float(np.max(preds))
    
    print(f"\n🏆 Results:")
    print(f"   Prediction: {prediction}")
    print(f"   Confidence: {confidence * 100:.2f}%")
    
    print(f"\n📈 All class probabilities:")
    for i, (class_name, prob) in enumerate(zip(CLASS_NAMES, preds)):
        print(f"   {i+1}. {class_name}: {prob * 100:.2f}%")
    
    return prediction, confidence

def main():
    """Main testing function"""
    print("🩺 AI Dermatologist Model Tester")
    print("=" * 50)
    
    # Test model loading
    model = test_model_loading()
    if model is None:
        print("❌ Cannot proceed without a working model.")
        return
    
    # Handle image input
    if len(sys.argv) > 1:
        # Use provided image path
        image_path = sys.argv[1]
        print(f"📁 Using provided image: {image_path}")
        try:
            img = Image.open(image_path)
            print("✅ Image loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            print("🔄 Falling back to dummy image...")
            img = create_test_image()
    else:
        # Use dummy image
        print("ℹ️  No image path provided. Usage: python test_model.py <image_path>")
        img = create_test_image()
    
    # Preprocess and predict
    try:
        img_array = preprocess_image(img)
        prediction, confidence = predict_image(model, img_array)
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during prediction: {e}")

if __name__ == "__main__":
    main()
