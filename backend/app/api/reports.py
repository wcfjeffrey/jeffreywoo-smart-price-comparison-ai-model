from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import Response
from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import csv
import io
import os
from app.services.product_analyzer import ProductAnalyzer
import logging

router = APIRouter()
analyzer = ProductAnalyzer()
logger = logging.getLogger(__name__)


@router.post("/generate/{product_name}")
async def generate_report(product_name: str, format: str = "html"):
    """Generate a structured report for a product"""
    try:
        # Analyze product with hybrid predictions
        analysis = await analyzer.analyze_product(product_name)

        # Generate report based on format
        if format == "html":
            report = await _generate_html_report(analysis)
        elif format == "json":
            report = await _generate_json_report(analysis)
        elif format == "csv":
            report = await _generate_csv_report(analysis)
        else:
            report = await _generate_html_report(analysis)

        return {
            "status": "success",
            "product": product_name,
            "format": format,
            "report": report,
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{product_name}")
async def download_report(product_name: str, format: str = "html"):
    """Download report as file"""
    try:
        analysis = await analyzer.analyze_product(product_name)

        if format == "html":
            content = await _generate_html_report(analysis)
            media_type = "text/html"
            filename = f"{product_name}_report.html"
        elif format == "json":
            content = await _generate_json_report(analysis)
            media_type = "application/json"
            filename = f"{product_name}_report.json"
        elif format == "csv":
            content = await _generate_csv_report(analysis)
            media_type = "text/csv"
            filename = f"{product_name}_report.csv"
        else:
            content = await _generate_html_report(analysis)
            media_type = "text/html"
            filename = f"{product_name}_report.html"

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_html_report(analysis: Dict[str, Any]) -> str:
    """Generate HTML report with hybrid predictions"""

    # Get data with defaults
    product_name = analysis.get('product_name', 'Unknown')
    timestamp = analysis.get('timestamp', datetime.now().isoformat())
    best_price = analysis.get('best_supplier', {})
    price_range = analysis.get('price_range', {'min': 0, 'max': 0})
    suppliers = analysis.get('data', [])
    ranked_suppliers = analysis.get('analysis', {}).get('ranked_suppliers', [])

    # ✅ GET HYBRID PREDICTIONS
    predictions = analysis.get('predictions', {})
    ml_predictions = analysis.get('ml_predictions', {})
    hybrid_rec = analysis.get('hybrid_recommendation', {})
    risk_analysis = analysis.get('risk_analysis', {})
    recommendations = analysis.get('recommendations', [])

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Price Analysis Report - {product_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric-card {{ display: inline-block; width: 30%; margin: 1%; padding: 20px; background: #f9f9f9; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #4CAF50; }}
        .supplier-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .supplier-table th, .supplier-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .supplier-table th {{ background: #4CAF50; color: white; }}
        .risk-high {{ color: red; font-weight: bold; }}
        .risk-medium {{ color: orange; font-weight: bold; }}
        .risk-low {{ color: green; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
        .prediction-card {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Price Analysis Report: {product_name}</h1>
        <p>Generated on: {timestamp}</p>

        <div>
            <div class="metric-card">
                <div>Best Price</div>
                <div class="metric-value">${best_price.get('price', 0):.2f}</div>
                <div>from {best_price.get('supplier', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div>Price Range</div>
                <div class="metric-value">${price_range.get('min', 0):.2f} - ${price_range.get('max', 0):.2f}</div>
                <div>Across suppliers</div>
            </div>
            <div class="metric-card">
                <div>Suppliers</div>
                <div class="metric-value">{len(suppliers)}</div>
                <div>Active suppliers</div>
            </div>
        </div>

        <h2>AI-Powered Price Predictions</h2>
        <div class="prediction-card">
            <p><strong>Short-term (30 days):</strong> {predictions.get('short_term_trend', {}).get('direction', 'N/A')} ({predictions.get('short_term_trend', {}).get('change_percent', 0):.1f}%)</p>
            <p><strong>Long-term (90 days):</strong> {predictions.get('long_term_trend', {}).get('direction', 'N/A')} ({predictions.get('long_term_trend', {}).get('change_percent', 0):.1f}%)</p>
            <p><strong>Recommended Timing:</strong> {predictions.get('recommended_timing', 'N/A')}</p>
            <p><strong>AI Confidence:</strong> {predictions.get('confidence_score', 0)}%</p>
        </div>

        {ml_predictions.get('average_predicted_price', 0) > 0 and f'''
        <h2>Machine Learning Forecast</h2>
        <div class="prediction-card" style="background: #e8f5e9;">
            <p><strong>ML Predicted Price:</strong> ${ml_predictions.get('average_predicted_price', 0):.2f}</p>
            <p><strong>ML Confidence:</strong> {ml_predictions.get('confidence', 0):.0f}%</p>
            <p><strong>Model Used:</strong> {ml_predictions.get('model_used', 'N/A')}</p>
        </div>
        '''}

        {hybrid_rec.get('combined_confidence', 0) > 0 and f'''
        <h2>Hybrid AI+ML Recommendation</h2>
        <div class="recommendation">
            <p><strong>Action:</strong> {hybrid_rec.get('action', 'N/A')}</p>
            <p><strong>Recommendation:</strong> {hybrid_rec.get('recommendation', 'N/A')}</p>
            <p><strong>Combined Confidence:</strong> {hybrid_rec.get('combined_confidence', 0)}%</p>
            <p><strong>Reasoning:</strong> {hybrid_rec.get('reasoning', 'N/A')}</p>
        </div>
        '''}

        <h2>Risk Analysis</h2>
        <div class="risk-{risk_analysis.get('risk_level', 'low')}">
            <p><strong>Risk Level:</strong> {risk_analysis.get('risk_level', 'N/A').upper()}</p>
            <p><strong>Risk Score:</strong> {risk_analysis.get('risk_score', 0)}/100</p>
        </div>
        <ul>
            {''.join([f"<li>{risk.get('description', '')}</li>" for risk in risk_analysis.get('risks', [])])}
        </ul>

        <h2>Supplier Rankings</h2>
        <table class="supplier-table">
            <tr><th>Rank</th><th>Supplier</th><th>Price</th><th>Delivery (days)</th><th>Rating</th></tr>
            {''.join([f"<tr><td>{i + 1}</td><td>{s.get('supplier', 'N/A')}</td><td>${s.get('price', 0):.2f}</td><td>{s.get('delivery_time', 'N/A')}</td><td>{s.get('rating', 'N/A')}/5</td></tr>" for i, s in enumerate(ranked_suppliers)])}
        </table>

        <h2>Recommendations</h2>
        <div class="recommendation">
            <ul>
                {''.join([f"<li>{rec}</li>" for rec in recommendations])}
            </ul>
        </div>
    </div>
</body>
</html>
    """
    return html


async def _generate_json_report(analysis: Dict[str, Any]) -> str:
    """Generate JSON report with hybrid predictions"""
    report_data = {
        "product_name": analysis.get('product_name'),
        "generated_at": analysis.get('timestamp'),
        "best_price": analysis.get('best_supplier', {}),
        "price_range": analysis.get('price_range', {}),
        "suppliers": analysis.get('data', []),
        "ranked_suppliers": analysis.get('analysis', {}).get('ranked_suppliers', []),
        # ✅ Include all predictions
        "predictions": analysis.get('predictions', {}),
        "ml_predictions": analysis.get('ml_predictions', {}),
        "hybrid_recommendation": analysis.get('hybrid_recommendation', {}),
        "risk_analysis": analysis.get('risk_analysis', {}),
        "recommendations": analysis.get('recommendations', [])
    }
    return json.dumps(report_data, indent=2, default=str)


async def _generate_csv_report(analysis: Dict[str, Any]) -> str:
    """Generate CSV report with hybrid predictions"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Product info
    writer.writerow(['Product', analysis.get('product_name', 'Unknown')])
    writer.writerow(['Generated At', analysis.get('timestamp', datetime.now().isoformat())])
    writer.writerow([])

    # Best price
    best_price = analysis.get('best_supplier', {})
    writer.writerow(['Best Price', f"${best_price.get('price', 0):.2f}", f"from {best_price.get('supplier', 'N/A')}"])
    writer.writerow([])

    # Price range
    price_range = analysis.get('price_range', {})
    writer.writerow(['Price Range', f"${price_range.get('min', 0):.2f}", f"${price_range.get('max', 0):.2f}"])
    writer.writerow([])

    # ✅ AI Predictions
    predictions = analysis.get('predictions', {})
    writer.writerow(['AI Price Predictions'])
    writer.writerow(['Short-term', predictions.get('short_term_trend', {}).get('direction', 'N/A'),
                     f"{predictions.get('short_term_trend', {}).get('change_percent', 0):.1f}%"])
    writer.writerow(['Long-term', predictions.get('long_term_trend', {}).get('direction', 'N/A'),
                     f"{predictions.get('long_term_trend', {}).get('change_percent', 0):.1f}%"])
    writer.writerow(['Recommended Timing', predictions.get('recommended_timing', 'N/A')])
    writer.writerow(['AI Confidence', f"{predictions.get('confidence_score', 0)}%"])
    writer.writerow([])

    # ✅ ML Predictions
    ml = analysis.get('ml_predictions', {})
    if ml.get('average_predicted_price', 0) > 0:
        writer.writerow(['Machine Learning Forecast'])
        writer.writerow(['ML Predicted Price', f"${ml.get('average_predicted_price', 0):.2f}"])
        writer.writerow(['ML Confidence', f"{ml.get('confidence', 0):.0f}%"])
        writer.writerow(['Model Used', ml.get('model_used', 'N/A')])
        writer.writerow([])

    # ✅ Hybrid Recommendation
    hybrid = analysis.get('hybrid_recommendation', {})
    if hybrid.get('combined_confidence', 0) > 0:
        writer.writerow(['Hybrid AI+ML Recommendation'])
        writer.writerow(['Action', hybrid.get('action', 'N/A')])
        writer.writerow(['Recommendation', hybrid.get('recommendation', 'N/A')])
        writer.writerow(['Combined Confidence', f"{hybrid.get('combined_confidence', 0)}%"])
        writer.writerow(['Reasoning', hybrid.get('reasoning', 'N/A')])
        writer.writerow([])

    # Risk analysis
    risk = analysis.get('risk_analysis', {})
    writer.writerow(['Risk Analysis'])
    writer.writerow(['Risk Level', risk.get('risk_level', 'N/A')])
    writer.writerow(['Risk Score', risk.get('risk_score', 0)])
    writer.writerow([])

    # Suppliers
    ranked = analysis.get('analysis', {}).get('ranked_suppliers', [])
    writer.writerow(['Supplier Rankings'])
    writer.writerow(['Rank', 'Supplier', 'Price', 'Delivery (days)', 'Rating'])
    for i, s in enumerate(ranked):
        writer.writerow([i + 1, s.get('supplier', 'N/A'), f"${s.get('price', 0):.2f}", s.get('delivery_time', 'N/A'),
                         f"{s.get('rating', 'N/A')}/5"])
    writer.writerow([])

    # Recommendations
    writer.writerow(['Recommendations'])
    for rec in analysis.get('recommendations', []):
        writer.writerow([rec])

    return output.getvalue()