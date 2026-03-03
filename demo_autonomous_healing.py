"""
Autonomous Healing Demo  First Self-Healing Code in History
Shows SynapticBricks with AI brain wired up.

Usage:
    python demo_autonomous_healing.py YOUR_GEMINI_API_KEY
    
Or set environment variable:
    set GEMINI_API_KEY=your_key_here
    python demo_autonomous_healing.py
"""
import sys
import os
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import (
    brick, BrickEngine, BrickTester, BrickHealer, AIHealer
)

# Get API key from command line or environment
if len(sys.argv) > 1:
    API_KEY = sys.argv[1]
elif "GEMINI_API_KEY" in os.environ:
    API_KEY = os.environ["GEMINI_API_KEY"]
else:
    print("ERROR: No API key provided.")
    print("Usage: python demo_autonomous_healing.py YOUR_GEMINI_API_KEY")
    print("Or set GEMINI_API_KEY environment variable")
    sys.exit(1)

print("="*60)
print("  AUTONOMOUS HEALING DEMO")
print("  The world's first truly self-healing codebase")
print("="*60)
print()

# Step 1: Create a BROKEN brick
print(" Step 1: Creating a broken brick...")

@brick("calculator", description="Simple calculator")
def calculator(a: int, b: int, operation: str) -> int:
    """Perform basic arithmetic."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b  # BUG: Will crash on divide-by-zero
    else:
        raise ValueError(f"Unknown operation: {operation}")

# Add tests
calculator.add_test(
    inputs={"a": 10, "b": 5, "operation": "add"},
    expected_output=15,
    label="test_add"
)
calculator.add_test(
    inputs={"a": 10, "b": 0, "operation": "divide"},
    expected_output=None,  # Should handle gracefully
    label="test_divide_by_zero"
)
calculator.add_test(
    inputs={"a": 10, "b": 5, "operation": "multiply"},
    expected_output=50,
    label="test_multiply"
)

# Step 2: Register and test
print(" Step 2: Registering brick...")
engine = BrickEngine()
engine.register(calculator)

print(" Step 3: Running tests (should fail on divide-by-zero)...")
tester = BrickTester(engine)
brick_obj = engine.get("calculator")
result = tester.test_brick(brick_obj)
print(f"   Tests: {result['passed']} passed, {result['failed']} failed")

if result['failed'] > 0:
    failed_test = [r for r in result['results'] if not r['passed']][0]
    print(f"    Test '{failed_test['label']}' failed: {failed_test['error'][:60]}...")

# Step 3: Create AI Healer
print()
print(" Step 4: Initializing AI Healer with Gemini API...")
healer = BrickHealer(engine, tester)
ai_healer = AIHealer(API_KEY, engine=engine, healer=healer)

# Step 4: AUTONOMOUS HEALING
print(" Step 5: Attempting autonomous repair...")
print("   (This will call Gemini API to fix the code)")
print()

heal_result = ai_healer.auto_heal("calculator", apply=True)

if heal_result["success"]:
    print(f"    HEALING SUCCESSFUL!")
    print(f"   Model used: {heal_result['model_used']}")
    print(f"   Duration: {heal_result['duration_ms']:.1f}ms")
    print(f"   Attempts: {heal_result['attempts']}")
    
    if "pre_apply_test" in heal_result:
        pat = heal_result["pre_apply_test"]
        print(f"   Pre-apply test: {pat['passed']}/{pat['total']} passed")
    
    if "test_result" in heal_result:
        tr = heal_result["test_result"]
        print(f"   Post-apply test: {tr['passed']}/{tr['total']} passed")
        
        if tr["passed"] == tr["total"]:
            print()
            print(" BRICK FULLY HEALED  ALL TESTS PASSING")
            print()
            print("Fixed code preview:")
            print("-" * 60)
            print(heal_result["fixed_code"][:500] + "...")
            print("-" * 60)
        else:
            print("     Some tests still failing after heal")
    elif heal_result.get("applied") == False and "error" in heal_result:
        print(f"     {heal_result['error']}")
    else:
        print("   (Fix generated but not applied)")
else:
    print(f"    Healing failed: {heal_result.get('error', 'Unknown error')}")

# Step 5: Show stats
print()
print(" Step 6: Healing Statistics")
stats = ai_healer.get_stats()
print(f"   Total attempts: {stats['total_attempts']}")
print(f"   Success rate: {stats['success_rate']*100:.1f}%")
print(f"   Avg duration: {stats['avg_duration_ms']:.1f}ms")

if stats["by_model"]:
    print()
    print("   By model:")
    for model, data in stats["by_model"].items():
        print(f"     {model}: {data['successes']}/{data['attempts']} ({data['success_rate']*100:.0f}%)")

print()
print("="*60)
print("  Demo complete. This is the future of code.")
print("="*60)
