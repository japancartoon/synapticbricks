"""
BrickLang Demo — Full cycle demonstration.

This demo shows:
1. Building bricks (individual functions)
2. Gluing them into a pipeline
3. Testing everything
4. Breaking a brick on purpose
5. Self-healing it

Run: python -m synapticbricks.demo
"""

import json
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapticbricks.core.brick import brick, Brick
from synapticbricks.core.engine import BrickEngine
from synapticbricks.core.pipeline import Pipeline
from synapticbricks.core.tester import BrickTester
from synapticbricks.core.healer import BrickHealer


def main():
    print("=" * 60)
    print("🧱 BrickLang v0.1.0 — Modular Self-Healing Code Engine")
    print("=" * 60)

    # ─────────────────────────────────────────────
    # STEP 1: BUILD BRICKS
    # ─────────────────────────────────────────────
    print("\n📦 STEP 1: Building Bricks...")

    @brick("parse_input", description="Parse raw CSV line into a dict")
    def parse_input(raw: str) -> dict:
        """Parse a CSV line into name, age, score."""
        parts = raw.strip().split(",")
        return {
            "name": parts[0].strip(),
            "age": int(parts[1].strip()),
            "score": float(parts[2].strip()),
        }

    @brick("validate", description="Validate parsed data", dependencies=["parse_input"])
    def validate(data: dict) -> dict:
        """Ensure data meets business rules."""
        if data["age"] < 0 or data["age"] > 150:
            raise ValueError(f"Invalid age: {data['age']}")
        if data["score"] < 0 or data["score"] > 100:
            raise ValueError(f"Invalid score: {data['score']}")
        data["valid"] = True
        return data

    @brick("compute_grade", description="Calculate letter grade from score", dependencies=["validate"])
    def compute_grade(data: dict) -> dict:
        """Assign a letter grade based on score."""
        score = data["score"]
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        data["grade"] = grade
        return data

    @brick("format_output", description="Format result as a summary string", dependencies=["compute_grade"])
    def format_output(data: dict) -> str:
        """Create human-readable output."""
        return f"{data['name']} (age {data['age']}): Score {data['score']} → Grade {data['grade']}"

    # Add test cases to each brick
    parse_input.add_test(
        inputs={"raw": "Alice, 22, 95.5"},
        expected_output={"name": "Alice", "age": 22, "score": 95.5},
        label="basic_parse"
    )

    validate.add_test(
        inputs={"data": {"name": "Bob", "age": 25, "score": 80.0}},
        expected_output={"name": "Bob", "age": 25, "score": 80.0, "valid": True},
        label="valid_data"
    )

    compute_grade.add_test(
        inputs={"data": {"name": "Carol", "age": 30, "score": 85.0, "valid": True}},
        expected_output={"name": "Carol", "age": 30, "score": 85.0, "valid": True, "grade": "B"},
        label="grade_b"
    )

    format_output.add_test(
        inputs={"data": {"name": "Dave", "age": 20, "score": 92.0, "grade": "A"}},
        expected_output="Dave (age 20): Score 92.0 → Grade A",
        label="format_a"
    )

    print(f"  ✅ {parse_input}")
    print(f"  ✅ {validate}")
    print(f"  ✅ {compute_grade}")
    print(f"  ✅ {format_output}")

    # ─────────────────────────────────────────────
    # STEP 2: REGISTER IN ENGINE
    # ─────────────────────────────────────────────
    print("\n⚙️  STEP 2: Registering in Engine...")
    engine = BrickEngine(project_dir=os.path.dirname(os.path.abspath(__file__)))
    engine.register_many([parse_input, validate, compute_grade, format_output])
    print(f"  {engine}")
    print(f"  Dependency order: {engine.get_dependency_order()}")

    print("\n📝 CODE MAP (AI-readable shorthand):")
    print(engine.get_code_map())

    # ─────────────────────────────────────────────
    # STEP 3: GLUE INTO PIPELINE
    # ─────────────────────────────────────────────
    print("\n🔗 STEP 3: Gluing Bricks into Pipeline...")

    pipeline = Pipeline("student_grader", engine)
    pipeline.add_step("parse_input", input_map={"raw": "input"}, output_key="parsed")
    pipeline.add_step("validate", input_map={"data": "parsed"}, output_key="validated")
    pipeline.add_step("compute_grade", input_map={"data": "validated"}, output_key="graded")
    pipeline.add_step("format_output", input_map={"data": "graded"}, output_key="output")

    print(pipeline.visualize())

    # ─────────────────────────────────────────────
    # STEP 4: TEST ALL BRICKS
    # ─────────────────────────────────────────────
    print("\n🧪 STEP 4: Testing All Bricks...")
    tester = BrickTester(engine, timeout=5.0)
    test_report = tester.test_all()

    for brick_id, result in test_report["results"].items():
        status = "✅" if result["status"] == "passed" else "❌"
        print(f"  {status} {brick_id}: {result['passed']}/{result['total']} tests passed")

    print(f"\n  Overall: {test_report['passed']}/{test_report['total_tests']} tests passed "
          f"in {test_report['duration_ms']}ms")

    # ─────────────────────────────────────────────
    # STEP 5: RUN THE PIPELINE
    # ─────────────────────────────────────────────
    print("\n🚀 STEP 5: Running Pipeline...")
    result = pipeline.run({"input": "Alice, 22, 95.5"})
    print(f"  Success: {result['success']}")
    print(f"  Result: {result['result']}")
    print(f"  Duration: {result['total_duration_ms']}ms")

    # ─────────────────────────────────────────────
    # STEP 6: BREAK A BRICK ON PURPOSE
    # ─────────────────────────────────────────────
    print("\n💥 STEP 6: Breaking a Brick (simulating a bug)...")

    # Replace compute_grade with a broken version
    def broken_grade(data: dict) -> dict:
        """Broken: divides by zero."""
        score = data["score"]
        grade = score / 0  # BUG!
        data["grade"] = grade
        return data

    engine.get("compute_grade").func = broken_grade
    engine.get("compute_grade").meta.last_error = None
    engine.get("compute_grade").meta.error_count = 0

    # Run pipeline — it should fail at compute_grade
    result = pipeline.run({"input": "Alice, 22, 95.5"})
    print(f"  Pipeline success: {result['success']}")
    print(f"  Failed brick: {result['failed_brick']}")
    print(f"  Error: {result['error']}")

    # ─────────────────────────────────────────────
    # STEP 7: SELF-HEAL
    # ─────────────────────────────────────────────
    print("\n🩹 STEP 7: Self-Healing...")
    healer = BrickHealer(engine, tester)

    # Generate repair request (what we'd send to AI)
    repair = healer.create_repair_request("compute_grade", pipeline_error=result["error"])
    print("\n  📋 Repair Prompt (what AI sees):")
    print("  " + "-" * 50)
    for line in repair.to_prompt().split("\n")[:15]:
        print(f"  {line}")
    print("  ... (truncated)")
    print("  " + "-" * 50)

    # Apply the fix (simulating AI providing a corrected function)
    def fixed_grade(data: dict) -> dict:
        """Fixed: proper grade calculation."""
        score = data["score"]
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        data["grade"] = grade
        return data

    heal_result = healer.auto_heal("compute_grade", fixed_grade)
    print(f"\n  Heal success: {heal_result['success']}")
    print(f"  New version: {heal_result['new_version']}")

    # ─────────────────────────────────────────────
    # STEP 8: VERIFY — RUN PIPELINE AGAIN
    # ─────────────────────────────────────────────
    print("\n✅ STEP 8: Running Pipeline Again After Healing...")
    result = pipeline.run({"input": "Bob, 30, 78.5"})
    print(f"  Success: {result['success']}")
    print(f"  Result: {result['result']}")
    print(f"  Duration: {result['total_duration_ms']}ms")

    # ─────────────────────────────────────────────
    # FINAL: HEALTH REPORT
    # ─────────────────────────────────────────────
    print("\n📊 FINAL HEALTH REPORT:")
    report = engine.health_report()
    print(f"  Total bricks: {report['total_bricks']}")
    print(f"  Healthy: {report['healthy']}")
    print(f"  Broken: {report['broken']}")
    print(f"  Total errors caught: {report['total_errors']}")
    print(f"  Total fixes applied: {report['total_fixes']}")

    print("\n  Repair history:")
    for entry in healer.get_repair_history():
        print(f"    🔧 {entry['brick_id']} → v{entry['new_version']} "
              f"(checksum: {entry['old_checksum'][:8]}→{entry['new_checksum'][:8]})")

    print("\n" + "=" * 60)
    print("🧱 BrickLang Demo Complete — All systems operational!")
    print("=" * 60)


if __name__ == "__main__":
    main()
