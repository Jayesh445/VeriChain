#!/usr/bin/env python3
"""
Production server startup script with environment validation.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """Setup environment and validate configuration."""
    project_root = Path(__file__).parent.parent
    
    print("🔧 Setting up VeriChain Environment...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print(f"❌ Python 3.11+ required, found {sys.version}")
        return False
    
    # Check UV installation
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        print(f"✅ UV package manager: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ UV package manager not found")
        print("   Install UV: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    # Install dependencies
    print("📦 Installing dependencies...")
    os.chdir(project_root)
    
    install_result = subprocess.run(["uv", "install"], capture_output=True, text=True)
    if install_result.returncode != 0:
        print(f"❌ Failed to install dependencies: {install_result.stderr}")
        return False
    
    print("✅ Dependencies installed successfully")
    
    # Check environment variables
    required_env = {
        "GEMINI_API_KEY": "Google Gemini API key for AI agent functionality"
    }
    
    missing_env = []
    for env_var, description in required_env.items():
        if not os.getenv(env_var):
            missing_env.append((env_var, description))
    
    if missing_env:
        print("\n⚠️  Missing environment variables:")
        for var, desc in missing_env:
            print(f"   • {var}: {desc}")
        
        print("\nCreate a .env file in the project root with:")
        for var, _ in missing_env:
            print(f"   {var}=your_key_here")
        
        # Create sample .env file
        env_file = project_root / ".env.example"
        with open(env_file, "w") as f:
            f.write("# VeriChain Environment Configuration\n")
            f.write("# Copy this file to .env and fill in your values\n\n")
            for var, desc in required_env.items():
                f.write(f"# {desc}\n")
                f.write(f"{var}=\n\n")
        
        print(f"\n📄 Sample configuration saved to: {env_file}")
        return False
    
    print("✅ Environment variables configured")
    return True

def start_production_server():
    """Start the production server with proper configuration."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("\n🚀 Starting VeriChain Production Server...")
    
    # Set production environment
    os.environ["ENVIRONMENT"] = "production"
    os.environ["LOG_LEVEL"] = "INFO"
    
    try:
        # Start with UV
        subprocess.run([
            "uv", "run", "uvicorn", "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "4",
            "--log-level", "info",
            "--access-log"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server startup failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    
    return True

def start_development_server():
    """Start the development server with hot reload."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("\n🔧 Starting VeriChain Development Server...")
    
    # Set development environment
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DEBUG"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    try:
        # Start with UV and reload
        subprocess.run([
            "uv", "run", "python", "main.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server startup failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    
    return True

def main():
    """Main startup process."""
    print("=" * 60)
    print("🏪 VeriChain Stationery Inventory Management System")
    print("🤖 AI-Powered Auto-Ordering & Pattern Recognition")
    print("=" * 60)
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Environment setup failed")
        sys.exit(1)
    
    # Choose server mode
    mode = input("\nSelect server mode:\n  1) Development (with hot reload)\n  2) Production\n\nChoice (1/2): ").strip()
    
    if mode == "2":
        success = start_production_server()
    else:
        success = start_development_server()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()