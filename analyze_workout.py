import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for plots
plt.style.use('ggplot')
sns.set(font_scale=1.2)

def load_data(file_path):
    """Load workout data from CSV file."""
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully with {df.shape[0]} rows and {df.shape[1]} columns.")
    return df

def basic_data_exploration(df):
    """Perform basic data exploration."""
    print("\n=== Basic Data Exploration ===")
    print("\nFirst few rows:")
    print(df.head())
    
    print("\nData types:")
    print(df.dtypes)
    
    print("\nSummary statistics:")
    print(df.describe())
    
    print("\nMissing values:")
    print(df.isnull().sum())
    
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
    
    print("Data preprocessing completed.")
    return df

def analyze_exercises(df):
    """Analyze exercises in the workout data."""
    print("\n=== Exercise Analysis ===")
    
    # Count unique exercises
    unique_exercises = df['exercise_title'].unique()
    print(f"Number of unique exercises: {len(unique_exercises)}")
    print("Unique exercises:", unique_exercises)
    
    # Exercise frequency
    exercise_counts = df['exercise_title'].value_counts()
    print("\nExercise frequency (sets per exercise):")
    print(exercise_counts)
    
    # Calculate average weight, reps, and volume (weight * reps) per exercise
    exercise_stats = df.groupby('exercise_title').agg({
        'weight_lbs': ['mean', 'max'],
        'reps': ['mean', 'max'],
    }).reset_index()
    
    # Calculate volume (weight * reps)
    df['volume'] = df['weight_lbs'] * df['reps']
    volume_stats = df.groupby('exercise_title')['volume'].sum().reset_index()
    
    print("\nExercise statistics:")
    print(exercise_stats)
    
    return exercise_counts, volume_stats

def visualize_data(df, exercise_counts, volume_stats):
    """Create visualizations for the workout data."""
    print("\n=== Data Visualization ===")
    
    # Create output directory for plots if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    
    # Plot 1: Exercise frequency
    plt.figure(figsize=(12, 8))
    ax = exercise_counts.head(10).plot(kind='bar')
    plt.title('Top 10 Exercises by Number of Sets')
    plt.xlabel('Exercise')
    plt.ylabel('Number of Sets')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/exercise_frequency.png')
    print("Saved exercise frequency plot to plots/exercise_frequency.png")
    
    # Plot 2: Total volume per exercise
    plt.figure(figsize=(12, 8))
    top_volume = volume_stats.sort_values('volume', ascending=False).head(10)
    ax = top_volume.plot(kind='bar', x='exercise_title', y='volume')
    plt.title('Top 10 Exercises by Total Volume (Weight × Reps)')
    plt.xlabel('Exercise')
    plt.ylabel('Total Volume')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('plots/exercise_volume.png')
    print("Saved exercise volume plot to plots/exercise_volume.png")
    
    # Plot 3: Weight distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df[df['weight_lbs'] > 0]['weight_lbs'], bins=20, kde=True)
    plt.title('Distribution of Weights Used')
    plt.xlabel('Weight (lbs)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('plots/weight_distribution.png')
    print("Saved weight distribution plot to plots/weight_distribution.png")
    
    # Plot 4: Reps distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df[df['reps'] > 0]['reps'], bins=15, kde=True)
    plt.title('Distribution of Reps')
    plt.xlabel('Reps')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('plots/reps_distribution.png')
    print("Saved reps distribution plot to plots/reps_distribution.png")
    
    # Plot 5: Heatmap of exercise vs set_index (to see progression patterns)
    pivot_df = df.pivot_table(
        index='exercise_title', 
        columns='set_index', 
        values='weight_lbs', 
        aggfunc='mean'
    ).fillna(0)
    
    plt.figure(figsize=(10, 12))
    sns.heatmap(pivot_df, cmap='YlGnBu', annot=True, fmt='.1f', linewidths=.5)
    plt.title('Average Weight by Exercise and Set Number')
    plt.xlabel('Set Number')
    plt.ylabel('Exercise')
    plt.tight_layout()
    plt.savefig('plots/exercise_set_heatmap.png')
    print("Saved exercise set heatmap to plots/exercise_set_heatmap.png")

def main():
    """Main function to run the analysis."""
    # Load data
    file_path = 'data/March 17, 2025.csv'
    df = load_data(file_path)
    
    # Explore and preprocess data
    df = basic_data_exploration(df)
    df = preprocess_data(df)
    
    # Analyze exercises
    exercise_counts, volume_stats = analyze_exercises(df)
    
    # Visualize data
    visualize_data(df, exercise_counts, volume_stats)
    
    print("\n=== Analysis Complete ===")
    print("Check the 'plots' directory for visualizations.")

if __name__ == "__main__":
    main() 