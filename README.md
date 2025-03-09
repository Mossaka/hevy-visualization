# Hevy Workout Data Analysis

This project analyzes workout data exported from the Hevy app to provide insights and visualizations.

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure your Hevy CSV export files are in the `data/` directory.

## Usage

### Unified Dashboard (Recommended)

Run the unified dashboard script for a complete experience:
```
python run_dashboard.py
```

This will:
1. Run all analysis scripts to generate the latest visualizations
2. Copy all visualizations to the web dashboard
3. Generate the HTML report
4. Start the interactive web dashboard

The dashboard will be available at http://localhost:8000 and includes:
- Interactive visualizations with real-time filtering
- Static visualizations from all analysis scripts
- Access to the full HTML report
- Detailed exercise and category breakdowns

### Interactive Web Dashboard

Run just the web application:
```
python app.py
```

This will start a Flask web server at http://localhost:8000 with an interactive dashboard that includes:
- Summary statistics
- Interactive visualizations
- Exercise analysis
- Category analysis
- Workout balance analysis

The web dashboard provides a modern, user-friendly interface for exploring your workout data with interactive charts and detailed breakdowns.

### Basic Analysis

Run the basic analysis script:
```
python analyze_workout.py
```

This will:
1. Load the workout data from the CSV file
2. Perform basic data exploration
3. Preprocess the data
4. Analyze exercises and generate statistics
5. Create visualizations in the `plots/` directory

### Progress Analysis

If you have multiple workout files, you can analyze your progress over time:
```
python analyze_progress.py
```

This will:
1. Load all workout data from CSV files in the `data/` directory
2. Preprocess the data
3. Analyze workout progress over time
4. Track progress for specific exercises
5. Calculate personal records
6. Create visualizations in the `progress_plots/` directory

### Category Analysis

To analyze your workouts by exercise categories (chest, back, legs, etc.):
```
python analyze_categories.py
```

This will:
1. Load the workout data from the CSV file
2. Categorize exercises into muscle groups
3. Analyze workout balance across different categories
4. Identify top exercises in each category
5. Analyze workout intensity by category
6. Create visualizations in the `category_plots/` directory

### Generate HTML Report

To generate a comprehensive HTML report with all analyses:
```
python generate_report.py
```

This will:
1. Load the workout data
2. Combine all the analyses and visualizations
3. Generate an interactive HTML report
4. Save the report to `report/workout_analysis.html`

The HTML report provides a dashboard-like interface with:
- Summary statistics
- Interactive visualizations
- Detailed exercise breakdowns
- Workout balance analysis
- Top exercises by category

## Visualizations

### Basic Analysis Visualizations
- Exercise frequency (number of sets per exercise)
- Total volume per exercise (weight × reps)
- Distribution of weights used
- Distribution of reps
- Heatmap of average weight by exercise and set number

### Progress Analysis Visualizations
- Total workout volume over time
- Workout frequency
- Max weight progress for top exercises
- Total volume progress for top exercises

### Category Analysis Visualizations
- Exercise distribution by category
- Total volume by category
- Workout balance (pie chart and bar chart)
- Top exercises in each category
- Average weight and reps by category

### Web Dashboard Visualizations
- Interactive bar charts for exercise frequency and volume
- Interactive histograms for weight and reps distribution
- Dynamic exercise progression charts
- Interactive category analysis charts
- Workout balance pie and bar charts
- Detailed exercise and category breakdowns

## Technologies Used

- **Python**: Core data processing and analysis
- **Pandas**: Data manipulation and analysis
- **Matplotlib & Seaborn**: Static visualizations
- **Flask**: Web server for the interactive dashboard
- **Plotly.js**: Interactive visualizations in the web dashboard
- **Tailwind CSS**: Styling for the web interface

## Extending the Analysis

You can modify the scripts to:
- Add more visualizations
- Analyze specific exercise performance in more detail
- Calculate additional metrics and statistics
- Compare different workout routines
- Identify trends and patterns in your training 