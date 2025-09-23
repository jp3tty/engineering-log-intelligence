"""
Interactive Demonstration for Day 20: Frontend Development
=========================================================

This script provides a step-by-step guide to demonstrate the Vue.js frontend
application we built on Day 20.

For beginners: This is a hands-on guide to see our frontend application
in action. It will show you how to start the development server and
explore the user interface.

Author: Engineering Log Intelligence Team
Date: September 22, 2025
"""

import subprocess
import time
import webbrowser
import os
import sys

def print_section_header(title):
    print(f"\n{'='*70}")
    print(f"--- {title.upper()} ---")
    print(f"{'='*70}")

def print_step(step_num, description):
    print(f"\n--- Step {step_num}: {description} ---")

def run_command(command, cwd=None, shell=True, capture_output=False):
    """Helper to run shell commands."""
    print(f"Executing: {command}")
    if capture_output:
        result = subprocess.run(command, cwd=cwd, shell=shell, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"Command failed with error:\n{result.stderr}")
        return result
    else:
        process = subprocess.Popen(command, cwd=cwd, shell=shell)
        return process

def check_node_installation():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ Node.js version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed or not in PATH")
        print("Please install Node.js from https://nodejs.org/")
        return False

def check_npm_installation():
    """Check if npm is installed."""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ npm version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed or not in PATH")
        return False

def install_dependencies(frontend_dir):
    """Install frontend dependencies."""
    print("Installing frontend dependencies...")
    try:
        result = subprocess.run(['npm', 'install'], cwd=frontend_dir, capture_output=True, text=True, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e.stderr}")
        return False

def start_frontend_server(frontend_dir):
    """Start the frontend development server."""
    print("Starting frontend development server...")
    try:
        process = subprocess.Popen(['npm', 'run', 'dev'], cwd=frontend_dir)
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def wait_for_server(url, timeout=60):
    """Wait for the frontend server to be ready."""
    print(f"Waiting for frontend server at {url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            import requests
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("✅ Frontend server is up and running!")
                return True
        except:
            pass
        time.sleep(1)
    print("❌ Frontend server did not start in time.")
    return False

def main():
    print_section_header("Day 20: Frontend Development Demonstration")
    print("Welcome to the interactive demo for Frontend Development!")
    print("Today, you'll learn how to build a modern Vue.js frontend application.")
    print("This frontend connects to our backend API and provides a beautiful user interface.")

    # Get project directory
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    frontend_dir = os.path.join(project_dir, 'frontend')

    print_step(1, "Checking Prerequisites")
    print("We need to make sure Node.js and npm are installed.")
    
    if not check_node_installation():
        print("\nPlease install Node.js and try again.")
        return
    
    if not check_npm_installation():
        print("\nPlease install npm and try again.")
        return

    print_step(2, "Installing Frontend Dependencies")
    print("We'll install all the required packages for our Vue.js application.")
    
    if not install_dependencies(frontend_dir):
        print("\nFailed to install dependencies. Please check the error messages above.")
        return

    print_step(3, "Starting Frontend Development Server")
    print("We'll start the Vite development server for our Vue.js application.")
    print("This will compile our code and serve it on http://localhost:3001")
    
    frontend_process = start_frontend_server(frontend_dir)
    if not frontend_process:
        print("\nFailed to start frontend server.")
        return

    # Wait for server to start
    if not wait_for_server("http://localhost:3001"):
        print("\nFrontend server did not start properly.")
        if frontend_process:
            frontend_process.terminate()
        return

    print_step(4, "Opening Application in Browser")
    print("We'll open the application in your default browser.")
    
    try:
        webbrowser.open("http://localhost:3001")
        print("✅ Application opened in browser!")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please manually open http://localhost:3001 in your browser")

    print_step(5, "Exploring the Application")
    print("""
    Now you can explore the Vue.js frontend application:

    🏠 Dashboard:
    - View system health and metrics
    - See recent activity
    - Monitor log processing statistics

    📊 Log Analysis:
    - Search and analyze log entries
    - Filter by different criteria
    - View detailed log information

    🧪 A/B Testing:
    - Manage A/B tests for ML models
    - Monitor test performance
    - View test results and statistics

    📈 Monitoring:
    - System monitoring dashboard
    - Real-time alerts and notifications
    - Performance metrics

    ⚙️ Settings:
    - User profile management
    - Application configuration
    - System preferences

    🔐 Authentication:
    - Login with demo credentials:
      - Admin: admin / password123
      - Analyst: analyst / password123
      - User: user / password123
    """)

    print_step(6, "Understanding the Frontend Architecture")
    print("""
    Our Vue.js frontend is built with modern web technologies:

    🎯 Vue.js 3:
    - Composition API for better code organization
    - Reactive data binding
    - Component-based architecture

    🎨 Tailwind CSS:
    - Utility-first CSS framework
    - Responsive design
    - Custom component styles

    🧭 Vue Router:
    - Client-side routing
    - Navigation between pages
    - Route guards for authentication

    🏪 Pinia State Management:
    - Centralized state management
    - Reactive stores for data
    - Easy to test and debug

    🔌 API Integration:
    - Axios for HTTP requests
    - Automatic token refresh
    - Error handling and loading states
    """)

    print_step(7, "Development Features")
    print("""
    The development server provides several useful features:

    🔥 Hot Module Replacement (HMR):
    - Changes are reflected instantly
    - No need to refresh the page
    - Preserves application state

    📱 Responsive Design:
    - Works on desktop, tablet, and mobile
    - Mobile-first approach
    - Touch-friendly interface

    🎨 Tailwind CSS:
    - Utility classes for styling
    - Consistent design system
    - Easy to customize

    🧪 Development Tools:
    - Vue DevTools browser extension
    - ESLint for code quality
    - Prettier for code formatting
    """)

    print_section_header("Day 20 Demo Complete")
    print("""
    🎉 Congratulations! You've successfully set up and explored the Vue.js frontend!

    What you've learned:
    ✅ How to set up a Vue.js application with Vite
    ✅ How to use Tailwind CSS for styling
    ✅ How to implement routing with Vue Router
    ✅ How to manage state with Pinia
    ✅ How to integrate with a backend API
    ✅ How to build responsive user interfaces

    Next steps:
    - Explore the code in the frontend/ directory
    - Try modifying components and see the changes
    - Add new features to the application
    - Learn more about Vue.js and modern frontend development

    The frontend is now ready for further development and can be deployed to Vercel!
    """)

    # Keep the server running
    print("\n🔄 Frontend server is running. Press Ctrl+C to stop it.")
    try:
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping frontend server...")
        frontend_process.terminate()
        print("✅ Frontend server stopped.")

if __name__ == "__main__":
    main()
