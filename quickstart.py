"""Quick diagnostic and launch script for GoodBoy.AI."""
import sys
import subprocess
from pathlib import Path
import json

def print_header(text):
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def check_installation():
    """Run diagnostic checks."""
    print_header("GoodBoy.AI Quick Diagnostic")
    
    issues = []
    
    # Check Python
    print("Checking Python...")
    if sys.version_info < (3, 8):
        issues.append(f"Python 3.8+ required (found {sys.version})")
    else:
        print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check directories
    print("\nChecking directories...")
    dirs = ["data", "models", "memory", "app", "app/agents"]
    for d in dirs:
        if Path(d).exists():
            print(f"  ✓ {d}/")
        else:
            issues.append(f"Missing directory: {d}")
            print(f"  ✗ {d}/ MISSING")
    
    # Check config
    print("\nChecking configuration...")
    config_path = Path("data/GoodBoy_config.json")
    if config_path.exists():
        print("  ✓ GoodBoy_config.json")
    else:
        issues.append("Missing config file")
        print("  ✗ GoodBoy_config.json MISSING")
    
    # Check models
    print("\nChecking models...")
    models = list(Path("models").glob("*.gguf")) if Path("models").exists() else []
    if models:
        print(f"  ✓ Found {len(models)} model(s)")
        for m in models:
            size_mb = m.stat().st_size / (1024 * 1024)
            print(f"    - {m.name} ({size_mb:.1f} MB)")
    else:
        print("  ⚠ No models found")
        print("    Run Model Manager to download")
    
    # Check core files
    print("\nChecking core files...")
    core_files = ["GoodBoy_ui.py", "app/main.py", "app/council.py", "requirements.txt"]
    for f in core_files:
        if Path(f).exists():
            print(f"  ✓ {f}")
        else:
            issues.append(f"Missing file: {f}")
            print(f"  ✗ {f} MISSING")
    
    # Summary
    print("\n" + "=" * 60)
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  ✗ {issue}")
        print("\nRun 'python install.py' to fix issues")
        return False
    else:
        print("ALL CHECKS PASSED!".center(60))
        print("\nYou're ready to launch GoodBoy.AI")
        return True

def launch():
    """Launch GoodBoy.AI."""
    print_header("Launching GoodBoy.AI")
    
    try:
        print("Starting Desktop UI...")
        subprocess.Popen([sys.executable, "GoodBoy_ui.py"])
        print("✓ Launch successful!")
        print("\nGoodBoy.AI should open shortly...")
    except Exception as e:
        print(f"✗ Launch failed: {e}")
        print("\nTry running: python GoodBoy_ui.py")

if __name__ == "__main__":
    if check_installation():
        response = input("\nLaunch GoodBoy.AI now? (y/n): ").strip().lower()
        if response == 'y':
            launch()
