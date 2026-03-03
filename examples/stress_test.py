"""
Manual test to find BrickLang issues.
Simulating what Gemini CLI would do after reading SKILL.md.
"""

import sys
sys.path.insert(0, "C:\\Users\\MedoRadi\\clawd")

print("=" * 70)
print("BRICKLANG STRESS TEST — Finding Issues")
print("=" * 70)

# Test 1: Can we import everything from SKILL.md?
print("\n[TEST 1] Importing from synapticbricks.core...")
try:
    from synapticbricks.core import brick, BrickEngine, Pipeline, BrickTester, BrickHealer
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ ISSUE: Import failed - {e}")
    sys.exit(1)

# Test 2: Can we build a brick following SKILL.md exactly?
print("\n[TEST 2] Building a brick following SKILL.md guidelines...")
try:
    @brick("parse_json", description="Parse JSON string")
    def parse_json(raw: str) -> dict:
        import json
        return json.loads(raw)
    
    parse_json.add_test(
        inputs={"raw": '{"name": "test"}'},
        expected_output={"name": "test"},
        label="basic"
    )
    print("✅ Brick created successfully")
except Exception as e:
    print(f"❌ ISSUE: Brick creation failed - {e}")
    sys.exit(1)

# Test 3: Can we register without specifying project_dir?
print("\n[TEST 3] Registering brick (default project_dir)...")
try:
    engine = BrickEngine()  # SKILL.md doesn't always show project_dir
    engine.register(parse_json)
    print(f"✅ Registered: {parse_json}")
    print(f"   Label assigned: {parse_json.label.full if parse_json.label else 'NONE'}")
except Exception as e:
    print(f"❌ ISSUE: Registration failed - {e}")
    import traceback
    traceback.print_exc()

# Test 4: Can we look up by label code?
print("\n[TEST 4] Looking up brick by label code...")
try:
    label_code = parse_json.label.code if parse_json.label else None
    if label_code:
        found = engine.get(label_code)
        if found:
            print(f"✅ Lookup by label '{label_code}' works")
        else:
            print(f"❌ ISSUE: Lookup by label '{label_code}' returned None")
    else:
        print("❌ ISSUE: Brick has no label")
except Exception as e:
    print(f"❌ ISSUE: Label lookup failed - {e}")

# Test 5: Build a pipeline with minimal code
print("\n[TEST 5] Building pipeline (minimal code from SKILL.md)...")
try:
    pipeline = Pipeline("test", engine)
    pipeline.add_step("parse_json", input_map={"raw": "input"}, output_key="parsed")
    print("✅ Pipeline created")
    print(pipeline.visualize())
except Exception as e:
    print(f"❌ ISSUE: Pipeline creation failed - {e}")
    import traceback
    traceback.print_exc()

# Test 6: Run the pipeline
print("\n[TEST 6] Running pipeline...")
try:
    result = pipeline.run({"input": '{"test": 123}'})
    if result["success"]:
        print(f"✅ Pipeline ran successfully")
        print(f"   Result: {result['result']}")
    else:
        print(f"❌ ISSUE: Pipeline failed - {result['error']}")
except Exception as e:
    print(f"❌ ISSUE: Pipeline execution failed - {e}")
    import traceback
    traceback.print_exc()

# Test 7: Test the brick
print("\n[TEST 7] Testing brick...")
try:
    tester = BrickTester(engine)
    test_result = tester.test_brick(parse_json)
    if test_result["status"] == "passed":
        print(f"✅ Tests passed ({test_result['passed']}/{test_result['total']})")
    else:
        print(f"❌ ISSUE: Tests failed")
        print(f"   Results: {test_result['results']}")
except Exception as e:
    print(f"❌ ISSUE: Testing failed - {e}")
    import traceback
    traceback.print_exc()

# Test 8: Get code map
print("\n[TEST 8] Getting code map...")
try:
    code_map = engine.get_code_map()
    print("✅ Code map generated:")
    print(code_map)
except Exception as e:
    print(f"❌ ISSUE: Code map generation failed - {e}")

# Test 9: Break a brick and heal it
print("\n[TEST 9] Simulating brick failure + healing...")
try:
    # Break it
    parse_json.func = lambda raw: 1/0  # Intentional error
    
    # Try to run
    result = pipeline.run({"input": '{"test": 123}'})
    if not result["success"]:
        print(f"✅ Pipeline correctly detected failure: {result['failed_brick']}")
        
        # Heal it
        healer = BrickHealer(engine, tester)
        repair = healer.create_repair_request("parse_json")
        prompt = repair.to_prompt()
        
        # Check if prompt has label info
        if "[parse" in prompt and "-" in prompt:
            print("✅ Repair prompt includes label")
        else:
            print("⚠️  WARNING: Repair prompt missing label visibility")
        
        print("\n   First 15 lines of repair prompt:")
        for i, line in enumerate(prompt.split("\n")[:15], 1):
            print(f"   {i:2}. {line}")
    else:
        print("❌ ISSUE: Pipeline should have failed but didn't")
except Exception as e:
    print(f"❌ ISSUE: Healing test failed - {e}")
    import traceback
    traceback.print_exc()

# Test 10: Edge case - brick with no tests
print("\n[TEST 10] Edge case: Brick without tests...")
try:
    @brick("no_test_brick", description="A brick with no tests")
    def no_test_brick(x: int) -> int:
        return x * 2
    
    engine.register(no_test_brick)
    
    test_result = tester.test_brick(no_test_brick)
    if test_result["status"] == "no_tests":
        print("✅ Correctly handles bricks with no tests")
    else:
        print(f"⚠️  WARNING: Unexpected status for no-test brick: {test_result['status']}")
except Exception as e:
    print(f"❌ ISSUE: No-test brick handling failed - {e}")

# Test 11: SKILL.md says you can use brick_id OR label code - verify both
print("\n[TEST 11] Lookup by both ID and label...")
try:
    by_id = engine.get("parse_json")
    by_label = engine.get(parse_json.label.code if parse_json.label else "")
    
    if by_id and by_label and by_id == by_label:
        print("✅ Both ID and label lookups work and return same brick")
    else:
        print(f"❌ ISSUE: Lookup mismatch - by_id={by_id}, by_label={by_label}")
except Exception as e:
    print(f"❌ ISSUE: Dual lookup test failed - {e}")

print("\n" + "=" * 70)
print("STRESS TEST COMPLETE")
print("=" * 70)
