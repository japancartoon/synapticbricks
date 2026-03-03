"""Test Gemini CLI - Simple version"""
import subprocess
import sys

print("=" * 80)
print("Testing Gemini CLI")
print("=" * 80)

print("\n1. Testing Gemini call...")
print("   Prompt: 'Say hello'")

try:
    result = subprocess.run(
        ["gemini", "Say hello in one word"],
        capture_output=True,
        text=True,
        timeout=30,
        encoding='utf-8'
    )
    
    print(f"\nReturn code: {result.returncode}")
    print(f"Output: {result.stdout[:200] if result.stdout else '(none)'}")
    print(f"Error: {result.stderr[:200] if result.stderr else '(none)'}")
    
    if result.returncode == 0 and result.stdout:
        print("\n[OK] Gemini CLI is working!")
    else:
        print("\n[WARN] Gemini CLI may need setup")

except subprocess.TimeoutExpired:
    print("\n[WARN] Timeout - CLI may be waiting for auth or input")
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "=" * 80)
