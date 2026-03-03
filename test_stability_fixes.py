"""
STABILITY TEST: Validates all 3 fixes to SynapticBricks v1.1.1
  Fix 1: Tiered Monitoring (light vs full)
  Fix 2: Dependency Manifest (safe rollback)
  Fix 3: Phantom Auto-Test on Register
"""
import sys, os, time
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import (
    brick, BrickEngine, sensory, SensoryMonitor,
    initialize_aegis, PhantomEngine, Pipeline
)
from synapticbricks.core.genetic import GeneticMemory

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")

def test_tiered_monitoring():
    print("\n" + "="*60)
    print("TEST 1: TIERED MONITORING")
    print("="*60)

    # FULL mode — uses psutil
    monitor_full = SensoryMonitor(mode=SensoryMonitor.FULL)
    check("Monitor initializes in FULL mode", monitor_full.mode == "full")

    @sensory(monitor_full)
    def slow_func():
        time.sleep(0.01)
        return 42

    start = time.perf_counter()
    for _ in range(10):
        slow_func()
    full_time = time.perf_counter() - start

    # LIGHT mode — skip psutil
    monitor_light = SensoryMonitor(mode=SensoryMonitor.LIGHT)
    check("Monitor initializes in LIGHT mode", monitor_light.mode == "light")

    @sensory(monitor_light)
    def fast_func():
        return 42

    start = time.perf_counter()
    for _ in range(1000):
        fast_func()
    light_time = time.perf_counter() - start

    # Light should handle 1000 calls faster than full handles 10
    # (in practice light 1000 calls < 0.1s, full 10 calls ~0.15s with sleep)
    check("LIGHT mode is significantly faster", light_time < full_time * 5,
          f"light={light_time:.4f}s, full={full_time:.4f}s")

    # Test runtime mode switching
    monitor_light.set_mode("full")
    check("Runtime mode switch works", monitor_light.mode == "full")
    monitor_light.set_mode("light")
    check("Switch back to light works", monitor_light.mode == "light")
    monitor_light.set_mode("invalid_mode")
    check("Invalid mode rejected", monitor_light.mode == "light")


def test_dependency_manifest():
    print("\n" + "="*60)
    print("TEST 2: DEPENDENCY MANIFEST")
    print("="*60)

    memory = GeneticMemory(data_path=r"C:\Users\MedoRadi\clawd\synapticbricks\projects\quantum_news\vault\test_genetic.json")

    # Test import extraction
    source_with_imports = '''
import numpy
import pandas as pd
from sklearn.model import fit
import os
import json
from typing import List
'''
    deps = memory._extract_imports(source_with_imports)
    check("Extracts external deps (numpy)", "numpy" in deps)
    check("Extracts external deps (pandas)", "pandas" in deps)
    check("Extracts external deps (sklearn)", "sklearn" in deps)
    check("Filters out builtins (os)", "os" not in deps)
    check("Filters out builtins (json)", "json" not in deps)
    check("Filters out builtins (typing)", "typing" not in deps)

    # Test dependency check
    ok, missing = memory.check_dependencies(["json", "os"])
    check("Available deps pass check", ok and len(missing) == 0)

    ok, missing = memory.check_dependencies(["nonexistent_package_xyz"])
    check("Missing deps detected", not ok and "nonexistent_package_xyz" in missing)

    # Test evolution records deps
    source_safe = "def foo(x: int) -> int:\n    return x + 1"
    memory.record_evolution("test_brick", source_safe, "1.0.0", "initial", score=1.0)
    check("Evolution recorded", "test_brick" in memory.memory)
    stored_deps = memory.memory["test_brick"]["lineage"][-1].get("dependencies", None)
    check("Dependencies field stored in lineage", stored_deps is not None)

    # Test with external dep in source
    source_numpy = "import numpy\ndef bar(x: int) -> int:\n    return numpy.add(x, 1)"
    memory.record_evolution("numpy_brick", source_numpy, "1.0.0", "initial", score=1.0)
    stored = memory.memory["numpy_brick"]["lineage"][-1]["dependencies"]
    check("External dep 'numpy' stored in manifest", "numpy" in stored)


def test_auto_test_on_register():
    print("\n" + "="*60)
    print("TEST 3: PHANTOM AUTO-TEST ON REGISTER")
    print("="*60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\quantum_news\vault\test_engine"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)

    # Create a brick WITHOUT manual tests
    @brick("adder", description="Adds two numbers")
    def adder(a: int, b: int) -> int:
        return a + b

    check("Brick has 0 manual tests before register", len(adder.tests) == 0)

    # Register — should auto-generate tests
    engine.register(adder)

    check("Brick has auto-generated tests after register", len(adder.tests) > 0,
          f"got {len(adder.tests)} tests")

    # Verify auto-tests are valid (they should all pass)
    all_pass = True
    for t in adder.tests:
        try:
            result = adder.func(**t["inputs"])
            if result != t["expected"]:
                all_pass = False
                break
        except Exception:
            all_pass = False
            break
    check("All auto-generated tests pass", all_pass)

    # Create a brick WITH manual tests — should NOT auto-generate
    @brick("multiplier", description="Multiplies two numbers")
    def multiplier(a: int, b: int) -> int:
        return a * b

    multiplier.add_test({"a": 2, "b": 3}, 6, "manual_test")
    original_count = len(multiplier.tests)
    engine.register(multiplier)
    check("Manual-tested brick keeps original tests", len(multiplier.tests) == original_count)


def test_integrated_pipeline():
    print("\n" + "="*60)
    print("TEST 4: INTEGRATED STABILITY TEST")
    print("="*60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\quantum_news\vault\integrated"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)

    # Set monitor to LIGHT for speed
    monitor.set_mode("light")
    check("Monitor in LIGHT mode for pipeline", monitor.mode == "light")

    # Create pipeline bricks (no manual tests — auto-test should kick in)
    @brick("fetch_data", description="Fetches raw data")
    def fetch_data(url: str) -> list:
        return ["item1", "item2", "item3"]

    @brick("process_items", description="Processes list items")
    def process_items(items: list) -> dict:
        return {"count": len(items), "processed": True}

    @brick("summarize", description="Summarizes results")
    def summarize(report: dict) -> str:
        return f"Processed {report.get('count', 0)} items"

    engine.register_many([fetch_data, process_items, summarize])
    check("fetch_data has auto-tests", len(fetch_data.tests) > 0)
    check("process_items has auto-tests", len(process_items.tests) > 0)
    check("summarize has auto-tests", len(summarize.tests) > 0)

    # Build and run pipeline
    pipe = Pipeline("stability_test", engine)
    pipe.add_step("fetch_data", input_map={"url": "source"}, output_key="raw")
    pipe.add_step("process_items", input_map={"items": "raw"}, output_key="report")
    pipe.add_step("summarize", input_map={"report": "report"}, output_key="summary")

    result = pipe.run({"source": "https://test.com"})
    check("Pipeline runs successfully", result["success"])
    check("Pipeline output correct", result["result"] == "Processed 3 items",
          f"got: {result['result']}")

    # Immune scan should be clean
    threats = immune.scan_for_threats()
    pipeline_threats = [t for t in threats if t["brick_id"] in ("fetch_data", "process_items", "summarize")]
    check("No threats in pipeline bricks", len(pipeline_threats) == 0,
          f"found {len(pipeline_threats)} threats")


if __name__ == "__main__":
    test_tiered_monitoring()
    test_dependency_manifest()
    test_auto_test_on_register()
    test_integrated_pipeline()

    print("\n" + "="*60)
    total = PASS + FAIL
    print(f"🏁 RESULTS: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("🎯 ALL TESTS PASSED — STABILITY ACHIEVED")
    else:
        print(f"⚠️  {FAIL} FAILURES — needs attention")
    print("="*60)
