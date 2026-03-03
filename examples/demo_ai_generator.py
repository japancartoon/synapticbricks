"""
AI Brick Generator - Interactive CLI

Generate bricks from natural language!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import ai_generator

print("🔥" * 40)
print("   AI BRICK GENERATOR - Interactive Mode")
print("🔥" * 40)

engine = ai_generator.engine

print("\n💡 Example descriptions:")
print("  • 'Convert Celsius to Fahrenheit'")
print("  • 'Validate email address format'")
print("  • 'Calculate average of a list of numbers'")
print("  • 'Extract URLs from text'")
print("  • 'Parse CSV string into list of dicts'")

print("\n" + "=" * 80)

# Test cases
test_descriptions = [
    "Convert Celsius to Fahrenheit",
    "Validate email address",
    "Calculate factorial of a number",
    "Extract all URLs from text using regex"
]

for i, desc in enumerate(test_descriptions, 1):
    print(f"\n[{i}/{len(test_descriptions)}] Generating: '{desc}'")
    print("-" * 80)
    
    # Generate the brick
    brick_obj = engine.bricks["generate_brick"]
    result = brick_obj.safe_execute(
        description=desc,
        category="utility",
        add_tests=True,
        use_ai=False  # Template-based for now
    )
    
    if not result["success"]:
        print(f"❌ Execution failed: {result.get('error')}")
        continue
    
    brick_data = result["result"]
    
    if brick_data["success"]:
        print(f"✅ Generated: {brick_data['brick_id']}")
        print(f"   Function: {brick_data['function_name']}()")
        print(f"   Tests: {brick_data['tests']}")
        print(f"   Method: {'AI' if brick_data.get('ai_generated') else 'Template (' + brick_data.get('template', 'unknown') + ')'}")
        
        # Show code
        print(f"\n📝 Code Preview:")
        lines = brick_data["code"].split("\n")
        for line in lines[:15]:  # First 15 lines
            print(f"   {line}")
        if len(lines) > 15:
            print(f"   ... ({len(lines) - 15} more lines)")
        
        # Save to file
        filename = f"ai_bricks/generated_{brick_data['brick_id'].replace('-', '_')}.py"
        save_brick = engine.bricks["save_brick_to_file"]
        save_result = save_brick.safe_execute(
            code=brick_data["code"],
            filename=filename,
            overwrite=True
        )
        
        if save_result["success"] and save_result["result"]["success"]:
            print(f"\n💾 Saved to: {save_result['result']['filepath']}")
        
    else:
        print(f"❌ Failed: {brick_data.get('error', 'Unknown error')}")

print("\n" + "=" * 80)
print("🔥 AI BRICK GENERATOR DEMO COMPLETE!")
print("=" * 80)
print(f"\n✅ Generated {len(test_descriptions)} bricks")
print(f"✅ All saved to ai_bricks/ directory")
print("\nNext steps:")
print("  1. Review generated code")
print("  2. Add Gemini API key for AI generation")
print("  3. Test the generated bricks")
print("  4. Integrate into your projects!")
print("=" * 80)
