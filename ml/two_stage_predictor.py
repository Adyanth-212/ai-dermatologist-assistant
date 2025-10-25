"""
Two-Stage Skin Disease Classification System

Stage 1: General classifier identifies if it's cancer-related
Stage 2: If cancer detected, specialized model provides detailed analysis
"""

import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
import json
from pathlib import Path

class TwoStagePredictor:
    """
    Two-stage skin disease prediction system
    """
    
    def __init__(self, 
                 stage1_model_path='models/finetuned_model.h5',
                 stage2_model_path='models/skin_cancer_model.h5'):
        """
        Initialize both models
        
        Args:
            stage1_model_path: Path to general skin disease classifier
            stage2_model_path: Path to specialized cancer classifier
        """
        print("🔧 Loading Two-Stage Prediction System...")
        
        # Load Stage 1 model (general classifier)
        print(f"📦 Loading Stage 1 model: {stage1_model_path}")
        self.stage1_model = load_model(stage1_model_path)
        
        # Load Stage 2 model (cancer specialist)
        print(f"📦 Loading Stage 2 model: {stage2_model_path}")
        self.stage2_model = load_model(stage2_model_path)
        
        # Define class mappings for Stage 1 (10 general classes)
        self.stage1_classes = {
            0: '1. Eczema 1677',
            1: '10. Warts Molluscum and other Viral Infections - 2103',
            2: '2. Melanoma 15.75k',
            3: '3. Atopic Dermatitis - 1.25k',
            4: '4. Basal Cell Carcinoma (BCC) 3323',
            5: '5. Melanocytic Nevi (NV) - 7970',
            6: '6. Benign Keratosis-like Lesions (BKL) 2624',
            7: '7. Psoriasis pictures Lichen Planus and related diseases - 2k',
            8: '8. Seborrheic Keratoses and other Benign Tumors - 1.8k',
            9: '9. Tinea Ringworm Candidiasis and other Fungal Infections - 1.7k'
        }
        
        # Cancer-related classes from Stage 1 (indices that trigger Stage 2)
        self.cancer_classes = [2, 4, 5, 6, 8]  # Melanoma, BCC, Nevi, BKL, Seborrheic
        
        # Define class mappings for Stage 2 (cancer types)
        # Adjust these based on your actual cancer model's classes
        self.stage2_classes = {
            0: 'Melanoma (Malignant)',
            1: 'Basal Cell Carcinoma',
            2: 'Squamous Cell Carcinoma',
            3: 'Benign Nevus',
            4: 'Seborrheic Keratosis',
            5: 'Actinic Keratosis',
            6: 'Dermatofibroma',
            7: 'Vascular Lesion'
        }
        
        print("✅ Two-Stage Prediction System Ready!")
        print(f"   Stage 1: {len(self.stage1_classes)} general disease classes")
        print(f"   Stage 2: {len(self.stage2_classes)} specialized cancer classes")
        print()
    
    def preprocess_image(self, img_path, target_size=(224, 224)):
        """
        Preprocess image for prediction
        
        Args:
            img_path: Path to image file
            target_size: Target size for model input
            
        Returns:
            Preprocessed image array
        """
        img = image.load_img(img_path, target_size=target_size)
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        return img_array
    
    def predict(self, img_path, confidence_threshold=0.5):
        """
        Two-stage prediction process
        
        Args:
            img_path: Path to image file
            confidence_threshold: Minimum confidence to trigger Stage 2
            
        Returns:
            Dictionary with prediction results
        """
        print(f"\n{'='*70}")
        print(f"🔍 ANALYZING IMAGE: {Path(img_path).name}")
        print(f"{'='*70}")
        
        # ========== STAGE 1: General Classification ==========
        print("\n📊 STAGE 1: General Skin Disease Classification")
        print("-" * 70)
        
        img_processed = self.preprocess_image(img_path)
        stage1_predictions = self.stage1_model.predict(img_processed, verbose=0)[0]
        
        # Get top 3 predictions from Stage 1
        top3_indices = np.argsort(stage1_predictions)[-3:][::-1]
        
        print("\nTop 3 Predictions:")
        for i, idx in enumerate(top3_indices, 1):
            class_name = self.stage1_classes[idx]
            confidence = stage1_predictions[idx] * 100
            print(f"  {i}. {class_name}: {confidence:.2f}%")
        
        # Primary prediction
        primary_class_idx = top3_indices[0]
        primary_class = self.stage1_classes[primary_class_idx]
        primary_confidence = stage1_predictions[primary_class_idx]
        
        result = {
            'stage1': {
                'class': primary_class,
                'class_index': int(primary_class_idx),
                'confidence': float(primary_confidence),
                'all_probabilities': {self.stage1_classes[i]: float(stage1_predictions[i]) 
                                     for i in range(len(self.stage1_classes))},
                'top3': [(self.stage1_classes[idx], float(stage1_predictions[idx])) 
                        for idx in top3_indices]
            },
            'stage2': None,
            'recommendation': None
        }
        
        # ========== STAGE 2: Specialized Cancer Analysis ==========
        if primary_class_idx in self.cancer_classes and primary_confidence >= confidence_threshold:
            print(f"\n⚠️  CANCER-RELATED CONDITION DETECTED!")
            print(f"   Triggering Stage 2: Specialized Cancer Analysis")
            print("\n📊 STAGE 2: Detailed Cancer Classification")
            print("-" * 70)
            
            stage2_predictions = self.stage2_model.predict(img_processed, verbose=0)[0]
            
            # Get top 3 predictions from Stage 2
            top3_stage2 = np.argsort(stage2_predictions)[-3:][::-1]
            
            print("\nDetailed Cancer Analysis:")
            for i, idx in enumerate(top3_stage2, 1):
                class_name = self.stage2_classes.get(idx, f'Class {idx}')
                confidence = stage2_predictions[idx] * 100
                malignancy_indicator = "⚠️  MALIGNANT" if 'malignant' in class_name.lower() or 'melanoma' in class_name.lower() else "✓ Likely Benign"
                print(f"  {i}. {class_name}: {confidence:.2f}% {malignancy_indicator}")
            
            stage2_class_idx = top3_stage2[0]
            stage2_class = self.stage2_classes.get(stage2_class_idx, f'Class {stage2_class_idx}')
            stage2_confidence = stage2_predictions[stage2_class_idx]
            
            result['stage2'] = {
                'class': stage2_class,
                'class_index': int(stage2_class_idx),
                'confidence': float(stage2_confidence),
                'all_probabilities': {self.stage2_classes.get(i, f'Class {i}'): float(stage2_predictions[i]) 
                                     for i in range(len(stage2_predictions))},
                'top3': [(self.stage2_classes.get(idx, f'Class {idx}'), float(stage2_predictions[idx])) 
                        for idx in top3_stage2]
            }
            
            # Generate recommendation based on both stages
            if 'melanoma' in stage2_class.lower() or 'malignant' in stage2_class.lower():
                severity = "HIGH"
                action = "URGENT: Immediate dermatologist consultation required"
            elif 'carcinoma' in stage2_class.lower():
                severity = "MEDIUM-HIGH"
                action = "Schedule appointment with dermatologist within 1-2 weeks"
            else:
                severity = "LOW-MEDIUM"
                action = "Recommend dermatologist check-up for confirmation"
            
            result['recommendation'] = {
                'severity': severity,
                'action': action,
                'details': f"Stage 1 identified {primary_class} with {primary_confidence*100:.1f}% confidence. "
                          f"Stage 2 refined diagnosis to {stage2_class} with {stage2_confidence*100:.1f}% confidence."
            }
            
        else:
            # Non-cancer condition
            print(f"\n✅ NON-CANCEROUS CONDITION")
            print(f"   Stage 2 analysis not required")
            
            if 'eczema' in primary_class.lower() or 'atopic' in primary_class.lower():
                severity = "LOW"
                action = "Consider over-the-counter moisturizers and anti-itch creams"
            elif 'psoriasis' in primary_class.lower():
                severity = "MEDIUM"
                action = "Dermatologist consultation recommended for treatment plan"
            elif 'infection' in primary_class.lower():
                severity = "MEDIUM"
                action = "May require antifungal/antiviral treatment - see doctor if persists"
            else:
                severity = "LOW-MEDIUM"
                action = "Monitor condition, consult dermatologist if worsens"
            
            result['recommendation'] = {
                'severity': severity,
                'action': action,
                'details': f"Identified as {primary_class} with {primary_confidence*100:.1f}% confidence. "
                          f"This is typically a non-cancerous skin condition."
            }
        
        # ========== FINAL SUMMARY ==========
        print(f"\n{'='*70}")
        print("📋 FINAL DIAGNOSIS SUMMARY")
        print(f"{'='*70}")
        print(f"\n🎯 Primary Diagnosis: {result['stage1']['class']}")
        print(f"   Confidence: {result['stage1']['confidence']*100:.2f}%")
        
        if result['stage2']:
            print(f"\n🔬 Refined Cancer Analysis: {result['stage2']['class']}")
            print(f"   Confidence: {result['stage2']['confidence']*100:.2f}%")
        
        print(f"\n⚠️  Severity Level: {result['recommendation']['severity']}")
        print(f"💡 Recommendation: {result['recommendation']['action']}")
        print(f"\n📝 Details: {result['recommendation']['details']}")
        print(f"\n{'='*70}\n")
        
        return result
    
    def predict_batch(self, image_paths, confidence_threshold=0.5):
        """
        Predict multiple images
        
        Args:
            image_paths: List of image file paths
            confidence_threshold: Minimum confidence to trigger Stage 2
            
        Returns:
            List of prediction results
        """
        results = []
        for img_path in image_paths:
            result = self.predict(img_path, confidence_threshold)
            results.append(result)
        return results


def main():
    """
    Example usage of Two-Stage Predictor
    """
    # Initialize predictor
    predictor = TwoStagePredictor(
        stage1_model_path='models/finetuned_model.h5',
        stage2_model_path='models/skin_cancer_model.h5'
    )
    
    # Example: Predict single image
    # Uncomment and replace with your image path
    # result = predictor.predict('path/to/your/test/image.jpg')
    
    # Save result as JSON
    # with open('prediction_result.json', 'w') as f:
    #     json.dump(result, f, indent=2)
    
    print("💡 To use this predictor:")
    print("   1. Import: from two_stage_predictor import TwoStagePredictor")
    print("   2. Initialize: predictor = TwoStagePredictor()")
    print("   3. Predict: result = predictor.predict('image.jpg')")
    print()


if __name__ == "__main__":
    main()
