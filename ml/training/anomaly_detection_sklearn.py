"""
Anomaly Detection Model using scikit-learn
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_anomaly_detection():
    """Train anomaly detection model using Isolation Forest"""
    print("Training anomaly detection model...")

    # Generate sample training data
    np.random.seed(42)
    n_samples = 5000

    # Features:
    # 1. Price
    # 2. Delivery time
    # 3. Rating
    # 4. Market average price
    # 5. Price volatility (historical)

    # Normal data
    price = np.random.normal(500, 100, n_samples)
    delivery_time = np.random.poisson(5, n_samples)
    rating = np.random.uniform(3, 5, n_samples)
    market_avg = np.random.normal(500, 50, n_samples)
    price_volatility = np.random.exponential(15, n_samples)

    X = np.column_stack([price, delivery_time, rating, market_avg, price_volatility])

    # Add anomalies (5% of data)
    n_anomalies = int(n_samples * 0.05)
    anomaly_indices = np.random.choice(n_samples, n_anomalies, replace=False)

    # Anomaly patterns:
    # - Price spike (2x normal)
    # - Extremely long delivery
    # - Very low rating
    X[anomaly_indices[:n_anomalies//3], 0] += np.random.normal(400, 100, n_anomalies//3)
    X[anomaly_indices[n_anomalies//3:2*n_anomalies//3], 1] += np.random.poisson(20, n_anomalies//3)
    X[anomaly_indices[2*n_anomalies//3:], 2] -= np.random.uniform(2, 3, n_anomalies - 2*n_anomalies//3)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest
    model = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )
    model.fit(X_scaled)

    # Calculate threshold
    anomaly_scores = model.decision_function(X_scaled)
    threshold = np.percentile(anomaly_scores, 5)

    # Save model and scaler
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'anomaly_detection_if.joblib')
    scaler_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'anomaly_scaler.joblib')
    threshold_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'anomaly_threshold.npy')

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    np.save(threshold_path, threshold)

    # Test detection rate
    predictions = model.predict(X_scaled)
    detected_anomalies = np.sum(predictions[anomaly_indices] == -1)
    detection_rate = detected_anomalies / n_anomalies * 100

    print(f"Model Performance:")
    print(f"  Anomaly detection rate: {detection_rate:.1f}%")
    print(f"  Anomaly threshold: {threshold:.4f}")

    print(f"\n✅ Model saved to: {model_path}")

    return model, scaler, threshold

def detect_anomalies(model, scaler, data, threshold):
    """Detect anomalies in new data"""
    data_scaled = scaler.transform(data)
    scores = model.decision_function(data_scaled)
    predictions = model.predict(data_scaled)

    anomalies = []
    for i, (score, pred) in enumerate(zip(scores, predictions)):
        if pred == -1 or score < threshold:
            anomalies.append({
                'index': i,
                'anomaly_score': float(score),
                'severity': 'high' if score < threshold * 0.8 else 'medium'
            })

    return anomalies

if __name__ == "__main__":
    train_anomaly_detection()