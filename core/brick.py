"""
Brick — The fundamental unit of synapticbricks.
Each brick is a single function with a strict contract:
  - Typed inputs
  - Typed outputs
  - Unique ID
  - Version tracking
  - Checksum for integrity
"""

import hashlib
import inspect
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .label import BrickLabel


@dataclass
class BrickContract:
    """Defines what a brick expects and what it produces."""
    inputs: Dict[str, str]     # param_name -> type_name
    output: str                # return type name
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)


@dataclass
class BrickMeta:
    """Metadata attached to every brick."""
    id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = "pure"      # pure | io | glue
    checksum: str = ""
    created_at: float = 0.0
    updated_at: float = 0.0
    error_count: int = 0
    fix_count: int = 0
    last_error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


class Brick:
    """
    A Brick wraps a single function with:
    - A strict I/O contract
    - Metadata for tracking
    - Source code capture for AI repair
    - Isolated execution with error capture
    """

    def __init__(
        self,
        func: Callable,
        brick_id: str,
        name: str = "",
        version: str = "1.0.0",
        description: str = "",
        category: str = "pure",
        dependencies: Optional[List[str]] = None,
        preconditions: Optional[List[str]] = None,
        postconditions: Optional[List[str]] = None,
        source_override: Optional[str] = None, # New param
    ):
        self.func = func
        
        if source_override:
            self.source = source_override
        else:
            try:
                self.source = inspect.getsource(func)
            except (OSError, TypeError):
                self.source = "# Source unavailable (dynamic function)"
        
        now = time.time()

        # Build contract from type hints
        hints = func.__annotations__.copy()
        return_type = hints.pop("return", "Any")
        inputs = {k: v.__name__ if isinstance(v, type) else str(v) for k, v in hints.items()}
        output_str = return_type.__name__ if isinstance(return_type, type) else str(return_type)

        self.contract = BrickContract(
            inputs=inputs,
            output=output_str,
            preconditions=preconditions or [],
            postconditions=postconditions or [],
        )

        self.meta = BrickMeta(
            id=brick_id,
            name=name or func.__name__,
            version=version,
            description=description or (func.__doc__ or "").strip(),
            category=category,
            checksum=self._compute_checksum(),
            created_at=now,
            updated_at=now,
            dependencies=dependencies or [],
        )

        # Test cases attached to this brick
        self.tests: List[Dict[str, Any]] = []

        # Label (assigned by LabelRegistry)
        self.label: Optional["BrickLabel"] = None

    def _compute_checksum(self) -> str:
        """SHA256 of the source code for integrity tracking."""
        return hashlib.sha256(self.source.encode()).hexdigest()[:16]

    def add_test(self, inputs: Dict[str, Any], expected_output: Any, label: str = ""):
        """Attach a test case to this brick."""
        self.tests.append({
            "inputs": inputs,
            "expected": expected_output,
            "label": label or f"test_{len(self.tests) + 1}",
        })

    def execute(self, **kwargs) -> Any:
        """Run the brick with given inputs. Returns result or raises."""
        return self.func(**kwargs)

    def safe_execute(self, **kwargs) -> Dict[str, Any]:
        """
        Run the brick safely — capture errors instead of crashing.
        Returns {success, result, error, brick_id, duration_ms}
        """
        start = time.perf_counter()
        try:
            result = self.func(**kwargs)
            duration = (time.perf_counter() - start) * 1000
            return {
                "success": True,
                "result": result,
                "error": None,
                "brick_id": self.meta.id,
                "duration_ms": round(duration, 2),
            }
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            self.meta.error_count += 1
            self.meta.last_error = f"{type(e).__name__}: {str(e)}"
            return {
                "success": False,
                "result": None,
                "error": self.meta.last_error,
                "brick_id": self.meta.id,
                "duration_ms": round(duration, 2),
            }

    def get_repair_context(self) -> Dict[str, Any]:
        """
        Extract everything an AI needs to fix this brick:
        - Source code
        - Contract (expected I/O)
        - Last error
        - Test cases
        Nothing else. No other bricks. Minimal context = better AI fix.
        """
        return {
            "brick_id": self.meta.id,
            "label": self.label.full if self.label else None,
            "label_code": self.label.code if self.label else None,
            "name": self.meta.name,
            "source_code": self.source,
            "contract": {
                "inputs": self.contract.inputs,
                "output": self.contract.output,
                "preconditions": self.contract.preconditions,
                "postconditions": self.contract.postconditions,
            },
            "last_error": self.meta.last_error,
            "error_count": self.meta.error_count,
            "tests": self.tests,
            "description": self.meta.description,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize brick metadata for the registry."""
        return {
            "meta": asdict(self.meta),
            "contract": asdict(self.contract),
            "tests": self.tests,
            "source": self.source,
        }

    def __repr__(self):
        status = "✅" if self.meta.error_count == 0 else f"❌ ({self.meta.error_count} errors)"
        label_str = f" {self.label.full}" if self.label else ""
        return f"Brick[{self.meta.id}]{label_str} {self.meta.name} v{self.meta.version} {status}"


def brick(
    brick_id: str,
    name: str = "",
    version: str = "1.0.0",
    description: str = "",
    category: str = "pure",
    dependencies: Optional[List[str]] = None,
    preconditions: Optional[List[str]] = None,
    postconditions: Optional[List[str]] = None,
):
    """
    Decorator to turn a function into a Brick.

    Usage:
        @brick("parse_input", description="Parse raw JSON input")
        def parse_input(raw: str) -> dict:
            return json.loads(raw)
    """
    def wrapper(func: Callable) -> Brick:
        return Brick(
            func=func,
            brick_id=brick_id,
            name=name,
            version=version,
            description=description,
            category=category,
            dependencies=dependencies,
            preconditions=preconditions,
            postconditions=postconditions,
            source_override=None
        )
    return wrapper
