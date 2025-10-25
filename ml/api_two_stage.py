"""
Flask API for Two-Stage Skin Disease Prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from two_stage_predictor import TwoStagePredictor
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize predictor (load models once at startup)
print("🚀 Initializing Two-Stage Prediction System...")
predictor = TwoStagePredictor(
    stage1_model_path='models/finetuned_model.h5',
    stage2_model_path='models/skin_cancer_model.h5'
)
print("✅ API Ready!\n")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Two-Stage Skin Disease Predictor',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Expects:
        - image file in request.files['image']
        - optional: confidence_threshold in request.form
    
    Returns:
        JSON with prediction results
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'message': 'Please upload an image file with key "image"'
            }), 400
        
        file = request.files['image']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Get confidence threshold (optional)
        confidence_threshold = float(request.form.get('confidence_threshold', 0.5))
        
        # Make prediction
        print(f"\n📸 Processing: {unique_filename}")
        result = predictor.predict(filepath, confidence_threshold)
        
        # Add metadata
        result['metadata'] = {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'confidence_threshold': confidence_threshold
        }
        
        # Optionally delete uploaded file after prediction
        # os.remove(filepath)
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint
    
    Expects:
        - Multiple image files in request.files
    
    Returns:
        JSON array with prediction results
    """
    try:
        files = request.files.getlist('images')
        
        if not files or len(files) == 0:
            return jsonify({
                'error': 'No images provided',
                'message': 'Please upload one or more image files with key "images"'
            }), 400
        
        results = []
        confidence_threshold = float(request.form.get('confidence_threshold', 0.5))
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                # Predict
                result = predictor.predict(filepath, confidence_threshold)
                result['metadata'] = {
                    'filename': filename,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
                
                # Optionally delete file
                # os.remove(filepath)
        
        return jsonify({
            'count': len(results),
            'results': results
        }), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'error': 'Batch prediction failed',
            'message': str(e)
        }), 500


@app.route('/info', methods=['GET'])
def info():
    """
    Get information about the prediction system
    """
    return jsonify({
        'service': 'Two-Stage Skin Disease Predictor',
        'version': '1.0',
        'description': 'AI-powered skin disease classification with specialized cancer analysis',
        'stages': {
            'stage1': {
                'name': 'General Skin Disease Classifier',
                'classes': list(predictor.stage1_classes.values()),
                'description': 'Identifies general skin condition category'
            },
            'stage2': {
                'name': 'Specialized Cancer Classifier',
                'classes': list(predictor.stage2_classes.values()),
                'description': 'Provides detailed cancer analysis when cancer-related condition detected',
                'triggers': [predictor.stage1_classes[i] for i in predictor.cancer_classes]
            }
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'endpoints': {
            '/health': 'Health check',
            '/predict': 'Single image prediction (POST)',
            '/predict/batch': 'Batch image prediction (POST)',
            '/info': 'API information (GET)'
        }
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Two-Stage Skin Disease Prediction API")
    print("="*70)
    print("\n📡 Endpoints:")
    print("   GET  /health         - Health check")
    print("   POST /predict        - Single image prediction")
    print("   POST /predict/batch  - Batch prediction")
    print("   GET  /info           - API information")
    print("\n💡 Example usage:")
    print('   curl -X POST -F "image=@test.jpg" http://localhost:5000/predict')
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
