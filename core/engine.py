"""
BrickEngine — The central registry and manager for all bricks.
Tracks every brick, its state, versions, and checksums.
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from .brick import Brick
from .label import LabelRegistry, BRICK_CATEGORIES
from .phantom import EdgeCaseGenerator, PhantomExecutor


class SecurityError(Exception):
    """Raised when a brick fails security validation."""
    pass


class BrickEngine:
    """
    Central engine that:
    - Registers bricks with automatic labeling
    - Tracks their state
    - Provides lookup by ID or label code
    - Persists registry to disk
    - Reports health status
    """

    def __init__(self, project_dir: str = ".", security_auditor=None, enforce_security: bool = True, min_security_score: int = 40):
        self.project_dir = os.path.abspath(project_dir)
        self.registry_path = os.path.join(self.project_dir, "registry.json")
        self.bricks: Dict[str, Brick] = {}
        self.labels = LabelRegistry()
        self.security_auditor = security_auditor
        self.enforce_security = enforce_security
        self.min_security_score = min_security_score
        self._load_registry()

    def register(self, brick: Brick, category: str = "") -> None:
        """Register a brick in the engine with automatic label assignment."""
        
        # --- SECURITY ENFORCEMENT ---
        if self.security_auditor and self.enforce_security:
            try:
                # Temporarily add to registry for auditing
                temp_registered = brick.meta.id not in self.bricks
                if temp_registered:
                    self.bricks[brick.meta.id] = brick
                
                report = self.security_auditor.audit_brick(brick.meta.id)
                
                # Remove temp registration if we're rejecting
                if temp_registered and report.score < self.min_security_score:
                    del self.bricks[brick.meta.id]
                
                if report.score < self.min_security_score:
                    print(f"🚫 SECURITY REJECTED: Brick '{brick.meta.id}' scored {report.score}/100 (minimum: {self.min_security_score})")
                    print(f"   Risk Level: {report.risk_level.upper()}")
                    if report.critical_issues:
                        print(f"   Critical Issues:")
                        for issue in report.critical_issues[:3]:
                            print(f"     - {issue}")
                    print(f"   Fix these issues or disable security enforcement.")
                    raise SecurityError(f"Brick security score too low: {report.score}/{self.min_security_score}")
                
                elif report.score < 60:
                    print(f"⚠️  SECURITY WARNING: Brick '{brick.meta.id}' scored {report.score}/100 ({report.risk_level})")
                    if report.warnings:
                        for warning in report.warnings[:2]:
                            print(f"     - {warning}")
                
                # Remove temp registration - will be re-added below
                if temp_registered:
                    del self.bricks[brick.meta.id]
                    
            except Exception as e:
                if "SecurityError" in str(type(e).__name__):
                    raise
                print(f"⚠️  Security audit failed for '{brick.meta.id}': {e}")
        
        # --- LOGICAL GUARD: Prevent "Blind" Registration ---
        # Validate brick has type hints
        if not brick.contract.inputs:
            print(f"❌ REJECTED: Brick '{brick.meta.id}' has no type hints.")
            print(f"   The Synaptic nervous system requires types to generate edge cases.")
            return

        # Warn if no tests (can't be healed)
        if not brick.tests:
            # AUTO-TEST: Generate baseline tests from Phantom edge cases
            try:
                edge_cases = EdgeCaseGenerator.generate(brick)
                if edge_cases:
                    results = PhantomExecutor.run(brick, edge_cases)
                    attached = 0
                    for r in results:
                        if r.success:
                            # Run the brick to get expected output for this passing case
                            try:
                                expected = brick.func(**r.edge_case.inputs)
                                brick.add_test(
                                    inputs=r.edge_case.inputs,
                                    expected_output=expected,
                                    label=f"auto:{r.edge_case.label}"
                                )
                                attached += 1
                            except Exception:
                                pass
                    if attached > 0:
                        print(f"🧬 AUTO-TEST: Generated {attached} baseline tests for '{brick.meta.id}' from Phantom edge cases.")
                    else:
                        print(f"⚠️  VULNERABLE: Brick '{brick.meta.id}' failed all edge cases. No auto-tests attached.")
                else:
                    print(f"⚠️  VULNERABLE: Brick '{brick.meta.id}' has no type hints for auto-test generation.")
            except Exception as e:
                print(f"⚠️  VULNERABLE: Auto-test generation failed for '{brick.meta.id}': {e}")
        
        
        # Check for duplicate IDs
        if brick.meta.id in self.bricks:
            existing = self.bricks[brick.meta.id]
            print(f"🔄 UPDATING: Brick ID '{brick.meta.id}' (v{existing.meta.version} -> v{brick.meta.version})")
        
        self.bricks[brick.meta.id] = brick

        # Auto-detect category if not provided
        cat = category or self._detect_category(brick)
        label = self.labels.assign(brick.meta.id, cat)
        brick.label = label

        self._save_registry()

    def register_many(self, bricks: List[Brick], categories: Optional[Dict[str, str]] = None) -> None:
        """Register multiple bricks at once with optional category overrides."""
        cats = categories or {}
        for b in bricks:
            cat = cats.get(b.meta.id, "")
            self.register(b, category=cat)

    def _detect_category(self, brick: Brick) -> str:
        """
        Auto-detect the category based on brick metadata.
        Uses name, description, and existing category hints.
        """
        name = brick.meta.name.lower()
        desc = (brick.meta.description or "").lower()
        text = f"{name} {desc}"

        # Pattern matching for auto-categorization
        patterns = {
            "parse": ["parse", "deserialize", "decode", "extract"],
            "v": ["valid", "check", "verify", "ensure", "assert"],
            "fmt": ["format", "display", "render", "pretty", "output", "template"],
            "io": ["read", "write", "file", "stream", "load", "save", "open"],
            "net": ["http", "api", "fetch", "request", "url", "socket", "webhook"],
            "db": ["database", "query", "sql", "insert", "select", "mongo", "redis"],
            "auth": ["auth", "login", "token", "password", "session", "oauth"],
            "err": ["error", "exception", "handle", "recover", "fallback", "retry"],
            "cfg": ["config", "setting", "env", "option", "parameter"],
            "log": ["log", "metric", "trace", "monitor", "telemetry"],
            "cache": ["cache", "memo", "store", "ttl"],
            "math": ["calc", "compute", "sum", "average", "math", "numeric"],
            "str": ["string", "text", "regex", "replace", "split", "join", "trim"],
            "arr": ["array", "list", "sort", "filter", "map", "reduce", "group"],
            "sec": ["encrypt", "decrypt", "hash", "sanitize", "escape"],
            "ctl": ["route", "switch", "branch", "dispatch", "control", "flow"],
            "d": ["transform", "convert", "map", "translate", "normalize"],
        }

        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text:
                    return category

        # Default: pure function
        return "f"

    def get(self, brick_id: str) -> Optional[Brick]:
        """Retrieve a brick by ID or label code (e.g., 'f54' or 'parse01')."""
        # Direct ID lookup first
        if brick_id in self.bricks:
            return self.bricks[brick_id]
        # Try label code lookup
        real_id = self.labels.get_brick_id(brick_id)
        if real_id:
            return self.bricks.get(real_id)
        return None

    def remove(self, brick_id: str) -> bool:
        """Remove a brick from the registry."""
        if brick_id in self.bricks:
            del self.bricks[brick_id]
            self._save_registry()
            return True
        return False

    def list_bricks(self) -> List[Dict[str, Any]]:
        """List all registered bricks with summary info including labels."""
        result = []
        for b in self.bricks.values():
            result.append({
                "id": b.meta.id,
                "label": b.label.full if b.label else None,
                "label_code": b.label.code if b.label else None,
                "name": b.meta.name,
                "version": b.meta.version,
                "category": b.meta.category,
                "checksum": b.meta.checksum,
                "errors": b.meta.error_count,
                "fixes": b.meta.fix_count,
                "tests": len(b.tests),
                "usage": b.label.usage_count if b.label else 0,
                "status": "healthy" if b.meta.error_count == 0 else "broken",
            })
        return result

    def get_code_map(self) -> str:
        """
        Generate the AI-readable code map.
        This is the compact 'dictionary' that shows all bricks in shorthand.
        """
        return self.labels.generate_code_map()

    def health_report(self) -> Dict[str, Any]:
        """Generate a health report for the entire brick system."""
        total = len(self.bricks)
        healthy = sum(1 for b in self.bricks.values() if b.meta.error_count == 0)
        broken = total - healthy
        total_errors = sum(b.meta.error_count for b in self.bricks.values())
        total_fixes = sum(b.meta.fix_count for b in self.bricks.values())

        broken_bricks = [
            {"id": b.meta.id, "name": b.meta.name, "error": b.meta.last_error}
            for b in self.bricks.values() if b.meta.error_count > 0
        ]

        return {
            "total_bricks": total,
            "healthy": healthy,
            "broken": broken,
            "total_errors": total_errors,
            "total_fixes": total_fixes,
            "broken_bricks": broken_bricks,
            "timestamp": time.time(),
        }

    def get_dependency_order(self) -> List[str]:
        """
        Topological sort of bricks by dependencies.
        Returns ordered list of brick IDs.
        """
        visited = set()
        order = []

        def visit(brick_id):
            if brick_id in visited:
                return
            visited.add(brick_id)
            brick = self.bricks.get(brick_id)
            if brick:
                for dep in brick.meta.dependencies:
                    visit(dep)
                order.append(brick_id)

        for bid in self.bricks:
            visit(bid)

        return order

    def _save_registry(self) -> None:
        """Persist registry metadata to disk."""
        data = {
            "version": "1.0",
            "brick_count": len(self.bricks),
            "last_updated": time.time(),
            "bricks": {}
        }
        for brick_id, b in self.bricks.items():
            data["bricks"][brick_id] = {
                "name": b.meta.name,
                "version": b.meta.version,
                "category": b.meta.category,
                "checksum": b.meta.checksum,
                "error_count": b.meta.error_count,
                "fix_count": b.meta.fix_count,
                "last_error": b.meta.last_error,
                "dependencies": b.meta.dependencies,
                "test_count": len(b.tests),
            }

        os.makedirs(os.path.dirname(self.registry_path) or ".", exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_registry(self) -> None:
        """Load registry from disk (metadata only — bricks must be re-registered)."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path) as f:
                    self._saved_registry = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._saved_registry = {}
        else:
            self._saved_registry = {}

    def __repr__(self):
        report = self.health_report()
        return (
            f"BrickEngine: {report['total_bricks']} bricks "
            f"({report['healthy']} healthy, {report['broken']} broken)"
        )
