import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

# Set style for plots
plt.style.use('ggplot')
sns.set(font_scale=1.2)

def load_all_data(data_dir='data'):
    """Load all workout data from CSV files in the data directory."""
    print(f"Looking for CSV files in {data_dir}...")
    csv_files = glob.glob(f"{data_dir}/*.csv")
    
    if not csv_files:
        print("No CSV files found in the data directory.")
        return None
    
    print(f"Found {len(csv_files)} CSV files.")
    
    # Load and combine all CSV files
    all_data = []
    for file in csv_files:
        print(f"Loading {os.path.basename(file)}...")
        df = pd.read_csv(file)
        # Add file date as a column (extract from filename)
        file_date = os.path.basename(file).split('.')[0]
        df['file_date'] = file_date
        all_data.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"Combined data has {combined_df.shape[0]} rows and {combined_df.shape[1]} columns.")
    return combined_df

def preprocess_data(df):
    """Preprocess the data for analysis."""
    print("\n=== Data Preprocessing ===")
    
    # Convert time columns to datetime
    df['start_time'] = pd.to_datetime(df['start_time'], format='%d %b %Y, %H:%M')
    df['end_time'] = pd.to_datetime(df['end_time'], format='%d %b %Y, %H:%M')
    
    # Extract date from start_time
    df['workout_date'] = df['start_time'].dt.date
    
    # Calculate workout duration in minutes
    df['workout_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
    
    # Fill missing numeric values with 0
    numeric_cols = ['weight_lbs', 'reps', 'distance_miles', 'duration_seconds', 'rpe']
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Calculate volume (weight * reps)
    df['volume'] = df['weight_lbs'] * df['reps']
    
    print("Data preprocessing completed.")
    return df

def analyze_progress(df):
    """Analyze workout progress over time."""
    print("\n=== Progress Analysis ===")
    
    # Create output directory for plots if it doesn't exist
    os.makedirs('progress_plots', exist_ok=True)
    
    # Group by date and calculate total volume per workout
    daily_volume = df.groupby('workout_date')['volume'].sum().reset_index()
    daily_volume['workout_date'] = pd.to_datetime(daily_volume['workout_date'])
    
    # Plot total volume over time
    plt.figure(figsize=(12, 6))
    plt.plot(daily_volume['workout_date'], daily_volume['volume'], marker='o', linestyle='-')
    plt.title('Total Workout Volume Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Volume (Weight × Reps)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('progress_plots/volume_over_time.png')
    print("Saved volume over time plot to progress_plots/volume_over_time.png")
    
    # Analyze progress for specific exercises
    # Get top exercises by frequency
    top_exercises = df['exercise_title'].value_counts().head(5).index.tolist()
    
    for exercise in top_exercises:
        analyze_exercise_progress(df, exercise)
    
    # Analyze workout frequency
    workout_counts = df.groupby('workout_date').size().reset_index(name='count')
    workout_counts['workout_date'] = pd.to_datetime(workout_counts['workout_date'])
    
    # Plot workout frequency
    plt.figure(figsize=(12, 6))
    plt.bar(workout_counts['workout_date'], workout_counts['count'])
    plt.title('Workout Frequency')
    plt.xlabel('Date')
    plt.ylabel('Number of Workouts')
    plt.tight_layout()
    plt.savefig('progress_plots/workout_frequency.png')
    print("Saved workout frequency plot to progress_plots/workout_frequency.png")

def analyze_exercise_progress(df, exercise_name):
    """Analyze progress for a specific exercise."""
    exercise_df = df[df['exercise_title'] == exercise_name]
    
    if exercise_df.empty:
        print(f"No data found for exercise: {exercise_name}")
        return
    
    # Group by date and calculate max weight and average reps
    exercise_progress = exercise_df.groupby('workout_date').agg({
        'weight_lbs': 'max',
        'reps': 'mean',
        'volume': 'sum'
    }).reset_index()
    
    exercise_progress['workout_date'] = pd.to_datetime(exercise_progress['workout_date'])
    
    # Plot max weight over time
    plt.figure(figsize=(12, 6))
    plt.plot(exercise_progress['workout_date'], exercise_progress['weight_lbs'], marker='o', linestyle='-')
    plt.title(f'Max Weight for {exercise_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Max Weight (lbs)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'progress_plots/{exercise_name.replace(" ", "_").lower()}_weight_progress.png')
    print(f"Saved weight progress plot for {exercise_name} to progress_plots/{exercise_name.replace(' ', '_').lower()}_weight_progress.png")
    
    # Plot total volume over time
    plt.figure(figsize=(12, 6))
    plt.plot(exercise_progress['workout_date'], exercise_progress['volume'], marker='o', linestyle='-')
    plt.title(f'Total Volume for {exercise_name} Over Time')
    plt.xlabel('Date')
    plt.ylabel('Total Volume (Weight × Reps)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'progress_plots/{exercise_name.replace(" ", "_").lower()}_volume_progress.png')
    print(f"Saved volume progress plot for {exercise_name} to progress_plots/{exercise_name.replace(' ', '_').lower()}_volume_progress.png")

def calculate_personal_records(df):
    """Calculate personal records for each exercise."""
    print("\n=== Personal Records ===")
    
    # Get max weight for each exercise
    max_weight = df.groupby('exercise_title')['weight_lbs'].max().reset_index()
    max_weight = max_weight.sort_values('weight_lbs', ascending=False)
    
    print("Personal Records (Max Weight):")
    print(max_weight.head(10))
    
    # Get max volume for each exercise
    max_volume = df.groupby(['exercise_title', 'workout_date'])['volume'].sum().reset_index()
    max_volume = max_volume.sort_values('volume', ascending=False).drop_duplicates('exercise_title')
    max_volume = max_volume.sort_values('volume', ascending=False)
    
    print("\nPersonal Records (Max Volume in a Single Workout):")
    print(max_volume.head(10))
    
    # Get max reps for each exercise
    max_reps = df.groupby('exercise_title')['reps'].max().reset_index()
    max_reps = max_reps.sort_values('reps', ascending=False)
    
    print("\nPersonal Records (Max Reps):")
    print(max_reps.head(10))
    
    return max_weight, max_volume, max_reps

def main():
    """Main function to run the progress analysis."""
    # Load all data
    df = load_all_data()
    
    if df is None:
        print("No data to analyze. Please make sure you have CSV files in the data directory.")
        return
    
    # Preprocess data
    df = preprocess_data(df)
    
    # Analyze progress
    analyze_progress(df)
    
    # Calculate personal records
    max_weight, max_volume, max_reps = calculate_personal_records(df)
    
    print("\n=== Analysis Complete ===")
    print("Check the 'progress_plots' directory for visualizations.")

if __name__ == "__main__":
    main() 