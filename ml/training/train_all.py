"""
Unified training script for all ML models (scikit-learn only)
"""

import os
import sys

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("Training ML Models for Price Comparison System")
    print("=" * 60)

    # Create models directory
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)

    # Train price prediction
    print("\n" + "-" * 40)
    print("1. Training Price Prediction Model...")
    print("-" * 40)
    try:
        from price_prediction_sklearn import create_price_prediction_model
        create_price_prediction_model()
        print("✅ Price prediction model trained successfully")
    except Exception as e:
        print(f"❌ Error training price prediction model: {e}")
        import traceback
        traceback.print_exc()

    # Train anomaly detection
    print("\n" + "-" * 40)
    print("2. Training Anomaly Detection Model...")
    print("-" * 40)
    try:
        from anomaly_detection_sklearn import train_anomaly_detection
        train_anomaly_detection()
        print("✅ Anomaly detection model trained successfully")
    except Exception as e:
        print(f"❌ Error training anomaly detection model: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"Models saved to: {models_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()