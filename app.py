import os
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, jsonify, request
import analyze_workout
import analyze_categories
from analyze_categories import EXERCISE_CATEGORIES
from datetime import datetime, timedelta

app = Flask(__name__)

# Global variables to store data
df = None
category_df = None

def load_data():
    """Load and preprocess data for the application."""
    global df, category_df
    
    # Load data
    file_path = 'data/March 8, 2025.csv'
    df = analyze_workout.load_data(file_path)
    
    # Preprocess data
    df = analyze_workout.preprocess_data(df)
    
    # Create a copy for category analysis
    category_df = df.copy()
    
    # Add category to the dataframe
    category_df['category'] = category_df['exercise_title'].apply(analyze_categories.categorize_exercise)
    
    # Calculate volume
    df['volume'] = df['weight_lbs'] * df['reps']
    category_df['volume'] = category_df['weight_lbs'] * category_df['reps']
    
    # Extract month and year for time-based analysis
    df['date'] = pd.to_datetime(df['start_time']).dt.date
    df['month'] = pd.to_datetime(df['start_time']).dt.to_period('M')
    df['year'] = pd.to_datetime(df['start_time']).dt.year
    
    category_df['date'] = pd.to_datetime(category_df['start_time']).dt.date
    category_df['month'] = pd.to_datetime(category_df['start_time']).dt.to_period('M')
    category_df['year'] = pd.to_datetime(category_df['start_time']).dt.year
    
    return df, category_df

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/api/summary')
def get_summary():
    """Get summary statistics for the dashboard."""
    total_exercises = df['exercise_title'].nunique()
    total_sets = len(df)
    total_volume = df['volume'].sum()
    
    # Calculate average weight, reps, and volume per exercise
    exercise_stats = df.groupby('exercise_title').agg({
        'weight_lbs': ['mean', 'max'],
        'reps': ['mean', 'max'],
        'volume': ['sum']
    }).reset_index()
    
    # Get top exercises by volume
    top_exercises = df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(10)
    top_exercises_list = [{"exercise": ex, "volume": vol} for ex, vol in top_exercises.items()]
    
    # Get category distribution
    category_counts = category_df['category'].value_counts()
    category_data = [{"category": cat, "count": count} for cat, count in category_counts.items()]
    
    # Get volume by category
    category_volume = category_df.groupby('category')['volume'].sum().reset_index()
    category_volume = category_volume.sort_values('volume', ascending=False)
    category_volume_data = [{"category": row['category'], "volume": row['volume']} 
                           for _, row in category_volume.iterrows()]
    
    return jsonify({
        "total_exercises": total_exercises,
        "total_sets": total_sets,
        "total_volume": float(total_volume),
        "top_exercises": top_exercises_list,
        "category_distribution": category_data,
        "category_volume": category_volume_data
    })

@app.route('/api/monthly_summary')
def get_monthly_summary():
    """Get summary statistics for the current month."""
    # Check if a specific month is requested
    requested_month = request.args.get('month')
    
    if requested_month:
        # Use the requested month
        month_data = df[df['month'].astype(str) == requested_month]
    else:
        # Get current month data
        current_month = datetime.now().strftime('%Y-%m')
        month_data = df[df['month'].astype(str).str.startswith(current_month)]
        
        if month_data.empty:
            # If no data for current month, use the most recent month with data
            most_recent_month = df['month'].max()
            month_data = df[df['month'] == most_recent_month]
            current_month = str(most_recent_month)
        else:
            current_month = current_month
    
    # If still empty (could happen with requested_month), return empty data
    if month_data.empty:
        return jsonify({
            "month": requested_month or "No data",
            "workouts": 0,
            "sets": 0,
            "volume": 0,
            "duration_minutes": 0,
            "top_exercises": []
        })
    
    # Calculate monthly stats
    monthly_workouts = month_data['title'].nunique()
    monthly_sets = len(month_data)
    monthly_volume = float(month_data['volume'].sum())
    
    # Calculate total workout duration for the month
    workout_durations = month_data.groupby('title').apply(
        lambda x: (x['end_time'].max() - x['start_time'].min()).total_seconds() / 60
    ).sum()
    
    # Get top exercises for the month
    monthly_top_exercises = month_data.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(5)
    monthly_top_exercises_list = [{"exercise": ex, "volume": float(vol)} for ex, vol in monthly_top_exercises.items()]
    
    return jsonify({
        "month": requested_month or current_month,
        "workouts": monthly_workouts,
        "sets": monthly_sets,
        "volume": monthly_volume,
        "duration_minutes": float(workout_durations),
        "top_exercises": monthly_top_exercises_list
    })

@app.route('/api/time_analysis')
def get_time_analysis():
    """Get time-based analysis data (monthly and yearly)."""
    # Monthly analysis
    monthly_data = df.groupby('month').agg({
        'title': 'nunique',
        'volume': 'sum',
        'set_index': 'count',
    }).reset_index()
    
    # Calculate workout duration by month
    monthly_duration = df.groupby(['month', 'title']).apply(
        lambda x: (x['end_time'].max() - x['start_time'].min()).total_seconds() / 60
    ).reset_index()
    monthly_duration = monthly_duration.groupby('month')[0].sum().reset_index()
    
    # Merge duration data
    monthly_data = monthly_data.merge(monthly_duration, on='month', how='left')
    
    # Convert to list of dictionaries for JSON
    monthly_result = []
    for _, row in monthly_data.iterrows():
        monthly_result.append({
            "month": str(row['month']),
            "workouts": int(row['title']),
            "volume": float(row['volume']),
            "sets": int(row['set_index']),
            "duration_minutes": float(row[0]) if not pd.isna(row[0]) else 0
        })
    
    # Yearly analysis
    yearly_data = df.groupby('year').agg({
        'title': 'nunique',
        'volume': 'sum',
        'set_index': 'count',
    }).reset_index()
    
    # Calculate workout duration by year
    yearly_duration = df.groupby(['year', 'title']).apply(
        lambda x: (x['end_time'].max() - x['start_time'].min()).total_seconds() / 60
    ).reset_index()
    yearly_duration = yearly_duration.groupby('year')[0].sum().reset_index()
    
    # Merge duration data
    yearly_data = yearly_data.merge(yearly_duration, on='year', how='left')
    
    # Convert to list of dictionaries for JSON
    yearly_result = []
    for _, row in yearly_data.iterrows():
        yearly_result.append({
            "year": int(row['year']),
            "workouts": int(row['title']),
            "volume": float(row['volume']),
            "sets": int(row['set_index']),
            "duration_minutes": float(row[0]) if not pd.isna(row[0]) else 0
        })
    
    return jsonify({
        "monthly": monthly_result,
        "yearly": yearly_result
    })

@app.route('/api/big_three_analysis')
def get_big_three_analysis():
    """Get analysis data for the big three lifts (bench press, squat, deadlift)."""
    # Define the big three exercises with more flexible matching
    bench_press_data = df[df['exercise_title'].str.contains('Bench Press', case=False, na=False) & 
                         ~df['exercise_title'].str.contains('Incline|Decline|Close', case=False, na=False)]
    
    squat_data = df[df['exercise_title'].str.contains('Squat', case=False, na=False) & 
                   ~df['exercise_title'].str.contains('Bulgarian|Split', case=False, na=False)]
    
    deadlift_data = df[df['exercise_title'].str.contains('Deadlift', case=False, na=False) & 
                      ~df['exercise_title'].str.contains('Romanian|Sumo', case=False, na=False)]
    
    # Print debug information
    print(f"Found {len(bench_press_data)} bench press records")
    print(f"Found {len(squat_data)} squat records")
    print(f"Found {len(deadlift_data)} deadlift records")
    
    # Create a dictionary to store the results
    result = {}
    
    # Process bench press data
    if not bench_press_data.empty:
        bench_stats = {
            "sets": len(bench_press_data),
            "avg_weight": float(bench_press_data['weight_lbs'].mean()),
            "max_weight": float(bench_press_data['weight_lbs'].max()),
            "avg_reps": float(bench_press_data['reps'].mean()),
            "max_reps": float(bench_press_data['reps'].max()),
            "total_volume": float(bench_press_data['volume'].sum())
        }
        
        # Calculate progress over time
        bench_progress_df = bench_press_data.groupby('date').agg({
            'weight_lbs': ['mean', 'max'],
            'reps': ['mean', 'max'],
            'volume': 'sum'
        })
        
        # Convert to list of dictionaries
        bench_progress_list = []
        for date_idx, row in bench_progress_df.iterrows():
            bench_progress_list.append({
                "date": date_idx.strftime('%Y-%m-%d'),
                "avg_weight": float(row[('weight_lbs', 'mean')]),
                "max_weight": float(row[('weight_lbs', 'max')]),
                "avg_reps": float(row[('reps', 'mean')]),
                "max_reps": float(row[('reps', 'max')]),
                "volume": float(row[('volume', 'sum')])
            })
    else:
        bench_stats = {
            "sets": 0,
            "avg_weight": 0,
            "max_weight": 0,
            "avg_reps": 0,
            "max_reps": 0,
            "total_volume": 0
        }
        bench_progress_list = []
    
    result['bench_press'] = {
        "stats": bench_stats,
        "progress": bench_progress_list
    }
    
    # Process squat data
    if not squat_data.empty:
        squat_stats = {
            "sets": len(squat_data),
            "avg_weight": float(squat_data['weight_lbs'].mean()),
            "max_weight": float(squat_data['weight_lbs'].max()),
            "avg_reps": float(squat_data['reps'].mean()),
            "max_reps": float(squat_data['reps'].max()),
            "total_volume": float(squat_data['volume'].sum())
        }
        
        # Calculate progress over time
        squat_progress_df = squat_data.groupby('date').agg({
            'weight_lbs': ['mean', 'max'],
            'reps': ['mean', 'max'],
            'volume': 'sum'
        })
        
        # Convert to list of dictionaries
        squat_progress_list = []
        for date_idx, row in squat_progress_df.iterrows():
            squat_progress_list.append({
                "date": date_idx.strftime('%Y-%m-%d'),
                "avg_weight": float(row[('weight_lbs', 'mean')]),
                "max_weight": float(row[('weight_lbs', 'max')]),
                "avg_reps": float(row[('reps', 'mean')]),
                "max_reps": float(row[('reps', 'max')]),
                "volume": float(row[('volume', 'sum')])
            })
    else:
        squat_stats = {
            "sets": 0,
            "avg_weight": 0,
            "max_weight": 0,
            "avg_reps": 0,
            "max_reps": 0,
            "total_volume": 0
        }
        squat_progress_list = []
    
    result['squat'] = {
        "stats": squat_stats,
        "progress": squat_progress_list
    }
    
    # Process deadlift data
    if not deadlift_data.empty:
        deadlift_stats = {
            "sets": len(deadlift_data),
            "avg_weight": float(deadlift_data['weight_lbs'].mean()),
            "max_weight": float(deadlift_data['weight_lbs'].max()),
            "avg_reps": float(deadlift_data['reps'].mean()),
            "max_reps": float(deadlift_data['reps'].max()),
            "total_volume": float(deadlift_data['volume'].sum())
        }
        
        # Calculate progress over time
        deadlift_progress_df = deadlift_data.groupby('date').agg({
            'weight_lbs': ['mean', 'max'],
            'reps': ['mean', 'max'],
            'volume': 'sum'
        })
        
        # Convert to list of dictionaries
        deadlift_progress_list = []
        for date_idx, row in deadlift_progress_df.iterrows():
            deadlift_progress_list.append({
                "date": date_idx.strftime('%Y-%m-%d'),
                "avg_weight": float(row[('weight_lbs', 'mean')]),
                "max_weight": float(row[('weight_lbs', 'max')]),
                "avg_reps": float(row[('reps', 'mean')]),
                "max_reps": float(row[('reps', 'max')]),
                "volume": float(row[('volume', 'sum')])
            })
    else:
        deadlift_stats = {
            "sets": 0,
            "avg_weight": 0,
            "max_weight": 0,
            "avg_reps": 0,
            "max_reps": 0,
            "total_volume": 0
        }
        deadlift_progress_list = []
    
    result['deadlift'] = {
        "stats": deadlift_stats,
        "progress": deadlift_progress_list
    }
    
    return jsonify(result)

@app.route('/api/exercise_frequency')
def get_exercise_frequency():
    """Get exercise frequency data for visualization."""
    exercise_counts = df['exercise_title'].value_counts().head(15)
    data = [{"exercise": ex, "count": count} for ex, count in exercise_counts.items()]
    return jsonify(data)

@app.route('/api/exercise_volume')
def get_exercise_volume():
    """Get exercise volume data for visualization."""
    exercise_volume = df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(15)
    data = [{"exercise": ex, "volume": vol} for ex, vol in exercise_volume.items()]
    return jsonify(data)

@app.route('/api/weight_distribution')
def get_weight_distribution():
    """Get weight distribution data for visualization."""
    weights = df[df['weight_lbs'] > 0]['weight_lbs'].tolist()
    return jsonify(weights)

@app.route('/api/reps_distribution')
def get_reps_distribution():
    """Get reps distribution data for visualization."""
    reps = df[df['reps'] > 0]['reps'].tolist()
    return jsonify(reps)

@app.route('/api/category_analysis')
def get_category_analysis():
    """Get category analysis data for visualization."""
    # Category counts
    category_counts = category_df['category'].value_counts()
    category_count_data = [{"category": cat, "count": count} for cat, count in category_counts.items()]
    
    # Category volume
    category_volume = category_df.groupby('category')['volume'].sum().reset_index()
    category_volume = category_volume.sort_values('volume', ascending=False)
    category_volume_data = [{"category": row['category'], "volume": float(row['volume'])} 
                           for _, row in category_volume.iterrows()]
    
    # Category weight and reps
    category_weight = category_df.groupby('category')['weight_lbs'].mean().reset_index()
    category_weight = category_weight.sort_values('weight_lbs', ascending=False)
    category_weight_data = [{"category": row['category'], "weight": float(row['weight_lbs'])} 
                           for _, row in category_weight.iterrows()]
    
    category_reps = category_df.groupby('category')['reps'].mean().reset_index()
    category_reps = category_reps.sort_values('reps', ascending=False)
    category_reps_data = [{"category": row['category'], "reps": float(row['reps'])} 
                         for _, row in category_reps.iterrows()]
    
    return jsonify({
        "category_counts": category_count_data,
        "category_volume": category_volume_data,
        "category_weight": category_weight_data,
        "category_reps": category_reps_data
    })

@app.route('/api/category_exercises/<category>')
def get_category_exercises(category):
    """Get top exercises for a specific category."""
    if category not in EXERCISE_CATEGORIES and category != 'Other':
        return jsonify({"error": "Category not found"}), 404
    
    category_exercises = category_df[category_df['category'] == category]
    
    if category_exercises.empty:
        return jsonify([])
    
    # Get top exercises by volume
    exercise_volume = category_exercises.groupby('exercise_title')['volume'].sum().reset_index()
    exercise_volume = exercise_volume.sort_values('volume', ascending=False).head(10)
    
    # Calculate stats for top exercises
    top_exercises = exercise_volume['exercise_title'].tolist()
    top_exercises_df = category_exercises[category_exercises['exercise_title'].isin(top_exercises)]
    
    exercise_stats = top_exercises_df.groupby('exercise_title').agg({
        'weight_lbs': ['mean', 'max'],
        'reps': ['mean', 'max'],
        'volume': ['mean', 'sum']
    })
    
    # Convert to list of dictionaries for JSON
    result = []
    for exercise in exercise_volume['exercise_title']:
        stats = exercise_stats.loc[exercise]
        result.append({
            "exercise": exercise,
            "volume": float(stats['volume']['sum']),
            "avg_weight": float(stats['weight_lbs']['mean']),
            "max_weight": float(stats['weight_lbs']['max']),
            "avg_reps": float(stats['reps']['mean']),
            "max_reps": float(stats['reps']['max'])
        })
    
    return jsonify(result)

@app.route('/api/exercise_details/<exercise>')
def get_exercise_details(exercise):
    """Get detailed information for a specific exercise."""
    exercise_data = df[df['exercise_title'] == exercise]
    
    if exercise_data.empty:
        return jsonify({"error": "Exercise not found"}), 404
    
    # Calculate stats
    stats = {
        "sets": len(exercise_data),
        "avg_weight": float(exercise_data['weight_lbs'].mean()),
        "max_weight": float(exercise_data['weight_lbs'].max()),
        "avg_reps": float(exercise_data['reps'].mean()),
        "max_reps": float(exercise_data['reps'].max()),
        "total_volume": float(exercise_data['volume'].sum())
    }
    
    # Get set data for visualization
    set_data = exercise_data.sort_values('set_index')[['set_index', 'weight_lbs', 'reps', 'volume']].to_dict('records')
    set_data = [{
        "set": row['set_index'],
        "weight": float(row['weight_lbs']),
        "reps": float(row['reps']),
        "volume": float(row['volume'])
    } for row in set_data]
    
    return jsonify({
        "stats": stats,
        "sets": set_data
    })

@app.route('/api/workout_balance')
def get_workout_balance():
    """Get workout balance data for visualization."""
    # Calculate percentage of volume by category
    total_volume = category_df['volume'].sum()
    category_volume = category_df.groupby('category')['volume'].sum()
    category_percentage = (category_volume / total_volume * 100)
    
    data = [{"category": cat, "percentage": float(pct)} for cat, pct in category_percentage.items()]
    return jsonify(data)

if __name__ == '__main__':
    # Load data on startup
    df, category_df = load_data()
    
    # Only run the dev server when executed directly, not when run by gunicorn
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # This will only run when file is executed directly, not through gunicorn
    app.run(host='0.0.0.0', port=port, debug=False) 