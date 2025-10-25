# 🎯 Two-Stage Skin Disease Classifier - READY TO USE

## ✅ What You Have Now

### Files Created:
1. **`two_stage_predictor.py`** - Core prediction system
2. **`api_two_stage.py`** - Flask REST API server  
3. **`test_two_stage.py`** - CLI testing tool
4. **`TWO_STAGE_README.md`** - Full documentation

### Models Required:
- `models/finetuned_model.h5` - Stage 1 (General classifier) ✅ EXISTS
- `models/skin_cancer_model.h5` - Stage 2 (Cancer specialist) ✅ EXISTS

---

## 🚀 HOW TO RUN

### Option 1: Start the API Server (RECOMMENDED)

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate
python api_two_stage.py
```

Server starts at: `http://localhost:5000`

### Option 2: Test from Command Line

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate

# Find a test image
python test_two_stage.py "../split_dataset/test/2. Melanoma 15.75k/<any-image.jpg>"
```

---

## 📡 API USAGE

### Test API (from browser or another terminal):

```bash
# Health check
curl http://localhost:5000/health

# Get API info
curl http://localhost:5000/info

# Upload and predict
curl -X POST -F "image=@path/to/your/image.jpg" http://localhost:5000/predict
```

---

## 🔬 How It Works

### Stage 1: General Classification
- Identifies 1 of 10 skin conditions
- Determines if cancer-related

### Stage 2: Specialized Cancer Analysis (Auto-triggered)
- **Triggers when Stage 1 detects:**
  - Melanoma
  - Basal Cell Carcinoma  
  - Melanocytic Nevi
  - Benign Keratosis-like Lesions
  - Seborrheic Keratoses

- **Provides:**
  - Detailed cancer type
  - Malignancy assessment
  - Severity level
  - Recommended action

---

## 📊 Example Output

```json
{
  "stage1": {
    "class": "2. Melanoma 15.75k",
    "confidence": 0.87
  },
  "stage2": {
    "class": "Melanoma (Malignant)",
    "confidence": 0.92
  },
  "recommendation": {
    "severity": "HIGH",
    "action": "URGENT: Immediate dermatologist consultation required"
  }
}
```

---

## 🎮 QUICK START NOW

**Run this in your terminal:**

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate
python api_two_stage.py
```

Then open another terminal and test:

```bash
# Find a melanoma image to test
find ../split_dataset/test -name "*.jpg" | head -1

# Test with that image
curl -X POST -F "image=@<path-from-above>" http://localhost:5000/predict
```

---

## 🔌 Frontend Integration

Use with your React frontend by sending POST requests to `/predict`:

```javascript
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch('http://localhost:5000/predict', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
```

---

## ⚡ THAT'S IT! 

You now have a complete two-stage classification system ready to use!

All code is in `/mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060/`
