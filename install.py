"""GoodBoy.AI Installer - Setup wizard for first-time users."""
import sys
import subprocess
import os
from pathlib import Path
import json

def check_python():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher required")
        print(f"Current: Python {sys.version}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def create_directories():
    """Create required directories."""
    dirs = ["data", "models", "memory", "memory/docs", "logs"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Directories created")

def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    requirements = Path("requirements.txt")
    if not requirements.exists():
        print("ERROR: requirements.txt not found")
        sys.exit(1)
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        sys.exit(1)

def create_config():
    """Create default config if missing."""
    config_path = Path("data/GoodBoy_config.json")
    if not config_path.exists():
        config = {
            "engine": "cloud",
            "model_path": "models/",
            "cloud_api_base": "http://127.0.0.1:8000",
            "api_port": 8000,
            "max_tokens": 512,
            "temperature": 0.6,
            "user_name": "Mayor",
            "theme": "dark",
            "auto_start_server": True
        }
        config_path.write_text(json.dumps(config, indent=2))
        print("✓ Config created")
    else:
        print("✓ Config exists")

def create_behavior():
    """Create default behavior instructions."""
    behavior_path = Path("data/Behavior_instructions.json")
    if not behavior_path.exists():
        behavior = {
            "system_prompt": "You are GoodBoy.AI, a loyal and intelligent personal assistant. You are helpful, efficient, and always learning. You operate within Bathy City, a council-based AI architecture.",
            "personality_traits": [
                "loyal", "efficient", "learning", "helpful"
            ],
            "response_style": "concise and actionable",
            "voice_tone": "professional yet warm"
        }
        behavior_path.write_text(json.dumps(behavior, indent=2))
        print("✓ Behavior instructions created")
    else:
        print("✓ Behavior instructions exist")

def main():
    """Run the installer."""
    print("=" * 60)
    print("GoodBoy.AI Installer".center(60))
    print("=" * 60)
    print()
    
    print("Step 1: Checking Python...")
    check_python()
    print()
    
    print("Step 2: Creating directories...")
    create_directories()
    print()
    
    print("Step 3: Installing dependencies...")
    install_dependencies()
    print()
    
    print("Step 4: Creating configuration files...")
    create_config()
    create_behavior()
    print()
    
    print("=" * 60)
    print("Installation Complete!".center(60))
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Run: GoodBoy_launcher.bat")
    print("  2. Download a model using the Model Manager")
    print("  3. Start chatting!")
    print()

if __name__ == "__main__":
    main()
