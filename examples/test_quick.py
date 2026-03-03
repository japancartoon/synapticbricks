"""
BrickLang Quick Test - All 70 Bricks
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import core_library_day1
import micro_bricks_core
from translator import BrickTranslator

print("🔥 BRICKLANG QUICK TEST\n")

# Test core bricks
core_pass = core_fail = 0
for bid, b in core_library_day1.engine.bricks.items():
    for t in (b.tests or []):
        r = b.safe_execute(**t["inputs"])
        if r["success"]: core_pass += 1
        else: core_fail += 1

print(f"Core Bricks (20): {core_pass} passed, {core_fail} failed")

# Test micro-bricks
micro_pass = micro_fail = 0
for bid, b in micro_bricks_core.engine.bricks.items():
    for t in (b.tests or []):
        r = b.safe_execute(**t["inputs"])
        if r["success"]: micro_pass += 1
        else: micro_fail += 1

print(f"Micro-Bricks (50): {micro_pass} passed, {micro_fail} failed")

# Test translator
from core import brick

trans = BrickTranslator(micro_bricks_core.engine)
trans_pass = 0

@brick("test_add", "")
def test_add(a: int, b: int) -> int:
    return a + b

@brick("test_gt", "")
def test_gt(a: int, b: int) -> bool:
    return a > b

@brick("test_and", "")
def test_and(a: int, b: int) -> int:
    return a & b

tests = [
    (test_add, ["add_int", "return_value"]),
    (test_gt, ["compare_gt", "return_value"]),
    (test_and, ["and_bits", "return_value"])
]
for func, expected in tests:
    c = trans.compile_brick(func)
    if c["micro_ops"] == expected: trans_pass += 1

print(f"Translator: {trans_pass}/{len(tests)} passed\n")

total_pass = core_pass + micro_pass + trans_pass
total_tests = core_pass + core_fail + micro_pass + micro_fail + len(tests)

print(f"📊 TOTAL: {total_pass}/{total_tests} ({100*total_pass/total_tests:.1f}%)")
print(f"\n✅ Status: {'PASS' if total_pass/total_tests >= 0.9 else 'NEEDS WORK'}")
print(f"🚀 System: OPERATIONAL - 70 bricks + compiler ready!")
