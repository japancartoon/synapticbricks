"""
BrickHealer — Self-healing system for broken bricks.
When a brick fails, the healer:
1. Identifies the broken brick
2. Extracts ONLY that brick's context (source + contract + error + tests)
3. Generates a repair prompt for AI
4. Applies the fix
5. Re-tests to verify
"""

import copy
import json
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
from .brick import Brick
from .engine import BrickEngine
from .tester import BrickTester


class RepairRequest:
    """Everything an AI needs to fix a broken brick - nothing more."""

    def __init__(self, brick: Brick, pipeline_error: Optional[str] = None):
        self.brick = brick
        self.pipeline_error = pipeline_error
        self.context = brick.get_repair_context()
        self.created_at = time.time()

    def to_prompt(self) -> str:
        """
        Generate a focused prompt for an AI to fix this brick.
        The prompt contains ONLY what's needed - no other code.
        Includes the brick's label for AI context compression.
        """
        label_info = ""
        if self.context.get('label'):
            label_info = f" [{self.context['label']}]"
            
        lines = [
            "# BRICK REPAIR REQUEST",
            "",
            f"## Brick: {self.context['name']}{label_info}",
            f"## ID: {self.context['brick_id']}",
        ]
        
        if self.context.get('label'):
            usage = self.context['label'].split('-')[1] if '-' in self.context['label'] else '?'
            lines.append(f"## Label: {self.context['label']} (used in {usage} places)")
            
        lines.extend([
            f"## Description: {self.context['description']}",
            "",
            "## Contract:",
            f"  Inputs: {json.dumps(self.context['contract']['inputs'])}",
            f"  Output: {self.context['contract']['output']}",
        ])

        if self.context['contract']['preconditions']:
            lines.append(f"  Preconditions: {self.context['contract']['preconditions']}")
        if self.context['contract']['postconditions']:
            lines.append(f"  Postconditions: {self.context['contract']['postconditions']}")

        lines.extend([
            "",
            "## Current Source Code:",
            "```python",
            self.context['source_code'],
            "```",
            "",
            f"## Error: {self.context['last_error']}",
            f"## Error Count: {self.context['error_count']}",
        ])

        if self.pipeline_error:
            lines.extend([
                "",
                f"## Pipeline Error Context: {self.pipeline_error}",
            ])

        if self.context['tests']:
            lines.extend(["", "## Test Cases:"])
            for t in self.context['tests']:
                lines.append(
                    f"  - {t['label']}: inputs={t['inputs']} -> expected={t['expected']}"
                )

        lines.extend([
            "",
            "## Instructions:",
            "1. Fix ONLY the specific bug causing test failures",
            "2. Make the MINIMAL change needed - don't rewrite working code",
            "3. Keep the function signature EXACTLY the same: @brick decorator, name, params, return type",
            "4. Handle edge cases gracefully (e.g., division by zero should return None or raise a clear error)",
            "5. Return ONLY the complete function code, including the @brick decorator",
            "6. The function must pass ALL test cases listed above",
            "",
            "Example format:",
            "```python",
            "@brick(\"function_id\", description=\"...\")",
            "def function_name(params):",
            "    # fixed code here",
            "    return result",
            "```",
        ])

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "brick_id": self.context["brick_id"],
            "context": self.context,
            "pipeline_error": self.pipeline_error,
            "prompt": self.to_prompt(),
            "created_at": self.created_at,
        }


class BrickHealer:
    """
    Self-healing engine for the brick system.

    Workflow:
    1. diagnose() - find all broken bricks
    2. create_repair_request() - generate AI-ready repair context
    3. apply_fix() - replace a brick's function with a fixed version
    4. verify_fix() - re-test to confirm the fix works
    """

    def __init__(self, engine: BrickEngine, tester: BrickTester):
        self.engine = engine
        self.tester = tester
        self.repair_history: List[Dict[str, Any]] = []

    def diagnose(self) -> Dict[str, Any]:
        """
        Run all tests and identify broken bricks.
        Returns diagnosis with broken brick IDs and their errors.
        """
        test_report = self.tester.test_all()
        broken = []

        for brick_id, result in test_report["results"].items():
            if result["status"] == "failed":
                brick = self.engine.get(brick_id)
                broken.append({
                    "brick_id": brick_id,
                    "label": brick.label.full if (brick and brick.label) else None,
                    "name": brick.meta.name if brick else "unknown",
                    "failed_tests": [
                        r for r in result["results"] if not r["passed"]
                    ],
                    "error_count": result["failed"],
                })

        return {
            "healthy": test_report["status"] == "all_passed",
            "total_bricks": test_report["total_bricks"],
            "broken_count": len(broken),
            "broken_bricks": broken,
            "test_report": test_report,
        }

    def create_repair_request(
        self, brick_id: str, pipeline_error: Optional[str] = None
    ) -> Optional[RepairRequest]:
        """
        Create a repair request for a specific broken brick.
        This is what gets sent to an AI for fixing.
        """
        brick = self.engine.get(brick_id)
        if not brick:
            return None
        return RepairRequest(brick, pipeline_error)

    def apply_fix(self, brick_id: str, fixed_func: Callable) -> bool:
        """
        Apply a fixed function to a brick.
        Preserves all metadata, tests, and contract.
        Updates checksum and version.
        """
        if fixed_func is None:
            return False
            
        brick = self.engine.get(brick_id)
        if not brick:
            return False

        # Save old state for rollback
        old_func = brick.func
        old_source = brick.source
        old_checksum = brick.meta.checksum

        # Apply fix
        import inspect
        brick.func = fixed_func
        try:
            brick.source = inspect.getsource(fixed_func)
        except OSError:
            brick.source = f"# Fixed function (source unavailable)\n# Original: {old_source}"
        brick.meta.checksum = brick._compute_checksum()
        brick.meta.updated_at = time.time()
        brick.meta.fix_count += 1

        # Bump patch version
        parts = brick.meta.version.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        brick.meta.version = ".".join(parts)

        # Record in history
        self.repair_history.append({
            "brick_id": brick_id,
            "label": brick.label.full if brick.label else None,
            "timestamp": time.time(),
            "old_checksum": old_checksum,
            "new_checksum": brick.meta.checksum,
            "new_version": brick.meta.version,
        })

        self.engine._save_registry()
        return True

    def verify_fix(self, brick_id: str) -> Dict[str, Any]:
        """
        Re-test a brick after a fix has been applied.
        Returns test results + whether the fix was successful.
        """
        brick = self.engine.get(brick_id)
        if not brick:
            return {"success": False, "error": "Brick not found"}

        result = self.tester.test_brick(brick)

        if result["status"] == "passed":
            # Fix worked - reset error count
            brick.meta.error_count = 0
            brick.meta.last_error = None
            self.engine._save_registry()

        return {
            "success": result["status"] == "passed",
            "brick_id": brick_id,
            "test_result": result,
        }

    def auto_heal(self, brick_id: str, fix_func: Callable) -> Dict[str, Any]:
        """
        Full heal cycle: apply fix -> verify -> report.
        One call does everything.
        """
        # Apply
        applied = self.apply_fix(brick_id, fix_func)
        if not applied:
            return {"success": False, "error": "Failed to apply fix", "brick_id": brick_id}

        # Verify
        verification = self.verify_fix(brick_id)

        return {
            "success": verification["success"],
            "brick_id": brick_id,
            "new_version": self.engine.get(brick_id).meta.version,
            "verification": verification,
        }

    def get_repair_history(self) -> List[Dict[str, Any]]:
        """Get full repair history."""
        return self.repair_history
