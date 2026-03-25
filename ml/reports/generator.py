"""
ML report generation for price analysis
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import json
import mlflow


class MLReportGenerator:
    """Generate ML-based reports for price analysis"""

    def __init__(self, output_dir="ml/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_model_performance_report(self, model_metrics: dict):
        """Generate model performance report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.output_dir}/model_performance_{timestamp}.html"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Model Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .good {{ color: green; }}
                .medium {{ color: orange; }}
                .poor {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Model Performance Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>Model Metrics</h2>
            <table>
                <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
        """

        for metric, value in model_metrics.items():
            status = "good" if value > 0.8 else "medium" if value > 0.6 else "poor"
            html_content += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{value:.4f}</td>
                    <td class="{status}">{status.upper()}</td>
                </tr>
            """

        html_content += """
            </table>
        </body>
        </html>
        """

        with open(report_path, 'w') as f:
            f.write(html_content)

        return report_path

    def generate_prediction_report(self, predictions: list):
        """Generate prediction report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.output_dir}/predictions_{timestamp}.json"

        with open(report_path, 'w') as f:
            json.dump(predictions, f, indent=2)

        return report_path

    def generate_anomaly_report(self, anomalies: list):
        """Generate anomaly detection report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"{self.output_dir}/anomalies_{timestamp}.csv"

        df = pd.DataFrame(anomalies)
        df.to_csv(report_path, index=False)

        return report_path

    def create_performance_chart(self, historical_metrics: dict):
        """Create performance chart"""
        fig, ax = plt.subplots(figsize=(10, 6))

        dates = list(historical_metrics.keys())
        scores = list(historical_metrics.values())

        ax.plot(dates, scores, marker='o', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Model Score')
        ax.set_title('Model Performance Over Time')
        ax.grid(True, alpha=0.3)

        plt.xticks(rotation=45)
        plt.tight_layout()

        chart_path = f"{self.output_dir}/performance_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=100)
        plt.close()

        return chart_path


# Example usage
if __name__ == "__main__":
    reporter = MLReportGenerator()

    # Generate test report
    metrics = {
        "r2_score": 0.85,
        "mae": 45.2,
        "rmse": 58.7,
        "mape": 0.12
    }

    report_path = reporter.generate_model_performance_report(metrics)
    print(f"Report generated: {report_path}")