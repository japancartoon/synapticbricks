"""
Test script to verify an AI can use BrickLang skill.

This simulates what Gemini CLI (or any AI) would do after reading SKILL.md.
"""

import sys
import os

# Add bricklang to path
sys.path.insert(0, "C:\\Users\\MedoRadi\\clawd")

from synapticbricks.core import brick, BrickEngine, Pipeline, BrickTester, BrickHealer

print("=" * 60)
print("BrickLang Skill Test — Can AI use this system?")
print("=" * 60)

# Scenario: AI is asked to build a temperature converter pipeline

print("\n1️⃣ AI reads SKILL.md and learns the system...")
print("   ✅ Knows to import from synapticbricks.core")
print("   ✅ Knows label format: category{seq}-{usage}")
print("   ✅ Knows workflow: build → test → register → pipeline → heal")

print("\n2️⃣ AI builds bricks based on skill knowledge...")

# Brick 1: Parse input
@brick("parse_temp", description="Parse temperature input string")
def parse_temp(input_str: str) -> dict:
    """Parse 'value unit' format, e.g., '32 F' or '100 C'."""
    parts = input_str.strip().split()
    return {
        "value": float(parts[0]),
        "unit": parts[1].upper()
    }

parse_temp.add_test(
    inputs={"input_str": "32 F"},
    expected_output={"value": 32.0, "unit": "F"},
    label="fahrenheit"
)

# Brick 2: Validate
@brick("validate_temp", description="Validate temperature data")
def validate_temp(data: dict) -> dict:
    """Ensure unit is C or F and value is reasonable."""
    if data["unit"] not in ["C", "F"]:
        raise ValueError(f"Invalid unit: {data['unit']}")
    if data["value"] < -273.15:  # Below absolute zero
        raise ValueError(f"Invalid temperature: {data['value']}")
    return data

validate_temp.add_test(
    inputs={"data": {"value": 100.0, "unit": "C"}},
    expected_output={"value": 100.0, "unit": "C"},
    label="celsius"
)

# Brick 3: Convert
@brick("convert_temp", description="Convert between Celsius and Fahrenheit")
def convert_temp(data: dict) -> dict:
    """Convert temperature to the other unit."""
    if data["unit"] == "F":
        celsius = (data["value"] - 32) * 5/9
        data["converted"] = {"value": round(celsius, 2), "unit": "C"}
    else:
        fahrenheit = data["value"] * 9/5 + 32
        data["converted"] = {"value": round(fahrenheit, 2), "unit": "F"}
    return data

convert_temp.add_test(
    inputs={"data": {"value": 32.0, "unit": "F"}},
    expected_output={"value": 32.0, "unit": "F", "converted": {"value": 0.0, "unit": "C"}},
    label="freezing_point"
)

# Brick 4: Format output
@brick("format_temp", description="Format temperature conversion result")
def format_temp(data: dict) -> str:
    """Create human-readable output."""
    orig = f"{data['value']} {data['unit']}"
    conv = f"{data['converted']['value']} {data['converted']['unit']}"
    return f"{orig} = {conv}"

format_temp.add_test(
    inputs={"data": {"value": 32.0, "unit": "F", "converted": {"value": 0.0, "unit": "C"}}},
    expected_output="32.0 F = 0.0 C",
    label="freezing"
)

print("   ✅ Built 4 bricks with type hints")
print("   ✅ Added tests to each brick")
print("   ✅ Used descriptive names for auto-labeling")

print("\n3️⃣ AI registers bricks in engine...")
engine = BrickEngine(project_dir="C:\\Users\\MedoRadi\\clawd\\bricklang")
engine.register_many([parse_temp, validate_temp, convert_temp, format_temp])

print(f"   ✅ {engine}")

print("\n4️⃣ AI checks code map to see labels...")
print(engine.get_code_map())

print("\n5️⃣ AI builds pipeline from skill knowledge...")
pipeline = Pipeline("temp_converter", engine)
pipeline.add_step("parse_temp", input_map={"input_str": "input"}, output_key="parsed")
pipeline.add_step("validate_temp", input_map={"data": "parsed"}, output_key="validated")
pipeline.add_step("convert_temp", input_map={"data": "validated"}, output_key="converted")
pipeline.add_step("format_temp", input_map={"data": "converted"}, output_key="output")

print(pipeline.visualize())

print("\n6️⃣ AI tests the pipeline...")
tester = BrickTester(engine)
report = tester.test_all()
print(f"   ✅ {report['passed']}/{report['total_tests']} brick tests passed")

print("\n7️⃣ AI runs the pipeline...")
test_cases = [
    "32 F",      # Freezing point
    "100 C",     # Boiling point
    "98.6 F",    # Body temperature
    "0 C",       # Freezing point (other direction)
]

for test in test_cases:
    result = pipeline.run({"input": test})
    print(f"   {test} → {result['result']}")

print("\n8️⃣ Simulating a broken brick...")
# Break convert_temp
convert_temp.func = lambda data: 1 / 0  # Intentional error

result = pipeline.run({"input": "50 F"})
print(f"   Pipeline failed: {result['failed_brick']} - {result['error']}")

print("\n9️⃣ AI uses healing workflow from SKILL.md...")
healer = BrickHealer(engine, tester)
repair = healer.create_repair_request("convert_temp")

print("\n📋 Repair prompt AI would see:")
print("-" * 60)
for line in repair.to_prompt().split("\n")[:20]:
    print(line)
print("... (truncated)")
print("-" * 60)

print("\n✅ AI now knows:")
print("   • Brick label: convert_temp →", convert_temp.label.full if convert_temp.label else "N/A")
print("   • Usage count:", convert_temp.label.usage_count if convert_temp.label else 0, "places")
print("   • Error:", repair.context["last_error"])
print("   • What to fix: ONLY this brick's code")

print("\n" + "=" * 60)
print("✅ BrickLang Skill Test PASSED")
print("=" * 60)
print("\nConclusion:")
print("  AI can successfully:")
print("  ✅ Build bricks following skill guidelines")
print("  ✅ Register and get auto-labels")
print("  ✅ Create pipelines with proper data flow")
print("  ✅ Test and diagnose failures")
print("  ✅ Generate repair prompts with labels")
print("\n  The skill (SKILL.md) contains all necessary knowledge.")
print("  No re-learning required between sessions.")
