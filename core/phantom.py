"""
Phantom — The Predictive Failure Engine for BrickLang/Aegis-Brick.

Phantom runs "ghost executions" — it automatically generates edge case inputs
for a brick based on its type contract, runs them in a sandboxed way, and
predicts which inputs are likely to cause failures BEFORE deployment.

Components:
    - EdgeCaseGenerator: Contract-based dangerous input generation
    - PhantomExecutor:   Sandboxed ghost execution of edge cases
    - FailurePredictor:  Fragility scoring and pattern analysis
    - PhantomEngine:     Orchestrator tying everything together
"""

import math
import sys
import time
import traceback
import os
import psutil
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

from .brick import Brick


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EdgeCase:
    """A single edge-case test scenario."""
    label: str                          # e.g. "edge:empty_input"
    inputs: Dict[str, Any]             # kwargs to pass to brick.execute()
    description: str = ""              # human-readable explanation
    target_param: str = ""             # which param this edge case targets
    edge_type: str = ""                # category: "boundary", "null", "overflow", etc.


@dataclass
class PhantomResult:
    """Result of a single phantom (ghost) execution."""
    edge_case: EdgeCase
    success: bool
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_ms: float = 0.0
    memory_delta_bytes: int = 0


@dataclass
class FragilityReport:
    """Full fragility analysis for a brick."""
    brick_id: str
    brick_name: str
    version: str
    total_cases: int = 0
    passed: int = 0
    failed: int = 0
    fragility_score: float = 0.0       # 0.0 = bulletproof, 1.0 = extremely fragile
    results: List[PhantomResult] = field(default_factory=list)
    dangerous_patterns: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    avg_duration_ms: float = 0.0
    max_duration_ms: float = 0.0


# ---------------------------------------------------------------------------
# 1. Contract-Based Edge Case Generator
# ---------------------------------------------------------------------------

class EdgeCaseGenerator:
    """
    Generates dangerous edge-case inputs based on a brick's type contract.
    For each parameter type, produces known problematic values.
    """

    # Type -> list of (label_suffix, value, description)
    _EDGE_CASES = {
        "str": [
            ("empty_string",     "",                         "Empty string"),
            ("none_string",      None,                       "None instead of string"),
            ("long_string",      "A" * 10_000,               "Very long string (10k chars)"),
            ("unicode",          "\u202e\u200b\u00e9\u00e8\u00ea\u00eb\U0001f480",  "Unicode with special chars"),
            ("special_chars",    "!@#$%^&*(){}[]|\\:\";<>?,./~`", "Special characters"),
            ("newlines",         "line1\nline2\rline3\r\n",  "String with mixed newlines"),
            ("null_byte",        "hello\x00world",           "String with null byte"),
            ("sql_injection",    "'; DROP TABLE users; --",  "SQL injection pattern"),
            ("whitespace_only",  "   \t\n  ",                "Whitespace-only string"),
            ("numeric_string",   "12345",                    "Numeric string"),
        ],
        "int": [
            ("zero",             0,                          "Zero"),
            ("negative_one",     -1,                         "Negative one"),
            ("max_int",          sys.maxsize,                "Maximum integer"),
            ("min_int",          -sys.maxsize - 1,           "Minimum integer"),
            ("none_int",         None,                       "None instead of int"),
            ("large_positive",   10**18,                     "Very large positive"),
            ("large_negative",   -(10**18),                  "Very large negative"),
            ("one",              1,                          "One"),
        ],
        "float": [
            ("zero_float",       0.0,                        "Zero float"),
            ("neg_zero",         -0.0,                       "Negative zero"),
            ("inf",              float("inf"),                "Positive infinity"),
            ("neg_inf",          float("-inf"),               "Negative infinity"),
            ("nan",              float("nan"),                "NaN"),
            ("none_float",       None,                       "None instead of float"),
            ("very_small",       1e-308,                     "Very small float"),
            ("very_large",       1e+308,                     "Very large float"),
            ("epsilon",          sys.float_info.epsilon,      "Machine epsilon"),
            ("neg_small",        -1e-308,                    "Very small negative float"),
        ],
        "list": [
            ("empty_list",       [],                         "Empty list"),
            ("single_element",   [1],                        "Single element list"),
            ("large_list",       list(range(10_000)),         "Very large list (10k items)"),
            ("nested_lists",     [[1, [2, [3]]]],            "Deeply nested list"),
            ("none_list",        None,                       "None instead of list"),
            ("mixed_types",      [1, "two", 3.0, None, True], "Mixed-type list"),
            ("list_with_none",   [None, None, None],         "List of Nones"),
        ],
        "dict": [
            ("empty_dict",       {},                         "Empty dict"),
            ("none_dict",        None,                       "None instead of dict"),
            ("nested_dict",      {"a": {"b": {"c": 1}}},    "Deeply nested dict"),
            ("large_dict",       {f"key_{i}": i for i in range(1000)}, "Large dict (1k keys)"),
            ("special_keys",     {"": 1, " ": 2, "\n": 3},  "Dict with special keys"),
            ("mixed_values",     {"a": 1, "b": "two", "c": None}, "Dict with mixed value types"),
        ],
        "bool": [
            ("true",             True,                       "True"),
            ("false",            False,                      "False"),
            ("none_bool",        None,                       "None instead of bool"),
            ("zero_as_bool",     0,                          "Zero (falsy int)"),
            ("one_as_bool",      1,                          "One (truthy int)"),
            ("empty_str_bool",   "",                         "Empty string (falsy)"),
        ],
    }

    # Aliases so type annotations using different spellings still match
    _TYPE_ALIASES = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
        "dictionary": "dict",
        "mapping": "dict",
        "sequence": "list",
    }

    @classmethod
    def generate(cls, brick: Brick) -> List[EdgeCase]:
        """
        Generate edge cases from a brick's contract.
        Returns a list of EdgeCase objects ready to be fed to PhantomExecutor.
        """
        contract_inputs = brick.contract.inputs  # Dict[str, str]
        if not contract_inputs:
            return []

        edge_cases: List[EdgeCase] = []
        param_names = list(contract_inputs.keys())
        param_types = list(contract_inputs.values())

        for param_name, type_str in contract_inputs.items():
            canonical = cls._canonicalize_type(type_str)
            cases_for_type = cls._EDGE_CASES.get(canonical, [])

            for label_suffix, value, description in cases_for_type:
                # Build full kwargs: use a "safe default" for other params,
                # only the target param gets the edge-case value.
                inputs = cls._build_safe_defaults(contract_inputs)
                inputs[param_name] = value

                edge_cases.append(EdgeCase(
                    label=f"edge:{label_suffix}",
                    inputs=inputs,
                    description=f"{param_name}: {description}",
                    target_param=param_name,
                    edge_type=cls._classify_edge(label_suffix),
                ))

        return edge_cases

    @classmethod
    def _canonicalize_type(cls, type_str: str) -> str:
        """Normalize a type string to one of our known categories."""
        t = type_str.strip().lower()
        # Strip typing wrappers like Optional[str] -> str
        for prefix in ("optional[", "list[", "dict[", "set[", "tuple["):
            if t.startswith(prefix):
                inner = t[len(prefix):-1] if t.endswith("]") else t[len(prefix):]
                # For Optional, use the inner type
                if prefix == "optional[":
                    t = inner.split(",")[0].strip()
                else:
                    # For containers keep the container type
                    t = prefix.split("[")[0]
                break
        return cls._TYPE_ALIASES.get(t, t)

    @classmethod
    def _build_safe_defaults(cls, contract_inputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Build a set of 'safe' default values for all params so we can
        isolate one param at a time for edge-case testing.
        """
        defaults = {
            "str": "test_input",
            "int": 1,
            "float": 1.0,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "bool": True,
        }
        result = {}
        for param, type_str in contract_inputs.items():
            canonical = cls._canonicalize_type(type_str)
            result[param] = defaults.get(canonical, "test")
        return result

    @classmethod
    def _classify_edge(cls, label_suffix: str) -> str:
        """Classify the edge type for pattern analysis."""
        if "none" in label_suffix or "null" in label_suffix:
            return "null_safety"
        if "empty" in label_suffix:
            return "empty_input"
        if "large" in label_suffix or "long" in label_suffix or "max" in label_suffix:
            return "overflow"
        if "inf" in label_suffix or "nan" in label_suffix:
            return "special_numeric"
        if "injection" in label_suffix:
            return "injection"
        if "neg" in label_suffix or "min" in label_suffix:
            return "boundary"
        if "zero" in label_suffix:
            return "zero_division"
        if "special" in label_suffix or "unicode" in label_suffix:
            return "encoding"
        return "general"


# ---------------------------------------------------------------------------
# 2. Phantom Executor
# ---------------------------------------------------------------------------

class PhantomExecutor:
    """
    Runs edge cases against a brick in a sandboxed try/except.
    Pure observation — never modifies the brick.
    """

    @staticmethod
    def run(brick: Brick, edge_cases: List[EdgeCase],
            timeout_ms: float = 5000) -> List[PhantomResult]:
        """
        Execute all edge cases against a brick and collect results.
        Each case runs independently; one crash doesn't stop the rest.
        """
        results: List[PhantomResult] = []
        process = psutil.Process(os.getpid())

        for case in edge_cases:
            mem_before = process.memory_info().rss
            start = time.perf_counter()

            try:
                brick.func(**case.inputs)
                duration_ms = (time.perf_counter() - start) * 1000
                mem_after = process.memory_info().rss

                results.append(PhantomResult(
                    edge_case=case,
                    success=True,
                    duration_ms=round(duration_ms, 3),
                    memory_delta_bytes=mem_after - mem_before,
                ))
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                mem_after = process.memory_info().rss

                results.append(PhantomResult(
                    edge_case=case,
                    success=False,
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_ms=round(duration_ms, 3),
                    memory_delta_bytes=mem_after - mem_before,
                ))

        return results


# ---------------------------------------------------------------------------
# 3. Failure Predictor
# ---------------------------------------------------------------------------

class FailurePredictor:
    """
    Analyzes phantom run results and computes fragility scores.
    """

    @staticmethod
    def predict(results: List[PhantomResult]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyze results to produce:
          - fragility_score: 0.0 (bulletproof) to 1.0 (extremely fragile)
          - dangerous_patterns: ranked list of most dangerous input patterns

        Returns (fragility_score, dangerous_patterns).
        """
        if not results:
            return 0.0, []

        total = len(results)
        failures = [r for r in results if not r.success]
        fail_count = len(failures)

        # Base fragility: fail ratio
        base_score = fail_count / total

        # Weight by severity: TypeError/ValueError are less scary than
        # ZeroDivisionError, MemoryError, RecursionError, etc.
        severity_weights = {
            "TypeError": 0.4,
            "ValueError": 0.5,
            "KeyError": 0.6,
            "IndexError": 0.6,
            "AttributeError": 0.7,
            "ZeroDivisionError": 0.8,
            "OverflowError": 0.8,
            "RecursionError": 0.9,
            "MemoryError": 1.0,
            "RuntimeError": 0.7,
        }

        if failures:
            severity_sum = sum(
                severity_weights.get(f.error_type, 0.6) for f in failures
            )
            avg_severity = severity_sum / len(failures)
        else:
            avg_severity = 0.0

        # Combine: 60% fail rate + 40% severity
        fragility = 0.6 * base_score + 0.4 * avg_severity * base_score
        fragility = round(min(1.0, fragility), 4)

        # Pattern analysis
        pattern_counter: Counter = Counter()
        pattern_errors: Dict[str, List[str]] = {}
        for r in failures:
            edge_type = r.edge_case.edge_type
            pattern_counter[edge_type] += 1
            pattern_errors.setdefault(edge_type, []).append(
                f"{r.error_type}: {r.error}"
            )

        dangerous_patterns = []
        for pattern, count in pattern_counter.most_common():
            dangerous_patterns.append({
                "pattern": pattern,
                "failure_count": count,
                "example_errors": list(set(pattern_errors[pattern]))[:3],
                "severity": round(count / total, 3),
            })

        return fragility, dangerous_patterns

    @staticmethod
    def generate_recommendations(
        fragility: float,
        dangerous_patterns: List[Dict[str, Any]],
        results: List[PhantomResult],
    ) -> List[str]:
        """Generate actionable hardening recommendations."""
        recs: List[str] = []

        if fragility == 0.0:
            recs.append("This brick handles all tested edge cases. Well done!")
            return recs

        if fragility >= 0.8:
            recs.append("CRITICAL: This brick is extremely fragile and needs immediate hardening.")
        elif fragility >= 0.5:
            recs.append("WARNING: This brick has significant fragility. Consider adding input validation.")
        elif fragility >= 0.2:
            recs.append("NOTICE: Some edge cases cause failures. Add guards for robustness.")

        pattern_names = [p["pattern"] for p in dangerous_patterns]

        if "null_safety" in pattern_names:
            recs.append("Add None/null checks for all input parameters.")
        if "empty_input" in pattern_names:
            recs.append("Handle empty inputs (empty string, empty list, empty dict) gracefully.")
        if "overflow" in pattern_names:
            recs.append("Add bounds checking for large inputs to prevent overflow/memory issues.")
        if "zero_division" in pattern_names:
            recs.append("Guard against zero-value inputs that may cause division errors.")
        if "special_numeric" in pattern_names:
            recs.append("Handle special float values (inf, NaN, -0.0) explicitly.")
        if "injection" in pattern_names:
            recs.append("Sanitize string inputs to prevent injection attacks.")
        if "encoding" in pattern_names:
            recs.append("Ensure proper handling of unicode and special characters.")
        if "boundary" in pattern_names:
            recs.append("Add boundary checks for negative and extreme values.")

        # Performance recs
        slow_results = [r for r in results if r.duration_ms > 100]
        if slow_results:
            recs.append(
                f"Performance: {len(slow_results)} edge cases took >100ms. "
                "Consider adding timeouts or input size limits."
            )

        return recs


# ---------------------------------------------------------------------------
# 4. Phantom Engine (Orchestrator)
# ---------------------------------------------------------------------------

class PhantomEngine:
    """
    Main orchestrator that ties together edge case generation,
    phantom execution, failure prediction, and reporting.

    Optionally integrates with SensoryMonitor and GeneticMemory.
    """

    def __init__(self, sensory=None, genetic=None):
        """
        Args:
            sensory: Optional SensoryMonitor instance for logging phantom runs
            genetic: Optional GeneticMemory instance for recording fragility per version
        """
        self.sensory = sensory
        self.genetic = genetic
        self.generator = EdgeCaseGenerator
        self.executor = PhantomExecutor
        self.predictor = FailurePredictor

    def analyze(self, brick: Brick) -> FragilityReport:
        """
        Full phantom analysis pipeline for a single brick:
        1. Generate edge cases from contract
        2. Run all edge cases
        3. Predict failures and score fragility
        4. Build report with recommendations
        5. Log to Sensory/Genetic if available
        """
        # Step 1: Generate
        edge_cases = self.generator.generate(brick)

        # Step 2: Execute
        results = self.executor.run(brick, edge_cases)

        # Step 3: Predict
        fragility, dangerous_patterns = self.predictor.predict(results)

        # Step 4: Recommendations
        recommendations = self.predictor.generate_recommendations(
            fragility, dangerous_patterns, results
        )

        # Build report
        total = len(results)
        passed = sum(1 for r in results if r.success)
        failed = total - passed
        durations = [r.duration_ms for r in results]

        report = FragilityReport(
            brick_id=brick.meta.id,
            brick_name=brick.meta.name,
            version=brick.meta.version,
            total_cases=total,
            passed=passed,
            failed=failed,
            fragility_score=fragility,
            results=results,
            dangerous_patterns=dangerous_patterns,
            recommendations=recommendations,
            avg_duration_ms=round(sum(durations) / max(len(durations), 1), 3),
            max_duration_ms=round(max(durations, default=0), 3),
        )

        # Step 5: Integrations
        self._log_to_sensory(brick, report)
        self._log_to_genetic(brick, report)

        return report

    def analyze_many(self, bricks: List[Brick]) -> List[FragilityReport]:
        """Analyze multiple bricks and return all reports."""
        return [self.analyze(brick) for brick in bricks]

    def _log_to_sensory(self, brick: Brick, report: FragilityReport) -> None:
        """Log phantom run to SensoryMonitor if available."""
        if self.sensory is None:
            return
        try:
            status = "healthy" if report.fragility_score < 0.3 else "fragile"
            self.sensory.log_event(
                brick_id=f"phantom:{brick.meta.id}",
                latency=report.avg_duration_ms / 1000,  # convert to seconds
                memory_delta=0,
                status=status,
                error=f"fragility={report.fragility_score}, failed={report.failed}/{report.total_cases}"
                      if report.failed > 0 else None,
            )
        except Exception:
            pass  # Don't let logging failures break phantom analysis

    def _log_to_genetic(self, brick: Brick, report: FragilityReport) -> None:
        """Record fragility score in GeneticMemory if available."""
        if self.genetic is None:
            return
        try:
            # Genetic score is inverse of fragility (higher = healthier)
            genetic_score = round(1.0 - report.fragility_score, 4)
            self.genetic.record_evolution(
                brick_id=brick.meta.id,
                source_code=brick.source,
                version=brick.meta.version,
                reason=f"phantom_analysis: fragility={report.fragility_score}",
                status="healthy" if report.fragility_score < 0.5 else "fragile",
                score=genetic_score,
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Report formatting
    # ------------------------------------------------------------------

    @staticmethod
    def generate_report(report: FragilityReport) -> str:
        """
        Generate a human-readable phantom analysis report.
        """
        lines = []
        bar = "=" * 60

        # Header
        lines.append(bar)
        lines.append(f"  PHANTOM ANALYSIS REPORT")
        lines.append(f"  Brick: {report.brick_name} ({report.brick_id})")
        lines.append(f"  Version: {report.version}")
        lines.append(bar)

        # Summary
        lines.append("")
        lines.append(f"  Total Edge Cases Tested:  {report.total_cases}")
        lines.append(f"  Passed:                   {report.passed}")
        lines.append(f"  Failed:                   {report.failed}")

        # Fragility gauge
        score = report.fragility_score
        if score == 0:
            gauge = "BULLETPROOF"
            icon = "\u2705"
        elif score < 0.2:
            gauge = "ROBUST"
            icon = "\U0001f7e2"
        elif score < 0.5:
            gauge = "MODERATE"
            icon = "\U0001f7e1"
        elif score < 0.8:
            gauge = "FRAGILE"
            icon = "\U0001f7e0"
        else:
            gauge = "CRITICAL"
            icon = "\U0001f534"

        filled = int(score * 20)
        bar_visual = "\u2588" * filled + "\u2591" * (20 - filled)
        lines.append("")
        lines.append(f"  Fragility Score: {score:.4f}  [{bar_visual}]  {icon} {gauge}")

        # Performance
        lines.append("")
        lines.append(f"  Avg Duration:  {report.avg_duration_ms:.2f} ms")
        lines.append(f"  Max Duration:  {report.max_duration_ms:.2f} ms")

        # Dangerous patterns
        lines.append("")
        lines.append("-" * 60)
        lines.append("  TOP DANGEROUS PATTERNS")
        lines.append("-" * 60)

        if report.dangerous_patterns:
            for i, p in enumerate(report.dangerous_patterns[:5], 1):
                lines.append(f"  {i}. [{p['pattern']}]  ({p['failure_count']} failures, severity: {p['severity']})")
                for err in p.get("example_errors", [])[:2]:
                    lines.append(f"     -> {err}")
        else:
            lines.append("  No dangerous patterns found. All edge cases passed!")

        # Recommendations
        lines.append("")
        lines.append("-" * 60)
        lines.append("  RECOMMENDATIONS")
        lines.append("-" * 60)
        for rec in report.recommendations:
            lines.append(f"  * {rec}")

        # Failure details (top 10)
        failed_results = [r for r in report.results if not r.success]
        if failed_results:
            lines.append("")
            lines.append("-" * 60)
            lines.append(f"  FAILURE DETAILS (showing {min(10, len(failed_results))} of {len(failed_results)})")
            lines.append("-" * 60)
            for r in failed_results[:10]:
                lines.append(f"  [{r.edge_case.label}] {r.edge_case.description}")
                lines.append(f"     Error: {r.error_type}: {r.error}")
                lines.append(f"     Duration: {r.duration_ms:.2f} ms")

        lines.append("")
        lines.append(bar)
        lines.append(f"  End of Phantom Report for {report.brick_id}")
        lines.append(bar)

        return "\n".join(lines)
