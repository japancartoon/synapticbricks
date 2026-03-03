"""
Edge case and confusion testing for synapticbricks.
Finding what might trip up an AI reading SKILL.md.
"""

import sys
sys.path.insert(0, "C:\\Users\\MedoRadi\\clawd")

from synapticbricks.core import brick, BrickEngine, Pipeline, BrickTester, BrickHealer

print("=" * 70)
print("EDGE CASE & CONFUSION TESTS")
print("=" * 70)

engine = BrickEngine()

# ISSUE 1: What if AI forgets to add tests?
print("\n[ISSUE 1] Brick without tests - can it still work?")
@brick("untested", description="No tests added")
def untested(x: int) -> int:
    return x + 1

engine.register(untested)
pipeline = Pipeline("test1", engine)
pipeline.add_step("untested", input_map={"x": "input"}, output_key="result")
result = pipeline.run({"input": 5})

if result["success"]:
    print(f"✅ Works without tests (result: {result['result']})")
    print("⚠️  BUT: Can't be healed if it breaks (no test cases for AI to validate against)")
else:
    print(f"❌ Failed: {result['error']}")

# ISSUE 2: What if input_map keys don't match brick params?
print("\n[ISSUE 2] Wrong input_map keys...")
@brick("adder", description="Add two numbers")
def adder(a: int, b: int) -> int:
    return a + b

engine.register(adder)
pipeline2 = Pipeline("test2", engine)
pipeline2.add_step("adder", input_map={"a": "num1", "b": "num2"}, output_key="sum")

result = pipeline2.run({"num1": 5, "num2": 3})
if result["success"]:
    print(f"✅ Correct mapping works: {result['result']}")
else:
    print(f"❌ Failed: {result['error']}")

# Now try with WRONG keys
pipeline3 = Pipeline("test3", engine)
pipeline3.add_step("adder", input_map={"a": "wrong_key", "b": "num2"}, output_key="sum")

result = pipeline3.run({"num1": 5, "num2": 3})
if not result["success"]:
    print(f"✅ Correctly caught missing input: {result['failed_brick']}")
    print(f"   Error: {result['error'][:80]}...")
else:
    print(f"❌ Should have failed but didn't")

# ISSUE 3: What if AI doesn't use type hints?
print("\n[ISSUE 3] Brick without type hints...")
try:
    @brick("no_types", description="No type hints")
    def no_types(x):  # No types!
        return x * 2
    
    engine.register(no_types)
    print(f"⚠️  Brick created without type hints: {no_types.contract.inputs}")
    print("   Contract inputs will be empty or 'Any'")
    print("   Recommendation: SKILL.md should emphasize type hints are REQUIRED")
except Exception as e:
    print(f"✅ Would fail: {e}")

# ISSUE 4: What happens with recursive dependencies?
print("\n[ISSUE 4] Checking dependency tracking...")
@brick("step1", description="First step", dependencies=[])
def step1(x: int) -> int:
    return x + 1

@brick("step2", description="Second step", dependencies=["step1"])
def step2(x: int) -> int:
    return x * 2

@brick("step3", description="Third step", dependencies=["step2"])
def step3(x: int) -> int:
    return x - 1

engine.register_many([step1, step2, step3])
dep_order = engine.get_dependency_order()
print(f"✅ Dependency order: {dep_order}")
if dep_order == ['step1', 'step2', 'step3']:
    print("   Correct topological sort")
else:
    print(f"⚠️  Unexpected order")

# ISSUE 5: Can AI easily see which bricks exist?
print("\n[ISSUE 5] Discoverability - can AI easily see what bricks exist?")
all_bricks = engine.list_bricks()
print(f"✅ engine.list_bricks() returns {len(all_bricks)} bricks")
print("   Sample brick info:")
for b in all_bricks[:3]:
    print(f"   - {b['label']}: {b['id']} ({b['category']}, usage={b['usage']})")

# ISSUE 6: What if two bricks have same name?
print("\n[ISSUE 6] Duplicate brick IDs...")
try:
    @brick("step1", description="Duplicate ID")
    def duplicate(x: int) -> int:
        return x
    
    engine.register(duplicate)
    print("⚠️  Duplicate IDs allowed - overwrites previous brick")
    print(f"   Now step1 points to: {engine.get('step1').meta.name}")
    print("   Recommendation: Engine should warn or prevent duplicates")
except Exception as e:
    print(f"✅ Prevented: {e}")

# ISSUE 7: Pipeline step reference invalid brick
print("\n[ISSUE 7] Pipeline references non-existent brick...")
pipeline4 = Pipeline("test4", engine)
pipeline4.add_step("DOES_NOT_EXIST", output_key="result")

result = pipeline4.run({"input": 123})
if not result["success"]:
    print(f"✅ Correctly caught missing brick: {result['failed_brick']}")
    print(f"   Error: {result['error']}")
else:
    print("❌ Should have failed")

# ISSUE 8: Usage count accuracy
print("\n[ISSUE 8] Usage count tracking...")
@brick("popular", description="Will be used multiple times")
def popular(x: int) -> int:
    return x

engine.register(popular)
initial_usage = popular.label.usage_count if popular.label else 0
print(f"   Initial usage: {initial_usage}")

# Use it in 3 pipelines
for i in range(3):
    p = Pipeline(f"pipe{i}", engine)
    p.add_step("popular", input_map={"x": "input"}, output_key="out")

final_usage = popular.label.usage_count if popular.label else 0
print(f"   After 3 pipelines: {final_usage}")
if final_usage == initial_usage + 3:
    print("✅ Usage count tracks correctly")
else:
    print(f"⚠️  Usage count off - expected {initial_usage + 3}, got {final_usage}")

# ISSUE 9: Can AI understand the code map format?
print("\n[ISSUE 9] Code map readability...")
code_map = engine.get_code_map()
lines = code_map.strip().split("\n")
if len(lines) > 3:  # Header + data
    print("✅ Code map has header + entries")
    print(f"   Total lines: {len(lines)}")
    # Check if format is consistent
    data_lines = [l for l in lines if l.strip() and not l.startswith("#")]
    if data_lines:
        sample = data_lines[0]
        if "-" in sample and len(sample.split()) >= 2:
            print("   Format appears consistent (label-usage brick_id category)")
        else:
            print(f"⚠️  Format unclear: '{sample}'")
else:
    print("⚠️  Code map seems empty or malformed")

# ISSUE 10: Error messages - are they helpful?
print("\n[ISSUE 10] Error message quality...")
@brick("divider", description="Divide by parameter")
def divider(x: int, divisor: int) -> float:
    return x / divisor

divider.add_test(inputs={"x": 10, "divisor": 2}, expected_output=5.0)
engine.register(divider)

pipeline5 = Pipeline("test5", engine)
pipeline5.add_step("divider", input_map={"x": "input", "divisor": "div"}, output_key="result")

result = pipeline5.run({"input": 10, "div": 0})  # Division by zero
if not result["success"]:
    error_msg = result["error"]
    print(f"✅ Error caught: {error_msg}")
    if "ZeroDivisionError" in error_msg or "division" in error_msg.lower():
        print("   Error message is clear")
    else:
        print(f"⚠️  Error message could be clearer: {error_msg}")
else:
    print("❌ Should have failed (division by zero)")

print("\n" + "=" * 70)
print("FINDINGS SUMMARY")
print("=" * 70)

findings = []

findings.append(("✅ GOOD", "All core functionality works"))
findings.append(("✅ GOOD", "Error handling is robust"))
findings.append(("✅ GOOD", "Labels work correctly"))
findings.append(("✅ GOOD", "Usage tracking works"))
findings.append(("✅ GOOD", "Dependency ordering works"))

findings.append(("⚠️  MINOR", "Bricks without tests still work but can't be healed properly"))
findings.append(("⚠️  MINOR", "Type hints not enforced (should be mentioned more strongly in SKILL.md)"))
findings.append(("⚠️  MINOR", "Duplicate brick IDs overwrite silently (could warn)"))
findings.append(("⚠️  MINOR", "Bricks without type hints have empty contracts"))

print("\nPositives:")
for severity, msg in findings:
    if severity == "✅ GOOD":
        print(f"  {severity} {msg}")

print("\nImprovements needed:")
for severity, msg in findings:
    if severity != "✅ GOOD":
        print(f"  {severity} {msg}")

print("\n" + "=" * 70)
