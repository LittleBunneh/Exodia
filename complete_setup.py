#!/usr/bin/env python3
"""Complete Setup Script for Exodia AI System
This script finalizes the deployment on PythonAnywhere"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class ExodiaSetup:
    """Handles complete Exodia setup and deployment"""
    
    def __init__(self):
        self.config = {}
        self.log_file = "setup_log.txt"
        
    def log(self, message):
        """Log setup progress"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def check_requirements(self):
        """Verify all required dependencies are installed"""
        self.log("Checking requirements...")
        required_packages = [
            "flask", "supabase", "requests", "python-dotenv",
            "openai", "flask-cors", "psycopg2"
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.log(f"✓ {package} found")
            except ImportError:
                missing.append(package)
                self.log(f"✗ {package} missing")
        
        if missing:
            self.log(f"Installing missing packages: {', '.join(missing)}")
            os.system(f"pip install {' '.join(missing)}")
        
        self.log("Requirements check complete")
    
    def create_env_file(self):
        """Create .env file with necessary configuration"""
        self.log("Creating .env configuration...")
        
        env_content = """# Exodia AI System - Environment Configuration
# Generated: {}

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# PythonAnywhere Configuration
PYTHONANYWHERE_USERNAME=your_pythonanywhere_username
PYTHONANYWHERE_API_TOKEN=your_pythonanywhere_api_token
PYTHONANYWHERE_DOMAIN=yourusername.pythonanywhere.com

# Application Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=change_this_to_a_random_secret_key
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost/exodia

# API Configuration
API_PORT=5000
API_HOST=0.0.0.0

# Security
CORS_ALLOWED_ORIGINS=*
MAX_CONTENT_LENGTH=16777216

# Logging
LOG_LEVEL=INFO
LOG_FILE=/tmp/exodia.log
""".format(datetime.now().isoformat())
        
        env_path = Path(".env")
        if not env_path.exists():
            with open(env_path, "w") as f:
                f.write(env_content)
            self.log("✓ Created .env file")
        else:
            self.log("⚠ .env already exists, skipping creation")
    
    def setup_directories(self):
        """Create necessary directory structure"""
        self.log("Setting up directory structure...")
        
        directories = [
            "logs",
            "data",
            "uploads",
            "cache",
            "backups"
        ]
        
        for dir_name in directories:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
            self.log(f"✓ Directory ensured: {dir_name}")
    
    def initialize_database(self):
        """Initialize Supabase database tables"""
        self.log("Initializing Supabase database...")
        
        try:
            from supabase_config import memory_manager
            if memory_manager:
                self.log("✓ Supabase connection successful")
                memory_manager.initialize_tables()
                self.log("✓ Database tables initialized")
            else:
                self.log("⚠ Supabase not configured, skipping DB init")
        except Exception as e:
            self.log(f"⚠ Database initialization failed: {e}")
    
    def test_apis(self):
        """Test critical API connections"""
        self.log("Testing API connections...")
        
        # Test DeepSeek
        try:
            import requests
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if api_key and api_key != "your_deepseek_api_key_here":
                response = requests.get(
                    "https://api.deepseek.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                if response.status_code == 200:
                    self.log("✓ DeepSeek API connection successful")
                else:
                    self.log(f"⚠ DeepSeek API returned {response.status_code}")
            else:
                self.log("⚠ DeepSeek API key not configured")
        except Exception as e:
            self.log(f"⚠ DeepSeek API test failed: {e}")
    
    def run_complete_setup(self):
        """Execute full setup sequence"""
        self.log("="*60)
        self.log("EXODIA COMPLETE SETUP STARTED")
        self.log("="*60)
        
        self.check_requirements()
        self.setup_directories()
        self.create_env_file()
        self.initialize_database()
        self.test_apis()
        
        self.log("="*60)
        self.log("EXODIA SETUP COMPLETE")
        self.log("="*60)
        self.log("\nNext steps:")
        self.log("1. Edit .env file with your actual credentials")
        self.log("2. Run: python main.py")
        self.log("3. Access at: http://localhost:5000")
        self.log("4. For PythonAnywhere: configure WSGI app")

if __name__ == "__main__":
    setup = ExodiaSetup()
    setup.run_complete_setup()
