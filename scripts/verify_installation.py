"""Verify GoodBoy.AI installation is complete and working."""
import sys
from pathlib import Path
import json

def check_mark(condition, msg):
    """Print check or X based on condition."""
    symbol = "✓" if condition else "✗"
    status = "OK" if condition else "MISSING"
    print(f"  [{symbol}] {msg}: {status}")
    return condition

def verify_structure():
    """Verify directory structure."""
    print("\n📁 Directory Structure")
    print("=" * 50)
    
    required_dirs = [
        Path("app"),
        Path("data"),
        Path("memory"),
        Path("models"),
        Path("logs"),
        Path("tests"),
        Path("installer"),
        Path("scripts"),
    ]
    
    all_good = True
    for d in required_dirs:
        exists = d.exists() and d.is_dir()
        check_mark(exists, str(d))
        all_good = all_good and exists
    
    return all_good

def verify_python_files():
    """Verify critical Python files exist."""
    print("\n🐍 Core Python Files")
    print("=" * 50)
    
    required_files = [
        Path("app/main.py"),
        Path("app/council.py"),
        Path("app/llm.py"),
        Path("app/memory.py"),
        Path("app/agents/base.py"),
        Path("app/agents/batman.py"),
        Path("app/agents/alfred.py"),
        Path("app/agents/jarvis.py"),
        Path("app/agents/davinci.py"),
        Path("app/agents/architect.py"),
        Path("app/agents/analyst.py"),
        Path("GoodBoy_ui.py"),
    ]
    
    all_good = True
    for f in required_files:
        exists = f.exists() and f.is_file()
        check_mark(exists, str(f))
        all_good = all_good and exists
    
    return all_good

def verify_build_files():
    """Verify build and installer files."""
    print("\n🔨 Build System Files")
    print("=" * 50)
    
    build_files = [
        Path("GoodBoy_ui.spec"),
        Path("GoodBoy_server.spec"),
        Path("installer/GoodBoy_installer.iss"),
        Path("build_full_installer.bat"),
        Path("requirements.txt"),
        Path("setup.ps1"),
    ]
    
    all_good = True
    for f in build_files:
        exists = f.exists() and f.is_file()
        check_mark(exists, str(f))
        all_good = all_good and exists
    
    return all_good

def verify_launcher_scripts():
    """Verify launcher scripts exist."""
    print("\n🚀 Launcher Scripts")
    print("=" * 50)
    
    scripts = [
        Path("GoodBoy_launcher.bat"),
        Path("run_server.bat"),
        Path("run_dashboard.bat"),
        Path("run_desktop_ui.bat"),
        Path("build_desktop_exe.bat"),
    ]
    
    all_good = True
    for s in scripts:
        exists = s.exists() and s.is_file()
        check_mark(exists, str(s))
        all_good = all_good and exists
    
    return all_good

def verify_config_files():
    """Verify configuration files."""
    print("\n⚙️ Configuration Files")
    print("=" * 50)
    
    # Check if config exists
    config_path = Path("data/GoodBoy_config.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            check_mark(True, "GoodBoy_config.json (valid JSON)")
            check_mark("engine" in config, "  - Has 'engine' setting")
            check_mark("model_path" in config, "  - Has 'model_path' setting")
        except Exception:
            check_mark(False, "GoodBoy_config.json (INVALID JSON)")
            return False
    else:
        check_mark(False, "GoodBoy_config.json")
        print("    Run scripts/post_install.py to create default config")
        return False
    
    # Check behavior instructions
    behavior_path = Path("data/Behavior_instructions.json")
    if behavior_path.exists():
        try:
            with open(behavior_path) as f:
                behavior = json.load(f)
            check_mark(True, "Behavior_instructions.json")
        except Exception:
            check_mark(False, "Behavior_instructions.json (INVALID JSON)")
            return False
    else:
        check_mark(False, "Behavior_instructions.json")
        print("    Run scripts/post_install.py to create default behavior")
    
    return True

def verify_dependencies():
    """Check if critical dependencies are installed."""
    print("\n📦 Python Dependencies")
    print("=" * 50)
    
    deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("httpx", "HTTPX"),
        ("gradio", "Gradio"),
    ]
    
    all_good = True
    for module_name, display_name in deps:
        try:
            __import__(module_name)
            check_mark(True, display_name)
        except ImportError:
            check_mark(False, display_name)
            all_good = False
    
    # Optional dependencies
    optional_deps = [
        ("gpt4all", "GPT4All (for local models)"),
        ("chromadb", "ChromaDB (for vector search)"),
        ("pypdf", "PyPDF (for PDF parsing)"),
    ]
    
    print("\n  Optional dependencies:")
    for module_name, display_name in optional_deps:
        try:
            __import__(module_name)
            check_mark(True, display_name)
        except ImportError:
            check_mark(False, display_name)
            print(f"    Note: {display_name} is optional but recommended")
    
    return all_good

def verify_documentation():
    """Check documentation files."""
    print("\n📚 Documentation")
    print("=" * 50)
    
    docs = [
        Path("README.md"),
        Path("BUILD_GUIDE.md"),
        Path("LICENSE.txt"),
        Path("installer/README_BEFORE.txt"),
        Path("installer/README_AFTER.txt"),
    ]
    
    all_good = True
    for d in docs:
        exists = d.exists() and d.is_file()
        check_mark(exists, str(d))
        all_good = all_good and exists
    
    return all_good

def main():
    """Run all verifications."""
    print("\n" + "=" * 50)
    print("  GoodBoy.AI Installation Verification")
    print("=" * 50)
    
    results = {
        "Structure": verify_structure(),
        "Python Files": verify_python_files(),
        "Build System": verify_build_files(),
        "Launchers": verify_launcher_scripts(),
        "Configuration": verify_config_files(),
        "Dependencies": verify_dependencies(),
        "Documentation": verify_documentation(),
    }
    
    print("\n" + "=" * 50)
    print("  Verification Summary")
    print("=" * 50)
    
    all_passed = True
    for category, passed in results.items():
        symbol = "✓" if passed else "✗"
        print(f"  [{symbol}] {category}")
        all_passed = all_passed and passed
    
    print("\n" + "=" * 50)
    if all_passed:
        print("  ✓ All checks passed!")
        print("  GoodBoy.AI is ready to build and deploy.")
        print("\n  Next steps:")
        print("  1. Run: .\\build_full_installer.bat")
        print("  2. Test: .\\scripts\\test_build.py")
        print("  3. Deploy: dist\\installer\\GoodBoy_AI_Setup.exe")
    else:
        print("  ✗ Some checks failed.")
        print("  Please review the issues above.")
        print("\n  Common fixes:")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Missing config: python scripts\\post_install.py")
        print("  - Missing files: Check git status and pull latest")
    
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
