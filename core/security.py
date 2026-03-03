"""
SecurityAuditor — Autonomous Security Scoring and Hardening
Scans bricks for vulnerabilities, scores them, and auto-hardens or regenerates.
"""
import ast
import re
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SecurityReport:
    """Security audit report for a brick."""
    brick_id: str
    score: int
    breakdown: Dict[str, int]
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    risk_level: str  # "trusted", "moderate", "risky", "dangerous"
    timestamp: float


class SecurityAuditor:
    """
    Autonomous security auditor for SynapticBricks.
    
    Scores bricks on a 0-100 scale across multiple dimensions:
    - Code patterns (dangerous imports, operations)
    - Input validation
    - Output safety
    - Dependency risk
    - Test coverage
    
    Auto-actions:
    - 80-100: Trusted (no action)
    - 60-79: Moderate (add validation)
    - 40-59: Risky (sandbox execution)
    - 0-39: Dangerous (auto-regenerate)
    """
    
    # Dangerous patterns and their severity
    DANGEROUS_PATTERNS = {
        # Critical (instant fail)
        "os.system": -20,
        "eval": -20,
        "exec": -20,
        "compile": -15,
        "__import__": -15,
        "pickle.loads": -20,
        "pickle.load": -20,
        
        # High risk
        "subprocess.Popen": -10,
        "subprocess.call": -8,
        "open": -4,  # File operations
        
        # Medium risk
        "requests.": -3,
        "urllib.": -3,
        "socket.": -8,
        "os.environ": -4,
        "sys.argv": -4,
        
        # Low risk (depends on context)
        "os.path": 0,  # Usually safe
        "os.remove": -8,
        "os.rmdir": -8,
        "shutil.rmtree": -15,
    }
    
    def __init__(self, engine, ai_healer=None):
        """
        Initialize SecurityAuditor.
        
        Args:
            engine: BrickEngine instance
            ai_healer: AIHealer instance (optional, for auto-regeneration)
        """
        self.engine = engine
        self.ai_healer = ai_healer
        self.audit_history: List[SecurityReport] = []
    
    def audit_brick(self, brick_id: str) -> SecurityReport:
        """
        Perform full security audit on a brick.
        
        Returns:
            SecurityReport with score, breakdown, and recommendations
        """
        brick = self.engine.get(brick_id)
        if not brick:
            raise ValueError(f"Brick '{brick_id}' not found")
        
        # Score each dimension
        scores = {
            "code_patterns": self._check_dangerous_patterns(brick),
            "input_validation": self._check_validation(brick),
            "output_safety": self._check_outputs(brick),
            "dependencies": self._check_dependencies(brick),
            "test_coverage": self._check_tests(brick)
        }
        
        total_score = sum(scores.values())
        
        # CRITICAL: If dangerous patterns detected, cap total score
        if scores["code_patterns"] < 25:  # Detected critical issues
            total_score = min(total_score, 45)  # Cap at 45 (below marketplace threshold)
        
        total_score = max(0, min(100, total_score))  # Clamp to 0-100
        
        # Determine risk level
        if total_score >= 80:
            risk_level = "trusted"
        elif total_score >= 60:
            risk_level = "moderate"
        elif total_score >= 40:
            risk_level = "risky"
        else:
            risk_level = "dangerous"
        
        # Generate detailed report
        critical_issues = []
        warnings = []
        recommendations = []
        
        # Check for critical issues
        if scores["code_patterns"] < 20:
            critical_issues.append("Dangerous code patterns detected (eval, exec, os.system)")
            recommendations.append("Remove dangerous operations or use safe alternatives")
        
        if scores["input_validation"] < 10:
            critical_issues.append("No input validation - vulnerable to injection attacks")
            recommendations.append("Add type checking and input sanitization")
        
        if scores["output_safety"] < 8:
            warnings.append("Weak error handling - may leak sensitive data")
            recommendations.append("Add comprehensive try/except blocks")
        
        if scores["test_coverage"] < 5:
            warnings.append("Low test coverage - untested edge cases")
            recommendations.append("Add security-focused test cases")
        
        report = SecurityReport(
            brick_id=brick_id,
            score=total_score,
            breakdown=scores,
            critical_issues=critical_issues,
            warnings=warnings,
            recommendations=recommendations,
            risk_level=risk_level,
            timestamp=time.time()
        )
        
        self.audit_history.append(report)
        return report
    
    def _check_dangerous_patterns(self, brick) -> int:
        """
        Check for dangerous code patterns via AST analysis.
        
        Returns:
            Score (0-40 points)
        """
        score = 40  # Start at max
        
        try:
            tree = ast.parse(brick.source)
        except SyntaxError:
            return 0  # Can't parse = dangerous
        
        dangerous_calls = []
        
        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                call_name = self._get_call_name(node)
                for pattern, penalty in self.DANGEROUS_PATTERNS.items():
                    if pattern in call_name:
                        score += penalty
                        dangerous_calls.append(call_name)
            
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = node.module if isinstance(node, ast.ImportFrom) else None
                names = [alias.name for alias in node.names]
                
                if module and any(danger in module for danger in ["os", "subprocess", "pickle", "socket"]):
                    score -= 2
                if any(danger in str(names) for danger in ["system", "exec", "eval"]):
                    score -= 5
        
        # Bonus for pure functions (no dangerous patterns)
        if score == 40:
            score += 5  # Bonus for clean code
        
        return max(0, min(40, score))
    
    def _check_validation(self, brick) -> int:
        """
        Check input validation quality.
        
        Returns:
            Score (0-20 points)
        """
        score = 0
        
        # Check if contract exists
        if brick.contract and brick.contract.inputs:
            score += 10  # Has type hints
        
        # Check for validation in source code
        validation_keywords = ["isinstance", "assert", "raise ValueError", "raise TypeError", "if not"]
        for keyword in validation_keywords:
            if keyword in brick.source:
                score += 2
        
        # Check for sanitization patterns
        if any(pattern in brick.source for pattern in ["strip()", "escape(", "sanitize"]):
            score += 3
        
        return min(20, score)
    
    def _check_outputs(self, brick) -> int:
        """
        Check output safety and error handling.
        
        Returns:
            Score (0-15 points)
        """
        score = 0
        
        # Check return type annotation
        if brick.contract and brick.contract.output:
            score += 5
        
        # Check for error handling
        if "try:" in brick.source and "except" in brick.source:
            score += 5
        
        # Check for specific exception handling (better than bare except)
        if re.search(r"except\s+\w+Error", brick.source):
            score += 3
        
        # Penalty for bare except (catches everything, bad practice)
        if re.search(r"except\s*:", brick.source):
            score -= 2
        
        return max(0, min(15, score))
    
    def _check_dependencies(self, brick) -> int:
        """
        Check dependency safety.
        
        Returns:
            Score (0-15 points)
        """
        score = 15  # Start at max
        
        # Parse imports
        try:
            tree = ast.parse(brick.source)
        except:
            return 5  # Can't parse, assume risky
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Penalty for risky modules
        risky_modules = ["subprocess", "pickle", "socket", "ctypes", "importlib"]
        for module in imports:
            if any(risky in module for risky in risky_modules):
                score -= 3
        
        # Bonus for minimal dependencies
        if len(imports) <= 2:
            score += 2
        
        return max(0, min(15, score))
    
    def _check_tests(self, brick) -> int:
        """
        Check test coverage and quality.
        
        Returns:
            Score (0-10 points)
        """
        if not brick.tests:
            return 0
        
        score = 0
        test_count = len(brick.tests)
        
        # Basic coverage
        if test_count >= 1:
            score += 3
        if test_count >= 3:
            score += 3
        if test_count >= 5:
            score += 2
        
        # Check for edge case tests
        edge_case_labels = ["edge", "boundary", "invalid", "error", "zero", "empty", "null"]
        for test in brick.tests:
            label = test.get("label", "").lower()
            if any(keyword in label for keyword in edge_case_labels):
                score += 1
        
        return min(10, score)
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function call name from AST node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return ".".join(parts)
        return ""
    
    def audit_all(self) -> Dict[str, SecurityReport]:
        """
        Audit all bricks in the engine.
        
        Returns:
            Dict mapping brick_id -> SecurityReport
        """
        results = {}
        bricks = self.engine.list_bricks()
        for brick_info in bricks:
            brick_id = brick_info["id"]
            try:
                report = self.audit_brick(brick_id)
                results[brick_id] = report
            except Exception as e:
                print(f"Error auditing brick '{brick_id}': {e}")
        
        return results
    
    def get_vulnerable_bricks(self, threshold: int = 60) -> List[str]:
        """
        Get list of brick IDs with security score below threshold.
        
        Args:
            threshold: Minimum acceptable score (default 60)
        
        Returns:
            List of brick IDs
        """
        vulnerable = []
        bricks = self.engine.list_bricks()
        for brick_info in bricks:
            brick_id = brick_info["id"]
            report = self.audit_brick(brick_id)
            if report.score < threshold:
                vulnerable.append(brick_id)
        
        return vulnerable
    
    def auto_harden(self, brick_id: str, report: SecurityReport = None) -> Dict[str, Any]:
        """
        Automatically harden a brick based on its security score.
        
        Actions:
        - 60-79: Add input validation wrapper
        - 40-59: Enable sandboxed execution
        - 0-39: Trigger AIHealer regeneration
        
        Args:
            brick_id: Brick to harden
            report: SecurityReport (auto-generated if not provided)
        
        Returns:
            Dict with action taken and result
        """
        if not report:
            report = self.audit_brick(brick_id)
        
        if report.score >= 80:
            return {"action": "none", "reason": "Brick is already trusted"}
        
        if report.score >= 60:
            # Add validation wrapper
            return {"action": "add_validation", "score": report.score, "status": "pending_implementation"}
        
        if report.score >= 40:
            # Sandbox execution
            brick = self.engine.get(brick_id)
            if brick:
                brick.meta.execution_mode = "sandboxed"
                return {"action": "sandboxed", "score": report.score, "status": "applied"}
        
        if report.score < 40:
            # Trigger regeneration via AIHealer
            if not self.ai_healer:
                return {"action": "regenerate", "status": "failed", "reason": "No AIHealer configured"}
            
            prompt = self._generate_security_prompt(brick_id, report)
            result = self.ai_healer.heal_brick(brick_id)
            
            return {
                "action": "regenerate",
                "score": report.score,
                "status": "completed" if result.get("success") else "failed",
                "result": result
            }
        
        return {"action": "unknown", "score": report.score}
    
    def _generate_security_prompt(self, brick_id: str, report: SecurityReport) -> str:
        """Generate security-focused regeneration prompt."""
        issues_str = "\n".join(f"- {issue}" for issue in report.critical_issues)
        recommendations_str = "\n".join(f"- {rec}" for rec in report.recommendations)
        
        return f"""
SECURITY AUDIT FAILED (Score: {report.score}/100)

Critical Issues:
{issues_str}

Recommendations:
{recommendations_str}

Regenerate this brick to be secure:
1. Remove ALL dangerous operations (os.system, eval, exec, pickle)
2. Add comprehensive input validation with type checking
3. Use safe alternatives only (subprocess.run with shell=False, not Popen)
4. Handle all exceptions explicitly (no bare except)
5. Return safe, validated outputs only
6. Add security-focused test cases

Keep the same functionality but make it production-safe.
"""
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get overall security summary for all bricks."""
        if not self.audit_history:
            return {"total_bricks": 0, "message": "No audits performed yet"}
        
        scores = [report.score for report in self.audit_history]
        risk_levels = [report.risk_level for report in self.audit_history]
        
        return {
            "total_bricks": len(scores),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "risk_distribution": {
                "trusted": risk_levels.count("trusted"),
                "moderate": risk_levels.count("moderate"),
                "risky": risk_levels.count("risky"),
                "dangerous": risk_levels.count("dangerous")
            }
        }
