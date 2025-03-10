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
                    
                    # Check if we're in production environment (Render)
                    # Render sets RENDER=true for all services on their platform
                    is_production = os.environ.get('RENDER') == 'true'
                    if is_production:
                        # Use gunicorn in production
                        port = os.environ.get('PORT', '10000')
                        command = f"gunicorn app:app --bind=0.0.0.0:{port}="
                        print(f"Starting server in PRODUCTION mode on port {port}")
                    else:
                        # Use Flask development server locally
                        # Make sure we explicitly set host and port for Flask too
                        port = os.environ.get('PORT', '10000')
                        command = f"python app.py"
                        # Ensure PORT environment variable is accessible to the Flask app
                        os.environ['PORT'] = port
                    
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