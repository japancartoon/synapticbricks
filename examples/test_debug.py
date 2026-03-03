"""
BrickLang Debug Test - Find the 3 failing tests
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import core_library_day1
import micro_bricks_core

print("🔍 DEBUGGING FAILURES\n")

# Test core bricks and report failures
print("Core Bricks:")
print("-" * 60)
for bid, b in core_library_day1.engine.bricks.items():
    for i, t in enumerate(b.tests or []):
        r = b.safe_execute(**t["inputs"])
        if not r["success"]:
            print(f"❌ {bid} (test {i}):")
            print(f"   Inputs: {t['inputs']}")
            print(f"   Error: {r.get('error', 'Unknown')}")
            print()

# Test micro-bricks and report failures
print("\nMicro-Bricks:")
print("-" * 60)
for bid, b in micro_bricks_core.engine.bricks.items():
    for i, t in enumerate(b.tests or []):
        r = b.safe_execute(**t["inputs"])
        if not r["success"]:
            print(f"❌ {bid} (test {i}):")
            print(f"   Inputs: {t['inputs']}")
            print(f"   Error: {r.get('error', 'Unknown')}")
            print()

print("=" * 60)
print("DEBUG COMPLETE - Now we can fix them!")
