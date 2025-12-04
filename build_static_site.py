#!/usr/bin/env python
"""
Build static site by generating JSON data files.
Run whenever CSV data is updated.
"""

import os
import json
import pandas as pd
import numpy as np
import shutil
from datetime import datetime
import analyze_workout
import analyze_categories
from analyze_categories import EXERCISE_CATEGORIES

# Output directory
OUTPUT_DIR = 'docs/data_json'

def json_serialize(obj):
    """Handle pandas/numpy/datetime types for JSON."""
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj) if not np.isnan(obj) else None
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Period):
        return str(obj)
    elif pd.isna(obj):
        return None
    return obj

def load_workout_data():
    """Load and preprocess workout data (from app.py)."""
    file_path = 'data/Dec 3,2025.csv'
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

    # FILTER TO 2025 DATA ONLY
    print(f"Filtering to 2025 data only...")
    print(f"  Before filter: {len(df):,} rows")
    df = df[df['year'] == 2025].copy()
    category_df = category_df[category_df['year'] == 2025].copy()
    print(f"  After filter: {len(df):,} rows (2025 only)")

    return df, category_df

def calculate_brzycki_1rm(weight, reps):
    """Calculate 1RM using Brzycki formula: 1RM = weight / (1.0278 - 0.0278 * reps)"""
    if reps == 0 or weight == 0:
        return 0
    if reps == 1:
        return weight
    if reps > 10:
        return weight * (1 + reps / 30)
    return weight / (1.0278 - 0.0278 * reps)

def generate_summary(df, category_df):
    """Generate summary.json - overall statistics."""
    print("  Generating summary.json...")

    total_exercises = df['exercise_title'].nunique()
    total_sets = len(df)
    total_volume = df['volume'].sum()

    # Get top exercises by volume
    top_exercises = df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(10)
    top_exercises_list = [{"exercise": ex, "volume": float(vol)} for ex, vol in top_exercises.items()]

    # Get category distribution
    category_counts = category_df['category'].value_counts()
    category_data = [{"category": cat, "count": int(count)} for cat, count in category_counts.items()]

    # Get volume by category
    category_volume = category_df.groupby('category')['volume'].sum().reset_index()
    category_volume = category_volume.sort_values('volume', ascending=False)
    category_volume_data = [{"category": row['category'], "volume": float(row['volume'])}
                           for _, row in category_volume.iterrows()]

    data = {
        "total_exercises": int(total_exercises),
        "total_sets": int(total_sets),
        "total_volume": float(total_volume),
        "top_exercises": top_exercises_list,
        "category_distribution": category_data,
        "category_volume": category_volume_data
    }

    output_path = f'{OUTPUT_DIR}/summary.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_time_analysis(df):
    """Generate time_analysis.json - monthly and yearly trends."""
    print("  Generating time_analysis.json...")

    # Monthly analysis
    monthly_data = df.groupby('month').agg({
        'title': 'nunique',
        'volume': 'sum',
        'set_index': 'count',
    }).reset_index()

    # Calculate workout duration by month
    monthly_durations = []
    for month in monthly_data['month']:
        month_df = df[df['month'] == month]

        # Group by both title AND date to identify unique workout sessions
        unique_workouts = month_df.groupby(['title', 'date']).agg({
            'start_time': 'min',
            'end_time': 'max'
        }).reset_index()

        month_duration = 0
        for _, workout in unique_workouts.iterrows():
            start_time = pd.to_datetime(workout['start_time'])
            end_time = pd.to_datetime(workout['end_time'])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            month_duration += duration_minutes

        monthly_durations.append({
            'month': month,
            'duration_minutes': month_duration
        })

    monthly_duration_df = pd.DataFrame(monthly_durations)

    # Merge duration data
    monthly_data = monthly_data.merge(monthly_duration_df, on='month', how='left')

    # Convert to list of dictionaries for JSON
    monthly_result = []
    for _, row in monthly_data.iterrows():
        monthly_result.append({
            "month": str(row['month']),
            "workouts": int(row['title']),
            "volume": float(row['volume']),
            "sets": int(row['set_index']),
            "duration_minutes": float(row['duration_minutes']) if not pd.isna(row['duration_minutes']) else 0
        })

    # Yearly analysis
    yearly_data = df.groupby('year').agg({
        'title': 'nunique',
        'volume': 'sum',
        'set_index': 'count',
    }).reset_index()

    # Calculate workout duration by year
    yearly_durations = []
    for year in yearly_data['year']:
        year_df = df[df['year'] == year]

        # Group by both title AND date to identify unique workout sessions
        unique_workouts = year_df.groupby(['title', 'date']).agg({
            'start_time': 'min',
            'end_time': 'max'
        }).reset_index()

        year_duration = 0
        for _, workout in unique_workouts.iterrows():
            start_time = pd.to_datetime(workout['start_time'])
            end_time = pd.to_datetime(workout['end_time'])
            duration_minutes = (end_time - start_time).total_seconds() / 60
            year_duration += duration_minutes

        yearly_durations.append({
            'year': year,
            'duration_minutes': year_duration
        })

    yearly_duration_df = pd.DataFrame(yearly_durations)

    # Merge duration data
    yearly_data = yearly_data.merge(yearly_duration_df, on='year', how='left')

    # Convert to list of dictionaries for JSON
    yearly_result = []
    for _, row in yearly_data.iterrows():
        yearly_result.append({
            "year": int(row['year']),
            "workouts": int(row['title']),
            "volume": float(row['volume']),
            "sets": int(row['set_index']),
            "duration_minutes": float(row['duration_minutes']) if not pd.isna(row['duration_minutes']) else 0
        })

    data = {
        "monthly": monthly_result,
        "yearly": yearly_result
    }

    output_path = f'{OUTPUT_DIR}/time_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_big_three_analysis(df):
    """Generate big_three_analysis.json - bench, squat, deadlift data."""
    print("  Generating big_three_analysis.json...")

    # Define the big three exercises with flexible matching
    bench_press_data = df[df['exercise_title'].str.contains('Bench Press', case=False, na=False) &
                         ~df['exercise_title'].str.contains('Incline|Decline|Close', case=False, na=False)]

    squat_data = df[df['exercise_title'].str.contains('Squat', case=False, na=False) &
                   ~df['exercise_title'].str.contains('Bulgarian|Split', case=False, na=False)]

    deadlift_data = df[df['exercise_title'].str.contains('Deadlift', case=False, na=False) &
                      ~df['exercise_title'].str.contains('Romanian|Sumo', case=False, na=False)]

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

        squat_progress_df = squat_data.groupby('date').agg({
            'weight_lbs': ['mean', 'max'],
            'reps': ['mean', 'max'],
            'volume': 'sum'
        })

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

        deadlift_progress_df = deadlift_data.groupby('date').agg({
            'weight_lbs': ['mean', 'max'],
            'reps': ['mean', 'max'],
            'volume': 'sum'
        })

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

    output_path = f'{OUTPUT_DIR}/big_three_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, default=json_serialize, indent=2)

def generate_exercise_frequency(df):
    """Generate exercise_frequency.json."""
    print("  Generating exercise_frequency.json...")

    exercise_counts = df['exercise_title'].value_counts().head(15)
    data = [{"exercise": ex, "count": int(count)} for ex, count in exercise_counts.items()]

    output_path = f'{OUTPUT_DIR}/exercise_frequency.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_exercise_volume(df):
    """Generate exercise_volume.json."""
    print("  Generating exercise_volume.json...")

    exercise_volume = df.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(15)
    data = [{"exercise": ex, "volume": float(vol)} for ex, vol in exercise_volume.items()]

    output_path = f'{OUTPUT_DIR}/exercise_volume.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_weight_distribution(df):
    """Generate weight_distribution.json."""
    print("  Generating weight_distribution.json...")

    weights = df[df['weight_lbs'] > 0]['weight_lbs'].tolist()

    output_path = f'{OUTPUT_DIR}/weight_distribution.json'
    with open(output_path, 'w') as f:
        json.dump(weights, f, default=json_serialize, indent=2)

def generate_reps_distribution(df):
    """Generate reps_distribution.json."""
    print("  Generating reps_distribution.json...")

    reps = df[df['reps'] > 0]['reps'].tolist()

    output_path = f'{OUTPUT_DIR}/reps_distribution.json'
    with open(output_path, 'w') as f:
        json.dump(reps, f, default=json_serialize, indent=2)

def generate_category_analysis(category_df):
    """Generate category_analysis.json."""
    print("  Generating category_analysis.json...")

    # Category counts
    category_counts = category_df['category'].value_counts()
    category_count_data = [{"category": cat, "count": int(count)} for cat, count in category_counts.items()]

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

    data = {
        "category_counts": category_count_data,
        "category_volume": category_volume_data,
        "category_weight": category_weight_data,
        "category_reps": category_reps_data
    }

    output_path = f'{OUTPUT_DIR}/category_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_workout_balance(category_df):
    """Generate workout_balance.json."""
    print("  Generating workout_balance.json...")

    # Calculate percentage of volume by category
    total_volume = category_df['volume'].sum()
    category_volume = category_df.groupby('category')['volume'].sum()
    category_percentage = (category_volume / total_volume * 100)

    data = [{"category": cat, "percentage": float(pct)} for cat, pct in category_percentage.items()]

    output_path = f'{OUTPUT_DIR}/workout_balance.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_workout_dates(df):
    """Generate workout_dates.json."""
    print("  Generating workout_dates.json...")

    # Get unique workout days
    workout_dates = df['date'].unique()

    # Sort dates in descending order
    sorted_dates = sorted(workout_dates, reverse=True)

    # Format dates
    formatted_dates = [date.strftime("%b %d, %Y") for date in sorted_dates]

    data = {
        "dates": formatted_dates,
        "total": len(formatted_dates)
    }

    output_path = f'{OUTPUT_DIR}/workout_dates.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_personal_records(df):
    """Generate personal_records.json with 1RM calculations."""
    print("  Generating personal_records.json...")

    main_lifts = ['Bench Press (Barbell)', 'Squat (Barbell)', 'Deadlift (Barbell)', 'Overhead Press (Barbell)']

    pr_data = {}

    for lift in main_lifts:
        lift_data = df[df['exercise_title'] == lift].copy()

        if lift_data.empty:
            pr_data[lift] = {
                "current_max_weight": 0,
                "estimated_1rm": 0,
                "best_set": None,
                "total_sets": 0,
                "hypertrophy_recommendation": {},
                "strength_recommendation": {},
                "power_recommendation": {}
            }
            continue

        normal_sets = lift_data[lift_data['set_type'] == 'normal']

        if normal_sets.empty:
            normal_sets = lift_data

        normal_sets['estimated_1rm'] = normal_sets.apply(
            lambda row: calculate_brzycki_1rm(row['weight_lbs'], row['reps']), axis=1
        )

        best_1rm_idx = normal_sets['estimated_1rm'].idxmax()
        best_set = normal_sets.loc[best_1rm_idx]

        current_max_weight = normal_sets['weight_lbs'].max()
        estimated_1rm = normal_sets['estimated_1rm'].max()

        hypertrophy_weight = estimated_1rm * 0.65
        hypertrophy_weight_high = estimated_1rm * 0.80

        strength_weight = estimated_1rm * 0.80
        strength_weight_high = estimated_1rm * 0.90

        power_weight = estimated_1rm * 0.30
        power_weight_high = estimated_1rm * 0.60

        pr_data[lift] = {
            "current_max_weight": float(current_max_weight),
            "estimated_1rm": float(estimated_1rm),
            "best_set": {
                "weight": float(best_set['weight_lbs']),
                "reps": int(best_set['reps']),
                "date": best_set['date'].strftime('%Y-%m-%d'),
                "estimated_1rm": float(best_set['estimated_1rm'])
            },
            "total_sets": len(normal_sets),
            "hypertrophy_recommendation": {
                "weight_range": f"{hypertrophy_weight:.0f}-{hypertrophy_weight_high:.0f} lbs",
                "rep_range": "8-15 reps",
                "sets": "3-5 sets",
                "rest": "60-90 seconds",
                "description": "Muscle growth focus - moderate weight, higher volume"
            },
            "strength_recommendation": {
                "weight_range": f"{strength_weight:.0f}-{strength_weight_high:.0f} lbs",
                "rep_range": "1-6 reps",
                "sets": "3-6 sets",
                "rest": "3-5 minutes",
                "description": "Maximum strength focus - heavy weight, low reps"
            },
            "power_recommendation": {
                "weight_range": f"{power_weight:.0f}-{power_weight_high:.0f} lbs",
                "rep_range": "1-5 reps",
                "sets": "3-6 sets",
                "rest": "3-5 minutes",
                "description": "Explosive power focus - light to moderate weight, fast movement"
            }
        }

    training_principles = {
        "hypertrophy": {
            "title": "Hypertrophy Training (Muscle Growth)",
            "intensity": "65-80% of 1RM",
            "volume": "High volume, moderate intensity",
            "frequency": "2-3x per week per muscle group",
            "research_note": "Based on Schoenfeld et al. (2017) meta-analysis showing optimal hypertrophy occurs at 6-20 reps with 65-85% 1RM"
        },
        "strength": {
            "title": "Strength Training (Max Effort)",
            "intensity": "80-100% of 1RM",
            "volume": "Low volume, high intensity",
            "frequency": "2-3x per week with adequate recovery",
            "research_note": "Based on Helms et al. (2018) recommendations for strength development at >85% 1RM"
        },
        "power": {
            "title": "Power Training (Speed-Strength)",
            "intensity": "30-60% of 1RM",
            "volume": "Low volume, explosive intent",
            "frequency": "2-3x per week when fresh",
            "research_note": "Based on Cormie et al. (2011) showing optimal power development at 30-60% 1RM with maximal intent"
        }
    }

    data = {
        "personal_records": pr_data,
        "training_principles": training_principles
    }

    output_path = f'{OUTPUT_DIR}/personal_records.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_goal_setting(df):
    """Generate goal_setting.json with 2025 goal tracking."""
    print("  Generating goal_setting.json...")

    main_lifts = ['Bench Press (Barbell)', 'Squat (Barbell)', 'Deadlift (Barbell)', 'Overhead Press (Barbell)']

    goal_data = {}

    # Define the baseline date (January 1, 2025)
    baseline_date = datetime(2025, 1, 1).date()

    for lift in main_lifts:
        lift_data = df[df['exercise_title'] == lift].copy()

        if lift_data.empty:
            goal_data[lift] = {
                "baseline_1rm": 0,
                "current_1rm": 0,
                "goal_1rm": 0,
                "progress_percentage": 0,
                "remaining_lbs": 0,
                "status": "No data available"
            }
            continue

        normal_sets = lift_data[lift_data['set_type'] == 'normal']
        if normal_sets.empty:
            normal_sets = lift_data

        normal_sets['estimated_1rm'] = normal_sets.apply(
            lambda row: calculate_brzycki_1rm(row['weight_lbs'], row['reps']), axis=1
        )

        # Get baseline 1RM (best performance around January 1, 2025)
        baseline_window_start = datetime(2024, 12, 1).date()
        baseline_window_end = datetime(2025, 2, 1).date()

        baseline_data = normal_sets[
            (normal_sets['date'] >= baseline_window_start) &
            (normal_sets['date'] <= baseline_window_end)
        ]

        if baseline_data.empty:
            # If no data in baseline window, use earliest 2025 data
            early_2025_data = normal_sets[normal_sets['date'] >= baseline_date]
            if not early_2025_data.empty:
                baseline_1rm = early_2025_data['estimated_1rm'].max()
            else:
                # Fallback to all-time best if no 2025 data
                baseline_1rm = normal_sets['estimated_1rm'].max()
        else:
            baseline_1rm = baseline_data['estimated_1rm'].max()

        # Get current 1RM (best performance in recent weeks)
        recent_data = normal_sets.tail(20)  # Last 20 sets
        current_1rm = recent_data['estimated_1rm'].max() if not recent_data.empty else baseline_1rm

        # Goal is 20% improvement from baseline
        goal_1rm = baseline_1rm * 1.20

        # Calculate progress percentage based on improvement from baseline
        if goal_1rm > baseline_1rm:
            progress_made = current_1rm - baseline_1rm
            total_progress_needed = goal_1rm - baseline_1rm
            progress_percentage = (progress_made / total_progress_needed) * 100
            progress_percentage = max(0, min(100, progress_percentage))
        else:
            progress_percentage = 100  # Already at or above goal

        remaining_lbs = max(0, goal_1rm - current_1rm)

        # Status based on progress
        if progress_percentage >= 100:
            status = "Goal Achieved! 🎉"
        elif progress_percentage >= 75:
            status = "Almost There! 💪"
        elif progress_percentage >= 50:
            status = "Good Progress 📈"
        elif progress_percentage >= 25:
            status = "Getting Started 🚀"
        else:
            status = "Building Foundation 💪"

        goal_data[lift] = {
            "baseline_1rm": float(baseline_1rm),
            "current_1rm": float(current_1rm),
            "goal_1rm": float(goal_1rm),
            "progress_percentage": float(progress_percentage),
            "remaining_lbs": float(remaining_lbs),
            "status": status
        }

    end_of_year = datetime(datetime.now().year, 12, 31)
    days_remaining = (end_of_year - datetime.now()).days

    # Calculate how much of the year has passed
    start_of_year = datetime(datetime.now().year, 1, 1)
    days_elapsed = (datetime.now() - start_of_year).days
    year_progress = (days_elapsed / 365) * 100

    data = {
        "goals": goal_data,
        "target_date": "End of 2025",
        "days_remaining": days_remaining,
        "year_progress": year_progress,
        "motivation_message": f"You're {year_progress:.1f}% through 2025 with {days_remaining} days left to achieve your 20% strength goals! Stay consistent and trust the process."
    }

    output_path = f'{OUTPUT_DIR}/goal_setting.json'
    with open(output_path, 'w') as f:
        json.dump(data, f, default=json_serialize, indent=2)

def generate_monthly_summary(df):
    """Generate monthly_summary.json - array of all months."""
    print("  Generating monthly_summary.json...")

    all_months_data = []

    # Get all unique months
    unique_months = sorted(df['month'].unique())

    for requested_month in unique_months:
        month_data = df[df['month'] == requested_month]

        if month_data.empty:
            continue

        # Calculate workout duration for the month
        workout_durations = 0

        # Group by both title AND date to identify unique workout sessions
        unique_workouts = month_data.groupby(['title', 'date']).agg({
            'start_time': 'min',
            'end_time': 'max'
        }).reset_index()

        for _, workout in unique_workouts.iterrows():
            try:
                start_time = pd.to_datetime(workout['start_time'])
                end_time = pd.to_datetime(workout['end_time'])
                duration_minutes = (end_time - start_time).total_seconds() / 60
                workout_durations += duration_minutes
            except Exception:
                pass

        # Calculate monthly stats
        monthly_workouts = month_data['title'].nunique()
        monthly_sets = len(month_data)
        monthly_volume = float(month_data['volume'].sum())

        # Get top exercises for the month
        monthly_top_exercises = month_data.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(5)
        monthly_top_exercises_list = [{"exercise": ex, "volume": float(vol)} for ex, vol in monthly_top_exercises.items()]

        all_months_data.append({
            "month": str(requested_month),
            "workouts": monthly_workouts,
            "sets": monthly_sets,
            "volume": monthly_volume,
            "duration_minutes": float(workout_durations),
            "top_exercises": monthly_top_exercises_list
        })

    output_path = f'{OUTPUT_DIR}/monthly_summary.json'
    with open(output_path, 'w') as f:
        json.dump(all_months_data, f, default=json_serialize, indent=2)

def generate_category_exercises(category_df):
    """Generate category exercises JSON files - 7 files."""
    print("  Generating category exercise files...")

    categories = ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Other']

    for category in categories:
        category_exercises = category_df[category_df['category'] == category]

        if category_exercises.empty:
            data = []
        else:
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
            data = []
            for exercise in exercise_volume['exercise_title']:
                if exercise in exercise_stats.index:
                    stats = exercise_stats.loc[exercise]
                    data.append({
                        "exercise": exercise,
                        "volume": float(stats['volume']['sum']),
                        "avg_weight": float(stats['weight_lbs']['mean']),
                        "max_weight": float(stats['weight_lbs']['max']),
                        "avg_reps": float(stats['reps']['mean']),
                        "max_reps": float(stats['reps']['max'])
                    })

        slug = category.lower()
        output_path = f'{OUTPUT_DIR}/category_exercises_{slug}.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, default=json_serialize, indent=2)

def generate_exercise_details(df):
    """Generate exercise details JSON files - one per exercise."""
    print("  Generating exercise detail files...")

    # Get unique exercises
    unique_exercises = df['exercise_title'].unique()
    print(f"    Processing {len(unique_exercises)} exercises...")

    for exercise in unique_exercises:
        exercise_data = df[df['exercise_title'] == exercise]

        if exercise_data.empty:
            continue

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
        set_data_list = [{
            "set": int(row['set_index']),
            "weight": float(row['weight_lbs']),
            "reps": float(row['reps']),
            "volume": float(row['volume'])
        } for row in set_data]

        data = {
            "stats": stats,
            "sets": set_data_list
        }

        # Create URL-safe slug
        slug = exercise.lower() \
            .replace(' (', '_') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(' ', '_') \
            .replace('/', '_') \
            .replace('-', '_') \
            .replace(',', '') \
            .replace("'", '') \
            .replace('"', '')

        output_path = f'{OUTPUT_DIR}/exercise_{slug}.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, default=json_serialize, indent=2)

def generate_recent_workouts(df):
    """Generate recent_workouts.json - full dataset."""
    print("  Generating recent_workouts.json...")

    # Get unique workout days (dates)
    workout_dates = sorted(df['date'].unique(), reverse=True)

    # Calculate the maximum weight for each exercise across the entire dataset
    max_weights = {}
    for exercise in df['exercise_title'].unique():
        exercise_data = df[df['exercise_title'] == exercise]
        normal_sets = exercise_data[exercise_data['set_type'] == 'normal']
        if len(normal_sets) > 0:
            max_weights[exercise] = normal_sets['weight_lbs'].max()
        else:
            max_weights[exercise] = 0

    result = []
    for date in workout_dates:
        # Filter data for this date
        day_data = df[df['date'] == date]

        # Get unique workout names for this day
        workouts = day_data['title'].unique()

        # Get exercises for each workout
        workout_details = []
        for workout in workouts:
            workout_exercises = day_data[day_data['title'] == workout]['exercise_title'].unique()

            # Calculate total volume for this workout
            workout_volume = day_data[day_data['title'] == workout]['volume'].sum()

            # Get exercise details
            exercise_details = []
            for exercise in workout_exercises:
                exercise_data = day_data[(day_data['title'] == workout) &
                                       (day_data['exercise_title'] == exercise)]

                sets = len(exercise_data)
                total_reps = exercise_data['reps'].sum()
                avg_weight = exercise_data['weight_lbs'].mean()

                # Get individual set details for this exercise
                set_details = []
                for _, set_row in exercise_data.iterrows():
                    # Calculate if this is a PR (personal record)
                    is_pr = False
                    if (set_row['set_type'] == 'normal' and
                        set_row['weight_lbs'] == max_weights.get(exercise, 0) and
                        max_weights.get(exercise, 0) > 0):
                        is_pr = True

                    # Get notes if they exist
                    notes = set_row.get('exercise_notes', '')
                    if pd.isna(notes):
                        notes = ''

                    set_details.append({
                        "reps": int(set_row['reps']),
                        "weight": float(set_row['weight_lbs']) if not np.isnan(set_row['weight_lbs']) else 0,
                        "notes": notes,
                        "is_pr": is_pr,
                        "set_type": set_row['set_type']
                    })

                exercise_details.append({
                    "name": exercise,
                    "sets": sets,
                    "total_reps": int(total_reps),
                    "avg_weight": round(float(avg_weight), 1) if not np.isnan(avg_weight) else 0,
                    "set_details": set_details
                })

            workout_details.append({
                "name": workout,
                "exercise_count": len(workout_exercises),
                "volume": float(workout_volume),
                "exercises": exercise_details
            })

        # Format date as string
        date_str = date.strftime("%b %d, %Y")

        result.append({
            "date": date_str,
            "workouts": workout_details
        })

    output_path = f'{OUTPUT_DIR}/recent_workouts.json'
    with open(output_path, 'w') as f:
        json.dump(result, f, default=json_serialize, indent=2)

def copy_assets():
    """Copy static assets and convert HTML template."""
    print("\nCopying assets...")

    # Copy static directory
    print("  Copying static/ to docs/static/...")
    if os.path.exists('docs/static'):
        shutil.rmtree('docs/static')
    shutil.copytree('static/', 'docs/static/', dirs_exist_ok=True)

    # Convert template
    print("  Converting templates/index.html to docs/index.html...")
    with open('templates/index.html', 'r') as f:
        html_content = f.read()

    # Replace Flask template syntax
    # Pattern 1: {{ url_for('static', filename='...') }} -> ./static/...
    import re

    # Replace all instances of {{ url_for('static', filename='...') }}
    html_content = re.sub(
        r"{{\s*url_for\('static',\s*filename='([^']+)'\)\s*}}",
        r'./static/\1',
        html_content
    )

    # Write converted HTML
    with open('docs/index.html', 'w') as f:
        f.write(html_content)

    print("  Assets copied successfully!")

def main():
    """Main build function."""
    print("Building static site...")
    print(f"Output directory: {OUTPUT_DIR}")

    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs('docs', exist_ok=True)

    # Load data
    print("\nLoading workout data...")
    df, category_df = load_workout_data()
    print(f"  Loaded {len(df)} workout records")
    print(f"  Unique exercises: {df['exercise_title'].nunique()}")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")

    # Generate JSON files
    print("\nGenerating simple JSON files...")
    generate_summary(df, category_df)
    generate_time_analysis(df)
    generate_big_three_analysis(df)
    generate_exercise_frequency(df)
    generate_exercise_volume(df)
    generate_weight_distribution(df)
    generate_reps_distribution(df)
    generate_category_analysis(category_df)
    generate_workout_balance(category_df)
    generate_workout_dates(df)
    generate_personal_records(df)
    generate_goal_setting(df)

    print("\nGenerating complex JSON files...")
    generate_monthly_summary(df)
    generate_category_exercises(category_df)
    generate_exercise_details(df)
    generate_recent_workouts(df)

    # Copy assets
    copy_assets()

    # Count generated files
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.json')]
    print(f"\nBuild complete!")
    print(f"Generated {len(json_files)} JSON files in {OUTPUT_DIR}/")
    print(f"Static site ready in docs/ directory")

if __name__ == '__main__':
    main()
