"""Test all EPIC 3 Phase 1 bricks"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import epic3_phase1

print("🔥 TESTING 30 NEW BRICKS\n")

engine = epic3_phase1.engine
passed = failed = 0

for bid, b in engine.bricks.items():
    for t in (b.tests or []):
        r = b.safe_execute(**t["inputs"])
        if r["success"]:
            passed += 1
        else:
            failed += 1
            print(f"❌ {bid}: {r.get('error', 'Unknown')}")

total = passed + failed
print(f"\n📊 Results: {passed}/{total} passed ({100*passed/total:.1f}%)")
print(f"✅ Status: {'PERFECT!' if failed == 0 else f'{failed} failures'}")
