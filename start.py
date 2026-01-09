#!/usr/bin/env python3
"""
Startup script for the Ultra-Efficient Google Cloud Manager
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import streamlit
        import openai
        import google.cloud
        print("✅ All Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r ../../admin/shared/dependencies/google_cloud_agent.txt")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy env.example to .env and configure your settings")
        return False
    
    # Check for required environment variables
    required_vars = [
        "GOOGLE_CLOUD_PROJECT_ID",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    
    try:
        # Start the FastAPI server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running on http://localhost:8000")
                return process
            else:
                print("❌ API server failed to start properly")
                process.terminate()
                return None
        except Exception as e:
            print(f"❌ API server health check failed: {e}")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_streamlit_app():
    """Start the Streamlit web interface"""
    print("🚀 Starting Streamlit web interface...")
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", 
            "run", "app/interface/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
        # Wait a moment for the app to start
        time.sleep(5)
        
        print("✅ Streamlit web interface is running on http://localhost:8501")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit app: {e}")
        return None

def main():
    """Main startup function"""
    print("🚀 Ultra-Efficient Google Cloud Manager")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        sys.exit(1)
    
    # Start Streamlit app
    streamlit_process = start_streamlit_app()
    if not streamlit_process:
        api_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Google Cloud Manager is now running!")
    print("📊 Web Interface: http://localhost:8501")
    print("🔌 API Server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the processes running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if streamlit_process.poll() is not None:
                print("❌ Streamlit app stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if api_process:
            api_process.terminate()
            print("✅ API server stopped")
            
        if streamlit_process:
            streamlit_process.terminate()
            print("✅ Streamlit app stopped")
            
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 