import subprocess
import sys
import os
from datetime import datetime

# ===============================
# FORCE PROJECT ROOT
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

def run_pytest():
    print("\n==============================")
    print("🧪 STARTING UNIT TEST SUITE")
    print("==============================\n")

    start_time = datetime.now()
    result = subprocess.run([
        sys.executable,
        "-m",
        "pytest",
        "-v",
        "--disable-warnings",
        "--maxfail=1",
        "-W", "ignore::UserWarning",
        "-W", "ignore::DeprecationWarning"
    ])
    end_time = datetime.now()

    print("\n==============================")
    print("📊 TEST SUMMARY")
    print("==============================\n")

    print(f"⏱ Duration: {end_time - start_time}")

    if result.returncode == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")

    return result.returncode

if __name__ == "__main__":
    sys.exit(run_pytest())