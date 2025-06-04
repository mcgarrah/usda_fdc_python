"""
Visualization utilities for nutrient analysis.
"""

from typing import Dict, List, Any, Optional

from .analysis import NutrientAnalysis

def generate_macronutrient_chart_data(analysis: NutrientAnalysis) -> Dict[str, Any]:
    """
    Generate data for a macronutrient distribution chart.
    
    Args:
        analysis: The nutrient analysis.
        
    Returns:
        A dictionary with chart data.
    """
    return {
        "type": "pie",
        "data": {
            "labels": ["Protein", "Carbohydrates", "Fat"],
            "datasets": [{
                "data": [
                    analysis.macronutrient_distribution.get("protein", 0),
                    analysis.macronutrient_distribution.get("carbs", 0),
                    analysis.macronutrient_distribution.get("fat", 0)
                ],
                "backgroundColor": [
                    "#FF6384",
                    "#36A2EB",
                    "#FFCE56"
                ]
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": "Macronutrient Distribution"
            }
        }
    }

def generate_dri_chart_data(analysis: NutrientAnalysis) -> Dict[str, Any]:
    """
    Generate data for a DRI comparison chart.
    
    Args:
        analysis: The nutrient analysis.
        
    Returns:
        A dictionary with chart data.
    """
    # Collect nutrients with DRI values
    nutrients_with_dri = [
        (nutrient_id, value)
        for nutrient_id, value in analysis.nutrients.items()
        if value.dri_percent is not None
    ]
    
    # Sort by DRI percentage
    nutrients_with_dri.sort(key=lambda x: x[1].dri_percent or 0, reverse=True)
    
    # Take top 10
    top_nutrients = nutrients_with_dri[:10]
    
    return {
        "type": "horizontalBar",
        "data": {
            "labels": [value.nutrient.name for _, value in top_nutrients],
            "datasets": [{
                "label": "% of DRI",
                "data": [value.dri_percent for _, value in top_nutrients],
                "backgroundColor": "#36A2EB"
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": "Nutrient Content (% of DRI)"
            },
            "scales": {
                "xAxes": [{
                    "ticks": {
                        "beginAtZero": True
                    }
                }]
            }
        }
    }

def generate_html_report(analysis: NutrientAnalysis) -> str:
    """
    Generate an HTML report for a nutrient analysis.
    
    Args:
        analysis: The nutrient analysis.
        
    Returns:
        An HTML string.
    """
    # Generate chart data
    macro_chart = generate_macronutrient_chart_data(analysis)
    dri_chart = generate_dri_chart_data(analysis)
    
    # Convert chart data to JSON strings
    import json
    macro_chart_json = json.dumps(macro_chart)
    dri_chart_json = json.dumps(dri_chart)
    
    # Create HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nutrient Analysis: {analysis.food.description}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .chart-container {{ width: 100%; height: 400px; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Nutrient Analysis: {analysis.food.description}</h1>
            <p>Serving Size: {analysis.serving_size}g</p>
            
            <h2>Macronutrients</h2>
            <table>
                <tr>
                    <th>Nutrient</th>
                    <th>Amount</th>
                    <th>% of Calories</th>
                </tr>
                <tr>
                    <td>Calories</td>
                    <td>{analysis.calories_per_serving:.1f} kcal</td>
                    <td>100%</td>
                </tr>
                <tr>
                    <td>Protein</td>
                    <td>{analysis.protein_per_serving:.1f} g</td>
                    <td>{analysis.macronutrient_distribution.get("protein", 0):.1f}%</td>
                </tr>
                <tr>
                    <td>Carbohydrates</td>
                    <td>{analysis.carbs_per_serving:.1f} g</td>
                    <td>{analysis.macronutrient_distribution.get("carbs", 0):.1f}%</td>
                </tr>
                <tr>
                    <td>Fat</td>
                    <td>{analysis.fat_per_serving:.1f} g</td>
                    <td>{analysis.macronutrient_distribution.get("fat", 0):.1f}%</td>
                </tr>
            </table>
            
            <div class="chart-container">
                <canvas id="macroChart"></canvas>
            </div>
            
            <h2>Nutrient Content</h2>
            <div class="chart-container">
                <canvas id="driChart"></canvas>
            </div>
            
            <h2>Detailed Nutrients</h2>
            <table>
                <tr>
                    <th>Nutrient</th>
                    <th>Amount</th>
                    <th>% of DRI</th>
                </tr>
    """
    
    # Add nutrient rows
    for nutrient_id, value in sorted(
        analysis.nutrients.items(),
        key=lambda x: x[1].dri_percent or 0,
        reverse=True
    ):
        dri_percent = f"{value.dri_percent:.1f}%" if value.dri_percent is not None else "N/A"
        html += f"""
                <tr>
                    <td>{value.nutrient.name}</td>
                    <td>{value.amount:.1f} {value.unit}</td>
                    <td>{dri_percent}</td>
                </tr>
        """
    
    # Close the table and add chart initialization
    html += f"""
            </table>
        </div>
        
        <script>
            // Initialize macronutrient chart
            var macroCtx = document.getElementById('macroChart').getContext('2d');
            var macroChart = new Chart(macroCtx, {macro_chart_json});
            
            // Initialize DRI chart
            var driCtx = document.getElementById('driChart').getContext('2d');
            var driChart = new Chart(driCtx, {dri_chart_json});
        </script>
    </body>
    </html>
    """
    
    return html