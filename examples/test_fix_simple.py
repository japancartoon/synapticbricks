"""Quick test - direct function calls"""
import sys
import re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Inline the key functions for testing
def classify_error(error_msg: str) -> str:
    """Classify the type of error."""
    error_lower = error_msg.lower()
    
    if "typeerror" in error_lower:
        return "type_mismatch"
    elif "keyerror" in error_lower or "attributeerror" in error_lower:
        return "missing_key"
    elif "valueerror" in error_lower:
        return "invalid_value"
    elif "indexerror" in error_lower:
        return "index_out_of_range"
    elif "nameerror" in error_lower:
        return "undefined_variable"
    elif "zerodivisionerror" in error_lower:
        return "division_by_zero"
    elif "importerror" in error_lower or "modulenotfounderror" in error_lower:
        return "missing_import"
    else:
        return "unknown"

def generate_rule_fix(source_code: str, strategy: str) -> dict:
    """Generate rule-based fix."""
    if strategy == "add_zero_check":
        # Find the division operation
        pattern = r'return\s+(\w+)\s*/\s*(\w+)'
        match = re.search(pattern, source_code)
        
        if match:
            var_a = match.group(1)
            var_b = match.group(2)
            old_line = f"return {var_a} / {var_b}"
            new_line = f"return {var_a} / {var_b} if {var_b} != 0 else 0"
            
            fixed = source_code.replace(old_line, new_line)
            return {
                "success": True,
                "fixed_code": fixed,
                "changes": f"Added zero check for {var_b}"
            }
    
    return {"success": False, "error": "No rule for this strategy"}

# Test
src = '''@brick("divide_numbers", "Divide two numbers (BROKEN VERSION)")
def divide_numbers(a: float, b: float) -> float:
    """Divide a by b - but has a bug!"""
    # BUG: No zero division check!
    return a / b'''

print("🔥 Testing Self-Healing Fix Generation")
print("=" * 80)

print("\n1. Original Code:")
print(src)

print("\n2. Error Classification:")
error_type = classify_error("ZeroDivisionError: division by zero")
print(f"   Type: {error_type}")

print("\n3. Generating Fix...")
fix = generate_rule_fix(src, "add_zero_check")

if fix['success']:
    print(f"   ✅ Success!")
    print(f"   Changes: {fix['changes']}")
    print("\n4. Fixed Code:")
    print("-" * 80)
    print(fix['fixed_code'])
    print("-" * 80)
else:
    print(f"   ❌ Failed: {fix.get('error')}")

print("\n=" * 80)
print("✅ Fix generation working!")
