"""
GoodBoy.AI Master Launcher
Handles all startup logic, diagnostics, and launch options.
"""
import sys
import subprocess
import os
from pathlib import Path
import json
import time

def print_banner():
    print("\n" + "=" * 70)
    print("  ____                 _ ____              _    ___")
    print(" / ___| ___   ___   __| | __ )  ___  _   _/ \\  |_ _|")
    print("| |  _ / _ \\ / _ \\ / _` |  _ \\ / _ \\| | | / _ \\  | |")
    print("| |_| | (_) | (_) | (_| | |_) | (_) | |_| / ___ \\ | |")
    print(" \\____|\\___/ \\___/ \\__,_|____/ \\___/ \\__, /_/   \\_\\___|")
    print("                                     |___/")
    print("\nSelf-Aware, Self-Learning Personal Assistant")
    print("=" * 70 + "\n")

def check_python():
    """Check Python version."""
    if sys.version_info < (3, 8):
        print(f"[X] ERROR: Python 3.8+ required (found {sys.version_info.major}.{sys.version_info.minor})")
        return False
    print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_files():
    """Check if core files exist."""
    required = ["GoodBoy_ui.py", "app/main.py", "app/council.py", "requirements.txt"]
    missing = [f for f in required if not Path(f).exists()]
    
    if missing:
        print("[X] ERROR: Missing core files:")
        for f in missing:
            print(f"   - {f}")
        return False
    print("[OK] Core files present")
    return True

def check_directories():
    """Ensure required directories exist."""
    dirs = ["data", "models", "memory", "memory/docs", "logs"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("[OK] Directories ready")
    return True

def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import gpt4all
        print("[OK] Core dependencies installed")
        return True
    except ImportError as e:
        print(f"[!] Warning: Some dependencies missing")
        print(f"   {e}")
        response = input("\nInstall now? (y/n): ").strip().lower()
        if response == 'y':
            return install_dependencies()
        return False

def install_dependencies():
    """Install required packages."""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_config():
    """Ensure config file exists."""
    config_path = Path("data/GoodBoy_config.json")
    if not config_path.exists():
        print("[!] Creating default configuration...")
        config = {
            "engine": "cloud",
            "model_path": "models/",
            "cloud_api_base": "http://127.0.0.1:8000",
            "api_port": 8000,
            "max_tokens": 512,
            "temperature": 0.6,
            "user_name": "Mayor",
            "theme": "dark",
            "auto_start_server": True,
            "show_chain_of_thought": True
        }
        config_path.write_text(json.dumps(config, indent=2))
        print("[OK] Configuration created")
    else:
        print("[OK] Configuration found")
    return True

def check_models():
    """Check if models are available."""
    models = list(Path("models").glob("*.gguf")) if Path("models").exists() else []
    if models:
        print(f"[OK] Found {len(models)} model(s):")
        for m in models[:3]:
            size_mb = m.stat().st_size / (1024 * 1024)
            print(f"   - {m.name} ({size_mb:.1f} MB)")
        return True
    else:
        print("[!] No models found")
        print("   You'll need to download a model using Model Manager")
        return True

def check_brain():
    """Check brain module."""
    try:
        from app.brain import get_brain
        brain = get_brain()
        print(f"[OK] Brain initialized - {brain.self_awareness.identity}")
        return True
    except Exception as e:
        print(f"[!] Brain module warning: {e}")
        return True  # Not critical

def start_server():
    """Start the FastAPI backend server."""
    print("\n[...] Starting GoodBoy.AI server...")
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)
        
        if process.poll() is None:
            print("[OK] Server started on http://127.0.0.1:8000")
            return process
        else:
            print("[X] Server failed to start")
            return None
    except Exception as e:
        print(f"[X] Error starting server: {e}")
        return None

def start_ui():
    """Start the desktop UI."""
    print("\n[...] Starting Desktop UI...")
    try:
        process = subprocess.Popen([sys.executable, "GoodBoy_ui.py"])
        print("[OK] UI launched")
        return process
    except Exception as e:
        print(f"[X] Error starting UI: {e}")
        return None

def main():
    """Main launcher logic."""
    print_banner()
    
    print("Running diagnostics...\n")
    
    if not check_python():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    if not check_files():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    check_directories()
    
    if not check_config():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    check_models()
    check_brain()  # Check brain module
    
    if not check_dependencies():
        print("\n[!] Cannot continue without dependencies")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("All checks passed! Ready to launch.")
    print("=" * 70)
    
    # Load config to determine startup mode
    try:
        config = json.loads(Path("data/GoodBoy_config.json").read_text())
        auto_start = config.get("auto_start_server", True)
        engine = config.get("engine", "cloud")
        show_chain_of_thought = config.get("show_chain_of_thought", True)
    except:
        auto_start = True
        engine = "cloud"
        show_chain_of_thought = True
    
    print(f"\nEngine: {engine.upper()}")
    print(f"Auto-start server: {auto_start}")
    print(f"Show chain of thought: {show_chain_of_thought}")
    
    processes = []
    
    # Start server if needed
    if auto_start and engine == "cloud":
        server_process = start_server()
        if server_process:
            processes.append(server_process)
        time.sleep(1)
    
    # Start UI
    ui_process = start_ui()
    if ui_process:
        processes.append(ui_process)
    
    if processes:
        print("\n" + "=" * 70)
        print("GoodBoy.AI is running!")
        print("=" * 70)
        print("\n💡 Tips:")
        print("   - Download a model using Tools → Model Manager")
        print("   - Adjust settings in Tools → Settings")
        print("   - GoodBoy learns from every conversation")
        print("\n   Close this window to shut down GoodBoy.AI")
        print("=" * 70)
        
        try:
            # Keep running until UI is closed
            ui_process.wait()
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        finally:
            # Clean up processes
            for p in processes:
                try:
                    p.terminate()
                    p.wait(timeout=5)
                except:
                    pass
    else:
        print("\n❌ Failed to launch GoodBoy.AI")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
