"""
NeuralGuard — Full Integration Test
Tests every SynapticBricks feature through a real code analysis pipeline.
"""
import sys, os, time
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")
sys.path.insert(0, r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard")

from synapticbricks.core import (
    brick, BrickEngine, sensory, SensoryMonitor,
    initialize_aegis, PhantomEngine, Pipeline
)
import bricks

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")

# ═══════════════════════════════════════════════════════════════
# SAMPLE CODE TO ANALYZE (intentionally has issues)
# ═══════════════════════════════════════════════════════════════
GOOD_CODE = '''
import json
from typing import List, Dict

def parse_config(path: str) -> dict:
    """Load and parse a JSON configuration file."""
    with open(path, 'r') as f:
        return json.load(f)

def validate_email(email: str) -> bool:
    """Check if email format is valid."""
    return '@' in email and '.' in email.split('@')[-1]

class UserManager:
    """Manages user operations."""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_user(self, user_id: int) -> dict:
        """Retrieve a user by ID."""
        return {"id": user_id, "name": "test"}
'''

BAD_CODE = '''
from os import *
import json

password = "super_secret_123"

def process(data, cache=[]):
    global total
    total = 0
    try:
        for item in data:
            total += item
            cache.append(item)
    except:
        pass
    if type(data) == list:
        exec("print('done')")
    return total

def another_function():
    pass

def yet_another():
    pass

def no_docs():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    xx = 27
    yy = 28
    zz = 29
    aa = 30
    bb = 31
    return bb
'''

EMPTY_CODE = ""
BROKEN_CODE = "def broken(:\n  pass"

# ═══════════════════════════════════════════════════════════════
# TEST SUITE
# ═══════════════════════════════════════════════════════════════

def test_1_auto_test_generation():
    """Fix 3: Every brick is born with auto-tests."""
    print("\n" + "=" * 60)
    print("TEST 1: AUTO-TEST GENERATION ON REGISTER")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t1"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)

    # All 5 bricks should get auto-tests (none have manual tests)
    engine.register(bricks.source_parser)
    engine.register(bricks.complexity_analyzer)
    engine.register(bricks.antipattern_detector)
    engine.register(bricks.quality_scorer)
    engine.register(bricks.report_generator)

    check("source_parser has auto-tests", len(bricks.source_parser.tests) > 0,
          f"got {len(bricks.source_parser.tests)}")
    check("complexity_analyzer has auto-tests", len(bricks.complexity_analyzer.tests) > 0,
          f"got {len(bricks.complexity_analyzer.tests)}")
    check("antipattern_detector has auto-tests", len(bricks.antipattern_detector.tests) > 0,
          f"got {len(bricks.antipattern_detector.tests)}")
    check("quality_scorer has auto-tests", len(bricks.quality_scorer.tests) > 0,
          f"got {len(bricks.quality_scorer.tests)}")
    check("report_generator has auto-tests", len(bricks.report_generator.tests) > 0,
          f"got {len(bricks.report_generator.tests)}")

    total_tests = sum(len(b.tests) for b in [bricks.source_parser, bricks.complexity_analyzer,
                      bricks.antipattern_detector, bricks.quality_scorer, bricks.report_generator])
    print(f"\n  >> Total auto-generated tests across 5 bricks: {total_tests}")


def test_2_pipeline_good_code():
    """Pipeline processes clean code correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: PIPELINE ON GOOD CODE")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t2"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)
    monitor.set_mode("light")  # Fix 1: Light mode

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    pipe = Pipeline("NeuralGuard", engine)
    pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
    pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
    pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
    pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
    pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                  "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

    result = pipe.run({"code": GOOD_CODE})

    check("Pipeline succeeds on good code", result["success"])
    check("Report is a string", isinstance(result.get("result"), str))

    quality = result["data"].get("quality", {})
    check("Good code scores >= 80", quality.get("score", 0) >= 80,
          f"score={quality.get('score')}")
    check("Good code gets A or B grade", quality.get("grade") in ("A", "B"),
          f"grade={quality.get('grade')}")

    parsed = result["data"].get("parsed", {})
    check("Parser found functions", len(parsed.get("functions", [])) > 0)
    check("Parser found classes", len(parsed.get("classes", [])) > 0)

    antipatterns = result["data"].get("antipatterns", {})
    check("No anti-patterns in good code", antipatterns.get("count", 99) == 0,
          f"found {antipatterns.get('count')} patterns")

    print(f"\n  >> Good code report preview:")
    for line in result["result"].split("\n")[:8]:
        print(f"     {line}")


def test_3_pipeline_bad_code():
    """Pipeline catches all issues in bad code."""
    print("\n" + "=" * 60)
    print("TEST 3: PIPELINE ON BAD CODE")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t3"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)
    monitor.set_mode("light")

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    pipe = Pipeline("NeuralGuard", engine)
    pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
    pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
    pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
    pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
    pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                  "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

    result = pipe.run({"code": BAD_CODE})

    check("Pipeline succeeds on bad code", result["success"])

    quality = result["data"].get("quality", {})
    check("Bad code scores < 60", quality.get("score", 100) < 60,
          f"score={quality.get('score')}")

    antipatterns = result["data"].get("antipatterns", {})
    found_names = [p["pattern"] for p in antipatterns.get("patterns_found", [])]
    check("Detects bare_except", "bare_except" in found_names, f"found: {found_names}")
    check("Detects mutable_default", "mutable_default" in found_names)
    check("Detects global_usage", "global_usage" in found_names)
    check("Detects star_import", "star_import" in found_names)
    check("Detects exec_eval", "exec_eval" in found_names)
    check("Detects hardcoded_secret", "hardcoded_secret" in found_names)
    check("Severity is critical", antipatterns.get("severity") == "critical")

    print(f"\n  >> Bad code: Score={quality.get('score')}, Grade={quality.get('grade')}, Patterns={len(found_names)}")


def test_4_edge_cases():
    """Pipeline handles empty and broken input gracefully."""
    print("\n" + "=" * 60)
    print("TEST 4: EDGE CASES (empty/broken code)")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t4"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    pipe = Pipeline("NeuralGuard", engine)
    pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
    pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
    pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
    pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
    pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                  "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

    # Empty code
    result = pipe.run({"code": EMPTY_CODE})
    check("Pipeline survives empty code", result["success"])

    # Broken syntax
    result = pipe.run({"code": BROKEN_CODE})
    check("Pipeline survives broken syntax", result["success"])
    parsed = result["data"].get("parsed", {})
    check("Parser marks broken code as invalid", parsed.get("valid") == False)

    # Unicode code
    unicode_code = 'def hello():\n    print("Hola mundo!")\n    x = 42\n'
    result = pipe.run({"code": unicode_code})
    check("Pipeline handles unicode code", result["success"])


def test_5_tiered_monitoring_perf():
    """Fix 1: Light mode is measurably faster."""
    print("\n" + "=" * 60)
    print("TEST 5: TIERED MONITORING PERFORMANCE")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t5"
    os.makedirs(vault, exist_ok=True)

    # FULL mode pipeline — wrap bricks with sensory decorator
    engine_full = BrickEngine(vault + "_full")
    _, monitor_full, _ = initialize_aegis(engine_full)
    monitor_full.set_mode("full")

    @brick("perf_brick_full", description="Perf test brick")
    def perf_full(x: int) -> int:
        return x * 2

    wrapped_full = sensory(monitor_full)(perf_full.func)
    
    start = time.perf_counter()
    for i in range(500):
        wrapped_full(x=i)
    full_time = time.perf_counter() - start

    # LIGHT mode
    engine_light = BrickEngine(vault + "_light")
    _, monitor_light, _ = initialize_aegis(engine_light)
    monitor_light.set_mode("light")

    @brick("perf_brick_light", description="Perf test brick")
    def perf_light(x: int) -> int:
        return x * 2

    wrapped_light = sensory(monitor_light)(perf_light.func)

    start = time.perf_counter()
    for i in range(500):
        wrapped_light(x=i)
    light_time = time.perf_counter() - start

    print(f"  >> Full mode (500 calls):  {full_time:.4f}s")
    print(f"  >> Light mode (500 calls): {light_time:.4f}s")
    print(f"  >> Speedup:                {full_time/max(light_time, 0.001):.2f}x")
    check("Light mode is faster than full on 500 iterations", light_time < full_time,
          f"light={light_time:.4f}s full={full_time:.4f}s")


def test_6_phantom_fragility():
    """Phantom scans all bricks for fragility."""
    print("\n" + "=" * 60)
    print("TEST 6: PHANTOM FRAGILITY ANALYSIS")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t6"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)
    phantom = PhantomEngine(sensory=monitor, genetic=memory)

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    all_bricks = [bricks.source_parser, bricks.antipattern_detector]
    for b in all_bricks:
        report = phantom.analyze(b)
        score = report.fragility_score
        label = "ROBUST" if score < 0.3 else "MODERATE" if score < 0.6 else "FRAGILE"
        print(f"  >> {b.meta.id}: fragility={score:.4f} ({label}), {report.passed}/{report.total_cases} passed")
        check(f"{b.meta.id} fragility analyzed", report.total_cases > 0)


def test_7_immune_scan():
    """Immune system detects no threats in healthy pipeline."""
    print("\n" + "=" * 60)
    print("TEST 7: IMMUNE SYSTEM SCAN")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t7"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)
    monitor.set_mode("light")

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    pipe = Pipeline("NeuralGuard", engine)
    pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
    pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
    pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
    pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
    pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                  "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

    # Run multiple times to build baseline
    for _ in range(5):
        pipe.run({"code": GOOD_CODE})

    threats = immune.scan_for_threats()
    ng_threats = [t for t in threats if t["brick_id"] in
                  ("source_parser", "complexity_analyzer", "antipattern_detector",
                   "quality_scorer", "report_generator")]
    check("No immune threats in healthy pipeline", len(ng_threats) == 0,
          f"found {len(ng_threats)} threats")


def test_8_dependency_manifest():
    """Fix 2: Genetic memory stores and checks deps."""
    print("\n" + "=" * 60)
    print("TEST 8: DEPENDENCY MANIFEST IN GENETIC MEMORY")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t8"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)

    # Record a brick with external dependency
    source_with_dep = 'import numpy\ndef heavy(x: int) -> int:\n    return numpy.square(x)'
    memory.record_evolution("heavy_brick", source_with_dep, "1.0.0", "initial", score=1.0)

    stored = memory.memory["heavy_brick"]["lineage"][-1]
    check("Dependencies stored with DNA", "numpy" in stored.get("dependencies", []))

    # Check dependency validation
    ok, missing = memory.check_dependencies(stored["dependencies"])
    # numpy may or may not be installed — test the mechanism itself
    check("Dependency check returns result", isinstance(ok, bool))
    if not ok:
        check("Missing deps identified", len(missing) > 0)
        print(f"  >> Missing: {missing} (expected if numpy not installed)")
    else:
        check("All deps available", ok)


def test_9_self_analysis():
    """NeuralGuard analyzes its own source code."""
    print("\n" + "=" * 60)
    print("TEST 9: SELF-ANALYSIS (NeuralGuard analyzes itself)")
    print("=" * 60)

    vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\t9"
    os.makedirs(vault, exist_ok=True)
    engine = BrickEngine(vault)
    immune, monitor, memory = initialize_aegis(engine)
    monitor.set_mode("light")

    engine.register_many([bricks.source_parser, bricks.complexity_analyzer,
                          bricks.antipattern_detector, bricks.quality_scorer,
                          bricks.report_generator])

    pipe = Pipeline("NeuralGuard_Self", engine)
    pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
    pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
    pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
    pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
    pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                  "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

    # Read its own source
    with open(r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\bricks.py", "r", encoding="utf-8") as f:
        own_source = f.read()

    result = pipe.run({"code": own_source})
    check("NeuralGuard can analyze itself", result["success"])
    quality = result["data"].get("quality", {})
    check("Self-analysis produces a score", quality.get("score") is not None)
    print(f"\n  >> NeuralGuard self-score: {quality.get('score')}/100 (Grade: {quality.get('grade')})")
    print(f"\n  >> FULL SELF-REPORT:")
    print(result["result"])


# ═══════════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    test_1_auto_test_generation()
    test_2_pipeline_good_code()
    test_3_pipeline_bad_code()
    test_4_edge_cases()
    test_5_tiered_monitoring_perf()
    test_6_phantom_fragility()
    test_7_immune_scan()
    test_8_dependency_manifest()
    test_9_self_analysis()

    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"  FINAL: {PASS}/{total} passed, {FAIL} failed")
    if FAIL == 0:
        print("  NEURALGUARD + SYNAPTICBRICKS: PERFECT STABILITY")
    else:
        print(f"  {FAIL} FAILURES need attention")
    print("=" * 60)
