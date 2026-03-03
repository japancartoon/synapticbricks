"""
EPIC 4: AI Brick Generator

Auto-generate bricks from natural language descriptions using Gemini AI.
"""

import sys
import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine

print("=" * 80)
print("🔥 EPIC 4: AI Brick Generator")
print("=" * 80)

# Gemini API setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("\n⚠️  WARNING: GEMINI_API_KEY not set!")
    print("Set it with: $env:GEMINI_API_KEY='your-key-here'")
    print("\nContinuing with template-based generation only...\n")

engine = BrickEngine(project_dir="ai_bricks")

@brick("generate_brick", "Generate a brick from description using AI")
def generate_brick(
    description: str,
    category: str = "utility",
    add_tests: bool = True,
    use_ai: bool = True
) -> Dict[str, Any]:
    """
    Generate a brick from natural language description.
    
    Args:
        description: What the brick should do
        category: Brick category (utility, data, text, etc.)
        add_tests: Whether to generate tests
        use_ai: Use Gemini AI or template-based
    
    Returns:
        Dict with 'code', 'brick_id', 'tests', 'success'
    """
    
    if use_ai and GEMINI_API_KEY:
        return _generate_with_ai(description, category, add_tests)
    else:
        return _generate_with_template(description, category, add_tests)

def _generate_with_ai(description: str, category: str, add_tests: bool) -> Dict:
    """Generate brick using Gemini AI."""
    import requests
    
    # Craft the prompt
    prompt = f"""You are a Python code generator for the BrickLang system.

Generate a complete, production-ready brick function based on this description:
"{description}"

Requirements:
1. Use the @brick decorator: @brick("brick_id", "short description")
2. Include full type hints
3. Add comprehensive docstring
4. Handle errors gracefully
5. Return appropriate types
{"6. Include 2-3 test cases using brick.add_test()" if add_tests else ""}
7. Keep it simple and focused
8. Category: {category}

Generate ONLY the Python code, no explanations. Start with the decorator.

Example format:
```python
@brick("example_id", "Short description")
def example_function(input1: str, input2: int = 0) -> dict:
    \"\"\"
    Detailed docstring.
    
    Args:
        input1: Description
        input2: Description (default: 0)
    
    Returns:
        Description of return value
    \"\"\"
    try:
        # Implementation
        result = {{}}
        return result
    except Exception as e:
        return {{"error": str(e), "success": False}}

example_function.add_test(
    inputs={{"input1": "test", "input2": 5}},
    expected_output={{"success": True}},
    label="test_name"
)
```

Now generate for: "{description}"
"""
    
    # Call Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Extract code from markdown if present
        code = _extract_code(generated_text)
        
        # Validate syntax
        validation = _validate_brick_code(code)
        
        if validation["valid"]:
            return {
                "success": True,
                "code": code,
                "brick_id": validation["brick_id"],
                "function_name": validation["function_name"],
                "tests": validation["test_count"],
                "ai_generated": True
            }
        else:
            return {
                "success": False,
                "error": f"Generated code has syntax errors: {validation['error']}",
                "code": code
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"AI generation failed: {str(e)}"
        }

def _generate_with_template(description: str, category: str, add_tests: bool) -> Dict:
    """Generate brick using smart templates."""
    
    # Extract key info from description
    brick_id = _generate_brick_id(description)
    func_name = brick_id.replace("-", "_")
    
    # Detect operation type
    operation = _detect_operation_type(description)
    
    # Generate based on template
    if operation == "transform":
        code = _template_transform(brick_id, func_name, description)
    elif operation == "validate":
        code = _template_validate(brick_id, func_name, description)
    elif operation == "calculate":
        code = _template_calculate(brick_id, func_name, description)
    else:
        code = _template_generic(brick_id, func_name, description)
    
    if add_tests:
        code += f"\n\n{func_name}.add_test(\n    inputs={{}},\n    expected_output=None,\n    label=\"{brick_id}_test\"\n)\n"
    
    validation = _validate_brick_code(code)
    
    return {
        "success": validation["valid"],
        "code": code,
        "brick_id": brick_id,
        "function_name": func_name,
        "tests": 1 if add_tests else 0,
        "ai_generated": False,
        "template": operation
    }

def _extract_code(text: str) -> str:
    """Extract Python code from markdown or plain text."""
    # Try markdown code blocks
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'```\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Return as-is if no markdown
    return text.strip()

def _validate_brick_code(code: str) -> Dict:
    """Validate generated brick code."""
    try:
        tree = ast.parse(code)
        
        # Find @brick decorator and function
        brick_id = None
        function_name = None
        test_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for @brick decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if getattr(decorator.func, 'id', None) == 'brick':
                            if decorator.args:
                                brick_id = ast.literal_eval(decorator.args[0])
                            function_name = node.name
            
            # Count test calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'add_test':
                        test_count += 1
        
        if not brick_id or not function_name:
            return {
                "valid": False,
                "error": "Missing @brick decorator or function definition"
            }
        
        return {
            "valid": True,
            "brick_id": brick_id,
            "function_name": function_name,
            "test_count": test_count
        }
    
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error: {str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation error: {str(e)}"
        }

def _generate_brick_id(description: str) -> str:
    """Generate brick ID from description."""
    # Extract key words
    words = re.findall(r'\b\w+\b', description.lower())
    
    # Remove common words
    skip = {'a', 'an', 'the', 'to', 'of', 'and', 'or', 'that', 'for', 'in'}
    words = [w for w in words if w not in skip and len(w) > 2]
    
    # Take first 2-3 meaningful words
    return "-".join(words[:3])

def _detect_operation_type(description: str) -> str:
    """Detect what type of operation is needed."""
    desc_lower = description.lower()
    
    if any(word in desc_lower for word in ['convert', 'transform', 'change', 'format']):
        return 'transform'
    elif any(word in desc_lower for word in ['validate', 'check', 'verify', 'test']):
        return 'validate'
    elif any(word in desc_lower for word in ['calculate', 'compute', 'sum', 'count']):
        return 'calculate'
    else:
        return 'generic'

def _template_transform(brick_id: str, func_name: str, description: str) -> str:
    """Template for transformation bricks."""
    return f'''@brick("{brick_id}", "{description[:50]}")
def {func_name}(value: Any) -> Any:
    """
    {description}
    
    Args:
        value: Input value to transform
    
    Returns:
        Transformed value
    """
    try:
        # TODO: Implement transformation logic
        result = value  # Placeholder
        return result
    except Exception as e:
        return {{"error": str(e), "success": False}}'''

def _template_validate(brick_id: str, func_name: str, description: str) -> str:
    """Template for validation bricks."""
    return f'''@brick("{brick_id}", "{description[:50]}")
def {func_name}(value: Any) -> bool:
    """
    {description}
    
    Args:
        value: Value to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # TODO: Implement validation logic
        return True  # Placeholder
    except Exception:
        return False'''

def _template_calculate(brick_id: str, func_name: str, description: str) -> str:
    """Template for calculation bricks."""
    return f'''@brick("{brick_id}", "{description[:50]}")
def {func_name}(value: float) -> float:
    """
    {description}
    
    Args:
        value: Input value
    
    Returns:
        Calculated result
    """
    try:
        # TODO: Implement calculation logic
        result = value  # Placeholder
        return result
    except Exception as e:
        return 0.0'''

def _template_generic(brick_id: str, func_name: str, description: str) -> str:
    """Generic template."""
    return f'''@brick("{brick_id}", "{description[:50]}")
def {func_name}(input_data: Any) -> Dict[str, Any]:
    """
    {description}
    
    Args:
        input_data: Input data
    
    Returns:
        Result dictionary
    """
    try:
        # TODO: Implement logic
        return {{"success": True, "data": input_data}}
    except Exception as e:
        return {{"success": False, "error": str(e)}}'''

# Register the generator
engine.register(generate_brick)

# Save brick to file helper
@brick("save_brick_to_file", "Save generated brick code to a file")
def save_brick_to_file(code: str, filename: str, overwrite: bool = False) -> Dict:
    """Save brick code to a Python file."""
    try:
        path = Path(filename)
        
        if path.exists() and not overwrite:
            return {"success": False, "error": "File already exists"}
        
        path.write_text(code, encoding='utf-8')
        
        return {
            "success": True,
            "filepath": str(path.absolute()),
            "size": len(code)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

engine.register(save_brick_to_file)

print("\n✅ AI Brick Generator Ready!")
print(f"✅ Bricks available: {len(engine.bricks)}")
print("\nYou can now:")
print("  1. Generate bricks from descriptions")
print("  2. Validate generated code")
print("  3. Save bricks to files")
print("  4. Auto-register and test")
print("=" * 80)
