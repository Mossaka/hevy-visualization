import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
import numpy as np

# Set style for plots
plt.style.use('ggplot')
sns.set(font_scale=1.2)

# Define exercise categories
EXERCISE_CATEGORIES = {
    'Chest': [
        'Bench Press', 'Incline Bench Press', 'Chest Press', 'Chest Fly', 
        'Decline Bench Press', 'Floor Press', 'Incline Chest Press'
    ],
    'Back': [
        'Dumbbell Row', 'Seated Cable Row', 'Bent Over Row', 'Lat Pulldown', 
        'Pull Up', 'Chin Up', 'T Bar Row', 'Iso-Lateral Row', 'Chest Supported Incline Row',
        'Single Arm Cable Row', 'Gorilla Row', 'Wide Pull Up'
    ],
    'Legs': [
        'Squat', 'Deadlift', 'Romanian Deadlift', 'Leg Press', 'Leg Extension',
        'Lying Leg Curl', 'Hip Thrust', 'Bulgarian Split Squat', 'Split Squat',
        'Walking Lunge', 'Hip Abduction', 'Hip Adduction', 'Seated Leg Curl',
        'Box step up', 'Sumo Deadlift'
    ],
    'Shoulders': [
        'Overhead Press', 'Shoulder Press', 'Lateral Raise', 'Rear Delt Reverse Fly',
        'Face Pull', 'Arnold Press'
    ],
    'Arms': [
        'Bicep Curl', 'Triceps Pushdown', 'Triceps Dip', 'Skullcrusher',
        'Preacher Curl', 'Triceps Extension', 'Triceps Rope Pushdown',
        'EZ Bar Biceps Curl', 'Floor Triceps Dip'
    ],
    'Core': [
        'Decline Crunch', 'Cable Crunch', 'Side Bend', 'Dragon Flag',
        'Plank', 'Ab Wheel', 'Jack Knife', 'Crunch', 'Landmine 180'
    ],
    'Other': []  # Will catch anything not in the above categories
}

def load_data(file_path):
    """Load workout data from CSV file."""
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    return df

def preprocess_data(df):
    """Preprocess the data for analysis."""
    print("\n=== Data Preprocessing ===")
    
    # Convert time columns to datetime
    df['start_time'] = pd.to_datetime(df['start_time'], format='%d %b %Y, %H:%M')
    df['end_time'] = pd.to_datetime(df['end_time'], format='%d %b %Y, %H:%M')
    
    # Calculate workout duration in minutes
    df['workout_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    
    # Fill missing numeric values with 0
    numeric_cols = ['weight_lbs', 'reps', 'distance_miles', 'duration_seconds', 'rpe']
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Calculate volume (weight * reps)
    df['volume'] = df['weight_lbs'] * df['reps']
    
    # Add exercise category
    df['category'] = df['exercise_title'].apply(categorize_exercise)
    
    print("Data preprocessing completed.")
    return df

def categorize_exercise(exercise_title):
    """Categorize exercise based on its title."""
    for category, exercises in EXERCISE_CATEGORIES.items():
        for exercise in exercises:
            if exercise.lower() in exercise_title.lower():
                return category
    return 'Other'

def analyze_categories(df):
    """Analyze workout data by exercise categories."""
    print("\n=== Category Analysis ===")
    
    # Create output directory for plots if it doesn't exist
    os.makedirs('category_plots', exist_ok=True)
    
    # Count exercises by category
    category_counts = df['category'].value_counts()
    print("\nExercise frequency by category:")
    print(category_counts)
    
    # Calculate total volume by category
    category_volume = df.groupby('category')['volume'].sum().reset_index()
    category_volume = category_volume.sort_values('volume', ascending=False)
    print("\nTotal volume by category:")
    print(category_volume)
    
    # Plot category distribution
    plt.figure(figsize=(12, 6))
    ax = category_counts.plot(kind='bar', color=sns.color_palette("viridis", len(category_counts)))
    plt.title('Exercise Distribution by Category')
    plt.xlabel('Category')
    plt.ylabel('Number of Sets')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('category_plots/category_distribution.png')
    print("Saved category distribution plot to category_plots/category_distribution.png")
    
    # Plot volume by category
    plt.figure(figsize=(12, 6))
    ax = category_volume.plot(kind='bar', x='category', y='volume', color=sns.color_palette("viridis", len(category_volume)))
    plt.title('Total Volume by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Volume (Weight × Reps)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('category_plots/category_volume.png')
    print("Saved category volume plot to category_plots/category_volume.png")
    
    # Analyze top exercises in each category
    for category in category_counts.index:
        analyze_category_exercises(df, category)
    
    return category_counts, category_volume

def analyze_category_exercises(df, category):
    """Analyze top exercises within a category."""
    category_df = df[df['category'] == category]
    
    if category_df.empty:
        print(f"No data found for category: {category}")
        return
    
    # Get top exercises by volume
    exercise_volume = category_df.groupby('exercise_title')['volume'].sum().reset_index()
    exercise_volume = exercise_volume.sort_values('volume', ascending=False)
    
    # Plot top exercises by volume
    plt.figure(figsize=(12, 6))
    top_n = min(10, len(exercise_volume))
    ax = exercise_volume.head(top_n).plot(
        kind='bar', 
        x='exercise_title', 
        y='volume',
        color=sns.color_palette("viridis", top_n)
    )
    plt.title(f'Top {top_n} {category} Exercises by Volume')
    plt.xlabel('Exercise')
    plt.ylabel('Total Volume (Weight × Reps)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'category_plots/{category.lower()}_top_exercises.png')
    print(f"Saved top {category} exercises plot to category_plots/{category.lower()}_top_exercises.png")
    
    # Calculate average weight and reps for top exercises
    top_exercises = exercise_volume.head(top_n)['exercise_title'].tolist()
    top_exercises_df = category_df[category_df['exercise_title'].isin(top_exercises)]
    
    exercise_stats = top_exercises_df.groupby('exercise_title').agg({
        'weight_lbs': ['mean', 'max'],
        'reps': ['mean', 'max'],
        'volume': ['mean', 'sum']
    }).reset_index()
    
    print(f"\nTop {category} exercises statistics:")
    print(exercise_stats)

def analyze_workout_balance(df):
    """Analyze workout balance across different muscle groups."""
    print("\n=== Workout Balance Analysis ===")
    
    # Calculate percentage of volume by category
    total_volume = df['volume'].sum()
    category_volume = df.groupby('category')['volume'].sum()
    category_percentage = (category_volume / total_volume * 100).reset_index()
    category_percentage.columns = ['category', 'percentage']
    category_percentage = category_percentage.sort_values('percentage', ascending=False)
    
    print("\nWorkout balance (percentage of total volume):")
    print(category_percentage)
    
    # Plot workout balance as a pie chart
    plt.figure(figsize=(10, 8))
    plt.pie(
        category_percentage['percentage'],
        labels=category_percentage['category'],
        autopct='%1.1f%%',
        startangle=90,
        colors=sns.color_palette("viridis", len(category_percentage))
    )
    plt.axis('equal')
    plt.title('Workout Volume Distribution by Category')
    plt.tight_layout()
    plt.savefig('category_plots/workout_balance_pie.png')
    print("Saved workout balance pie chart to category_plots/workout_balance_pie.png")
    
    # Plot workout balance as a horizontal bar chart
    plt.figure(figsize=(10, 6))
    ax = category_percentage.plot(
        kind='barh',
        x='category',
        y='percentage',
        color=sns.color_palette("viridis", len(category_percentage))
    )
    plt.title('Workout Volume Distribution by Category')
    plt.xlabel('Percentage of Total Volume')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig('category_plots/workout_balance_bar.png')
    print("Saved workout balance bar chart to category_plots/workout_balance_bar.png")
    
    return category_percentage

def analyze_intensity(df):
    """Analyze workout intensity by category."""
    print("\n=== Intensity Analysis ===")
    
    # Calculate average weight and reps by category
    intensity_stats = df.groupby('category').agg({
        'weight_lbs': ['mean', 'max'],
        'reps': ['mean', 'max'],
        'volume': ['mean', 'sum']
    }).reset_index()
    
    print("\nIntensity statistics by category:")
    print(intensity_stats)
    
    # Plot average weight by category
    plt.figure(figsize=(12, 6))
    category_weight = df.groupby('category')['weight_lbs'].mean().reset_index()
    category_weight = category_weight.sort_values('weight_lbs', ascending=False)
    
    ax = category_weight.plot(
        kind='bar',
        x='category',
        y='weight_lbs',
        color=sns.color_palette("viridis", len(category_weight))
    )
    plt.title('Average Weight by Category')
    plt.xlabel('Category')
    plt.ylabel('Average Weight (lbs)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('category_plots/category_weight.png')
    print("Saved category weight plot to category_plots/category_weight.png")
    
    # Plot average reps by category
    plt.figure(figsize=(12, 6))
    category_reps = df.groupby('category')['reps'].mean().reset_index()
    category_reps = category_reps.sort_values('reps', ascending=False)
    
    ax = category_reps.plot(
        kind='bar',
        x='category',
        y='reps',
        color=sns.color_palette("viridis", len(category_reps))
    )
    plt.title('Average Reps by Category')
    plt.xlabel('Category')
    plt.ylabel('Average Reps')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('category_plots/category_reps.png')
    print("Saved category reps plot to category_plots/category_reps.png")
    
    return intensity_stats

def main():
    """Main function to run the category analysis."""
    # Load data
    file_path = 'data/March 8, 2025.csv'
    df = load_data(file_path)
    
    # Preprocess data
    df = preprocess_data(df)
    
    # Analyze categories
    category_counts, category_volume = analyze_categories(df)
    
    # Analyze workout balance
    category_percentage = analyze_workout_balance(df)
    
    # Analyze intensity
    intensity_stats = analyze_intensity(df)
    
    print("\n=== Analysis Complete ===")
    print("Check the 'category_plots' directory for visualizations.")

if __name__ == "__main__":
    main() 