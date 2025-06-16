import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import base64
import io
from jinja2 import Template

# Import our analysis modules
import analyze_workout
import analyze_categories

def encode_image_to_base64(fig):
    """Convert a matplotlib figure to a base64 encoded string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return img_str

def load_image_to_base64(image_path):
    """Load an image file and convert it to a base64 encoded string."""
    with open(image_path, 'rb') as img_file:
        img_str = base64.b64encode(img_file.read()).decode('utf-8')
    return img_str

def generate_report(df):
    """Generate an HTML report with all the analyses."""
    print("Generating HTML report...")
    
    # Create output directory if it doesn't exist
    os.makedirs('report', exist_ok=True)
    
    # Basic statistics
    total_exercises = df['exercise_title'].nunique()
    total_sets = len(df)
    total_volume = df['weight_lbs'].fillna(0) * df['reps'].fillna(0)
    total_volume_sum = total_volume.sum()
    
    # Get top exercises by volume
    df['volume'] = df['weight_lbs'].fillna(0) * df['reps'].fillna(0)
    top_exercises = df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(10)
    
    # Convert top_exercises to a list of tuples for Jinja2
    top_exercises_list = [(i+1, exercise, volume) for i, (exercise, volume) in enumerate(top_exercises.items())]
    
    # Load images from plots directory
    basic_plots = {}
    for plot_file in os.listdir('plots'):
        if plot_file.endswith('.png'):
            plot_path = os.path.join('plots', plot_file)
            plot_name = os.path.splitext(plot_file)[0]
            basic_plots[plot_name] = load_image_to_base64(plot_path)
    
    # Load images from category_plots directory
    category_plots = {}
    for plot_file in os.listdir('category_plots'):
        if plot_file.endswith('.png'):
            plot_path = os.path.join('category_plots', plot_file)
            plot_name = os.path.splitext(plot_file)[0]
            category_plots[plot_name] = load_image_to_base64(plot_path)
    
    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Workout Analysis Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2, h3 {
                color: #2c3e50;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }
            .summary {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }
            .summary-card {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 20px;
                margin: 10px;
                min-width: 200px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                text-align: center;
            }
            .summary-card h3 {
                margin-top: 0;
                color: #3498db;
            }
            .summary-card p {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
            .plot-section {
                margin-bottom: 40px;
            }
            .plot-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 20px;
                margin-top: 20px;
            }
            .plot-item {
                max-width: 100%;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                border-radius: 5px;
                overflow: hidden;
            }
            .plot-item img {
                max-width: 100%;
                height: auto;
                display: block;
            }
            .plot-item h4 {
                padding: 10px;
                margin: 0;
                background-color: #f8f9fa;
                text-align: center;
            }
            .two-column {
                max-width: 45%;
            }
            .three-column {
                max-width: 30%;
            }
            .full-width {
                width: 100%;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f8f9fa;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Workout Analysis Report</h1>
            <p>Generated on {{ date }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Unique Exercises</h3>
                <p>{{ total_exercises }}</p>
            </div>
            <div class="summary-card">
                <h3>Total Sets</h3>
                <p>{{ total_sets }}</p>
            </div>
            <div class="summary-card">
                <h3>Total Volume</h3>
                <p>{{ '{:,.0f}'.format(total_volume_sum) }}</p>
            </div>
        </div>
        
        <div class="plot-section">
            <h2>Basic Analysis</h2>
            
            <h3>Exercise Frequency and Volume</h3>
            <div class="plot-container">
                <div class="plot-item two-column">
                    <h4>Exercise Frequency</h4>
                    <img src="data:image/png;base64,{{ basic_plots.exercise_frequency }}" alt="Exercise Frequency">
                </div>
                <div class="plot-item two-column">
                    <h4>Exercise Volume</h4>
                    <img src="data:image/png;base64,{{ basic_plots.exercise_volume }}" alt="Exercise Volume">
                </div>
            </div>
            
            <h3>Weight and Reps Distribution</h3>
            <div class="plot-container">
                <div class="plot-item two-column">
                    <h4>Weight Distribution</h4>
                    <img src="data:image/png;base64,{{ basic_plots.weight_distribution }}" alt="Weight Distribution">
                </div>
                <div class="plot-item two-column">
                    <h4>Reps Distribution</h4>
                    <img src="data:image/png;base64,{{ basic_plots.reps_distribution }}" alt="Reps Distribution">
                </div>
            </div>
            
            <h3>Exercise Set Progression</h3>
            <div class="plot-container">
                <div class="plot-item full-width">
                    <h4>Average Weight by Exercise and Set Number</h4>
                    <img src="data:image/png;base64,{{ basic_plots.exercise_set_heatmap }}" alt="Exercise Set Heatmap">
                </div>
            </div>
        </div>
        
        <div class="plot-section">
            <h2>Category Analysis</h2>
            
            <h3>Workout Balance</h3>
            <div class="plot-container">
                <div class="plot-item two-column">
                    <h4>Workout Balance (Pie Chart)</h4>
                    <img src="data:image/png;base64,{{ category_plots.workout_balance_pie }}" alt="Workout Balance Pie">
                </div>
                <div class="plot-item two-column">
                    <h4>Workout Balance (Bar Chart)</h4>
                    <img src="data:image/png;base64,{{ category_plots.workout_balance_bar }}" alt="Workout Balance Bar">
                </div>
            </div>
            
            <h3>Category Distribution and Volume</h3>
            <div class="plot-container">
                <div class="plot-item two-column">
                    <h4>Exercise Distribution by Category</h4>
                    <img src="data:image/png;base64,{{ category_plots.category_distribution }}" alt="Category Distribution">
                </div>
                <div class="plot-item two-column">
                    <h4>Total Volume by Category</h4>
                    <img src="data:image/png;base64,{{ category_plots.category_volume }}" alt="Category Volume">
                </div>
            </div>
            
            <h3>Category Intensity</h3>
            <div class="plot-container">
                <div class="plot-item two-column">
                    <h4>Average Weight by Category</h4>
                    <img src="data:image/png;base64,{{ category_plots.category_weight }}" alt="Category Weight">
                </div>
                <div class="plot-item two-column">
                    <h4>Average Reps by Category</h4>
                    <img src="data:image/png;base64,{{ category_plots.category_reps }}" alt="Category Reps">
                </div>
            </div>
            
            <h3>Top Exercises by Category</h3>
            <div class="plot-container">
                <div class="plot-item three-column">
                    <h4>Top Chest Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.chest_top_exercises }}" alt="Top Chest Exercises">
                </div>
                <div class="plot-item three-column">
                    <h4>Top Back Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.back_top_exercises }}" alt="Top Back Exercises">
                </div>
                <div class="plot-item three-column">
                    <h4>Top Legs Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.legs_top_exercises }}" alt="Top Legs Exercises">
                </div>
            </div>
            <div class="plot-container">
                <div class="plot-item three-column">
                    <h4>Top Shoulders Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.shoulders_top_exercises }}" alt="Top Shoulders Exercises">
                </div>
                <div class="plot-item three-column">
                    <h4>Top Arms Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.arms_top_exercises }}" alt="Top Arms Exercises">
                </div>
                <div class="plot-item three-column">
                    <h4>Top Core Exercises</h4>
                    <img src="data:image/png;base64,{{ category_plots.core_top_exercises }}" alt="Top Core Exercises">
                </div>
            </div>
        </div>
        
        <div class="plot-section">
            <h2>Top Exercises by Volume</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Exercise</th>
                        <th>Total Volume</th>
                    </tr>
                </thead>
                <tbody>
                    {% for rank, exercise, volume in top_exercises_list %}
                    <tr>
                        <td>{{ rank }}</td>
                        <td>{{ exercise }}</td>
                        <td>{{ '{:,.0f}'.format(volume) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated with Python using pandas, matplotlib, and seaborn</p>
        </div>
    </body>
    </html>
    """
    
    # Render template
    template = Template(html_template)
    html_content = template.render(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_exercises=total_exercises,
        total_sets=total_sets,
        total_volume_sum=total_volume_sum,
        basic_plots=basic_plots,
        category_plots=category_plots,
        top_exercises_list=top_exercises_list
    )
    
    # Write HTML to file
    with open('report/workout_analysis.html', 'w') as f:
        f.write(html_content)
    
    print("HTML report generated successfully at report/workout_analysis.html")

def main():
    """Main function to run the report generation."""
    # Load data
    file_path = 'data/June 16, 2025.csv'
    df = analyze_workout.load_data(file_path)
    
    # Generate report
    generate_report(df)

if __name__ == "__main__":
    main() 