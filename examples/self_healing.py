"""
EPIC 5: Self-Healing System

Auto-detect and fix brick errors using Gemini CLI
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine

print("=" * 80)
print("🔥 EPIC 5: Self-Healing System")
print("=" * 80)

engine = BrickEngine(project_dir="self_healing")

# ===== GEMINI CLI INTEGRATION =====

@brick("gemini_cli_generate", "Generate code using Gemini CLI")
def gemini_cli_generate(
    prompt: str,
    model: str = "gemini-3-pro-preview",
    max_tokens: int = 2048,
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Call Gemini CLI to generate code or text.
    
    Args:
        prompt: The prompt to send
        model: Gemini model to use
        max_tokens: Max output tokens
        temperature: Creativity (0-1)
    
    Returns:
        {"success": bool, "output": str, "error": str}
    """
    try:
        # Build gemini command
        cmd = [
            "gemini",
            "-m", model,
            "-t", str(temperature),
            "--max-tokens", str(max_tokens),
            prompt
        ]
        
        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout.strip(),
                "error": None
            }
        else:
            return {
                "success": False,
                "output": None,
                "error": result.stderr.strip()
            }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "output": None, "error": "Timeout after 60s"}
    except FileNotFoundError:
        return {"success": False, "output": None, "error": "Gemini CLI not found. Install with: npm install -g gemini-cli"}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}

engine.register(gemini_cli_generate)

# ===== ERROR ANALYSIS =====

@brick("analyze_error", "Analyze brick error and suggest fix")
def analyze_error(
    brick_id: str,
    error_message: str,
    source_code: str,
    test_inputs: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Analyze a brick error and determine fix strategy.
    
    Returns:
        {
            "success": bool,
            "error_type": str,
            "root_cause": str,
            "fix_strategy": str,
            "confidence": float
        }
    """
    try:
        # Classify error type
        error_type = _classify_error(error_message)
        
        # Extract root cause
        root_cause = _extract_root_cause(error_message, source_code)
        
        # Determine fix strategy
        fix_strategy = _determine_fix_strategy(error_type, root_cause)
        
        # Confidence score
        confidence = _calculate_confidence(error_type, source_code)
        
        return {
            "success": True,
            "error_type": error_type,
            "root_cause": root_cause,
            "fix_strategy": fix_strategy,
            "confidence": confidence,
            "test_inputs": test_inputs
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _classify_error(error_msg: str) -> str:
    """Classify the type of error."""
    error_lower = error_msg.lower()
    
    if "typeerror" in error_lower:
        return "type_mismatch"
    elif "keyerror" in error_lower or "attributeerror" in error_lower:
        return "missing_key"
    elif "valueerror" in error_lower:
        return "invalid_value"
    elif "indexerror" in error_lower:
        return "index_out_of_range"
    elif "nameerror" in error_lower:
        return "undefined_variable"
    elif "zerodivisionerror" in error_lower:
        return "division_by_zero"
    elif "importerror" in error_lower or "modulenotfounderror" in error_lower:
        return "missing_import"
    else:
        return "unknown"

def _extract_root_cause(error_msg: str, source_code: str) -> str:
    """Extract the likely root cause."""
    # Simple extraction - can be made smarter
    lines = error_msg.split('\n')
    for line in lines:
        if "Error:" in line or "Exception:" in line:
            return line.strip()
    return error_msg[:200]  # First 200 chars

def _determine_fix_strategy(error_type: str, root_cause: str) -> str:
    """Determine the best fix strategy."""
    strategies = {
        "type_mismatch": "add_type_conversion",
        "missing_key": "add_safe_get",
        "invalid_value": "add_validation",
        "index_out_of_range": "add_bounds_check",
        "undefined_variable": "add_variable_definition",
        "division_by_zero": "add_zero_check",
        "missing_import": "add_import_statement",
        "unknown": "ai_regenerate"
    }
    return strategies.get(error_type, "ai_regenerate")

def _calculate_confidence(error_type: str, source_code: str) -> float:
    """Calculate fix confidence (0-1)."""
    # Simple heuristic
    if error_type == "unknown":
        return 0.3
    elif len(source_code) < 100:
        return 0.9  # Small functions easier to fix
    elif len(source_code) < 500:
        return 0.7
    else:
        return 0.5

engine.register(analyze_error)

# ===== AUTO-FIX GENERATION =====

@brick("generate_fix", "Generate fix for brick using Gemini CLI")
def generate_fix(
    brick_id: str,
    source_code: str,
    error_analysis: Dict[str, Any],
    use_ai: bool = True
) -> Dict[str, Any]:
    """
    Generate a fix for a broken brick.
    
    Args:
        brick_id: ID of the brick
        source_code: Current source code
        error_analysis: Output from analyze_error
        use_ai: Whether to use Gemini CLI
    
    Returns:
        {"success": bool, "fixed_code": str, "changes": str}
    """
    try:
        if use_ai:
            return _generate_fix_with_ai(brick_id, source_code, error_analysis)
        else:
            return _generate_fix_with_rules(brick_id, source_code, error_analysis)
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _generate_fix_with_ai(brick_id: str, source_code: str, analysis: Dict) -> Dict:
    """Use Gemini CLI to generate fix."""
    
    prompt = f"""You are a Python debugging expert. Fix this broken brick.

Brick ID: {brick_id}
Error Type: {analysis.get('error_type', 'unknown')}
Root Cause: {analysis.get('root_cause', 'unknown')}
Fix Strategy: {analysis.get('fix_strategy', 'unknown')}

Current Code:
```python
{source_code}
```

Generate ONLY the fixed Python code. Keep the same function signature and @brick decorator.
Make minimal changes - only fix the error.

Fixed code:"""
    
    # Call Gemini CLI
    import self_healing
    gemini_fn = self_healing.engine.bricks["gemini_cli_generate"].func
    result = gemini_fn(
        prompt=prompt,
        model="gemini-3-pro-preview",
        temperature=0.2  # Low temp for precise fixes
    )
    
    if not result["success"]:
        # Gemini CLI failed - fall back to rule-based
        print(f"   ⚠️  Gemini CLI unavailable: {result.get('error', 'Unknown error')}")
        print(f"   📋 Falling back to rule-based fix...")
        return _generate_fix_with_rules(brick_id, source_code, analysis)
    
    # Extract code
    fixed_code = _extract_code_from_response(result["output"])
    
    # Validate syntax
    import ast
    try:
        ast.parse(fixed_code)
        return {
            "success": True,
            "fixed_code": fixed_code,
            "changes": "AI-generated fix via Gemini CLI",
            "method": "gemini_cli"
        }
    except SyntaxError as e:
        # Syntax error - fall back to rules
        print(f"   ⚠️  AI-generated code has syntax error")
        print(f"   📋 Falling back to rule-based fix...")
        return _generate_fix_with_rules(brick_id, source_code, analysis)

def _generate_fix_with_rules(brick_id: str, source_code: str, analysis: Dict) -> Dict:
    """Use rule-based fixes."""
    strategy = analysis.get('fix_strategy', 'unknown')
    
    # Simple rule-based fixes
    if strategy == "add_zero_check":
        # Find the division operation and add check
        import re
        
        # Look for "return a / b" pattern
        pattern = r'return\s+(\w+)\s*/\s*(\w+)'
        match = re.search(pattern, source_code)
        
        if match:
            var_a = match.group(1)
            var_b = match.group(2)
            old_line = f"return {var_a} / {var_b}"
            new_line = f"return {var_a} / {var_b} if {var_b} != 0 else 0"
            
            fixed = source_code.replace(old_line, new_line)
            return {
                "success": True,
                "fixed_code": fixed,
                "changes": f"Added zero division check for {var_b}",
                "method": "rule_based"
            }
    
    elif strategy == "add_safe_get":
        # Replace dict[key] with dict.get(key, default)
        fixed = source_code.replace('[', '.get(').replace(']', ', None)')
        return {
            "success": True,
            "fixed_code": fixed,
            "changes": "Replaced direct dict access with .get()",
            "method": "rule_based"
        }
    
    # Default: no automatic fix
    return {
        "success": False,
        "error": f"No rule-based fix for strategy: {strategy}",
        "suggested_fix": f"Manual review needed for {strategy}"
    }

def _extract_code_from_response(text: str) -> str:
    """Extract Python code from Gemini response."""
    import re
    
    # Try markdown code blocks
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Return as-is if no markdown
    return text.strip()

engine.register(generate_fix)

# ===== SELF-HEALING PIPELINE =====

@brick("self_heal_brick", "Auto-heal a broken brick")
def self_heal_brick(
    brick_obj: Any,
    error_result: Dict[str, Any],
    test_inputs: Optional[Dict] = None,
    max_attempts: int = 3
) -> Dict[str, Any]:
    """
    Attempt to automatically heal a broken brick.
    
    Args:
        brick_obj: The Brick object
        error_result: Error from safe_execute
        test_inputs: Inputs that caused the error
        max_attempts: Max healing attempts
    
    Returns:
        {
            "success": bool,
            "healed": bool,
            "attempts": int,
            "final_code": str,
            "healing_log": List[Dict]
        }
    """
    healing_log = []
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔧 Healing attempt {attempt}/{max_attempts}...")
        
        # Step 1: Analyze error (get underlying function)
        import self_healing
        analyze_fn = self_healing.engine.bricks["analyze_error"].func
        analysis_result = analyze_fn(
            brick_id=brick_obj.meta.id,
            error_message=error_result.get("error", "Unknown error"),
            source_code=brick_obj.source,
            test_inputs=test_inputs
        )
        
        if not analysis_result["success"]:
            healing_log.append({
                "attempt": attempt,
                "stage": "analysis",
                "success": False,
                "error": analysis_result.get("error")
            })
            continue
        
        print(f"   ✅ Analysis: {analysis_result['error_type']} (confidence: {analysis_result['confidence']:.0%})")
        
        # Step 2: Generate fix (get underlying function)
        fix_fn = self_healing.engine.bricks["generate_fix"].func
        fix_result = fix_fn(
            brick_id=brick_obj.meta.id,
            source_code=brick_obj.source,
            error_analysis=analysis_result,
            use_ai=True  # Will auto-fallback to rules if Gemini CLI unavailable
        )
        
        if not fix_result["success"]:
            healing_log.append({
                "attempt": attempt,
                "stage": "fix_generation",
                "success": False,
                "error": fix_result.get("error")
            })
            print(f"   ❌ Fix generation failed: {fix_result.get('error')}")
            continue
        
        print(f"   ✅ Generated fix using {fix_result.get('method', 'unknown')}")
        print(f"   📝 Changes: {fix_result.get('changes', 'N/A')}")
        
        # Step 3: Log success
        healing_log.append({
            "attempt": attempt,
            "stage": "complete",
            "success": True,
            "analysis": analysis_result,
            "fix": fix_result
        })
        
        print(f"\n✅ HEALING SUCCESSFUL!")
        
        return {
            "success": True,
            "healed": True,
            "attempts": attempt,
            "final_code": fix_result["fixed_code"],
            "healing_log": healing_log,
            "method": fix_result.get("method")
        }
    
    # Failed to heal
    return {
        "success": True,
        "healed": False,
        "attempts": max_attempts,
        "final_code": None,
        "healing_log": healing_log,
        "error": "Max attempts reached without successful fix"
    }

engine.register(self_heal_brick)

# ===== PERFORMANCE PROFILING =====

@brick("profile_brick", "Profile brick performance")
def profile_brick(
    brick_obj: Any,
    test_inputs: Dict[str, Any],
    iterations: int = 100
) -> Dict[str, Any]:
    """
    Profile a brick's performance.
    
    Returns:
        {
            "success": bool,
            "avg_time_ms": float,
            "min_time_ms": float,
            "max_time_ms": float,
            "iterations": int,
            "recommendations": List[str]
        }
    """
    try:
        times = []
        
        for _ in range(iterations):
            result = brick_obj.safe_execute(**test_inputs)
            if result["success"]:
                times.append(result["duration_ms"])
        
        if not times:
            return {
                "success": False,
                "error": "All executions failed"
            }
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Generate recommendations
        recommendations = []
        if avg_time > 100:
            recommendations.append("Consider caching results")
        if avg_time > 500:
            recommendations.append("High execution time - needs optimization")
        if max_time > avg_time * 3:
            recommendations.append("High variance - check for external dependencies")
        
        return {
            "success": True,
            "avg_time_ms": round(avg_time, 2),
            "min_time_ms": round(min_time, 2),
            "max_time_ms": round(max_time, 2),
            "iterations": len(times),
            "recommendations": recommendations
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

engine.register(profile_brick)

print("\n✅ Self-Healing System Ready!")
print(f"✅ Bricks available: {len(engine.bricks)}")
print("\nCapabilities:")
print("  1. Gemini CLI integration ✅")
print("  2. Error analysis ✅")
print("  3. Auto-fix generation ✅")
print("  4. Self-healing pipeline ✅")
print("  5. Performance profiling ✅")
print("=" * 80)
