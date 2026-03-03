"""
NeuralGuard — Self-Healing Code Quality Analyzer
Built on SynapticBricks to stress-test every feature of the ecosystem.

A project I genuinely wish existed: a pipeline that takes raw Python source code,
analyzes it for bugs, anti-patterns, complexity, and security issues, scores it,
and generates a human-readable report. If any analysis brick breaks on weird input,
the immune system heals it autonomously.

Tests EVERY SynapticBricks feature:
  - Pipeline (5-step analysis chain)
  - Sensory (light + full monitoring)
  - Phantom Auto-Test (bricks born with tests)
  - Immune System (self-healing on failure)
  - Genetic Memory (version tracking + dependency manifest)
  - Dependency Manifest (safe rollback)
"""
import sys, os, re, ast, math
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from synapticbricks.core import (
    brick, BrickEngine, sensory, SensoryMonitor,
    initialize_aegis, PhantomEngine, Pipeline
)

# ═══════════════════════════════════════════════════════════════
# BRICK 1: Source Parser — Converts raw code string into an AST
# ═══════════════════════════════════════════════════════════════
@brick("source_parser", description="Parses Python source code into structured data")
def source_parser(code: str) -> dict:
    """Parse Python source into structured metadata."""
    if not code or not code.strip():
        return {"valid": False, "error": "Empty source", "lines": 0, "functions": [], "classes": [], "imports": []}

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"valid": False, "error": str(e), "lines": code.count("\n") + 1,
                "functions": [], "classes": [], "imports": []}

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            has_docstring = (isinstance(node.body[0], ast.Expr) and
                          isinstance(node.body[0].value, (ast.Str, ast.Constant))) if node.body else False
            functions.append({
                "name": node.name,
                "args": args,
                "line": node.lineno,
                "length": node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                "has_docstring": has_docstring,
                "decorators": [getattr(d, 'id', getattr(d, 'attr', '?')) for d in node.decorator_list]
            })
        elif isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "line": node.lineno,
                          "methods": sum(1 for n in ast.walk(node) if isinstance(n, ast.FunctionDef))})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                imports.extend(a.name for a in node.names)
            else:
                imports.append(node.module or "")

    return {
        "valid": True,
        "lines": code.count("\n") + 1,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "tree": True  # Flag that AST parsed ok
    }


# ═══════════════════════════════════════════════════════════════
# BRICK 2: Complexity Analyzer — Calculates cyclomatic complexity
# ═══════════════════════════════════════════════════════════════
@brick("complexity_analyzer", description="Calculates code complexity metrics")
def complexity_analyzer(parsed: dict) -> dict:
    """Analyze complexity from parsed source data."""
    if not parsed.get("valid", False):
        return {"complexity_score": 0, "issues": [parsed.get("error", "Invalid source")],
                "func_count": 0, "avg_func_length": 0, "long_functions": []}

    functions = parsed.get("functions", [])
    func_count = len(functions)
    lengths = [f["length"] for f in functions]
    avg_length = sum(lengths) / max(len(lengths), 1)

    # Flag long functions (>30 lines)
    long_functions = [f["name"] for f in functions if f["length"] > 30]

    # Complexity heuristic: lines * (1 + funcs_without_docstrings / total)
    undocumented = sum(1 for f in functions if not f["has_docstring"])
    doc_penalty = undocumented / max(func_count, 1)
    lines = parsed.get("lines", 0)
    complexity_score = round(min(10, (lines / 50) * (1 + doc_penalty)), 2)

    issues = []
    if long_functions:
        issues.append(f"Long functions detected: {', '.join(long_functions)}")
    if doc_penalty > 0.5:
        issues.append(f"{undocumented}/{func_count} functions lack docstrings")
    if lines > 500:
        issues.append(f"File is {lines} lines — consider splitting")

    return {
        "complexity_score": complexity_score,
        "issues": issues,
        "func_count": func_count,
        "avg_func_length": round(avg_length, 1),
        "long_functions": long_functions
    }


# ═══════════════════════════════════════════════════════════════
# BRICK 3: Anti-Pattern Detector — Finds common Python mistakes
# ═══════════════════════════════════════════════════════════════
@brick("antipattern_detector", description="Detects common anti-patterns in code")
def antipattern_detector(code: str) -> dict:
    """Scan raw source for known anti-patterns."""
    if not code or not code.strip():
        return {"patterns_found": [], "severity": "none", "count": 0}

    patterns_found = []

    # Bare except
    if re.search(r'except\s*:', code):
        patterns_found.append({"pattern": "bare_except", "severity": "high",
                              "msg": "Bare 'except:' catches everything including SystemExit"})

    # Mutable default argument
    if re.search(r'def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})', code):
        patterns_found.append({"pattern": "mutable_default", "severity": "high",
                              "msg": "Mutable default argument (list/dict) — shared across calls"})

    # Global variable usage
    if re.search(r'^\s*global\s+', code, re.MULTILINE):
        patterns_found.append({"pattern": "global_usage", "severity": "medium",
                              "msg": "Global variable mutation — hard to test and debug"})

    # Star imports
    if re.search(r'from\s+\w+\s+import\s+\*', code):
        patterns_found.append({"pattern": "star_import", "severity": "medium",
                              "msg": "Star import pollutes namespace"})

    # exec/eval usage
    if re.search(r'\b(exec|eval)\s*\(', code):
        patterns_found.append({"pattern": "exec_eval", "severity": "critical",
                              "msg": "exec/eval usage — potential code injection risk"})

    # Hardcoded passwords/secrets
    if re.search(r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE):
        patterns_found.append({"pattern": "hardcoded_secret", "severity": "critical",
                              "msg": "Hardcoded secret/password detected"})

    # Type comparison with == instead of isinstance
    if re.search(r'type\s*\([^)]+\)\s*==', code):
        patterns_found.append({"pattern": "type_comparison", "severity": "low",
                              "msg": "Use isinstance() instead of type() =="})

    max_severity = "none"
    for p in patterns_found:
        if p["severity"] == "critical": max_severity = "critical"; break
        elif p["severity"] == "high" and max_severity != "critical": max_severity = "high"
        elif p["severity"] == "medium" and max_severity not in ("critical", "high"): max_severity = "medium"
        elif p["severity"] == "low" and max_severity == "none": max_severity = "low"

    return {
        "patterns_found": patterns_found,
        "severity": max_severity,
        "count": len(patterns_found)
    }


# ═══════════════════════════════════════════════════════════════
# BRICK 4: Quality Scorer — Combines all metrics into a final score
# ═══════════════════════════════════════════════════════════════
@brick("quality_scorer", description="Calculates final quality score from all analyses")
def quality_scorer(complexity: dict, antipatterns: dict) -> dict:
    """Combine complexity and anti-pattern data into a quality score."""
    base_score = 100.0

    # Deduct for complexity
    complexity_score = complexity.get("complexity_score", 0)
    base_score -= complexity_score * 3

    # Deduct for anti-patterns
    severity_costs = {"critical": 20, "high": 12, "medium": 6, "low": 3}
    for p in antipatterns.get("patterns_found", []):
        base_score -= severity_costs.get(p["severity"], 5)

    # Deduct for missing docs
    if complexity.get("func_count", 0) > 0:
        doc_ratio = len(complexity.get("long_functions", [])) / max(complexity["func_count"], 1)
        base_score -= doc_ratio * 10

    final_score = round(max(0, min(100, base_score)), 1)

    if final_score >= 85: grade = "A"
    elif final_score >= 70: grade = "B"
    elif final_score >= 55: grade = "C"
    elif final_score >= 40: grade = "D"
    else: grade = "F"

    return {"score": final_score, "grade": grade, "max_score": 100}


# ═══════════════════════════════════════════════════════════════
# BRICK 5: Report Generator — Builds human-readable output
# ═══════════════════════════════════════════════════════════════
@brick("report_generator", description="Generates a formatted quality report")
def report_generator(parsed: dict, complexity: dict, antipatterns: dict, quality: dict) -> str:
    """Generate a readable code quality report."""
    lines = []
    lines.append("=" * 50)
    lines.append("  NEURALGUARD CODE QUALITY REPORT")
    lines.append("=" * 50)
    lines.append("")

    # File stats
    lines.append(f"  Lines of Code:    {parsed.get('lines', '?')}")
    lines.append(f"  Functions:        {complexity.get('func_count', '?')}")
    lines.append(f"  Avg Func Length:  {complexity.get('avg_func_length', '?')} lines")
    lines.append(f"  Classes:          {len(parsed.get('classes', []))}")
    lines.append(f"  Imports:          {len(parsed.get('imports', []))}")
    lines.append("")

    # Quality score
    score = quality.get("score", 0)
    grade = quality.get("grade", "?")
    bar_filled = int(score / 5)
    bar = chr(9608) * bar_filled + chr(9617) * (20 - bar_filled)
    lines.append(f"  QUALITY SCORE: {score}/100  [{bar}]  Grade: {grade}")
    lines.append("")

    # Complexity issues
    issues = complexity.get("issues", [])
    if issues:
        lines.append("  COMPLEXITY ISSUES:")
        for issue in issues:
            lines.append(f"    - {issue}")
        lines.append("")

    # Anti-patterns
    patterns = antipatterns.get("patterns_found", [])
    if patterns:
        lines.append(f"  ANTI-PATTERNS ({len(patterns)} found):")
        for p in patterns:
            icon = {"critical": "!!!", "high": "!!", "medium": "!", "low": "~"}.get(p["severity"], "?")
            lines.append(f"    [{icon}] {p['pattern']}: {p['msg']}")
        lines.append("")

    if not issues and not patterns:
        lines.append("  No issues found. Clean code!")
        lines.append("")

    lines.append("=" * 50)
    return "\n".join(lines)
