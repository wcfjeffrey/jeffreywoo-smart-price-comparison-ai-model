"""
Price Prediction Model using scikit-learn (no TensorFlow)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os


def create_price_prediction_model():
    """Create and train a price prediction model"""
    print("Training price prediction model (scikit-learn)...")

    # Generate sample training data
    np.random.seed(42)
    n_samples = 2000

    # Features:
    # 1. Historical average price
    # 2. Price volatility
    # 3. Seasonality factor
    # 4. Demand indicator
    # 5. Competitor average price
    # 6. Economic indicator

    historical_avg = np.random.normal(500, 100, n_samples)
    volatility = np.random.exponential(20, n_samples)
    seasonality = np.sin(np.linspace(0, 4 * np.pi, n_samples)) * 50 + np.random.normal(0, 10, n_samples)
    demand = np.random.normal(100, 30, n_samples)
    competitor_avg = np.random.normal(480, 80, n_samples)
    economic_indicator = np.random.normal(0, 1, n_samples)

    X = np.column_stack([
        historical_avg,
        volatility,
        seasonality,
        demand,
        competitor_avg,
        economic_indicator
    ])

    # Target: next month's price
    y = (historical_avg * 0.6 +
         competitor_avg * 0.3 +
         seasonality * 0.1 +
         np.random.normal(0, 30, n_samples))

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model Performance:")
    print(f"  RMSE: ${np.sqrt(mse):.2f}")
    print(f"  R² Score: {r2:.4f}")

    # Save model and scaler
    model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'price_prediction_rf.joblib')
    scaler_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'price_scaler.joblib')

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"\n✅ Model saved to: {model_path}")

    return model, scaler


def predict_price(model, scaler, features):
    """Predict price using trained model"""
    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)
    return prediction[0]


if __name__ == "__main__":
    create_price_prediction_model()