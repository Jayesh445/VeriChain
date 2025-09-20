#!/usr/bin/env python3
"""
Simple environment test script to debug configuration issues.
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🔍 Environment Debug Information")
print("=" * 50)

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")

# Check current directory
print(f"Current Directory: {os.getcwd()}")
print(f"Project Root: {project_root}")

# Check .env file
env_file = project_root / ".env"
print(f".env File Exists: {env_file.exists()}")

if env_file.exists():
    print(f".env File Path: {env_file}")
    with open(env_file, 'r') as f:
        lines = f.readlines()[:10]  # First 10 lines
        print("First 10 lines of .env:")
        for i, line in enumerate(lines, 1):
            print(f"  {i}: {line.strip()}")

# Check environment variables directly
print(f"\nEnvironment Variables:")
print(f"GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"GOOGLE_API_KEY: {'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f"DEBUG: {os.getenv('DEBUG', 'NOT SET')}")

# Try to load settings
print(f"\nTrying to load settings...")
try:
    from app.core.config import settings
    print(f"✅ Settings loaded successfully")
    print(f"App Name: {settings.app_name}")
    print(f"Debug Mode: {settings.debug}")
    print(f"Environment: {settings.environment}")
    print(f"API Key Present: {'YES' if settings.effective_api_key else 'NO'}")
    if settings.effective_api_key:
        print(f"API Key (first 10 chars): {settings.effective_api_key[:10]}...")
except Exception as e:
    print(f"❌ Settings loading failed: {e}")

# Check if we can import the main modules
print(f"\nTrying to import main modules...")
try:
    from app.agents.stationery_agent import StationeryInventoryAgent
    print(f"✅ StationeryInventoryAgent imported successfully")
except Exception as e:
    print(f"❌ StationeryInventoryAgent import failed: {e}")

print("=" * 50)
print("Debug complete!")