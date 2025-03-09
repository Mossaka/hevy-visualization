#!/usr/bin/env python
"""
Unified script to run all analysis and start the web dashboard.
This script will:
1. Run the basic analysis (analyze_workout.py)
2. Run the category analysis (analyze_categories.py)
3. Generate the HTML report (generate_report.py)
4. Start the web dashboard (app.py)
"""

import os
import sys
import subprocess
import time
import shutil
from datetime import datetime

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message} ".center(80, "="))
    print("=" * 80 + "\n")

def run_command(command, description):
    """Run a shell command and print its output."""
    print_header(description)
    print(f"Running command: {command}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode != 0:
            print(f"\nCommand failed with exit code {process.returncode}")
            return False
        
        print(f"\nCommand completed successfully.")
        return True
    
    except Exception as e:
        print(f"\nError running command: {e}")
        return False

def copy_plots_to_static():
    """Copy all plot images to the static directory for the web dashboard."""
    print_header("Copying plots to static directory")
    
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Copy plots from plots directory
    if os.path.exists('plots'):
        for filename in os.listdir('plots'):
            if filename.endswith('.png'):
                src = os.path.join('plots', filename)
                dst = os.path.join('static/images', filename)
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")
    
    # Copy plots from category_plots directory
    if os.path.exists('category_plots'):
        for filename in os.listdir('category_plots'):
            if filename.endswith('.png'):
                src = os.path.join('category_plots', filename)
                dst = os.path.join('static/images', filename)
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")
    
    # Copy plots from progress_plots directory
    if os.path.exists('progress_plots'):
        for filename in os.listdir('progress_plots'):
            if filename.endswith('.png'):
                src = os.path.join('progress_plots', filename)
                dst = os.path.join('static/images', filename)
                shutil.copy2(src, dst)
                print(f"Copied {src} to {dst}")
    
    print("\nAll plots copied to static/images directory.")

def update_index_html():
    """Update the index.html file to include static images."""
    print_header("Updating index.html to include static images")
    
    # Create a new section in the HTML file to display static images
    static_images_section = """
    <!-- Static Images Section -->
    <section id="static-images" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Static Visualizations</h2>
        
        <div class="bg-white shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Basic Analysis</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Exercise Frequency</h4>
                    <img src="{{ url_for('static', filename='images/exercise_frequency.png') }}" alt="Exercise Frequency" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Exercise Volume</h4>
                    <img src="{{ url_for('static', filename='images/exercise_volume.png') }}" alt="Exercise Volume" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Weight Distribution</h4>
                    <img src="{{ url_for('static', filename='images/weight_distribution.png') }}" alt="Weight Distribution" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Reps Distribution</h4>
                    <img src="{{ url_for('static', filename='images/reps_distribution.png') }}" alt="Reps Distribution" class="w-full rounded-lg">
                </div>
                <div class="md:col-span-2">
                    <h4 class="text-md font-medium text-gray-700 mb-2">Exercise Set Heatmap</h4>
                    <img src="{{ url_for('static', filename='images/exercise_set_heatmap.png') }}" alt="Exercise Set Heatmap" class="w-full rounded-lg">
                </div>
            </div>
        </div>
        
        <div class="mt-6 bg-white shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Category Analysis</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Category Distribution</h4>
                    <img src="{{ url_for('static', filename='images/category_distribution.png') }}" alt="Category Distribution" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Category Volume</h4>
                    <img src="{{ url_for('static', filename='images/category_volume.png') }}" alt="Category Volume" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Workout Balance (Pie)</h4>
                    <img src="{{ url_for('static', filename='images/workout_balance_pie.png') }}" alt="Workout Balance Pie" class="w-full rounded-lg">
                </div>
                <div>
                    <h4 class="text-md font-medium text-gray-700 mb-2">Workout Balance (Bar)</h4>
                    <img src="{{ url_for('static', filename='images/workout_balance_bar.png') }}" alt="Workout Balance Bar" class="w-full rounded-lg">
                </div>
            </div>
        </div>
        
        <div class="mt-6">
            <a href="{{ url_for('static', filename='../report/workout_analysis.html') }}" target="_blank" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                View Full HTML Report
            </a>
        </div>
    </section>
    """
    
    try:
        # Read the current index.html file
        with open('templates/index.html', 'r') as file:
            content = file.read()
        
        # Check if the static images section already exists
        if "<!-- Static Images Section -->" in content:
            print("Static images section already exists in index.html")
            return True
        
        # Insert the static images section before the footer
        new_content = content.replace("<!-- Footer -->", f"{static_images_section}\n\n    <!-- Footer -->")
        
        # Write the updated content back to the file
        with open('templates/index.html', 'w') as file:
            file.write(new_content)
        
        print("Successfully updated index.html with static images section.")
        return True
    
    except Exception as e:
        print(f"Error updating index.html: {e}")
        return False

def update_navbar():
    """Update the navbar in index.html to include the static images section."""
    print_header("Updating navbar in index.html")
    
    try:
        # Read the current index.html file
        with open('templates/index.html', 'r') as file:
            content = file.read()
        
        # Check if the static images link already exists
        if 'href="#static-images"' in content:
            print("Static images link already exists in navbar")
            return True
        
        # Add the static images link to the navbar
        navbar_links = """
                        <a href="#workout-balance" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Workout Balance
                        </a>
                        <a href="#static-images" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Static Images
                        </a>"""
        
        # Replace the existing navbar links
        new_content = content.replace(
            """
                        <a href="#workout-balance" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                            Workout Balance
                        </a>""", 
            navbar_links
        )
        
        # Write the updated content back to the file
        with open('templates/index.html', 'w') as file:
            file.write(new_content)
        
        print("Successfully updated navbar in index.html.")
        return True
    
    except Exception as e:
        print(f"Error updating navbar in index.html: {e}")
        return False

def main():
    """Main function to run all analysis and start the web dashboard."""
    start_time = datetime.now()
    print_header(f"Starting unified dashboard at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run basic analysis
    if not run_command("python analyze_workout.py", "Running Basic Analysis"):
        print("Basic analysis failed. Exiting.")
        return
    
    # Run category analysis
    if not run_command("python analyze_categories.py", "Running Category Analysis"):
        print("Category analysis failed. Exiting.")
        return
    
    # Generate HTML report
    if not run_command("python generate_report.py", "Generating HTML Report"):
        print("HTML report generation failed. Exiting.")
        return
    
    # Copy plots to static directory
    copy_plots_to_static()
    
    # Update index.html
    update_index_html()
    
    # Update navbar
    update_navbar()
    
    # Calculate elapsed time
    elapsed_time = datetime.now() - start_time
    print_header(f"Analysis completed in {elapsed_time.total_seconds():.2f} seconds")
    
    # Start the web dashboard
    print_header("Starting Web Dashboard")
    print("Access the dashboard at http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    try:
        # Try to use port 5000 first
        port = 5000
        command = f"python app.py"
        
        # Start the Flask app
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
            
            # If port 5000 is in use, try port 8000
            if "Address already in use" in line and "Port 5000 is in use" in line:
                print("\nPort 5000 is in use. Trying port 8000...")
                process.terminate()
                time.sleep(1)
                
                # Modify app.py to use port 8000
                with open('app.py', 'r') as file:
                    content = file.read()
                
                # Replace the app.run line
                if "app.run(debug=True)" in content:
                    new_content = content.replace(
                        "app.run(debug=True)", 
                        "app.run(host='0.0.0.0', port=8000, debug=True)"
                    )
                    
                    with open('app.py', 'w') as file:
                        file.write(new_content)
                    
                    print("Updated app.py to use port 8000")
                    
                    # Start the Flask app on port 8000
                    command = f"python app.py"
                    process = subprocess.Popen(
                        command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True
                    )
                    
                    # Print output in real-time
                    for line in process.stdout:
                        print(line, end='')
                    
                    break
        
        process.wait()
    
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"\nError starting web dashboard: {e}")

if __name__ == "__main__":
    main() 