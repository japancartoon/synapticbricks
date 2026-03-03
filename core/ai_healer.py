"""
AI Healer — Autonomous Code Repair via LLM
Connects BrickHealer repair prompts to Gemini API for true self-healing.
"""
import requests
import json
import re
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class HealAttempt:
    """Record of a healing attempt."""
    brick_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    success: bool
    error: Optional[str]
    duration_ms: float
    timestamp: float


class AIHealer:
    """
    Autonomous AI-powered brick repair system.
    
    Features:
    - Tiered healing (Flash → Pro → Opus fallback)
    - Token tracking
    - Success rate monitoring
    - Repair history
    """
    
    def __init__(self, api_key: str, engine=None, healer=None):
        """
        Initialize AI Healer.
        
        Args:
            api_key: Gemini API key
            engine: BrickEngine instance (optional, for auto-apply)
            healer: BrickHealer instance (optional, for generating prompts)
        """
        self.api_key = api_key
        self.engine = engine
        self.healer = healer
        self.history: List[HealAttempt] = []
        
        # Model tiers (fastest → strongest)
        self.models = [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
        ]
        
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def _call_gemini(self, prompt: str, model: str = "gemini-2.5-flash", temperature: float = 0.2) -> Optional[str]:
        """Call Gemini API and return generated text."""
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if "candidates" not in data or len(data["candidates"]) == 0:
                return None
            
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text.strip()
        except Exception:
            return None
    
    def _extract_code(self, response: str) -> Optional[str]:
        """
        Extract Python code from LLM response.
        Handles markdown code blocks and raw code.
        """
        # Try markdown code block first
        match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try generic code block
        match = re.search(r'```\n(.*?)```', response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            if code.startswith("def ") or code.startswith("class "):
                return code
        
        # Last resort: if response looks like pure code
        if response.startswith("def ") or response.startswith("class "):
            return response.strip()
        
        return None
    
    def heal_brick(self, brick_id: str, max_attempts: int = 2) -> Dict[str, Any]:
        """
        Attempt to heal a broken brick using tiered AI models.
        
        Args:
            brick_id: ID of the brick to heal
            max_attempts: Maximum healing attempts per model tier
        
        Returns:
            Dict with keys: success, fixed_code, model_used, attempts, error
        """
        if not self.healer:
            return {"success": False, "error": "No BrickHealer instance provided"}
        
        # Generate repair prompt
        repair_request = self.healer.create_repair_request(brick_id)
        if not repair_request:
            return {"success": False, "error": f"Could not generate repair request for '{brick_id}'"}
        
        prompt = repair_request.to_prompt()
        
        # Try each model tier
        for model in self.models:
            for attempt in range(max_attempts):
                start = time.time()
                
                response = self._call_gemini(prompt, model=model)
                if not response:
                    # API call failed
                    duration_ms = (time.time() - start) * 1000
                    self.history.append(HealAttempt(
                        brick_id=brick_id,
                        model=model,
                        prompt_tokens=len(prompt.split()),
                        completion_tokens=0,
                        success=False,
                        error="API call failed",
                        duration_ms=duration_ms,
                        timestamp=time.time()
                    ))
                    continue
                
                # Extract code
                fixed_code = self._extract_code(response)
                if not fixed_code:
                    # Code extraction failed
                    duration_ms = (time.time() - start) * 1000
                    self.history.append(HealAttempt(
                        brick_id=brick_id,
                        model=model,
                        prompt_tokens=len(prompt.split()),
                        completion_tokens=len(response.split()),
                        success=False,
                        error="Could not extract code from response",
                        duration_ms=duration_ms,
                        timestamp=time.time()
                    ))
                    continue
                
                # Validate fix (try to compile)
                try:
                    compile(fixed_code, "<string>", "exec")
                except SyntaxError as e:
                    # Syntax error in generated code
                    duration_ms = (time.time() - start) * 1000
                    self.history.append(HealAttempt(
                        brick_id=brick_id,
                        model=model,
                        prompt_tokens=len(prompt.split()),
                        completion_tokens=len(response.split()),
                        success=False,
                        error=f"Syntax error: {str(e)}",
                        duration_ms=duration_ms,
                        timestamp=time.time()
                    ))
                    continue
                
                # Success!
                duration_ms = (time.time() - start) * 1000
                self.history.append(HealAttempt(
                    brick_id=brick_id,
                    model=model,
                    prompt_tokens=len(prompt.split()),
                    completion_tokens=len(response.split()),
                    success=True,
                    error=None,
                    duration_ms=duration_ms,
                    timestamp=time.time()
                ))
                
                return {
                    "success": True,
                    "fixed_code": fixed_code,
                    "model_used": model,
                    "attempts": attempt + 1,
                    "duration_ms": duration_ms
                }
        
        # All attempts failed
        return {
            "success": False,
            "error": "All healing attempts exhausted across all model tiers",
            "attempts": max_attempts * len(self.models)
        }
    
    def auto_heal(self, brick_id: str, apply: bool = True) -> Dict[str, Any]:
        """
        Fully autonomous healing: diagnose → fix → TEST → apply → verify.
        
        Args:
            brick_id: Brick to heal
            apply: If True, automatically apply the fix (only if tests pass)
        
        Returns:
            Dict with success, fixed_code, model_used, test_result
        """
        result = self.heal_brick(brick_id)
        
        if not result["success"]:
            return result
        
        if apply and self.engine and self.healer:
            fixed_code = result["fixed_code"]
            
            # Execute to get the function object (provide brick decorator in namespace)
            from .brick import brick as brick_decorator
            namespace = {"brick": brick_decorator}
            
            try:
                exec(fixed_code, namespace)
            except Exception as e:
                result["success"] = False
                result["error"] = f"Execution error: {str(e)}"
                return result
            
            # Find the function (should be the only def in namespace)
            # Look for the brick-decorated function
            func = None
            for name, obj in namespace.items():
                if name == brick_id or (callable(obj) and hasattr(obj, 'meta')):
                    func = obj
                    break
            
            if not func:
                result["success"] = False
                result["error"] = f"Could not find brick '{brick_id}' in generated code"
                return result
            
            # If the AI forgot to add @brick decorator, apply it now
            if not hasattr(func, 'meta'):
                original_brick = self.engine.get(brick_id)
                if not original_brick:
                    result["success"] = False
                    result["error"] = f"Original brick '{brick_id}' not found"
                    return result
                
                # Apply the decorator with original metadata
                func = brick_decorator(
                    brick_id,
                    description=original_brick.meta.description
                )(func)
            
            # Copy tests from original brick to the fixed brick
            original_brick = self.engine.get(brick_id)
            if not original_brick:
                result["success"] = False
                result["error"] = f"Original brick '{brick_id}' not found"
                return result
            
            func.tests = original_brick.tests
            
            # Test the fixed function BEFORE applying
            from .tester import BrickTester
            temp_tester = BrickTester(self.engine)
            pre_apply_test = temp_tester.test_brick(func)
            
            result["pre_apply_test"] = {
                "passed": pre_apply_test["passed"],
                "failed": pre_apply_test["failed"],
                "total": pre_apply_test["total"]
            }
            
            # Only apply if ALL tests pass
            if pre_apply_test["failed"] > 0:
                result["success"] = False
                result["error"] = f"Fix failed tests ({pre_apply_test['failed']}/{pre_apply_test['total']} tests failed). Not applied."
                result["applied"] = False
                return result
            
            # Tests passed — apply the fix
            # Pass the unwrapped function to the healer
            unwrapped_func = func.func if hasattr(func, 'func') else func
            self.healer.auto_heal(brick_id, unwrapped_func)
            
            # Re-verify after application
            brick_obj = self.engine.get(brick_id)
            post_apply_test = temp_tester.test_brick(brick_obj)
            
            result["test_result"] = {
                "passed": post_apply_test["passed"],
                "failed": post_apply_test["failed"],
                "total": post_apply_test["total"]
            }
            result["applied"] = True
        else:
            result["applied"] = False
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get healing statistics."""
        if not self.history:
            return {
                "total_attempts": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "by_model": {}
            }
        
        total = len(self.history)
        successes = sum(1 for h in self.history if h.success)
        avg_duration = sum(h.duration_ms for h in self.history) / total
        
        # Per-model stats
        by_model = {}
        for model in self.models:
            model_attempts = [h for h in self.history if h.model == model]
            if model_attempts:
                model_successes = sum(1 for h in model_attempts if h.success)
                by_model[model] = {
                    "attempts": len(model_attempts),
                    "successes": model_successes,
                    "success_rate": model_successes / len(model_attempts),
                    "avg_duration_ms": sum(h.duration_ms for h in model_attempts) / len(model_attempts)
                }
        
        return {
            "total_attempts": total,
            "successes": successes,
            "success_rate": successes / total if total > 0 else 0.0,
            "avg_duration_ms": avg_duration,
            "by_model": by_model
        }
    
    def clear_history(self):
        """Clear healing history."""
        self.history = []
