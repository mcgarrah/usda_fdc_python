"""
Visualization tools for nutrient analysis.

This module provides functions for visualizing nutrient data, including
macronutrient distribution, nutrient comparison, and DRI percentages.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
import json

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
            "labels": ["Protein", "Fat", "Carbohydrate"],
            "datasets": [{
                "data": [
                    analysis.macronutrient_distribution.get("protein", 0),
                    analysis.macronutrient_distribution.get("fat", 0),
                    analysis.macronutrient_distribution.get("carbohydrate", 0)
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
                "text": f"Macronutrient Distribution for {analysis.food.description}"
            }
        }
    }


def generate_dri_chart_data(
    analysis: NutrientAnalysis,
    nutrient_ids: Optional[List[str]] = None,
    min_percent: float = 1.0
) -> Dict[str, Any]:
    """
    Generate data for a DRI percentage chart.
    
    Args:
        analysis: The nutrient analysis.
        nutrient_ids: The nutrient IDs to include (all with DRI values if None).
        min_percent: The minimum DRI percentage to include.
        
    Returns:
        A dictionary with chart data.
    """
    # Get nutrients with DRI values
    nutrients_with_dri = {
        nutrient_id: value
        for nutrient_id, value in analysis.nutrients.items()
        if value.dri_percent is not None and value.dri_percent >= min_percent
    }
    
    # Filter by nutrient_ids if provided
    if nutrient_ids is not None:
        nutrients_with_dri = {
            nutrient_id: value
            for nutrient_id, value in nutrients_with_dri.items()
            if nutrient_id in nutrient_ids
        }
    
    # Sort by DRI percentage
    sorted_nutrients = sorted(
        nutrients_with_dri.items(),
        key=lambda x: x[1].dri_percent or 0,
        reverse=True
    )
    
    # Generate chart data
    labels = [value.nutrient.display_name for _, value in sorted_nutrients]
    data = [value.dri_percent or 0 for _, value in sorted_nutrients]
    
    return {
        "type": "horizontalBar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": "% of DRI",
                "data": data,
                "backgroundColor": "rgba(54, 162, 235, 0.5)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": f"DRI Percentages for {analysis.food.description}"
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


def generate_nutrient_comparison_chart_data(
    analyses: List[NutrientAnalysis],
    nutrient_id: str
) -> Dict[str, Any]:
    """
    Generate data for a nutrient comparison chart.
    
    Args:
        analyses: The nutrient analyses to compare.
        nutrient_id: The nutrient ID to compare.
        
    Returns:
        A dictionary with chart data.
    """
    # Get the nutrient values for each food
    labels = []
    data = []
    
    for analysis in analyses:
        nutrient_value = analysis.get_nutrient(nutrient_id)
        if nutrient_value:
            labels.append(analysis.food.description)
            data.append(nutrient_value.amount)
    
    # Get the nutrient display name
    nutrient_name = "Unknown"
    for analysis in analyses:
        nutrient_value = analysis.get_nutrient(nutrient_id)
        if nutrient_value:
            nutrient_name = nutrient_value.nutrient.display_name
            break
    
    return {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": f"{nutrient_name} Content",
                "data": data,
                "backgroundColor": "rgba(75, 192, 192, 0.5)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": f"{nutrient_name} Comparison"
            },
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": True
                    }
                }]
            }
        }
    }


def generate_nutrient_radar_chart_data(
    analysis: NutrientAnalysis,
    nutrient_ids: List[str]
) -> Dict[str, Any]:
    """
    Generate data for a nutrient radar chart.
    
    Args:
        analysis: The nutrient analysis.
        nutrient_ids: The nutrient IDs to include.
        
    Returns:
        A dictionary with chart data.
    """
    # Get the nutrient values
    labels = []
    data = []
    
    for nutrient_id in nutrient_ids:
        nutrient_value = analysis.get_nutrient(nutrient_id)
        if nutrient_value and nutrient_value.dri_percent is not None:
            labels.append(nutrient_value.nutrient.display_name)
            # Cap at 100% for better visualization
            data.append(min(nutrient_value.dri_percent, 100))
    
    return {
        "type": "radar",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": analysis.food.description,
                "data": data,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgba(54, 162, 235, 1)"
            }]
        },
        "options": {
            "title": {
                "display": True,
                "text": f"Nutrient Profile for {analysis.food.description}"
            },
            "scale": {
                "ticks": {
                    "beginAtZero": True,
                    "max": 100
                }
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
    macro_chart_data = generate_macronutrient_chart_data(analysis)
    dri_chart_data = generate_dri_chart_data(analysis)
    
    # Convert chart data to JSON
    macro_chart_json = json.dumps(macro_chart_data)
    dri_chart_json = json.dumps(dri_chart_data)
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nutrient Analysis: {analysis.food.description}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .chart-container {{ width: 100%; max-width: 600px; margin: 20px auto; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Nutrient Analysis: {analysis.food.description}</h1>
            <p>FDC ID: {analysis.food.fdc_id}</p>
            <p>Data Type: {analysis.food.data_type}</p>
            <p>Serving Size: {analysis.serving_size}g</p>
            <p>Calories: {analysis.calories_per_serving:.1f} kcal</p>
            
            <h2>Macronutrient Distribution</h2>
            <div class="chart-container">
                <canvas id="macroChart"></canvas>
            </div>
            
            <h2>Nutrient Content</h2>
            <div class="chart-container">
                <canvas id="driChart"></canvas>
            </div>
            
            <h2>Detailed Nutrient Information</h2>
            <table>
                <tr>
                    <th>Nutrient</th>
                    <th>Amount</th>
                    <th>% of DRI</th>
                </tr>
    """
    
    # Add macronutrients
    html += "<tr><th colspan='3'>Macronutrients</th></tr>"
    for nutrient_id in ["protein", "fat", "carbohydrate", "fiber"]:
        nutrient_value = analysis.get_nutrient(nutrient_id)
        if nutrient_value:
            dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
            html += f"""
                <tr>
                    <td>{nutrient_value.nutrient.display_name}</td>
                    <td>{nutrient_value.amount:.1f} {nutrient_value.unit}</td>
                    <td>{dri_percent}</td>
                </tr>
            """
    
    # Add vitamins
    html += "<tr><th colspan='3'>Vitamins</th></tr>"
    for nutrient_id, nutrient_value in analysis.get_vitamins().items():
        dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
        html += f"""
            <tr>
                <td>{nutrient_value.nutrient.display_name}</td>
                <td>{nutrient_value.amount:.1f} {nutrient_value.unit}</td>
                <td>{dri_percent}</td>
            </tr>
        """
    
    # Add minerals
    html += "<tr><th colspan='3'>Minerals</th></tr>"
    for nutrient_id, nutrient_value in analysis.get_minerals().items():
        dri_percent = f"{nutrient_value.dri_percent:.1f}%" if nutrient_value.dri_percent is not None else "N/A"
        html += f"""
            <tr>
                <td>{nutrient_value.nutrient.display_name}</td>
                <td>{nutrient_value.amount:.1f} {nutrient_value.unit}</td>
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