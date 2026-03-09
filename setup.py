"""
Quick setup script to initialize the swing-model project.

Run this after cloning the repository.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.10+ is being used."""
    if sys.version_info < (3, 10):
        print("✗ Error: Python 3.10 or higher is required")
        print(f"  Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def check_env_file():
    """Check if .env file exists, create from example if not."""
    env_path = Path(".env")
    example_path = Path(".env.example")

    if not env_path.exists():
        if example_path.exists():
            print("\n⚠ .env file not found")
            print("  Creating .env from .env.example...")
            example_path.read_text().replace(".env.example", ".env")
            with open(env_path, 'w') as f:
                f.write(example_path.read_text())
            print("✓ Created .env file")
            print("\n⚠ IMPORTANT: Edit .env and add your API keys:")
            print("  - FINNHUB_API_KEY (required)")
            print("  - EULERPOOL_API_KEY (optional for Phase 3)")
            print("  - DATABENTO_API_KEY (optional for Phase 1)")
            return False
        else:
            print("✗ Error: .env.example not found")
            return False
    else:
        print("✓ .env file exists")
        return True

def install_dependencies():
    """Install Python dependencies from requirements.txt."""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Error installing dependencies")
        return False

def create_database():
    """Create SQLite database with schema."""
    print("\nCreating database schema...")
    try:
        from data.db import create_tables
        create_tables()
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def main():
    """Run setup steps."""
    print("=" * 60)
    print("SWING MODEL - SETUP")
    print("=" * 60 + "\n")

    # Check Python version
    check_python_version()

    # Check/create .env file
    env_ready = check_env_file()

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Create database
    if not create_database():
        sys.exit(1)

    # Summary
    print("\n" + "=" * 60)
    if env_ready:
        print("✓ SETUP COMPLETE!")
        print("\nNext step: Run Phase 1 data pipeline")
        print("  python main.py")
    else:
        print("⚠ SETUP PARTIALLY COMPLETE")
        print("\nNext steps:")
        print("  1. Edit .env and add your API keys")
        print("  2. Run: python main.py")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
