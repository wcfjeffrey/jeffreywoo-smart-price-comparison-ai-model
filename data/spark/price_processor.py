"""
Apache Spark data processing for price comparison data
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, min, max, stddev, when, lit, count, rank
from pyspark.sql.window import Window
from datetime import datetime

class PriceDataProcessor:
    """Spark-based data processing for price analysis"""

    def __init__(self, app_name="PriceComparisonProcessor"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")

    def load_from_warehouse(self, table_name: str):
        """Load data from warehouse"""
        file_path = f"data/warehouse/{table_name}.parquet"
        if os.path.exists(file_path):
            return self.spark.read.parquet(file_path)
        return None

    def process_supplier_rankings(self, df):
        """Process supplier rankings"""
        return df.groupBy("supplier") \
            .agg(
                avg("price").alias("avg_price"),
                avg("rating").alias("avg_rating"),
                avg("delivery_time").alias("avg_delivery"),
                count("product_name").alias("product_count")
            ) \
            .withColumn("score",
                (1000 / col("avg_price")) +
                (30 / col("avg_delivery")) +
                (col("avg_rating") * 20)
            ) \
            .withColumn("rank", rank().over(Window.orderBy(col("score").desc())))

    def detect_market_anomalies(self, df, threshold=2.5):
        """Detect market-wide anomalies"""
        stats = df.groupBy("product_name") \
            .agg(
                avg("price").alias("mean_price"),
                stddev("price").alias("stddev_price")
            )

        joined = df.join(stats, "product_name")

        return joined.withColumn(
            "is_anomaly",
            (col("price") > col("mean_price") + threshold * col("stddev_price")) |
            (col("price") < col("mean_price") - threshold * col("stddev_price"))
        ).filter(col("is_anomaly") == True)

    def generate_daily_report(self, df):
        """Generate daily price report"""
        from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

        # Calculate daily aggregates
        daily_stats = df.groupBy("product_name") \
            .agg(
                avg("price").alias("avg_daily_price"),
                min("price").alias("min_price"),
                max("price").alias("max_price"),
                count("supplier").alias("supplier_count")
            )

        # Save results
        output_path = f"data/warehouse/daily_report_{datetime.now().strftime('%Y%m%d')}"
        daily_stats.write.mode("overwrite").parquet(output_path)

        return daily_stats

    def stop(self):
        """Stop Spark session"""
        self.spark.stop()

# Example usage
if __name__ == "__main__":
    processor = PriceDataProcessor()

    # Load data from warehouse
    df = processor.load_from_warehouse("price_comparison")

    if df:
        # Process supplier rankings
        rankings = processor.process_supplier_rankings(df)
        rankings.show()

        # Detect anomalies
        anomalies = processor.detect_market_anomalies(df)
        print(f"Anomalies detected: {anomalies.count()}")

        # Generate report
        report = processor.generate_daily_report(df)

    processor.stop()