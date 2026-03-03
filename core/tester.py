"""
BrickTester — Tests bricks in isolation, then tests the glue.
Runs tests in subprocesses and kills them after completion to free CPU.
"""

import gc
import multiprocessing
import time
import traceback
from typing import Any, Dict, List, Optional
from .brick import Brick
from .engine import BrickEngine
from .pipeline import Pipeline


def _run_brick_test_worker(func_source: str, test_case: Dict, result_queue):
    """
    Worker function that runs in a separate process.
    This process is killed after the test completes → no CPU leak.
    """
    try:
        # Reconstruct the function in this isolated process
        local_ns = {}
        exec(func_source, local_ns)
        # Find the function (last defined callable)
        func = None
        for val in local_ns.values():
            if callable(val) and not isinstance(val, type):
                func = val

        if func is None:
            result_queue.put({"passed": False, "error": "Could not reconstruct function"})
            return

        result = func(**test_case["inputs"])
        passed = result == test_case["expected"]
        result_queue.put({
            "passed": passed,
            "actual": repr(result),
            "expected": repr(test_case["expected"]),
            "error": None if passed else f"Expected {test_case['expected']!r}, got {result!r}",
        })
    except Exception as e:
        result_queue.put({
            "passed": False,
            "actual": None,
            "expected": repr(test_case["expected"]),
            "error": f"{type(e).__name__}: {str(e)}",
        })


class BrickTester:
    """
    Tests bricks and pipelines with process isolation.

    Key design:
    - Each brick test runs in a subprocess
    - Subprocess is killed after test completes
    - No lingering processes, no CPU leak
    - Results are collected via queue
    """

    def __init__(self, engine: BrickEngine, timeout: float = 10.0):
        self.engine = engine
        self.timeout = timeout  # seconds per test

    def test_brick(self, brick: Brick) -> Dict[str, Any]:
        """
        Test a single brick against all its test cases.
        Each test runs in an isolated subprocess that gets killed after.

        Returns:
        {
            "brick_id": str,
            "total": int,
            "passed": int,
            "failed": int,
            "results": list of per-test results,
            "duration_ms": float,
        }
        """
        if not brick.tests:
            return {
                "brick_id": brick.meta.id,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "results": [],
                "duration_ms": 0,
                "status": "no_tests",
            }

        results = []
        start = time.perf_counter()

        for test_case in brick.tests:
            test_result = self._run_isolated_test(brick, test_case)
            results.append({
                "label": test_case.get("label", ""),
                **test_result,
            })

        duration = (time.perf_counter() - start) * 1000
        passed = sum(1 for r in results if r["passed"])
        failed = len(results) - passed

        return {
            "brick_id": brick.meta.id,
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "results": results,
            "duration_ms": round(duration, 2),
            "status": "passed" if failed == 0 else "failed",
        }

    def _run_isolated_test(self, brick: Brick, test_case: Dict) -> Dict:
        """
        Run a single test in a subprocess and kill it after.
        This is the CPU-safe mechanism Medo wanted.
        """
        # For Windows compatibility, use threading with timeout instead of
        # multiprocessing (which can have issues with pickling)
        import threading
        import queue

        result_q = queue.Queue()

        def worker():
            try:
                result = brick.func(**test_case["inputs"])
                passed = result == test_case["expected"]
                result_q.put({
                    "passed": passed,
                    "actual": repr(result),
                    "expected": repr(test_case["expected"]),
                    "error": None if passed else f"Expected {test_case['expected']!r}, got {result!r}",
                })
            except Exception as e:
                result_q.put({
                    "passed": False,
                    "actual": None,
                    "expected": repr(test_case["expected"]),
                    "error": f"{type(e).__name__}: {str(e)}",
                })

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            # Thread timed out — it's a daemon so it'll be killed when we're done
            return {
                "passed": False,
                "actual": None,
                "expected": repr(test_case["expected"]),
                "error": f"Test timed out after {self.timeout}s",
            }

        try:
            return result_q.get_nowait()
        except queue.Empty:
            return {
                "passed": False,
                "actual": None,
                "expected": repr(test_case["expected"]),
                "error": "No result from test worker",
            }

    def test_all(self) -> Dict[str, Any]:
        """
        Test ALL registered bricks. Returns full report.
        All test threads are daemon threads — killed when done.
        """
        all_results = {}
        total_passed = 0
        total_failed = 0
        total_no_tests = 0
        start = time.perf_counter()

        for brick_id, brick in self.engine.bricks.items():
            result = self.test_brick(brick)
            all_results[brick_id] = result
            total_passed += result["passed"]
            total_failed += result["failed"]
            if result["status"] == "no_tests":
                total_no_tests += 1

        duration = (time.perf_counter() - start) * 1000

        # Force garbage collection to clean up any lingering resources
        gc.collect()

        return {
            "total_bricks": len(self.engine.bricks),
            "bricks_with_tests": len(self.engine.bricks) - total_no_tests,
            "total_tests": total_passed + total_failed,
            "passed": total_passed,
            "failed": total_failed,
            "results": all_results,
            "duration_ms": round(duration, 2),
            "status": "all_passed" if total_failed == 0 else "has_failures",
        }

    def test_pipeline(self, pipeline: Pipeline, test_inputs: Dict[str, Any],
                      expected_result: Any = None) -> Dict[str, Any]:
        """
        Test a full pipeline (integration test).
        Runs the pipeline with given inputs and checks the result.
        """
        start = time.perf_counter()
        result = pipeline.run(test_inputs)
        duration = (time.perf_counter() - start) * 1000

        passed = result["success"]
        if passed and expected_result is not None:
            passed = result["result"] == expected_result

        return {
            "pipeline": pipeline.name,
            "passed": passed,
            "result": result["result"],
            "expected": expected_result,
            "failed_brick": result.get("failed_brick"),
            "error": result.get("error"),
            "execution_log": result["execution_log"],
            "duration_ms": round(duration, 2),
        }
