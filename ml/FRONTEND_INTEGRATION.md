# 🚀 Frontend Integration Guide - AI Dermatologist API

## For Frontend Developers

This guide will help you integrate the two-stage skin disease classification API with your React frontend.

---

## 📡 API Server Setup

### Starting the API Server

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate
python api_two_stage.py
```

**Server URL:** `http://localhost:5000`

**Note:** Models take ~30-60 seconds to load on startup. Wait for the console message: "✅ API Ready!"

---

## 🔌 API Endpoints

### 1. Health Check
**GET** `/health`

```javascript
const response = await fetch('http://localhost:5000/health');
const data = await response.json();
// { status: 'healthy', service: '...', timestamp: '...' }
```

### 2. Get API Info
**GET** `/info`

```javascript
const response = await fetch('http://localhost:5000/info');
const data = await response.json();
// Returns: API details, supported formats, endpoints, etc.
```

### 3. Single Image Prediction (MAIN ENDPOINT)
**POST** `/predict`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `image` (file), optional: `confidence_threshold` (float, default: 0.5)

**Response:**
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
    "details": "Stage 1 identified 2. Melanoma 15.75k with 87.0% confidence..."
  },
  "metadata": {
    "filename": "skin_lesion.jpg",
    "timestamp": "2025-10-25T17:30:00.000Z",
    "confidence_threshold": 0.5
  }
}
```

### 4. Batch Prediction
**POST** `/predict/batch`

For multiple images at once.

---

## 💻 React Integration Examples

### Example 1: Simple Image Upload Component

```jsx
import React, { useState } from 'react';

function SkinDiseaseAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select an image');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('confidence_threshold', '0.5');

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Prediction failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="analyzer-container">
      <h2>Skin Disease Analysis</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="results">
          <h3>Analysis Results</h3>
          
          <div className="stage1">
            <h4>Primary Diagnosis</h4>
            <p><strong>{result.stage1.class}</strong></p>
            <p>Confidence: {(result.stage1.confidence * 100).toFixed(2)}%</p>
          </div>

          {result.stage2 && (
            <div className="stage2">
              <h4>Detailed Cancer Analysis</h4>
              <p><strong>{result.stage2.class}</strong></p>
              <p>Confidence: {(result.stage2.confidence * 100).toFixed(2)}%</p>
            </div>
          )}

          <div className="recommendation">
            <h4>Recommendation</h4>
            <p className={`severity-${result.recommendation.severity.toLowerCase()}`}>
              Severity: {result.recommendation.severity}
            </p>
            <p><strong>{result.recommendation.action}</strong></p>
            <p className="details">{result.recommendation.details}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default SkinDiseaseAnalyzer;
```

### Example 2: Using React Hooks

```jsx
// useSkinAnalysis.js - Custom Hook
import { useState } from 'react';

export function useSkinAnalysis() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = async (file, confidenceThreshold = 0.5) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', file);
      formData.append('confidence_threshold', confidenceThreshold.toString());

      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Prediction failed');
      }

      const data = await response.json();
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { analyze, result, loading, error };
}

// Usage in component:
// const { analyze, result, loading, error } = useSkinAnalysis();
// await analyze(imageFile);
```

### Example 3: API Service Module

```javascript
// services/skinAnalysisAPI.js
const API_BASE_URL = 'http://localhost:5000';

class SkinAnalysisAPI {
  async checkHealth() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }

  async getInfo() {
    const response = await fetch(`${API_BASE_URL}/info`);
    return response.json();
  }

  async predict(imageFile, options = {}) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    if (options.confidenceThreshold) {
      formData.append('confidence_threshold', options.confidenceThreshold);
    }

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Prediction failed');
    }

    return response.json();
  }

  async predictBatch(imageFiles, options = {}) {
    const formData = new FormData();
    
    imageFiles.forEach(file => {
      formData.append('images', file);
    });

    if (options.confidenceThreshold) {
      formData.append('confidence_threshold', options.confidenceThreshold);
    }

    const response = await fetch(`${API_BASE_URL}/predict/batch`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Batch prediction failed');
    }

    return response.json();
  }
}

export default new SkinAnalysisAPI();
```

---

## 🎨 Response Structure Guide

### Understanding the Response

#### Stage 1 (Always Present)
- **class:** The general skin disease category
- **confidence:** Probability (0.0 to 1.0)
- **top3:** Top 3 predictions with confidences

#### Stage 2 (Only for Cancer Cases)
- Appears when Stage 1 detects: Melanoma, BCC, Nevi, BKL, or Seborrheic
- **class:** Detailed cancer classification
- **confidence:** Refined probability

#### Recommendation (Always Present)
- **severity:** "LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH"
- **action:** Recommended next steps
- **details:** Full explanation

---

## 🎯 UI/UX Suggestions

### Color Coding by Severity

```css
.severity-low {
  color: green;
  background: #e8f5e9;
}

.severity-medium {
  color: orange;
  background: #fff3e0;
}

.severity-medium-high {
  color: #ff6f00;
  background: #ffe0b2;
}

.severity-high {
  color: red;
  background: #ffebee;
  font-weight: bold;
}
```

### Progress Indicators

```jsx
{loading && (
  <div className="analysis-steps">
    <p>🔍 Stage 1: Analyzing skin condition...</p>
    {result?.stage1 && result?.stage2 && (
      <p>🔬 Stage 2: Running specialized cancer analysis...</p>
    )}
  </div>
)}
```

---

## ⚠️ Error Handling

### Common Errors

```javascript
try {
  const result = await analyze(file);
} catch (error) {
  if (error.message.includes('No image file')) {
    // User didn't upload an image
  } else if (error.message.includes('Invalid file type')) {
    // Wrong file format (only JPG, JPEG, PNG allowed)
  } else if (error.message.includes('Prediction failed')) {
    // Server error or model issue
  } else {
    // Network or other error
  }
}
```

### File Validation

```javascript
function validateImageFile(file) {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  const maxSize = 16 * 1024 * 1024; // 16MB

  if (!validTypes.includes(file.type)) {
    throw new Error('Please upload JPG, JPEG, or PNG images only');
  }

  if (file.size > maxSize) {
    throw new Error('File size must be less than 16MB');
  }

  return true;
}
```

---

## 🔐 CORS Configuration

The API already has CORS enabled for all origins. If you need to restrict it in production:

Edit `api_two_stage.py`:
```python
# Current: CORS(app)  # All origins
# Production:
CORS(app, origins=['https://your-frontend-domain.com'])
```

---

## 🧪 Testing the API

### Using cURL (Command Line)

```bash
# Health check
curl http://localhost:5000/health

# Test prediction
curl -X POST -F "image=@test_image.jpg" http://localhost:5000/predict

# With custom confidence threshold
curl -X POST -F "image=@test_image.jpg" -F "confidence_threshold=0.7" \
  http://localhost:5000/predict
```

### Using Postman

1. **Method:** POST
2. **URL:** `http://localhost:5000/predict`
3. **Body:**
   - Select "form-data"
   - Key: `image`, Type: File, Value: Select image
   - Key: `confidence_threshold`, Type: Text, Value: `0.5`
4. **Send**

---

## 📊 Sample Test Images

Test images are available in:
```
/mnt/c/Users/ashma/ai-dermatologist-assistant/ml/split_dataset/test/
```

Folders include:
- `1. Eczema 1677/`
- `2. Melanoma 15.75k/` (triggers Stage 2)
- `3. Atopic Dermatitis - 1.25k/`
- `4. Basal Cell Carcinoma (BCC) 3323/` (triggers Stage 2)
- And more...

---

## 🚨 Important Notes

### Production Deployment

1. **Security:**
   - Add authentication (JWT tokens, API keys)
   - Enable HTTPS
   - Add rate limiting
   - Validate file uploads strictly

2. **Performance:**
   - Consider using Gunicorn/uWSGI instead of Flask dev server
   - Add Redis caching for frequent predictions
   - Load balance multiple model instances

3. **Monitoring:**
   - Add logging for all predictions
   - Track accuracy metrics
   - Monitor model performance over time

### Medical Disclaimer

**CRITICAL:** Add this disclaimer prominently in your UI:

> "This AI system is for educational and informational purposes only. It is NOT a substitute for professional medical diagnosis. Always consult with a qualified dermatologist for proper evaluation of any skin condition."

---

## 📞 Support & Troubleshooting

### API Not Starting?
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Kill existing process
kill -9 <PID>

# Restart API
python api_two_stage.py
```

### Models Not Loading?
Ensure these files exist:
- `models/finetuned_model.h5`
- `models/skin_cancer_model.h5`

### Predictions Taking Too Long?
- First prediction is slow (model warmup) ~30s
- Subsequent predictions: ~2-5s
- Consider adding a loading spinner for at least 30s on first use

---

## 🎉 You're Ready!

Everything is set up and working:
- ✅ Flask API running
- ✅ Both models loaded
- ✅ CORS enabled
- ✅ Error handling in place
- ✅ Test images available

**Start the server and begin integration!**

```bash
cd /mnt/c/Users/ashma/ai-dermatologist-assistant/ml/brain_3060
source .env-wsl/bin/activate
python api_two_stage.py
```

Good luck with the frontend integration! 🚀
