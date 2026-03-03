"""Quick test of self-healing fix generation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from self_healing import generate_fix, analyze_error

src = '''@brick("test", "test")
def divide(a, b):
    return a / b'''

print("Testing fix generation...")
print("=" * 80)

# Analyze
analysis = analyze_error('test', 'ZeroDivisionError: division by zero', src, {})
print(f"\n1. Analysis Result:")
print(f"   Success: {analysis['success']}")
if analysis['success']:
    print(f"   Error Type: {analysis['error_type']}")
    print(f"   Fix Strategy: {analysis['fix_strategy']}")

# Generate fix
print(f"\n2. Generating Fix...")
fix = generate_fix('test', src, analysis, use_ai=True)
print(f"   Success: {fix['success']}")
if fix['success']:
    print(f"   Method: {fix.get('method')}")
    print(f"   Changes: {fix.get('changes')}")
    print(f"\n3. Fixed Code:")
    print("-" * 80)
    print(fix['fixed_code'])
else:
    print(f"   Error: {fix.get('error')}")

print("=" * 80)
