#!/usr/bin/env python
"""
2025 Comprehensive Workout Analysis Report Generator

This script analyzes all 2025 workout data from Hevy CSV exports and generates
a comprehensive markdown report covering:
- Progress and strength gains (PRs, 1RM progression)
- Training volume and frequency patterns
- Muscle group balance
- Q1 vs Later period comparisons
"""

import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime
from analyze_categories import EXERCISE_CATEGORIES, categorize_exercise

# Constants
DATA_DIR = 'data'
OUTPUT_FILE = '2025_workout_analysis_report.md'

# Major lifts to track for detailed PR analysis
MAJOR_LIFTS = [
    'Bench Press',
    'Deadlift',
    'Squat',
    'Overhead Press',
    'Pull Up',
    'Hip Thrust',
    'Romanian Deadlift'
]

def calculate_brzycki_1rm(weight, reps):
    """
    Calculate 1RM using Brzycki formula.
    Formula: 1RM = weight / (1.0278 - 0.0278 * reps)

    For reps > 10, uses alternative formula: weight * (1 + reps / 30)
    """
    if reps == 0 or weight == 0:
        return 0
    if reps == 1:
        return weight
    if reps > 10:
        return weight * (1 + reps / 30)
    return weight / (1.0278 - 0.0278 * reps)


def load_all_2025_data():
    """
    Load all 2025 CSV files and combine into a single dataframe.

    Returns:
        pd.DataFrame: Combined dataframe with all 2025 workout data
    """
    print("=" * 80)
    print("LOADING 2025 WORKOUT DATA")
    print("=" * 80)

    # Find all CSV files
    csv_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    csv_files = sorted(csv_files)

    print(f"\nFound {len(csv_files)} CSV files:")
    for f in csv_files:
        file_size_kb = os.path.getsize(f) / 1024
        print(f"  - {os.path.basename(f)} ({file_size_kb:.1f} KB)")

    # Load and combine all files
    dfs = []
    for file_path in csv_files:
        df_temp = pd.read_csv(file_path)
        # Extract file date from filename
        filename = os.path.basename(file_path)
        df_temp['file_source'] = filename
        dfs.append(df_temp)

    # Combine all dataframes
    df = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal rows loaded: {len(df):,}")

    # Preprocess data
    print("\nPreprocessing data...")

    # Convert datetime columns
    df['start_time'] = pd.to_datetime(df['start_time'], format='%d %b %Y, %H:%M')
    df['end_time'] = pd.to_datetime(df['end_time'], format='%d %b %Y, %H:%M')

    # Extract date and time components
    df['date'] = df['start_time'].dt.date
    df['month_num'] = df['start_time'].dt.month
    df['month'] = df['start_time'].dt.to_period('M')
    df['year'] = df['start_time'].dt.year

    # FILTER TO 2025 DATA ONLY
    print(f"\nFiltering to 2025 data only...")
    print(f"  Before filter: {len(df):,} rows")
    df = df[df['year'] == 2025].copy()
    print(f"  After filter: {len(df):,} rows (2025 only)")

    # Assign time period for 2025
    # Q1 = Jan-Mar, Q2 = Apr-Jun, Q3 = Jul-Sep, Q4 = Oct-Dec
    def assign_quarter(month):
        if month <= 3:
            return 'Q1'
        elif month <= 6:
            return 'Q2'
        elif month <= 9:
            return 'Q3'
        else:
            return 'Q4'

    df['quarter'] = df['month_num'].apply(assign_quarter)

    # Also keep the original period definition for comparison
    df['period'] = df['month_num'].apply(lambda m: 'Q1' if m <= 3 else 'Later')

    # Fill missing numeric values
    numeric_cols = ['weight_lbs', 'reps', 'distance_miles', 'duration_seconds', 'rpe']
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Calculate volume
    df['volume'] = df['weight_lbs'] * df['reps']

    # Calculate workout duration
    df['workout_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

    # Categorize exercises
    df['category'] = df['exercise_title'].apply(categorize_exercise)

    # Calculate estimated 1RM for each set
    df['estimated_1rm'] = df.apply(
        lambda row: calculate_brzycki_1rm(row['weight_lbs'], row['reps']),
        axis=1
    )

    print(f"  - Added time period labels (Q1, Later)")
    print(f"  - Calculated volume and 1RM estimates")
    print(f"  - Categorized {df['category'].nunique()} exercise categories")

    # Data summary
    print("\nData Summary:")
    print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  - Unique exercises: {df['exercise_title'].nunique()}")
    print(f"  - Total workouts: {df['title'].nunique()}")
    print(f"  - Q1 sets: {len(df[df['period'] == 'Q1']):,}")
    print(f"  - Later period sets: {len(df[df['period'] == 'Later']):,}")

    return df


def analyze_strength_progress(df):
    """
    Analyze strength progress and personal records.

    Returns:
        dict: Dictionary containing strength analysis results
    """
    print("\n" + "=" * 80)
    print("ANALYZING STRENGTH PROGRESS")
    print("=" * 80)

    # Filter to normal sets only (exclude warmup)
    working_sets = df[df['set_type'] == 'normal'].copy()

    # Filter out zero weights
    working_sets = working_sets[working_sets['weight_lbs'] > 0]

    # Calculate PRs per exercise
    prs = working_sets.groupby('exercise_title').agg({
        'weight_lbs': 'max',
        'estimated_1rm': 'max',
        'volume': 'sum',
        'set_index': 'count'
    }).reset_index()
    prs.columns = ['exercise', 'max_weight', 'max_1rm', 'total_volume', 'total_sets']
    prs = prs.sort_values('max_1rm', ascending=False)

    # Calculate PRs by period
    q1_prs = working_sets[working_sets['period'] == 'Q1'].groupby('exercise_title').agg({
        'weight_lbs': 'max',
        'estimated_1rm': 'max'
    }).reset_index()
    q1_prs.columns = ['exercise', 'q1_max_weight', 'q1_max_1rm']

    later_prs = working_sets[working_sets['period'] == 'Later'].groupby('exercise_title').agg({
        'weight_lbs': 'max',
        'estimated_1rm': 'max'
    }).reset_index()
    later_prs.columns = ['exercise', 'later_max_weight', 'later_max_1rm']

    # Merge to compare
    pr_comparison = q1_prs.merge(later_prs, on='exercise', how='outer').fillna(0)
    pr_comparison['weight_improvement'] = pr_comparison['later_max_weight'] - pr_comparison['q1_max_weight']
    pr_comparison['1rm_improvement'] = pr_comparison['later_max_1rm'] - pr_comparison['q1_max_1rm']
    pr_comparison['1rm_improvement_pct'] = pr_comparison.apply(
        lambda row: ((row['1rm_improvement'] / row['q1_max_1rm']) * 100) if row['q1_max_1rm'] > 0 else 0,
        axis=1
    )

    # Filter to exercises present in both periods
    pr_comparison = pr_comparison[
        (pr_comparison['q1_max_1rm'] > 0) & (pr_comparison['later_max_1rm'] > 0)
    ]
    pr_comparison = pr_comparison.sort_values('1rm_improvement_pct', ascending=False)

    # Monthly progression for major lifts
    monthly_progress = {}
    for lift in MAJOR_LIFTS:
        lift_data = working_sets[
            working_sets['exercise_title'].str.contains(lift, case=False, na=False)
        ]
        if not lift_data.empty:
            monthly = lift_data.groupby('month').agg({
                'weight_lbs': 'max',
                'estimated_1rm': 'max'
            }).reset_index()
            monthly_progress[lift] = monthly

    # Count exercises with new PRs
    improved_exercises = len(pr_comparison[pr_comparison['1rm_improvement'] > 0])
    stagnant_exercises = len(pr_comparison[pr_comparison['1rm_improvement'] <= 0])

    print(f"\nTotal PRs analyzed: {len(prs)}")
    print(f"Exercises with improvement: {improved_exercises}")
    print(f"Exercises with no improvement: {stagnant_exercises}")
    print(f"Average 1RM improvement: {pr_comparison['1rm_improvement_pct'].mean():.1f}%")

    return {
        'all_prs': prs,
        'pr_comparison': pr_comparison,
        'monthly_progress': monthly_progress,
        'improved_count': improved_exercises,
        'stagnant_count': stagnant_exercises,
        'avg_improvement_pct': pr_comparison['1rm_improvement_pct'].mean()
    }


def analyze_volume_frequency(df):
    """
    Analyze training volume and frequency patterns.

    Returns:
        dict: Dictionary containing volume and frequency analysis
    """
    print("\n" + "=" * 80)
    print("ANALYZING VOLUME AND FREQUENCY")
    print("=" * 80)

    # Volume analysis by period
    q1_data = df[df['period'] == 'Q1']
    later_data = df[df['period'] == 'Later']

    # Total volume
    q1_volume = q1_data['volume'].sum()
    later_volume = later_data['volume'].sum()
    volume_change_pct = ((later_volume - q1_volume) / q1_volume * 100) if q1_volume > 0 else 0

    # Workout frequency
    q1_workouts = q1_data['title'].nunique()
    later_workouts = later_data['title'].nunique()

    # Get date ranges for each period to calculate weeks
    q1_date_range = (q1_data['date'].max() - q1_data['date'].min()).days / 7
    later_date_range = (later_data['date'].max() - later_data['date'].min()).days / 7

    q1_workouts_per_week = q1_workouts / q1_date_range if q1_date_range > 0 else 0
    later_workouts_per_week = later_workouts / later_date_range if later_date_range > 0 else 0

    # Sets per period
    q1_sets = len(q1_data)
    later_sets = len(later_data)

    # Average volume per workout
    q1_avg_volume = q1_volume / q1_workouts if q1_workouts > 0 else 0
    later_avg_volume = later_volume / later_workouts if later_workouts > 0 else 0

    # Volume by category
    q1_category_volume = q1_data.groupby('category')['volume'].sum().reset_index()
    later_category_volume = later_data.groupby('category')['volume'].sum().reset_index()

    # Monthly volume progression
    monthly_volume = df.groupby('month').agg({
        'volume': 'sum',
        'title': 'nunique',
        'set_index': 'count'
    }).reset_index()
    monthly_volume.columns = ['month', 'total_volume', 'workouts', 'total_sets']
    monthly_volume['avg_volume_per_workout'] = monthly_volume['total_volume'] / monthly_volume['workouts']

    # Intensity metrics
    working_sets = df[df['set_type'] == 'normal']
    working_sets = working_sets[working_sets['weight_lbs'] > 0]

    # Rep range distribution
    def get_rep_range(reps):
        if reps <= 5:
            return 'Heavy (1-5)'
        elif reps <= 12:
            return 'Moderate (6-12)'
        else:
            return 'High (13+)'

    working_sets['rep_range'] = working_sets['reps'].apply(get_rep_range)

    q1_working = working_sets[working_sets['period'] == 'Q1']
    later_working = working_sets[working_sets['period'] == 'Later']

    q1_avg_weight = q1_working['weight_lbs'].mean()
    later_avg_weight = later_working['weight_lbs'].mean()

    q1_avg_reps = q1_working['reps'].mean()
    later_avg_reps = later_working['reps'].mean()

    q1_rep_dist = q1_working['rep_range'].value_counts(normalize=True) * 100
    later_rep_dist = later_working['rep_range'].value_counts(normalize=True) * 100

    # Exercise variety
    q1_exercises = q1_data['exercise_title'].nunique()
    later_exercises = later_data['exercise_title'].nunique()

    print(f"\nVolume Analysis:")
    print(f"  Q1 total volume: {q1_volume:,.0f} lbs")
    print(f"  Later total volume: {later_volume:,.0f} lbs")
    print(f"  Change: {volume_change_pct:+.1f}%")

    print(f"\nFrequency Analysis:")
    print(f"  Q1 workouts/week: {q1_workouts_per_week:.1f}")
    print(f"  Later workouts/week: {later_workouts_per_week:.1f}")

    return {
        'q1_volume': q1_volume,
        'later_volume': later_volume,
        'volume_change_pct': volume_change_pct,
        'q1_workouts': q1_workouts,
        'later_workouts': later_workouts,
        'q1_workouts_per_week': q1_workouts_per_week,
        'later_workouts_per_week': later_workouts_per_week,
        'q1_sets': q1_sets,
        'later_sets': later_sets,
        'q1_avg_volume': q1_avg_volume,
        'later_avg_volume': later_avg_volume,
        'q1_category_volume': q1_category_volume,
        'later_category_volume': later_category_volume,
        'monthly_volume': monthly_volume,
        'q1_avg_weight': q1_avg_weight,
        'later_avg_weight': later_avg_weight,
        'q1_avg_reps': q1_avg_reps,
        'later_avg_reps': later_avg_reps,
        'q1_rep_dist': q1_rep_dist,
        'later_rep_dist': later_rep_dist,
        'q1_exercises': q1_exercises,
        'later_exercises': later_exercises
    }


def analyze_muscle_balance(df):
    """
    Analyze muscle group balance and distribution.

    Returns:
        dict: Dictionary containing muscle group balance analysis
    """
    print("\n" + "=" * 80)
    print("ANALYZING MUSCLE GROUP BALANCE")
    print("=" * 80)

    # Calculate total volume by category and period
    q1_data = df[df['period'] == 'Q1']
    later_data = df[df['period'] == 'Later']

    # Volume distribution
    total_volume = df['volume'].sum()
    q1_total = q1_data['volume'].sum()
    later_total = later_data['volume'].sum()

    category_volume = df.groupby('category')['volume'].sum().reset_index()
    category_volume['percentage'] = (category_volume['volume'] / total_volume * 100)
    category_volume = category_volume.sort_values('percentage', ascending=False)

    q1_category = q1_data.groupby('category')['volume'].sum().reset_index()
    q1_category['percentage'] = (q1_category['volume'] / q1_total * 100)
    q1_category = q1_category.sort_values('percentage', ascending=False)

    later_category = later_data.groupby('category')['volume'].sum().reset_index()
    later_category['percentage'] = (later_category['volume'] / later_total * 100)
    later_category = later_category.sort_values('percentage', ascending=False)

    # Push vs Pull analysis
    push_categories = ['Chest', 'Shoulders']
    pull_categories = ['Back']

    push_volume = df[df['category'].isin(push_categories)]['volume'].sum()
    pull_volume = df[df['category'].isin(pull_categories)]['volume'].sum()
    push_pull_ratio = push_volume / pull_volume if pull_volume > 0 else 0

    q1_push = q1_data[q1_data['category'].isin(push_categories)]['volume'].sum()
    q1_pull = q1_data[q1_data['category'].isin(pull_categories)]['volume'].sum()
    q1_push_pull = q1_push / q1_pull if q1_pull > 0 else 0

    later_push = later_data[later_data['category'].isin(push_categories)]['volume'].sum()
    later_pull = later_data[later_data['category'].isin(pull_categories)]['volume'].sum()
    later_push_pull = later_push / later_pull if later_pull > 0 else 0

    # Upper vs Lower analysis
    upper_categories = ['Chest', 'Back', 'Shoulders', 'Arms']
    lower_categories = ['Legs']

    upper_volume = df[df['category'].isin(upper_categories)]['volume'].sum()
    lower_volume = df[df['category'].isin(lower_categories)]['volume'].sum()
    upper_lower_ratio = upper_volume / lower_volume if lower_volume > 0 else 0

    q1_upper = q1_data[q1_data['category'].isin(upper_categories)]['volume'].sum()
    q1_lower = q1_data[q1_data['category'].isin(lower_categories)]['volume'].sum()
    q1_upper_lower = q1_upper / q1_lower if q1_lower > 0 else 0

    later_upper = later_data[later_data['category'].isin(upper_categories)]['volume'].sum()
    later_lower = later_data[later_data['category'].isin(lower_categories)]['volume'].sum()
    later_upper_lower = later_upper / later_lower if later_lower > 0 else 0

    # Identify imbalances (categories < 15% of total volume)
    imbalanced = category_volume[
        (category_volume['percentage'] < 15) &
        (category_volume['category'].isin(['Chest', 'Back', 'Legs', 'Shoulders']))
    ]

    print(f"\nMuscle Group Distribution:")
    for _, row in category_volume.head(7).iterrows():
        print(f"  {row['category']}: {row['percentage']:.1f}%")

    print(f"\nPush:Pull Ratio: {push_pull_ratio:.2f}:1")
    print(f"Upper:Lower Ratio: {upper_lower_ratio:.2f}:1")

    return {
        'category_volume': category_volume,
        'q1_category': q1_category,
        'later_category': later_category,
        'push_pull_ratio': push_pull_ratio,
        'q1_push_pull': q1_push_pull,
        'later_push_pull': later_push_pull,
        'upper_lower_ratio': upper_lower_ratio,
        'q1_upper_lower': q1_upper_lower,
        'later_upper_lower': later_upper_lower,
        'imbalanced': imbalanced
    }


def analyze_quarterly_progression(df):
    """
    Analyze quarterly progression throughout 2025 to identify trends.

    Returns:
        dict: Dictionary containing quarterly analysis
    """
    print("\n" + "=" * 80)
    print("ANALYZING QUARTERLY PROGRESSION (2025)")
    print("=" * 80)

    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    quarterly_stats = {}

    for quarter in quarters:
        q_data = df[df['quarter'] == quarter]

        if len(q_data) == 0:
            continue

        # Calculate key metrics
        total_volume = q_data['volume'].sum()
        num_workouts = q_data['title'].nunique()
        avg_volume_per_workout = total_volume / num_workouts if num_workouts > 0 else 0
        total_sets = len(q_data)

        # Get top exercises by volume
        top_exercises = q_data.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(5)

        # Calculate max 1RMs for big three
        working_sets = q_data[(q_data['set_type'] == 'normal') & (q_data['weight_lbs'] > 0)]

        big_three_1rms = {}
        for lift in ['Bench Press', 'Squat', 'Deadlift']:
            lift_data = working_sets[working_sets['exercise_title'].str.contains(lift, case=False, na=False)]
            if not lift_data.empty:
                max_1rm = lift_data['estimated_1rm'].max()
                big_three_1rms[lift] = max_1rm

        quarterly_stats[quarter] = {
            'total_volume': total_volume,
            'num_workouts': num_workouts,
            'avg_volume_per_workout': avg_volume_per_workout,
            'total_sets': total_sets,
            'top_exercises': top_exercises,
            'big_three_1rms': big_three_1rms
        }

        print(f"\n{quarter}:")
        print(f"  Volume: {total_volume:,.0f} lbs")
        print(f"  Workouts: {num_workouts}")
        print(f"  Avg/workout: {avg_volume_per_workout:,.0f} lbs")
        if big_three_1rms:
            print(f"  Big 3 1RMs: {', '.join([f'{k}: {v:.0f}' for k, v in big_three_1rms.items()])}")

    return quarterly_stats


def compare_periods(df):
    """
    Compare Q1 vs Later periods in detail.

    Returns:
        dict: Dictionary containing period comparison analysis
    """
    print("\n" + "=" * 80)
    print("COMPARING TIME PERIODS")
    print("=" * 80)

    q1_data = df[df['period'] == 'Q1']
    later_data = df[df['period'] == 'Later']

    # Top exercises by volume
    q1_top = q1_data.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(10)
    later_top = later_data.groupby('exercise_title')['volume'].sum().sort_values(ascending=False).head(10)

    # Exercise changes
    q1_exercises = set(q1_data['exercise_title'].unique())
    later_exercises = set(later_data['exercise_title'].unique())

    new_exercises = later_exercises - q1_exercises
    dropped_exercises = q1_exercises - later_exercises
    common_exercises = q1_exercises & later_exercises

    # Average workout duration
    q1_duration = q1_data.groupby(['title', 'date'])['workout_duration'].first().mean()
    later_duration = later_data.groupby(['title', 'date'])['workout_duration'].first().mean()

    print(f"\nExercise Variety:")
    print(f"  Q1 exercises: {len(q1_exercises)}")
    print(f"  Later exercises: {len(later_exercises)}")
    print(f"  New exercises added: {len(new_exercises)}")
    print(f"  Exercises dropped: {len(dropped_exercises)}")

    return {
        'q1_top_exercises': q1_top,
        'later_top_exercises': later_top,
        'new_exercises': new_exercises,
        'dropped_exercises': dropped_exercises,
        'common_exercises': common_exercises,
        'q1_duration': q1_duration,
        'later_duration': later_duration
    }


def generate_markdown_report(analyses, df, output_path):
    """
    Generate comprehensive markdown report from analyses.

    Args:
        analyses: Dictionary containing all analysis results
        df: Original dataframe
        output_path: Path to save the markdown report
    """
    print("\n" + "=" * 80)
    print("GENERATING MARKDOWN REPORT")
    print("=" * 80)

    strength = analyses['strength']
    volume = analyses['volume']
    balance = analyses['balance']
    quarterly = analyses['quarterly']
    comparison = analyses['comparison']

    report_lines = []

    # Header
    report_lines.append("# 2025 Comprehensive Workout Analysis Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    report_lines.append(f"**Data Period:** {df['date'].min()} to {df['date'].max()}")
    report_lines.append(f"**Data Sources:** {df['file_source'].nunique()} CSV files")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    total_workouts = df['title'].nunique()
    total_volume = df['volume'].sum()
    total_exercises = df['exercise_title'].nunique()
    date_range_days = (df['date'].max() - df['date'].min()).days
    date_range_months = date_range_days / 30
    avg_workouts_per_week = total_workouts / (date_range_days / 7)

    report_lines.append(f"- **Total workouts analyzed:** {total_workouts}")
    report_lines.append(f"- **Total training volume:** {total_volume:,.0f} lbs")
    report_lines.append(f"- **Training period:** {date_range_months:.1f} months")
    report_lines.append(f"- **Unique exercises:** {total_exercises}")
    report_lines.append(f"- **Average workouts per week:** {avg_workouts_per_week:.1f}")
    report_lines.append("")

    report_lines.append("### Key Highlights")
    report_lines.append("")

    # Top improvement
    top_improvement = strength['pr_comparison'].head(1)
    if not top_improvement.empty:
        best_exercise = top_improvement.iloc[0]['exercise']
        best_gain = top_improvement.iloc[0]['1rm_improvement_pct']
        report_lines.append(f"- **Strongest improvement:** {best_exercise} (+{best_gain:.1f}% estimated 1RM)")

    # Most trained muscle group
    top_category = balance['category_volume'].iloc[0]
    report_lines.append(f"- **Most trained muscle group:** {top_category['category']} ({top_category['percentage']:.1f}% of volume)")

    # Volume trend
    volume_trend = "increasing" if volume['volume_change_pct'] > 0 else "decreasing"
    report_lines.append(f"- **Total weight moved:** {total_volume:,.0f} lbs")
    report_lines.append(f"- **Volume trend:** {volume_trend} ({volume['volume_change_pct']:+.1f}% from Q1 to Later)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Section 1: Strength Progress
    report_lines.append("## 1. Overall Progress and Strength Gains")
    report_lines.append("")

    report_lines.append("### 1.1 Personal Records Summary")
    report_lines.append("")
    report_lines.append("Top 15 exercises by estimated 1RM:")
    report_lines.append("")
    report_lines.append("| Exercise | Max Weight | Est. 1RM | Total Volume | Total Sets |")
    report_lines.append("|----------|------------|----------|--------------|------------|")

    for _, row in strength['all_prs'].head(15).iterrows():
        report_lines.append(
            f"| {row['exercise']} | {row['max_weight']:.0f} lbs | "
            f"{row['max_1rm']:.0f} lbs | {row['total_volume']:,.0f} | {row['total_sets']:.0f} |"
        )
    report_lines.append("")

    report_lines.append("### 1.2 Estimated 1RM Progression")
    report_lines.append("")
    report_lines.append("Major lifts tracked over time:")
    report_lines.append("")

    for lift, monthly_data in strength['monthly_progress'].items():
        if not monthly_data.empty:
            report_lines.append(f"**{lift}:**")
            first_1rm = monthly_data.iloc[0]['estimated_1rm']
            last_1rm = monthly_data.iloc[-1]['estimated_1rm']
            gain = last_1rm - first_1rm
            gain_pct = (gain / first_1rm * 100) if first_1rm > 0 else 0

            report_lines.append(f"- Starting 1RM: {first_1rm:.0f} lbs")
            report_lines.append(f"- Latest 1RM: {last_1rm:.0f} lbs")
            report_lines.append(f"- Total Gain: {gain:+.0f} lbs ({gain_pct:+.1f}%)")
            report_lines.append("")

    report_lines.append("### 1.3 Top 10 Strength Improvements")
    report_lines.append("")
    report_lines.append("Exercises with greatest 1RM gains from Q1 to Later:")
    report_lines.append("")
    report_lines.append("| Exercise | Q1 1RM | Later 1RM | Improvement | % Gain |")
    report_lines.append("|----------|--------|-----------|-------------|--------|")

    for _, row in strength['pr_comparison'].head(10).iterrows():
        report_lines.append(
            f"| {row['exercise']} | {row['q1_max_1rm']:.0f} lbs | "
            f"{row['later_max_1rm']:.0f} lbs | {row['1rm_improvement']:+.0f} lbs | "
            f"{row['1rm_improvement_pct']:+.1f}% |"
        )
    report_lines.append("")

    report_lines.append("### 1.4 Strength Trends")
    report_lines.append("")
    report_lines.append(f"- **Exercises hitting new PRs:** {strength['improved_count']} ({strength['improved_count'] / (strength['improved_count'] + strength['stagnant_count']) * 100:.0f}% of tracked exercises)")
    report_lines.append(f"- **Average improvement across all lifts:** +{strength['avg_improvement_pct']:.1f}%")

    # List stagnant exercises
    stagnant = strength['pr_comparison'][strength['pr_comparison']['1rm_improvement'] <= 0]
    if not stagnant.empty:
        report_lines.append(f"- **Exercises with no improvement:** {strength['stagnant_count']}")
        report_lines.append("")
        report_lines.append("  Exercises needing attention:")
        for _, row in stagnant.head(5).iterrows():
            report_lines.append(f"  - {row['exercise']}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Section 2: Volume and Frequency
    report_lines.append("## 2. Training Volume and Frequency")
    report_lines.append("")

    report_lines.append("### 2.1 Volume Overview")
    report_lines.append("")
    report_lines.append("**Q1 (March):**")
    report_lines.append(f"- Total volume: {volume['q1_volume']:,.0f} lbs")
    report_lines.append(f"- Average per workout: {volume['q1_avg_volume']:,.0f} lbs")
    report_lines.append(f"- Total sets: {volume['q1_sets']:,}")
    report_lines.append(f"- Workouts: {volume['q1_workouts']} sessions")
    report_lines.append("")
    report_lines.append("**Later Period (June-December):**")
    report_lines.append(f"- Total volume: {volume['later_volume']:,.0f} lbs ({volume['volume_change_pct']:+.1f}%)")
    report_lines.append(f"- Average per workout: {volume['later_avg_volume']:,.0f} lbs ({(volume['later_avg_volume'] - volume['q1_avg_volume']) / volume['q1_avg_volume'] * 100:+.1f}%)")
    report_lines.append(f"- Total sets: {volume['later_sets']:,} ({(volume['later_sets'] - volume['q1_sets']) / volume['q1_sets'] * 100:+.1f}%)")
    report_lines.append(f"- Workouts: {volume['later_workouts']} sessions")
    report_lines.append("")

    report_lines.append("### 2.2 Frequency Patterns")
    report_lines.append("")
    report_lines.append(f"- **Q1 Average:** {volume['q1_workouts_per_week']:.1f} workouts/week")
    report_lines.append(f"- **Later Period Average:** {volume['later_workouts_per_week']:.1f} workouts/week")
    freq_change = ((volume['later_workouts_per_week'] - volume['q1_workouts_per_week']) / volume['q1_workouts_per_week'] * 100) if volume['q1_workouts_per_week'] > 0 else 0
    report_lines.append(f"- **Change:** {freq_change:+.1f}%")
    report_lines.append("")

    report_lines.append("### 2.3 Volume Progression by Month")
    report_lines.append("")
    report_lines.append("| Month | Total Volume | Workouts | Avg Volume/Workout |")
    report_lines.append("|-------|--------------|----------|-------------------|")

    for _, row in volume['monthly_volume'].iterrows():
        report_lines.append(
            f"| {row['month']} | {row['total_volume']:,.0f} lbs | "
            f"{row['workouts']} | {row['avg_volume_per_workout']:,.0f} lbs |"
        )
    report_lines.append("")

    report_lines.append("### 2.4 Intensity Metrics")
    report_lines.append("")
    report_lines.append(f"- **Average weight per set:** Q1 {volume['q1_avg_weight']:.1f} lbs → Later {volume['later_avg_weight']:.1f} lbs ({(volume['later_avg_weight'] - volume['q1_avg_weight']) / volume['q1_avg_weight'] * 100:+.1f}%)")
    report_lines.append(f"- **Average reps per set:** Q1 {volume['q1_avg_reps']:.1f} → Later {volume['later_avg_reps']:.1f}")
    report_lines.append("")

    report_lines.append("**Rep Range Distribution:**")
    report_lines.append("")
    report_lines.append("Q1:")
    for rep_range in ['Heavy (1-5)', 'Moderate (6-12)', 'High (13+)']:
        pct = volume['q1_rep_dist'].get(rep_range, 0)
        report_lines.append(f"- {rep_range}: {pct:.1f}%")
    report_lines.append("")
    report_lines.append("Later Period:")
    for rep_range in ['Heavy (1-5)', 'Moderate (6-12)', 'High (13+)']:
        pct = volume['later_rep_dist'].get(rep_range, 0)
        report_lines.append(f"- {rep_range}: {pct:.1f}%")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Section 3: Muscle Group Balance
    report_lines.append("## 3. Muscle Group Balance")
    report_lines.append("")

    report_lines.append("### 3.1 Volume Distribution")
    report_lines.append("")
    report_lines.append("**Overall (2025):**")
    report_lines.append("")
    for _, row in balance['category_volume'].iterrows():
        report_lines.append(f"- **{row['category']}:** {row['percentage']:.1f}% ({row['volume']:,.0f} lbs)")
    report_lines.append("")

    report_lines.append("**Q1 vs Later Comparison:**")
    report_lines.append("")
    report_lines.append("| Category | Q1 % | Later % | Change |")
    report_lines.append("|----------|------|---------|--------|")

    # Merge Q1 and Later category data
    q1_dict = {row['category']: row['percentage'] for _, row in balance['q1_category'].iterrows()}
    later_dict = {row['category']: row['percentage'] for _, row in balance['later_category'].iterrows()}

    all_categories = set(q1_dict.keys()) | set(later_dict.keys())
    for cat in sorted(all_categories):
        q1_pct = q1_dict.get(cat, 0)
        later_pct = later_dict.get(cat, 0)
        change = later_pct - q1_pct
        report_lines.append(f"| {cat} | {q1_pct:.1f}% | {later_pct:.1f}% | {change:+.1f}% |")
    report_lines.append("")

    report_lines.append("### 3.2 Push vs Pull Analysis")
    report_lines.append("")
    report_lines.append(f"- **Overall Push:Pull Ratio:** {balance['push_pull_ratio']:.2f}:1")
    report_lines.append(f"- **Q1 Push:Pull Ratio:** {balance['q1_push_pull']:.2f}:1")
    report_lines.append(f"- **Later Push:Pull Ratio:** {balance['later_push_pull']:.2f}:1")
    report_lines.append("")

    # Recommendation
    if balance['push_pull_ratio'] > 1.5:
        report_lines.append("**Recommendation:** Consider increasing pulling movements (back exercises) to improve balance.")
    elif balance['push_pull_ratio'] < 0.7:
        report_lines.append("**Recommendation:** Consider increasing pushing movements (chest, shoulders) to improve balance.")
    else:
        report_lines.append("**Status:** Push/Pull ratio is well balanced.")
    report_lines.append("")

    report_lines.append("### 3.3 Upper vs Lower Split")
    report_lines.append("")
    report_lines.append(f"- **Overall Upper:Lower Ratio:** {balance['upper_lower_ratio']:.2f}:1")
    report_lines.append(f"- **Q1 Upper:Lower Ratio:** {balance['q1_upper_lower']:.2f}:1")
    report_lines.append(f"- **Later Upper:Lower Ratio:** {balance['later_upper_lower']:.2f}:1")
    report_lines.append("")

    # Recommendation
    if balance['upper_lower_ratio'] > 2.5:
        report_lines.append("**Recommendation:** Consider increasing lower body training volume.")
    elif balance['upper_lower_ratio'] < 1.5:
        report_lines.append("**Recommendation:** Consider increasing upper body training volume.")
    else:
        report_lines.append("**Status:** Upper/Lower split is reasonable.")
    report_lines.append("")

    report_lines.append("### 3.4 Muscle Group Focus Changes")
    report_lines.append("")

    # Identify categories with significant changes
    significant_changes = []
    for cat in all_categories:
        q1_pct = q1_dict.get(cat, 0)
        later_pct = later_dict.get(cat, 0)
        change = later_pct - q1_pct
        if abs(change) > 3:  # More than 3% change
            significant_changes.append((cat, change))

    if significant_changes:
        report_lines.append("Muscle groups with significant focus changes (>3%):")
        report_lines.append("")
        for cat, change in sorted(significant_changes, key=lambda x: abs(x[1]), reverse=True):
            direction = "increased" if change > 0 else "decreased"
            report_lines.append(f"- **{cat}:** {direction} by {abs(change):.1f}%")
    else:
        report_lines.append("No significant muscle group focus changes between periods.")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Section 4: Time Period Comparison
    report_lines.append("## 4. Time Period Comparison")
    report_lines.append("")

    report_lines.append("### 4.1 Q1 (March) Profile")
    report_lines.append("")
    report_lines.append(f"- **Training days:** {volume['q1_workouts']}")
    report_lines.append(f"- **Average session duration:** {comparison['q1_duration']:.1f} minutes")
    report_lines.append(f"- **Unique exercises:** {volume['q1_exercises']}")
    report_lines.append("")
    report_lines.append("**Most frequent exercises (by volume):**")
    for i, (exercise, vol) in enumerate(comparison['q1_top_exercises'].head(5).items(), 1):
        report_lines.append(f"{i}. {exercise}: {vol:,.0f} lbs")
    report_lines.append("")

    report_lines.append("### 4.2 Later Period (June-December) Profile")
    report_lines.append("")
    report_lines.append(f"- **Training days:** {volume['later_workouts']}")
    report_lines.append(f"- **Average session duration:** {comparison['later_duration']:.1f} minutes")
    report_lines.append(f"- **Unique exercises:** {volume['later_exercises']}")
    report_lines.append("")
    report_lines.append("**Most frequent exercises (by volume):**")
    for i, (exercise, vol) in enumerate(comparison['later_top_exercises'].head(5).items(), 1):
        report_lines.append(f"{i}. {exercise}: {vol:,.0f} lbs")
    report_lines.append("")

    report_lines.append("### 4.3 Key Changes")
    report_lines.append("")

    # Volume change
    if volume['volume_change_pct'] > 0:
        report_lines.append(f"- Training volume **increased** by {volume['volume_change_pct']:.1f}%")
    else:
        report_lines.append(f"- Training volume **decreased** by {abs(volume['volume_change_pct']):.1f}%")

    # Frequency change
    if freq_change > 0:
        report_lines.append(f"- Workout frequency **increased** by {freq_change:.1f}%")
    else:
        report_lines.append(f"- Workout frequency **decreased** by {abs(freq_change):.1f}%")

    # Duration change
    duration_change = ((comparison['later_duration'] - comparison['q1_duration']) / comparison['q1_duration'] * 100) if comparison['q1_duration'] > 0 else 0
    if duration_change > 0:
        report_lines.append(f"- Average workout duration **increased** by {duration_change:.1f}%")
    else:
        report_lines.append(f"- Average workout duration **decreased** by {abs(duration_change):.1f}%")

    report_lines.append("")

    report_lines.append("### 4.4 Exercise Variety")
    report_lines.append("")
    report_lines.append(f"- **Q1 unique exercises:** {len(comparison['common_exercises'] | comparison['dropped_exercises'])}")
    report_lines.append(f"- **Later unique exercises:** {len(comparison['common_exercises'] | comparison['new_exercises'])}")
    report_lines.append(f"- **New exercises added:** {len(comparison['new_exercises'])}")
    report_lines.append(f"- **Exercises dropped:** {len(comparison['dropped_exercises'])}")
    report_lines.append("")

    if comparison['new_exercises']:
        report_lines.append("**New exercises added:**")
        for ex in sorted(list(comparison['new_exercises']))[:10]:
            report_lines.append(f"- {ex}")
        report_lines.append("")

    if comparison['dropped_exercises']:
        report_lines.append("**Exercises dropped:**")
        for ex in sorted(list(comparison['dropped_exercises']))[:10]:
            report_lines.append(f"- {ex}")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Section 5: Quarterly Progression Analysis
    report_lines.append("## 5. Quarterly Progression Analysis (2025)")
    report_lines.append("")
    report_lines.append("This section breaks down your 2025 performance by quarter to identify trends and potential regression.")
    report_lines.append("")

    # Quarterly volume and workout trends
    report_lines.append("### 5.1 Volume Trends by Quarter")
    report_lines.append("")
    report_lines.append("| Quarter | Total Volume | Workouts | Avg Volume/Workout | Change from Previous |")
    report_lines.append("|---------|--------------|----------|-------------------|----------------------|")

    prev_vol = None
    for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
        if quarter in quarterly:
            stats = quarterly[quarter]
            quarter_volume = stats['total_volume']
            workouts = stats['num_workouts']
            avg_vol = stats['avg_volume_per_workout']

            if prev_vol is not None and prev_vol > 0:
                change = ((quarter_volume - prev_vol) / prev_vol * 100)
                change_str = f"{change:+.1f}%"
            else:
                change_str = "-"

            report_lines.append(
                f"| {quarter} | {quarter_volume:,.0f} lbs | {workouts} | {avg_vol:,.0f} lbs | {change_str} |"
            )
            prev_vol = quarter_volume

    report_lines.append("")

    # Big Three progression by quarter
    report_lines.append("### 5.2 Big Three 1RM Progression by Quarter")
    report_lines.append("")

    for lift in ['Bench Press', 'Squat', 'Deadlift']:
        report_lines.append(f"**{lift}:**")

        quarterly_1rms = []
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            if quarter in quarterly:
                big_three = quarterly[quarter]['big_three_1rms']
                if lift in big_three:
                    quarterly_1rms.append((quarter, big_three[lift]))

        if quarterly_1rms:
            for i, (quarter, rm) in enumerate(quarterly_1rms):
                if i > 0:
                    prev_rm = quarterly_1rms[i-1][1]
                    change = rm - prev_rm
                    change_pct = (change / prev_rm * 100) if prev_rm > 0 else 0
                    report_lines.append(f"- {quarter}: {rm:.0f} lbs ({change:+.0f} lbs, {change_pct:+.1f}%)")
                else:
                    report_lines.append(f"- {quarter}: {rm:.0f} lbs")
        else:
            report_lines.append("- No data available")

        report_lines.append("")

    # Q4 regression analysis
    if 'Q4' in quarterly and 'Q3' in quarterly:
        q4_vol = quarterly['Q4']['total_volume']
        q3_vol = quarterly['Q3']['total_volume']
        vol_change = ((q4_vol - q3_vol) / q3_vol * 100) if q3_vol > 0 else 0

        report_lines.append("### 5.3 Q4 Performance Analysis")
        report_lines.append("")

        if vol_change < -20:
            report_lines.append(f"**SIGNIFICANT REGRESSION DETECTED IN Q4:**")
            report_lines.append("")
            report_lines.append(f"- Volume dropped {abs(vol_change):.1f}% from Q3 to Q4")
        elif vol_change < 0:
            report_lines.append(f"**Q4 Performance Declined:**")
            report_lines.append("")
            report_lines.append(f"- Volume dropped {abs(vol_change):.1f}% from Q3 to Q4")
        else:
            report_lines.append(f"**Q4 Performance:**")
            report_lines.append("")
            report_lines.append(f"- Volume increased {vol_change:.1f}% from Q3 to Q4")

        report_lines.append(f"- Q4 workouts: {quarterly['Q4']['num_workouts']}")
        report_lines.append(f"- Q4 average volume per workout: {quarterly['Q4']['avg_volume_per_workout']:,.0f} lbs")

        # Check for 1RM regression in big three
        report_lines.append("")
        report_lines.append("**Big Three 1RM Changes (Q3 to Q4):**")

        if 'Q4' in quarterly and 'Q3' in quarterly:
            for lift in ['Bench Press', 'Squat', 'Deadlift']:
                q3_1rm = quarterly['Q3']['big_three_1rms'].get(lift)
                q4_1rm = quarterly['Q4']['big_three_1rms'].get(lift)

                if q3_1rm and q4_1rm:
                    change = q4_1rm - q3_1rm
                    change_pct = (change / q3_1rm * 100) if q3_1rm > 0 else 0

                    if change < 0:
                        report_lines.append(f"- {lift}: {q3_1rm:.0f} → {q4_1rm:.0f} lbs ({change:.0f} lbs, {change_pct:.1f}%) ⚠️ REGRESSION")
                    elif change == 0:
                        report_lines.append(f"- {lift}: {q3_1rm:.0f} → {q4_1rm:.0f} lbs (no change)")
                    else:
                        report_lines.append(f"- {lift}: {q3_1rm:.0f} → {q4_1rm:.0f} lbs ({change:+.0f} lbs, {change_pct:+.1f}%)")
                elif q3_1rm and not q4_1rm:
                    report_lines.append(f"- {lift}: Not performed in Q4 (Q3: {q3_1rm:.0f} lbs)")
                elif q4_1rm and not q3_1rm:
                    report_lines.append(f"- {lift}: {q4_1rm:.0f} lbs (not performed in Q3)")

        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Section 6: Recommendations (was Section 5)
    report_lines.append("## 6. Training Recommendations")
    report_lines.append("")

    report_lines.append("### 6.1 Strengths")
    report_lines.append("")

    # Identify strengths based on data
    strengths = []

    avg_improvement = strength['avg_improvement_pct']
    if avg_improvement > 10:
        strengths.append(f"Excellent overall strength progression ({avg_improvement:.1f}% average improvement)")

    vol_change = volume['volume_change_pct']
    if vol_change > 10:
        strengths.append(f"Strong volume progression over the year ({vol_change:+.1f}% increase)")

    push_pull = balance['push_pull_ratio']
    if 0.8 <= push_pull <= 1.3:
        strengths.append("Well-balanced push/pull training")

    later_freq = volume['later_workouts_per_week']
    if later_freq >= 3:
        strengths.append(f"Consistent training frequency ({later_freq:.1f} workouts/week)")

    if not strengths:
        strengths.append("Consistent training throughout the year")

    for strength_item in strengths:
        report_lines.append(f"- {strength_item}")
    report_lines.append("")

    report_lines.append("### 6.2 Areas for Improvement")
    report_lines.append("")

    # Identify areas for improvement
    improvements = []

    if balance['push_pull_ratio'] > 1.5:
        improvements.append("Increase back/pulling exercises to balance with pushing movements")

    if balance['upper_lower_ratio'] > 2.5:
        improvements.append("Add more lower body training volume")

    if strength['stagnant_count'] > strength['improved_count'] * 0.3:
        improvements.append(f"Address stagnant exercises ({strength['stagnant_count']} exercises with no improvement)")

    if not balance['imbalanced'].empty:
        for _, row in balance['imbalanced'].iterrows():
            improvements.append(f"Increase {row['category']} training volume (currently only {row['percentage']:.1f}%)")

    if not improvements:
        improvements.append("Continue current training approach - showing good overall balance")

    for improvement in improvements:
        report_lines.append(f"- {improvement}")
    report_lines.append("")

    report_lines.append("### 6.3 Suggested Focus Areas")
    report_lines.append("")

    # Top 3 exercises that showed great improvement - continue prioritizing
    top_3 = strength['pr_comparison'].head(3)
    if not top_3.empty:
        report_lines.append("**Continue prioritizing these high-performing exercises:**")
        for _, row in top_3.iterrows():
            report_lines.append(f"- {row['exercise']} (+{row['1rm_improvement_pct']:.1f}%)")
        report_lines.append("")

    # Bottom 3 exercises - need attention
    bottom_3 = strength['pr_comparison'].tail(3)
    if not bottom_3.empty and len(bottom_3[bottom_3['1rm_improvement'] <= 0]) > 0:
        report_lines.append("**Focus on improving these exercises:**")
        for _, row in bottom_3.iterrows():
            if row['1rm_improvement'] <= 0:
                report_lines.append(f"- {row['exercise']} (no improvement from Q1)")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    # Appendix
    report_lines.append("## Appendix")
    report_lines.append("")

    report_lines.append("### A. Exercise Categorization")
    report_lines.append("")
    report_lines.append("Exercises are categorized into the following muscle groups:")
    report_lines.append("")

    for category, exercises in EXERCISE_CATEGORIES.items():
        if exercises:
            report_lines.append(f"**{category}:** {', '.join(exercises)}")
        else:
            report_lines.append(f"**{category}:** (catches uncategorized exercises)")
    report_lines.append("")

    report_lines.append("### B. Data Sources")
    report_lines.append("")
    report_lines.append(f"- **Number of CSV files:** {df['file_source'].nunique()}")
    report_lines.append(f"- **Date range:** {df['date'].min()} to {df['date'].max()}")
    report_lines.append(f"- **Total data points:** {len(df):,} sets")
    report_lines.append("")
    report_lines.append("Files analyzed:")
    for file in sorted(df['file_source'].unique()):
        report_lines.append(f"- {file}")
    report_lines.append("")

    report_lines.append("### C. Methodology")
    report_lines.append("")
    report_lines.append("- **Volume calculation:** `weight_lbs × reps`")
    report_lines.append("- **1RM estimation:** Brzycki formula")
    report_lines.append("  - For reps ≤ 10: `weight / (1.0278 - 0.0278 × reps)`")
    report_lines.append("  - For reps > 10: `weight × (1 + reps / 30)`")
    report_lines.append("- **Time periods:** Q1 (January-March), Later (April-December)")
    report_lines.append("- **PR calculations:** Based on normal working sets only (warmup sets excluded)")
    report_lines.append("")

    # Write report to file
    report_content = '\n'.join(report_lines)
    with open(output_path, 'w') as f:
        f.write(report_content)

    print(f"\nReport successfully generated: {output_path}")
    print(f"Report length: {len(report_lines)} lines")


def main():
    """Main execution function."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "2025 WORKOUT ANALYSIS REPORT GENERATOR" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    print("")

    try:
        # Load data
        df = load_all_2025_data()

        # Run analyses
        strength_analysis = analyze_strength_progress(df)
        volume_analysis = analyze_volume_frequency(df)
        balance_analysis = analyze_muscle_balance(df)
        quarterly_analysis = analyze_quarterly_progression(df)
        comparison_analysis = compare_periods(df)

        # Generate report
        generate_markdown_report(
            analyses={
                'strength': strength_analysis,
                'volume': volume_analysis,
                'balance': balance_analysis,
                'quarterly': quarterly_analysis,
                'comparison': comparison_analysis
            },
            df=df,
            output_path=OUTPUT_FILE
        )

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"\nYour comprehensive 2025 workout analysis report is ready:")
        print(f"  📄 {OUTPUT_FILE}")
        print("\nOpen the file to view detailed insights, progress tracking, and recommendations.")
        print("")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
