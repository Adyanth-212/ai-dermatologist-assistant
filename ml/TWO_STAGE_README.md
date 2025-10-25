# Two-Stage Skin Disease Prediction System

## 🎯 Overview

This system uses a **two-stage classification approach** for skin disease diagnosis:

1. **Stage 1**: General skin disease classifier (10 classes)
   - Identifies the broad category of skin condition
   - Determines if condition is cancer-related

2. **Stage 2**: Specialized cancer classifier (triggered automatically)
   - Only runs when Stage 1 detects cancer-related conditions
   - Provides detailed cancer analysis and malignancy assessment

## 📁 Files

- `two_stage_predictor.py` - Main prediction class
- `api_two_stage.py` - Flask REST API
- `test_two_stage.py` - Command-line test script

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate
pip install flask flask-cors
```

### 2. Test with Command Line

```bash
# Test with a single image
python test_two_stage.py "../split_dataset/test/2. Melanoma 15.75k/image.jpg"
```

### 3. Run as API Server

```bash
python api_two_stage.py
```

The API will start on `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```

### Single Image Prediction
```bash
curl -X POST -F "image=@test.jpg" http://localhost:5000/predict
```

### Batch Prediction
```bash
curl -X POST \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg" \
  http://localhost:5000/predict/batch
```

### Get API Info
```bash
curl http://localhost:5000/info
```

## 🔬 How It Works

### Stage 1: General Classification

The first model identifies one of 10 skin conditions:
1. Eczema
2. Warts/Molluscum/Viral Infections
3. **Melanoma** ⚠️
4. Atopic Dermatitis
5. **Basal Cell Carcinoma (BCC)** ⚠️
6. **Melanocytic Nevi (NV)** ⚠️
7. **Benign Keratosis-like Lesions (BKL)** ⚠️
8. Psoriasis/Lichen Planus
9. **Seborrheic Keratoses** ⚠️
10. Tinea/Ringworm/Fungal Infections

⚠️ = Triggers Stage 2 analysis

### Stage 2: Specialized Cancer Analysis

When a cancer-related condition is detected, the second model provides:
- Detailed cancer type classification
- Malignancy assessment
- Confidence scores
- Recommended actions

## 📊 Output Format

```json
{
  "stage1": {
    "class": "2. Melanoma 15.75k",
    "confidence": 0.87,
    "top3": [
      ["2. Melanoma 15.75k", 0.87],
      ["5. Melanocytic Nevi (NV) - 7970", 0.08],
      ["4. Basal Cell Carcinoma (BCC) 3323", 0.03]
    ]
  },
  "stage2": {
    "class": "Melanoma (Malignant)",
    "confidence": 0.92,
    "top3": [
      ["Melanoma (Malignant)", 0.92],
      ["Benign Nevus", 0.05],
      ["Seborrheic Keratosis", 0.02]
    ]
  },
  "recommendation": {
    "severity": "HIGH",
    "action": "URGENT: Immediate dermatologist consultation required",
    "details": "Stage 1 identified 2. Melanoma 15.75k with 87.0% confidence. Stage 2 refined diagnosis to Melanoma (Malignant) with 92.0% confidence."
  }
}
```

## 🔧 Integration with Frontend

### React/JavaScript Example

```javascript
async function predictSkinDisease(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('confidence_threshold', '0.5');
  
  const response = await fetch('http://localhost:5000/predict', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  console.log('Primary diagnosis:', result.stage1.class);
  console.log('Confidence:', result.stage1.confidence);
  
  if (result.stage2) {
    console.log('Cancer analysis:', result.stage2.class);
    console.log('Severity:', result.recommendation.severity);
  }
  
  return result;
}
```

### Python Example

```python
from two_stage_predictor import TwoStagePredictor

# Initialize once
predictor = TwoStagePredictor(
    stage1_model_path='models/finetuned_model.h5',
    stage2_model_path='models/skin_cancer_model.h5'
)

# Predict
result = predictor.predict('test_image.jpg', confidence_threshold=0.5)

print(f"Diagnosis: {result['stage1']['class']}")
print(f"Severity: {result['recommendation']['severity']}")
print(f"Action: {result['recommendation']['action']}")
```

## ⚙️ Configuration

### Adjust Confidence Threshold

Lower threshold = More sensitive (Stage 2 triggers more often)
Higher threshold = More specific (Stage 2 only for high-confidence cancer cases)

```python
# Conservative (trigger Stage 2 more often)
result = predictor.predict('image.jpg', confidence_threshold=0.3)

# Standard
result = predictor.predict('image.jpg', confidence_threshold=0.5)

# Aggressive (only trigger Stage 2 for very confident cases)
result = predictor.predict('image.jpg', confidence_threshold=0.7)
```

### Customize Cancer Classes

Edit `two_stage_predictor.py`:

```python
# Define which Stage 1 classes trigger Stage 2
self.cancer_classes = [2, 4, 5, 6, 8]  # Modify indices as needed
```

## 🧪 Testing

### Test with Sample Images

```bash
# Non-cancer case (Eczema)
python test_two_stage.py "../split_dataset/test/1. Eczema 1677/sample.jpg"

# Cancer case (Melanoma) - triggers Stage 2
python test_two_stage.py "../split_dataset/test/2. Melanoma 15.75k/sample.jpg"

# Borderline case (Nevi)
python test_two_stage.py "../split_dataset/test/5. Melanocytic Nevi (NV) - 7970/sample.jpg"
```

## 📝 Notes

- **Models Required**: Both `finetuned_model.h5` (Stage 1) and `skin_cancer_model.h5` (Stage 2) must be present in the `models/` directory
- **Image Size**: Images are automatically resized to 224x224
- **File Formats**: Supports JPG, JPEG, PNG
- **Max File Size**: 16MB per image

## 🚨 Disclaimer

This system is for **educational and research purposes only**. It should NOT be used as a substitute for professional medical diagnosis. Always consult with a qualified dermatologist for proper skin condition evaluation.

## 🔄 Future Improvements

- [ ] Add confidence intervals
- [ ] Implement grad-CAM visualization
- [ ] Add treatment recommendations
- [ ] Support for multiple image formats
- [ ] Real-time webcam analysis
- [ ] Integration with medical databases
