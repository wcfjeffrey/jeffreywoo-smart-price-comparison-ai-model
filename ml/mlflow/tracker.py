"""
MLflow model tracking for price prediction models
"""
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import os
from datetime import datetime


class MLflowTracker:
    """MLflow-based model tracking for price prediction"""

    def __init__(self, experiment_name="price_prediction"):
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        mlflow.set_experiment(experiment_name)
        self.experiment = mlflow.get_experiment_by_name(experiment_name)

    def log_model(self, model, model_name: str, params: dict, metrics: dict):
        """Log model to MLflow"""
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            for key, value in params.items():
                mlflow.log_param(key, value)

            # Log metrics
            for key, value in metrics.items():
                mlflow.log_metric(key, value)

            # Log model
            mlflow.sklearn.log_model(model, model_name)

            # Log artifacts
            mlflow.log_artifact("data/warehouse/price_summary.parquet")

            print(f"Model logged: {model_name}")

    def train_price_prediction_model(self, data_path: str):
        """Train price prediction model and log to MLflow"""
        # Load data
        df = pd.read_parquet(data_path)

        # Prepare features
        features = ['delivery_time', 'rating', 'score']
        X = df[features].values
        y = df['price'].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Random Forest model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # Train Linear Regression model
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)

        # Evaluate models
        rf_score = rf_model.score(X_test, y_test)
        lr_score = lr_model.score(X_test, y_test)

        # Log Random Forest model
        self.log_model(
            model=rf_model,
            model_name="random_forest_price_predictor",
            params={"n_estimators": 100, "model_type": "random_forest"},
            metrics={"r2_score": rf_score, "test_size": 0.2}
        )

        # Log Linear Regression model
        self.log_model(
            model=lr_model,
            model_name="linear_regression_price_predictor",
            params={"model_type": "linear_regression"},
            metrics={"r2_score": lr_score, "test_size": 0.2}
        )

        return rf_model, lr_model

    def load_best_model(self, model_name: str):
        """Load the best model from MLflow"""
        # Find the latest run with the best metrics
        runs = mlflow.search_runs(experiment_ids=[self.experiment.experiment_id])
        best_run = runs.loc[runs['metrics.r2_score'].idxmax()]

        model_uri = f"runs:/{best_run.run_id}/{model_name}"
        model = mlflow.sklearn.load_model(model_uri)

        return model

    def compare_models(self):
        """Compare all logged models"""
        runs = mlflow.search_runs(experiment_ids=[self.experiment.experiment_id])
        print("\n=== Model Comparison ===")
        for _, run in runs.iterrows():
            print(
                f"Run: {run['run_id'][:8]} | Model: {run['tags.mlflow.runName']} | R2: {run.get('metrics.r2_score', 'N/A')}")


# Example usage
if __name__ == "__main__":
    tracker = MLflowTracker()

    # Train and log models
    rf_model, lr_model = tracker.train_price_prediction_model("data/warehouse/price_comparison.parquet")

    # Compare models
    tracker.compare_models()