import sys
sys.path.insert(0, "C:\\Users\\MedoRadi\\clawd")

from synapticbricks.core import brick, BrickEngine

print("Testing warning messages...")
print()

# Test 1: No type hints
print("[TEST 1] Brick without type hints:")
@brick('no_types', description='Test')
def test_no_types(x):
    return x*2

engine = BrickEngine()
engine.register(test_no_types)

print()

# Test 2: No tests
print("[TEST 2] Brick without tests:")
@brick('no_tests', description='Test')
def test_no_tests(x: int) -> int:
    return x*2

engine.register(test_no_tests)

print()

# Test 3: Duplicate ID
print("[TEST 3] Duplicate brick ID:")
@brick('no_tests', description='Duplicate')
def test_duplicate(x: int) -> int:
    return x*3

engine.register(test_duplicate)

print()

# Test 4: All good
print("[TEST 4] Proper brick (should have no warnings):")
@brick('proper', description='Proper brick')
def test_proper(x: int) -> int:
    return x*2

test_proper.add_test(inputs={"x": 5}, expected_output=10)
engine.register(test_proper)

print()
print("All tests complete!")
