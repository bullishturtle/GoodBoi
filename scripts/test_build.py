"""Test script to verify built executables work correctly."""
import subprocess
import sys
import time
from pathlib import Path
import httpx

def test_server():
    """Test backend server executable."""
    print("Testing backend server...")
    
    server_exe = Path("dist/GoodBoyServer/GoodBoyServer.exe")
    if not server_exe.exists():
        print(f"❌ Server executable not found: {server_exe}")
        return False
    
    # Start server
    print("Starting server...")
    proc = subprocess.Popen([str(server_exe)])
    
    # Wait for server to start
    time.sleep(5)
    
    # Test health endpoint
    try:
        response = httpx.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Server is responding correctly")
            result = True
        else:
            print(f"❌ Server returned status {response.status_code}")
            result = False
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        result = False
    
    # Stop server
    proc.terminate()
    proc.wait()
    
    return result

def test_ui():
    """Test desktop UI executable."""
    print("\nTesting desktop UI...")
    
    ui_exe = Path("dist/GoodBoy/GoodBoy.exe")
    if not ui_exe.exists():
        print(f"❌ UI executable not found: {ui_exe}")
        return False
    
    print(f"✓ UI executable exists: {ui_exe}")
    print("  (Manual testing required - launch the UI to verify)")
    return True

def test_installer():
    """Check installer was created."""
    print("\nChecking installer...")
    
    installer = Path("dist/installer/GoodBoy_AI_Setup.exe")
    if not installer.exists():
        print(f"❌ Installer not found: {installer}")
        return False
    
    size_mb = installer.stat().st_size / (1024 * 1024)
    print(f"✓ Installer exists: {installer} ({size_mb:.1f} MB)")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("GoodBoy.AI Build Verification")
    print("=" * 60)
    print()
    
    results = {
        "Server": test_server(),
        "UI": test_ui(),
        "Installer": test_installer(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("=" * 60))
    if all_passed:
        print("✓ All tests passed! Build is ready for distribution.")
    else:
        print("❌ Some tests failed. Review output above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
