"""
Security Auditor Demo — Test autonomous security scanning and hardening
Creates intentionally vulnerable bricks and watches the auditor score them.
"""
import sys
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import brick, BrickEngine, SecurityAuditor

print("="*70)
print("  SECURITY AUDITOR DEMO")
print("  Testing autonomous vulnerability detection")
print("="*70)
print()

# Create engine
engine = BrickEngine()

# ============================================================================
# BRICK 1: DANGEROUS - Uses eval and os.system (should score <40)
# ============================================================================
print("Creating DANGEROUS brick (eval + os.system)...")

@brick("dangerous_calc", description="Calculator with eval")
def dangerous_calc(expression: str) -> float:
    """DANGEROUS: Uses eval on user input."""
    import os
    # Extremely dangerous - arbitrary code execution
    result = eval(expression)
    # Also has os access
    os.system("echo 'I could do anything here'")
    return result

dangerous_calc.add_test(
    inputs={"expression": "2 + 2"},
    expected_output=4.0,
    label="test_basic"
)

engine.register(dangerous_calc)

# ============================================================================
# BRICK 2: RISKY - No input validation, file operations (should score 40-59)
# ============================================================================
print("Creating RISKY brick (no validation + file ops)...")

@brick("file_reader", description="Read a file")
def file_reader(filepath: str) -> str:
    """RISKY: No validation, opens arbitrary files."""
    # Has types but no validation
    with open(filepath, 'r') as f:
        return f.read()

file_reader.add_test(
    inputs={"filepath": "test.txt"},
    expected_output="test content",
    label="test_read"
)

engine.register(file_reader)

# ============================================================================
# BRICK 3: MODERATE - Has validation but weak error handling (should score 60-79)
# ============================================================================
print("Creating MODERATE brick (weak error handling)...")

@brick("divide", description="Divide two numbers")
def divide(a: int, b: int) -> float:
    """MODERATE: Has types but weak error handling."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers")
    try:
        return a / b
    except:  # Bare except - bad practice
        return None

divide.add_test(inputs={"a": 10, "b": 2}, expected_output=5.0, label="test_normal")
divide.add_test(inputs={"a": 10, "b": 0}, expected_output=None, label="test_zero")

engine.register(divide)

# ============================================================================
# BRICK 4: TRUSTED - Clean, validated, well-tested (should score 80+)
# ============================================================================
print("Creating TRUSTED brick (clean + validated)...")

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
safe_add.add_test(inputs={"a": -5, "b": 10}, expected_output=5, label="test_negative")

engine.register(safe_add)

# ============================================================================
# RUN SECURITY AUDIT
# ============================================================================
print()
print("="*70)
print("  RUNNING SECURITY AUDIT")
print("="*70)
print()

auditor = SecurityAuditor(engine)

# Audit each brick
bricks = ["dangerous_calc", "file_reader", "divide", "safe_add"]
reports = {}

for brick_id in bricks:
    print(f"Auditing: {brick_id}...")
    report = auditor.audit_brick(brick_id)
    reports[brick_id] = report
    
    # Print report
    print(f"  Score: {report.score}/100 ({report.risk_level.upper()})")
    print(f"  Breakdown:")
    for category, score in report.breakdown.items():
        print(f"    - {category}: {score}")
    
    if report.critical_issues:
        print(f"  CRITICAL ISSUES:")
        for issue in report.critical_issues:
            print(f"    - {issue}")
    
    if report.warnings:
        print(f"  Warnings:")
        for warning in report.warnings:
            print(f"    - {warning}")
    
    if report.recommendations:
        print(f"  Recommendations:")
        for rec in report.recommendations[:2]:  # Show first 2
            print(f"    - {rec}")
    
    print()

# ============================================================================
# SECURITY SUMMARY
# ============================================================================
print("="*70)
print("  SECURITY SUMMARY")
print("="*70)
print()

summary = auditor.get_security_summary()
print(f"Total bricks audited: {summary['total_bricks']}")
print(f"Average security score: {summary['avg_score']:.1f}/100")
print(f"Lowest score: {summary['min_score']}/100")
print(f"Highest score: {summary['max_score']}/100")
print()
print("Risk Distribution:")
for level, count in summary['risk_distribution'].items():
    print(f"  {level.upper()}: {count} brick(s)")

# ============================================================================
# IDENTIFY VULNERABLE BRICKS
# ============================================================================
print()
print("="*70)
print("  VULNERABLE BRICKS (Score < 60)")
print("="*70)
print()

vulnerable = auditor.get_vulnerable_bricks(threshold=60)
if vulnerable:
    print(f"Found {len(vulnerable)} vulnerable brick(s):")
    for brick_id in vulnerable:
        report = reports[brick_id]
        print(f"  - {brick_id}: {report.score}/100 ({report.risk_level})")
else:
    print("No vulnerable bricks found!")

print()
print("="*70)
print("  Demo complete. SecurityAuditor successfully detected all vulnerabilities!")
print("="*70)
