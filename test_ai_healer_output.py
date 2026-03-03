"""Quick test to see what Gemini is generating"""
import sys
import os
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import brick, BrickEngine, BrickTester, BrickHealer, AIHealer

# Get API key from environment
API_KEY = os.environ.get("GEMINI_API_KEY", "your_key_here")

@brick("calculator", description="Simple calculator")
def calculator(a: int, b: int, operation: str) -> int:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b  # BUG
    else:
        raise ValueError(f"Unknown operation: {operation}")

calculator.add_test(
    inputs={"a": 10, "b": 5, "operation": "add"},
    expected_output=15,
    label="test_add"
)
calculator.add_test(
    inputs={"a": 10, "b": 0, "operation": "divide"},
    expected_output=None,
    label="test_divide_by_zero"
)

engine = BrickEngine()
engine.register(calculator)

tester = BrickTester(engine)
healer = BrickHealer(engine, tester)
ai_healer = AIHealer(API_KEY, engine=engine, healer=healer)

print("Calling Gemini to generate fix...")
result = ai_healer.heal_brick("calculator")

if result["success"]:
    print("\n" + "="*60)
    print("GENERATED CODE:")
    print("="*60)
    print(result["fixed_code"])
    print("="*60)
else:
    print(f"Failed: {result.get('error')}")
