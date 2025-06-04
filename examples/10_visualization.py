#!/usr/bin/env python3
"""
Example of visualizing nutrient data using the USDA FDC API.

This script demonstrates how to create visualizations of nutrient data,
including charts and HTML reports.
"""

import os
import json
import webbrowser
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from usda_fdc import FdcClient
from usda_fdc.analysis import analyze_food, DriType, Gender
from usda_fdc.analysis.visualization import generate_html_report

# Path to the example data directory
DATA_DIR = Path(__file__).parent / "data"

def create_dri_chart_html(chart_data):
    """Create an HTML file with a DRI chart using Chart.js."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DRI Percentages Chart</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.4/dist/Chart.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .chart-container {{ width: 100%; height: 500px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DRI Percentages for {chart_data['recipe']['name']}</h1>
            <div class="chart-container">
                <canvas id="driChart"></canvas>
            </div>
        </div>
        
        <script>
            // Initialize chart
            var ctx = document.getElementById('driChart').getContext('2d');
            var chart = new Chart(ctx, {{
                type: 'horizontalBar',
                data: {{
                    labels: {json.dumps(chart_data['chart_data']['nutrients'])},
                    datasets: [{{
                        label: '% of DRI',
                        data: {json.dumps(chart_data['chart_data']['percentages'])},
                        backgroundColor: {json.dumps(chart_data['chart_data']['colors'])},
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        xAxes: [{{
                            ticks: {{
                                beginAtZero: true,
                                max: 100
                            }}
                        }}]
                    }},
                    title: {{
                        display: true,
                        text: 'Nutrient Content (% of DRI)'
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html)
        return f.name

def main():
    # Load API key from environment variable
    load_dotenv()
    api_key = os.getenv("FDC_API_KEY")
    
    if not api_key:
        print("Error: FDC_API_KEY environment variable not set.")
        return
    
    # Initialize the client
    client = FdcClient(api_key)
    
    print("=== Nutrient Data Visualization Examples ===")
    
    # Example 1: Generate HTML report for a food
    print("\n=== Example 1: Generate HTML report for a food ===")
    
    # Get food by FDC ID (Apple, raw, with skin)
    fdc_id = 1750340
    food = client.get_food(fdc_id)
    
    # Analyze the food
    analysis = analyze_food(
        food,
        dri_type=DriType.RDA,
        gender=Gender.MALE,
        serving_size=100.0
    )
    
    # Generate HTML report
    html_report = generate_html_report(analysis)
    
    # Save the report to a temporary file and open in browser
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html_report)
        report_path = f.name
    
    print(f"HTML report generated and saved to {report_path}")
    print("Opening report in browser...")
    webbrowser.open(f"file://{report_path}")
    
    # Example 2: Create a DRI chart from sample data
    print("\n=== Example 2: Create a DRI chart from sample data ===")
    
    # Load sample data
    sample_data_path = DATA_DIR / "breakfast_dri_chart.json"
    with open(sample_data_path, 'r') as f:
        sample_data = json.load(f)
    
    # Create HTML chart
    chart_path = create_dri_chart_html(sample_data)
    
    print(f"DRI chart generated and saved to {chart_path}")
    print("Opening chart in browser...")
    webbrowser.open(f"file://{chart_path}")
    
    print("\nExamples completed. You can view the generated files in your browser.")
    print("Note: The temporary files will be deleted when you close the program.")
    
    # Keep the program running to view the files
    input("Press Enter to exit and delete temporary files...")
    
    # Clean up temporary files
    os.unlink(report_path)
    os.unlink(chart_path)

if __name__ == "__main__":
    main()