"""
Test Gemini CLI integration

Simple test to see if Gemini CLI works
"""

import subprocess
import sys

print("=" * 80)
print("Testing Gemini CLI")
print("=" * 80)

print("\n1. Checking if gemini command exists...")
try:
    result = subprocess.run(
        ["where.exe", "gemini"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print(f"✅ Found gemini at:")
        for line in result.stdout.strip().split('\n'):
            print(f"   {line}")
    else:
        print("❌ Gemini command not found")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n2. Testing simple Gemini call...")
print("   Prompt: 'What is 2+2? Reply with just the number.'")

try:
    result = subprocess.run(
        ["gemini", "What is 2+2? Reply with just the number."],
        capture_output=True,
        text=True,
        timeout=30,
        encoding='utf-8'
    )
    
    if result.returncode == 0:
        print(f"✅ Gemini CLI works!")
        print(f"   Response: {result.stdout.strip()}")
    else:
        print(f"⚠️  Gemini returned error code {result.returncode}")
        if result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")

except subprocess.TimeoutExpired:
    print("⚠️  Gemini CLI timed out after 30 seconds")
    print("   This might mean:")
    print("   • Need to authenticate first")
    print("   • Network issue")
    print("   • CLI waiting for input")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
