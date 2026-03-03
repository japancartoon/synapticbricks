"""
Security Enforcement Demo — Test that dangerous bricks get REJECTED
"""
import sys
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import brick, BrickEngine, SecurityAuditor, SecurityError

print("="*70)
print("  SECURITY ENFORCEMENT DEMO")
print("  Testing automatic brick rejection")
print("="*70)
print()

# Create engine WITH security enforcement
auditor = SecurityAuditor(None)  # No engine yet
engine = BrickEngine(security_auditor=auditor, enforce_security=True, min_security_score=50)
auditor.engine = engine  # Wire them together

print("Engine configured with:")
print(f"  - Security enforcement: ENABLED")
print(f"  - Minimum security score: 50/100")
print()

# ============================================================================
# TEST 1: Try to register DANGEROUS brick (should be REJECTED)
# ============================================================================
print("="*70)
print("TEST 1: Attempting to register DANGEROUS brick (eval + os.system)")
print("="*70)
print()

@brick("evil_calc", description="Evil calculator")
def evil_calc(expression: str) -> float:
    """DANGEROUS: Uses eval on user input."""
    import os
    result = eval(expression)
    os.system("echo 'pwned'")
    return result

evil_calc.add_test(
    inputs={"expression": "2 + 2"},
    expected_output=4.0,
    label="test_basic"
)

try:
    engine.register(evil_calc)
    print("❌ TEST FAILED: Dangerous brick was allowed!")
except SecurityError as e:
    print(f"✅ TEST PASSED: Brick was rejected!")
    print(f"   Reason: {e}")

print()

# ============================================================================
# TEST 2: Register MODERATE brick (should WARN but ALLOW)
# ============================================================================
print("="*70)
print("TEST 2: Attempting to register MODERATE brick (weak error handling)")
print("="*70)
print()

@brick("divide", description="Divide two numbers")
def divide(a: int, b: int) -> float:
    """MODERATE: Has types but weak error handling."""
    try:
        return a / b
    except:  # Bare except - bad practice
        return None

divide.add_test(inputs={"a": 10, "b": 2}, expected_output=5.0, label="test_normal")

try:
    engine.register(divide)
    print(f"✅ TEST PASSED: Moderate brick was allowed (with warning)")
except SecurityError as e:
    print(f"❌ TEST FAILED: Moderate brick was rejected: {e}")

print()

# ============================================================================
# TEST 3: Register TRUSTED brick (should ALLOW silently)
# ============================================================================
print("="*70)
print("TEST 3: Attempting to register TRUSTED brick (clean + validated)")
print("="*70)
print()

@brick("safe_add", description="Safely add two numbers")
def safe_add(a: int, b: int) -> int:
    """TRUSTED: Type-safe, validated, well-tested."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both inputs must be integers")
    
    try:
        result = a + b
        if not isinstance(result, int):
            raise ValueError("Result validation failed")
        return result
    except OverflowError as e:
        raise ValueError(f"Overflow: {e}")

safe_add.add_test(inputs={"a": 2, "b": 3}, expected_output=5, label="test_basic")
safe_add.add_test(inputs={"a": 0, "b": 0}, expected_output=0, label="test_zero")

try:
    engine.register(safe_add)
    print(f"✅ TEST PASSED: Trusted brick was allowed")
except SecurityError as e:
    print(f"❌ TEST FAILED: Trusted brick was rejected: {e}")

print()

# ============================================================================
# TEST 4: Disable enforcement and try dangerous brick again
# ============================================================================
print("="*70)
print("TEST 4: Disable enforcement and retry dangerous brick")
print("="*70)
print()

engine.enforce_security = False
print("Security enforcement: DISABLED")
print()

try:
    engine.register(evil_calc)
    print(f"✅ TEST PASSED: With enforcement disabled, dangerous brick was allowed")
except SecurityError as e:
    print(f"❌ TEST FAILED: Brick still rejected even with enforcement disabled: {e}")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("="*70)
print("  ENFORCEMENT SUMMARY")
print("="*70)
print()

bricks = engine.list_bricks()
print(f"Registered bricks: {len(bricks)}")
for b in bricks:
    print(f"  - {b['id']}")

print()
print("="*70)
print("  Security enforcement works! Dangerous bricks are blocked.")
print("="*70)
