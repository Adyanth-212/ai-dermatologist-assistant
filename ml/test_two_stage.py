"""
Test script for Two-Stage Predictor
"""

from two_stage_predictor import TwoStagePredictor
import sys
from pathlib import Path

def test_predictor(image_path):
    """
    Test the two-stage predictor with a sample image
    """
    # Initialize predictor
    print("Initializing Two-Stage Prediction System...")
    predictor = TwoStagePredictor(
        stage1_model_path='models/finetuned_model.h5',
        stage2_model_path='models/skin_cancer_model.h5'
    )
    
    # Make prediction
    result = predictor.predict(image_path, confidence_threshold=0.5)
    
    # Return result
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_two_stage.py <path_to_image>")
        print("\nExample:")
        print("  python test_two_stage.py ../split_dataset/test/2.\\ Melanoma\\ 15.75k/sample.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ Error: Image not found at {image_path}")
        sys.exit(1)
    
    result = test_predictor(image_path)
    
    print("\n✅ Prediction complete! Result saved to prediction_result.json")
