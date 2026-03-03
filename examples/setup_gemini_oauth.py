"""
Gemini CLI OAuth Setup for BrickLang

Helps you authenticate with Gemini CLI and use it in self-healing.
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔥 Gemini CLI OAuth Setup")
print("=" * 80)

print("\nThis will help you set up Gemini CLI with OAuth authentication.")
print("Your authenticated account will be used for AI-powered brick generation")
print("and self-healing fixes!")

print("\n" + "=" * 80)
print("STEP 1: Check if Gemini CLI is installed")
print("=" * 80)

try:
    result = subprocess.run(
        ["gemini", "--version"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print(f"✅ Gemini CLI is installed!")
        print(f"   Version: {result.stdout.strip()}")
    else:
        print("❌ Gemini CLI not found!")
        print("\nInstall it with:")
        print("  npm install -g @google/generative-ai-cli")
        sys.exit(1)

except FileNotFoundError:
    print("❌ Gemini CLI not found!")
    print("\nInstall it with:")
    print("  npm install -g @google/generative-ai-cli")
    sys.exit(1)

print("\n" + "=" * 80)
print("STEP 2: Authenticate with OAuth")
print("=" * 80)

print("\nThis will open a browser window for OAuth authentication.")
print("Log in with your Google account that has Gemini API access.")

input("\nPress Enter to start OAuth login...")

try:
    # Run gemini auth command
    print("\nStarting OAuth flow...")
    result = subprocess.run(
        ["gemini", "auth", "login"],
        text=True,
        timeout=120  # 2 minute timeout
    )
    
    if result.returncode == 0:
        print("\n✅ OAuth authentication successful!")
    else:
        print("\n⚠️  OAuth authentication may have failed.")
        print("   Check the error messages above.")

except subprocess.TimeoutExpired:
    print("\n⚠️  OAuth timeout after 2 minutes.")
    print("   Please try again.")
except Exception as e:
    print(f"\n❌ Error during OAuth: {str(e)}")

print("\n" + "=" * 80)
print("STEP 3: Test Authentication")
print("=" * 80)

print("\nTesting if Gemini CLI can make requests...")

try:
    result = subprocess.run(
        ["gemini", "What is 2+2? Reply with just the number."],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        print(f"✅ Gemini CLI is working!")
        print(f"   Response: {result.stdout.strip()}")
    else:
        print(f"⚠️  Gemini CLI returned an error:")
        print(f"   {result.stderr.strip()}")

except Exception as e:
    print(f"❌ Test failed: {str(e)}")

print("\n" + "=" * 80)
print("STEP 4: Configure BrickLang")
print("=" * 80)

print("\nBrickLang is already configured to use Gemini CLI!")
print("The self-healing system will now:")
print("  1. Try Gemini CLI first (using your OAuth account)")
print("  2. Fall back to rule-based fixes if unavailable")

print("\n💡 Tips:")
print("  • OAuth token is stored securely by Gemini CLI")
print("  • Token auto-refreshes when needed")
print("  • Use 'gemini auth logout' to sign out")
print("  • Use 'gemini auth status' to check current auth")

print("\n" + "=" * 80)
print("✅ SETUP COMPLETE!")
print("=" * 80)

print("\nYour BrickLang system is now powered by Gemini AI!")
print("Try running the self-healing demo:")
print("  python bricklang\\demo_self_healing.py")

print("\n🔥 Ready to self-heal with AI! 🔥")
print("=" * 80)
