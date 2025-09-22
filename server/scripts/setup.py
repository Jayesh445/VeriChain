#!/usr/bin/env python3
"""
VeriChain Agentic Supply Chain Management Setup Script
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 VeriChain Agentic Supply Chain Management Setup")
    print("="*60)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the server directory.")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -e .", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Initialize database
    if not run_command("python scripts/init_db.py", "Initializing database"):
        print("❌ Failed to initialize database.")
        sys.exit(1)
    
    # Seed database
    if not run_command("python scripts/seed_database.py", "Seeding database with sample data"):
        print("❌ Failed to seed database.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("🎯 Next steps:")
    print("   1. Set up your .env file with your Gemini API key:")
    print("      cp .env.example .env")
    print("      # Edit .env and add your GEMINI_API_KEY")
    print("   2. Start the server:")
    print("      python scripts/start_server.py")
    print("   3. Access the API documentation:")
    print("      http://localhost:8000/docs")
    print("   4. Test the AI agent:")
    print("      python scripts/test_agent.py")
    print("="*60)


if __name__ == "__main__":
    main()