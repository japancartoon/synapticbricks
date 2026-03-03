"""
Pipeline — The glue that connects bricks together.
Defines execution order, data flow, and handles brick failures.
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from .brick import Brick
from .engine import BrickEngine


class PipelineStep:
    """A single step in a pipeline — maps to one brick."""

    def __init__(
        self,
        brick_id: str,
        input_map: Optional[Dict[str, str]] = None,
        output_key: str = "",
    ):
        self.brick_id = brick_id
        # input_map: maps brick param names to pipeline data keys
        # e.g. {"raw": "pipeline_input"} means brick's "raw" param gets value from pipeline's "pipeline_input"
        self.input_map = input_map or {}
        # output_key: where to store this brick's result in the pipeline data
        self.output_key = output_key or brick_id


class Pipeline:
    """
    Connects bricks in sequence with data flowing between them.

    The pipeline maintains a data dict. Each step:
    1. Pulls inputs from the data dict (via input_map)
    2. Runs the brick
    3. Stores the result back in the data dict (via output_key)

    If any brick fails, the pipeline stops and reports exactly which brick broke.
    """

    def __init__(self, name: str, engine: BrickEngine):
        self.name = name
        self.engine = engine
        self.steps: List[PipelineStep] = []
        self.execution_log: List[Dict[str, Any]] = []

    def add_step(
        self,
        brick_id: str,
        input_map: Optional[Dict[str, str]] = None,
        output_key: str = "",
    ) -> "Pipeline":
        """Add a brick step to the pipeline. Returns self for chaining."""
        self.steps.append(PipelineStep(brick_id, input_map, output_key))
        # Track usage in label registry
        self.engine.labels.record_usage(brick_id)
        return self

    def run(self, initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the full pipeline.

        Returns:
        {
            "success": bool,
            "result": final output or None,
            "data": full pipeline data dict,
            "failed_brick": brick_id or None,
            "error": error message or None,
            "execution_log": list of per-step results,
            "total_duration_ms": float,
        }
        """
        data = dict(initial_data or {})
        self.execution_log = []
        pipeline_start = time.perf_counter()

        for i, step in enumerate(self.steps):
            brick = self.engine.get(step.brick_id)
            if not brick:
                error_msg = f"Brick '{step.brick_id}' not found in registry"
                self.execution_log.append({
                    "step": i + 1,
                    "brick_id": step.brick_id,
                    "success": False,
                    "error": error_msg,
                })
                return self._failure_result(
                    data, step.brick_id, error_msg, pipeline_start
                )

            # Map inputs from pipeline data to brick params
            kwargs = {}
            if step.input_map:
                for param_name, data_key in step.input_map.items():
                    # Support nested key access (e.g., "validation.valid")
                    value = self._get_nested_value(data, data_key)
                    
                    if value is not None:
                        kwargs[param_name] = value
                    else:
                        error_msg = (
                            f"Input '{data_key}' not found in pipeline data "
                            f"for brick '{step.brick_id}' param '{param_name}'"
                        )
                        self.execution_log.append({
                            "step": i + 1,
                            "brick_id": step.brick_id,
                            "success": False,
                            "error": error_msg,
                        })
                        return self._failure_result(
                            data, step.brick_id, error_msg, pipeline_start
                        )
            else:
                # Auto-map: if no explicit map, pass all data as kwargs
                # Only pass params the brick actually accepts
                import inspect
                sig = inspect.signature(brick.func)
                for param in sig.parameters:
                    if param in data:
                        kwargs[param] = data[param]

            # Execute the brick safely
            result = brick.safe_execute(**kwargs)

            self.execution_log.append({
                "step": i + 1,
                "brick_id": step.brick_id,
                "success": result["success"],
                "duration_ms": result["duration_ms"],
                "error": result["error"],
            })

            if not result["success"]:
                return self._failure_result(
                    data, step.brick_id, result["error"], pipeline_start
                )

            # Store result in pipeline data
            data[step.output_key] = result["result"]

        total_duration = (time.perf_counter() - pipeline_start) * 1000

        # Final result is the output of the last step
        final_key = self.steps[-1].output_key if self.steps else None
        final_result = data.get(final_key) if final_key else None

        return {
            "success": True,
            "result": final_result,
            "data": data,
            "failed_brick": None,
            "error": None,
            "execution_log": self.execution_log,
            "total_duration_ms": round(total_duration, 2),
        }

    def _failure_result(
        self,
        data: Dict,
        failed_brick_id: str,
        error: str,
        start_time: float,
    ) -> Dict[str, Any]:
        total_duration = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "result": None,
            "data": data,
            "failed_brick": failed_brick_id,
            "error": error,
            "execution_log": self.execution_log,
            "total_duration_ms": round(total_duration, 2),
        }

    def visualize(self) -> str:
        """Show the pipeline as a text diagram with brick labels."""
        lines = [f"Pipeline: {self.name}", "=" * 40]
        for i, step in enumerate(self.steps):
            brick = self.engine.get(step.brick_id)
            status = "✅" if brick and brick.meta.error_count == 0 else "❌"
            name = brick.meta.name if brick else "MISSING"
            label = brick.label.full if (brick and brick.label) else "???"
            arrow = "  │" if i < len(self.steps) - 1 else ""
            lines.append(f"  [{i+1}] {status} {label:<12} {name}")
            if step.input_map:
                for param, key in step.input_map.items():
                    lines.append(f"      ← {key} → {param}")
            lines.append(f"      → {step.output_key}")
            if arrow:
                lines.append(arrow)
                lines.append("  ↓")
        return "\n".join(lines)
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """
        Get value from nested dict using dot notation.
        
        Examples:
            _get_nested_value({"a": {"b": 1}}, "a.b") -> 1
            _get_nested_value({"x": [1, 2]}, "x") -> [1, 2]
        
        Returns None if key not found.
        """
        if "." not in key:
            return data.get(key)
        
        keys = key.split(".")
        value = data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value

    def __repr__(self):
        return f"Pipeline[{self.name}] ({len(self.steps)} steps)"
