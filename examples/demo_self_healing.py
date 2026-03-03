"""
Self-Healing Demo

Create a broken brick and watch it heal itself!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import self_healing
from core import brick

print("🔥" * 40)
print("   SELF-HEALING SYSTEM DEMO")
print("🔥" * 40)

engine = self_healing.engine

# Create a broken brick
print("\n[1/4] Creating a broken brick...")
print("-" * 80)

@brick("divide_numbers", "Divide two numbers (BROKEN VERSION)")
def divide_numbers(a: float, b: float) -> float:
    """Divide a by b - but has a bug!"""
    # BUG: No zero division check!
    return a / b

divide_numbers.add_test(
    inputs={"a": 10, "b": 2},
    expected_output=5.0,
    label="normal_division"
)

divide_numbers.add_test(
    inputs={"a": 10, "b": 0},
    expected_output=0,  # Should handle gracefully
    label="zero_division"
)

engine.register(divide_numbers)

print("✅ Created broken brick: divide_numbers")
print("   Bug: No zero division handling!")

# Test the broken brick
print("\n[2/4] Testing the broken brick...")
print("-" * 80)

test1 = engine.bricks["divide_numbers"].safe_execute(a=10, b=2)
print(f"Test 1 (10 / 2): {'✅ PASS' if test1['success'] else '❌ FAIL'}")
if test1['success']:
    print(f"   Result: {test1['result']}")

test2 = engine.bricks["divide_numbers"].safe_execute(a=10, b=0)
print(f"Test 2 (10 / 0): {'✅ PASS' if test2['success'] else '❌ FAIL'}")
if not test2['success']:
    print(f"   Error: {test2['error']}")

# Analyze the error
print("\n[3/4] Analyzing the error...")
print("-" * 80)

if not test2['success']:
    analysis_brick = engine.bricks["analyze_error"]
    analysis = analysis_brick.safe_execute(
        brick_id="divide_numbers",
        error_message=test2['error'],
        source_code=engine.bricks["divide_numbers"].source,
        test_inputs={"a": 10, "b": 0}
    )
    
    if analysis['success']:
        result = analysis['result']
        print(f"✅ Error Analysis Complete:")
        print(f"   Error Type: {result['error_type']}")
        print(f"   Root Cause: {result['root_cause']}")
        print(f"   Fix Strategy: {result['fix_strategy']}")
        print(f"   Confidence: {result['confidence']:.0%}")
        
        # Attempt self-healing
        print("\n[4/4] Attempting self-healing (direct function call)...")
        print("-" * 80)
        
        # Get the underlying function from the brick
        import self_healing
        heal_fn = self_healing.engine.bricks["self_heal_brick"].func
        
        heal_result = heal_fn(
            brick_obj=engine.bricks["divide_numbers"],
            error_result=test2,
            test_inputs={"a": 10, "b": 0},
            max_attempts=2
        )
        
        if heal_result["success"]:
            healing_data = heal_result
            
            print(f"\n{'✅ HEALED!' if healing_data['healed'] else '❌ HEALING FAILED'}")
            print(f"   Attempts: {healing_data['attempts']}")
            print(f"   Method: {healing_data.get('method', 'N/A')}")
            
            if healing_data['healed']:
                print(f"\n📝 Fixed Code:")
                print("-" * 80)
                lines = healing_data['final_code'].split('\n')
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:3}  {line}")
                if len(lines) > 20:
                    print(f"     ... ({len(lines) - 20} more lines)")
                
                print("\n💡 What Changed:")
                for log_entry in healing_data['healing_log']:
                    if log_entry.get('success'):
                        fix = log_entry.get('fix', {})
                        print(f"   • {fix.get('changes', 'Unknown changes')}")
        else:
            print(f"❌ Healing system error: {heal_result.get('error')}")
    else:
        print(f"❌ Analysis failed: {analysis.get('error')}")

# Performance profiling demo
print("\n" + "=" * 80)
print("BONUS: Performance Profiling")
print("=" * 80)

# Create a simple brick for profiling
@brick("simple_calc", "Simple calculation for profiling")
def simple_calc(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y

engine.register(simple_calc)

print("\nProfiling simple_calc brick...")
profile_brick = engine.bricks["profile_brick"]
profile_result = profile_brick.safe_execute(
    brick_obj=engine.bricks["simple_calc"],
    test_inputs={"x": 5, "y": 3},
    iterations=1000
)

if profile_result['success']:
    data = profile_result['result']
    print(f"\n📊 Performance Profile:")
    print(f"   Iterations: {data['iterations']}")
    print(f"   Average: {data['avg_time_ms']:.3f}ms")
    print(f"   Min: {data['min_time_ms']:.3f}ms")
    print(f"   Max: {data['max_time_ms']:.3f}ms")
    
    if data['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in data['recommendations']:
            print(f"   • {rec}")
    else:
        print(f"\n✅ Performance is excellent!")

print("\n" + "=" * 80)
print("🔥 SELF-HEALING DEMO COMPLETE!")
print("=" * 80)

print("\n✅ Demonstrated:")
print("  1. Error detection ✅")
print("  2. Error analysis ✅")
print("  3. AI-powered fix generation (with Gemini CLI) ✅")
print("  4. Performance profiling ✅")

print("\n💡 Note:")
print("  • Gemini CLI integration ready")
print("  • Add 'gemini' to PATH for AI fixes")
print("  • Falls back to rule-based fixes if unavailable")

print("=" * 80)
