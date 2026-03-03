"""
Test suite for Phantom — Predictive Failure Engine.
"""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapticbricks.core.brick import Brick, brick
from synapticbricks.core.phantom import (
    EdgeCaseGenerator,
    PhantomExecutor,
    FailurePredictor,
    PhantomEngine,
    EdgeCase,
    PhantomResult,
    FragilityReport,
)


# ---------------------------------------------------------------------------
# Test bricks
# ---------------------------------------------------------------------------

@brick("test_robust", description="Robust brick for testing")
def robust_brick(x: int, y: str) -> str:
    """Handles edge cases well."""
    if x is None:
        x = 0
    if y is None:
        y = ""
    if not isinstance(x, int):
        x = int(x) if x else 0
    if not isinstance(y, str):
        y = str(y)
    return f"{y}_{x}"


@brick("test_fragile", description="Fragile brick for testing")
def fragile_brick(data: str) -> int:
    """Crashes on many inputs."""
    import json
    parsed = json.loads(data)
    return parsed["value"] + 1


@brick("test_medium", description="Medium fragility brick")
def medium_brick(a: float, b: float) -> float:
    """Division — handles some edges but not all."""
    if b == 0:
        return 0.0
    return a / b


@brick("test_no_contract", description="Brick with no type hints")
def no_contract_brick(x, y):
    return x + y


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEdgeCaseGenerator(unittest.TestCase):
    """Tests for EdgeCaseGenerator."""

    def test_generates_cases_for_typed_brick(self):
        """Should generate edge cases for a brick with type hints."""
        cases = EdgeCaseGenerator.generate(robust_brick)
        self.assertGreater(len(cases), 0, "Should generate at least some edge cases")

    def test_all_cases_are_edge_case_objects(self):
        """Every generated case should be an EdgeCase dataclass."""
        cases = EdgeCaseGenerator.generate(robust_brick)
        for case in cases:
            self.assertIsInstance(case, EdgeCase)
            self.assertTrue(case.label.startswith("edge:"))
            self.assertIsInstance(case.inputs, dict)

    def test_str_param_gets_str_edge_cases(self):
        """A str param should get string-specific edge cases."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        labels = [c.label for c in cases]
        self.assertIn("edge:empty_string", labels)
        self.assertIn("edge:none_string", labels)
        self.assertIn("edge:sql_injection", labels)

    def test_float_param_gets_float_edge_cases(self):
        """A float param should get float-specific edge cases."""
        cases = EdgeCaseGenerator.generate(medium_brick)
        labels = [c.label for c in cases]
        self.assertIn("edge:nan", labels)
        self.assertIn("edge:inf", labels)
        self.assertIn("edge:zero_float", labels)

    def test_no_cases_for_untyped_brick(self):
        """A brick with no type hints should produce no edge cases."""
        cases = EdgeCaseGenerator.generate(no_contract_brick)
        self.assertEqual(len(cases), 0)

    def test_each_case_has_all_params(self):
        """Each edge case should provide values for ALL parameters."""
        cases = EdgeCaseGenerator.generate(robust_brick)
        expected_params = set(robust_brick.contract.inputs.keys())
        for case in cases:
            self.assertEqual(
                set(case.inputs.keys()), expected_params,
                f"Edge case {case.label} missing params"
            )

    def test_edge_type_classification(self):
        """Edge types should be classified correctly."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        types = {c.edge_type for c in cases}
        # str type should produce null_safety, empty_input, etc.
        self.assertTrue(
            len(types) > 1,
            "Should have multiple edge type categories"
        )


class TestPhantomExecutor(unittest.TestCase):
    """Tests for PhantomExecutor."""

    def test_runs_all_cases(self):
        """Executor should run every edge case and return results."""
        cases = EdgeCaseGenerator.generate(robust_brick)
        results = PhantomExecutor.run(robust_brick, cases)
        self.assertEqual(len(results), len(cases))

    def test_results_are_phantom_result_objects(self):
        """Each result should be a PhantomResult."""
        cases = EdgeCaseGenerator.generate(robust_brick)
        results = PhantomExecutor.run(robust_brick, cases)
        for r in results:
            self.assertIsInstance(r, PhantomResult)
            self.assertIsInstance(r.duration_ms, float)

    def test_fragile_brick_has_failures(self):
        """Fragile brick should fail on many edge cases."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        results = PhantomExecutor.run(fragile_brick, cases)
        failures = [r for r in results if not r.success]
        self.assertGreater(len(failures), 0, "Fragile brick should have failures")

    def test_robust_brick_has_fewer_failures(self):
        """Robust brick should pass more edge cases than fragile."""
        robust_cases = EdgeCaseGenerator.generate(robust_brick)
        robust_results = PhantomExecutor.run(robust_brick, robust_cases)

        fragile_cases = EdgeCaseGenerator.generate(fragile_brick)
        fragile_results = PhantomExecutor.run(fragile_brick, fragile_cases)

        robust_pass_rate = sum(1 for r in robust_results if r.success) / max(len(robust_results), 1)
        fragile_pass_rate = sum(1 for r in fragile_results if r.success) / max(len(fragile_results), 1)

        self.assertGreater(
            robust_pass_rate, fragile_pass_rate,
            "Robust brick should have higher pass rate"
        )

    def test_failure_records_error_info(self):
        """Failed results should have error and error_type set."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        results = PhantomExecutor.run(fragile_brick, cases)
        failures = [r for r in results if not r.success]
        for f in failures:
            self.assertIsNotNone(f.error)
            self.assertIsNotNone(f.error_type)


class TestFailurePredictor(unittest.TestCase):
    """Tests for FailurePredictor."""

    def test_fragile_scores_higher_than_robust(self):
        """Fragile brick should have a higher fragility score than robust."""
        # Robust
        r_cases = EdgeCaseGenerator.generate(robust_brick)
        r_results = PhantomExecutor.run(robust_brick, r_cases)
        r_score, _ = FailurePredictor.predict(r_results)

        # Fragile
        f_cases = EdgeCaseGenerator.generate(fragile_brick)
        f_results = PhantomExecutor.run(fragile_brick, f_cases)
        f_score, _ = FailurePredictor.predict(f_results)

        self.assertGreater(
            f_score, r_score,
            f"Fragile ({f_score}) should score higher than robust ({r_score})"
        )

    def test_score_range(self):
        """Fragility score should be between 0.0 and 1.0."""
        cases = EdgeCaseGenerator.generate(medium_brick)
        results = PhantomExecutor.run(medium_brick, cases)
        score, _ = FailurePredictor.predict(results)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_empty_results(self):
        """Empty results should return 0.0 fragility."""
        score, patterns = FailurePredictor.predict([])
        self.assertEqual(score, 0.0)
        self.assertEqual(patterns, [])

    def test_dangerous_patterns_have_fields(self):
        """Dangerous patterns should have required fields."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        results = PhantomExecutor.run(fragile_brick, cases)
        _, patterns = FailurePredictor.predict(results)

        for p in patterns:
            self.assertIn("pattern", p)
            self.assertIn("failure_count", p)
            self.assertIn("example_errors", p)
            self.assertIn("severity", p)

    def test_recommendations_generated(self):
        """Recommendations should be generated for fragile bricks."""
        cases = EdgeCaseGenerator.generate(fragile_brick)
        results = PhantomExecutor.run(fragile_brick, cases)
        score, patterns = FailurePredictor.predict(results)
        recs = FailurePredictor.generate_recommendations(score, patterns, results)
        self.assertGreater(len(recs), 0, "Should have at least one recommendation")


class TestPhantomEngine(unittest.TestCase):
    """Tests for PhantomEngine (orchestrator)."""

    def setUp(self):
        self.engine = PhantomEngine()

    def test_analyze_returns_fragility_report(self):
        """analyze() should return a FragilityReport."""
        report = self.engine.analyze(robust_brick)
        self.assertIsInstance(report, FragilityReport)

    def test_report_has_required_fields(self):
        """Report should have all required fields."""
        report = self.engine.analyze(fragile_brick)
        self.assertIsNotNone(report.brick_id)
        self.assertIsNotNone(report.brick_name)
        self.assertIsNotNone(report.version)
        self.assertGreater(report.total_cases, 0)
        self.assertEqual(report.total_cases, report.passed + report.failed)
        self.assertGreaterEqual(report.fragility_score, 0.0)
        self.assertLessEqual(report.fragility_score, 1.0)
        self.assertIsInstance(report.results, list)
        self.assertIsInstance(report.dangerous_patterns, list)
        self.assertIsInstance(report.recommendations, list)

    def test_generate_report_text(self):
        """generate_report() should produce a non-empty string."""
        report = self.engine.analyze(medium_brick)
        text = PhantomEngine.generate_report(report)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 100)
        self.assertIn("PHANTOM ANALYSIS REPORT", text)
        self.assertIn("Fragility Score", text)
        self.assertIn("RECOMMENDATIONS", text)

    def test_analyze_many(self):
        """analyze_many() should return a report for each brick."""
        bricks = [robust_brick, fragile_brick, medium_brick]
        reports = self.engine.analyze_many(bricks)
        self.assertEqual(len(reports), 3)
        for r in reports:
            self.assertIsInstance(r, FragilityReport)

    def test_fragile_vs_robust_ordering(self):
        """Fragile brick should always score higher than robust brick."""
        r_report = self.engine.analyze(robust_brick)
        f_report = self.engine.analyze(fragile_brick)
        self.assertGreater(
            f_report.fragility_score,
            r_report.fragility_score,
            "Fragile brick should be scored more fragile"
        )

    def test_with_sensory_integration(self):
        """Engine should work with SensoryMonitor without errors."""
        from synapticbricks.core.sensory import SensoryMonitor
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        sm = SensoryMonitor(data_path=os.path.join(data_dir, "test_phantom_sensory.json"))
        engine = PhantomEngine(sensory=sm)
        report = engine.analyze(robust_brick)
        self.assertIsInstance(report, FragilityReport)

    def test_with_genetic_integration(self):
        """Engine should work with GeneticMemory without errors."""
        from synapticbricks.core.genetic import GeneticMemory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        gm = GeneticMemory(data_path=os.path.join(data_dir, "test_phantom_genetic.json"))
        engine = PhantomEngine(genetic=gm)
        report = engine.analyze(fragile_brick)
        self.assertIsInstance(report, FragilityReport)


if __name__ == "__main__":
    unittest.main(verbosity=2)
