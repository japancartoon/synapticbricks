# 🚀 Setup Guide - Enable AI-Powered Healing

This guide shows you how to unlock the full power of SynapticBricks with AI-powered self-healing.

---

## Option 1: Interactive Setup (Easiest)

```python
import synapticbricks

# One command - saves config permanently
synapticbricks.configure(api_key="YOUR_API_KEY_HERE")
```

**Output:**
```
✅ Config saved to: /home/user/.synapticbricks/config.json
✅ AI healing enabled!
   All bricks can now self-heal using AI 🧠
```

Done! All your bricks now have AI-powered self-healing.

---

## Option 2: Environment Variables

Set these in your shell or `.env` file:

```bash
export SYNAPTICBRICKS_API_KEY="your-gemini-api-key"
export SYNAPTICBRICKS_MODEL="gemini-2.5-flash"  # optional
```

SynapticBricks will auto-detect and use these.

---

## Option 3: Manual Config File

Create `~/.synapticbricks/config.json`:

```json
{
  "api_key": "your-gemini-api-key",
  "model": "gemini-2.5-flash",
  "version": "1.4.1"
}
```

---

## Get a Free API Key

1. Go to: https://ai.google.dev/
2. Click "Get API key"
3. Sign in with Google
4. Copy your key
5. Run: `synapticbricks.configure(api_key="YOUR_KEY")`

**Free tier includes:**
- 1,500 requests/day
- 1 million tokens/month
- More than enough for most projects!

---

## Test It Works

```python
import synapticbricks

# Check if AI is enabled
if synapticbricks.is_ai_enabled():
    print("🧠 AI healing is active!")
else:
    print("⚠️  AI healing not configured")
    print("   Run: synapticbricks.configure(api_key='...')")
```

---

## Example: AI Healing in Action

```python
from synapticbricks.core import brick

@brick("safe_divide")
def safe_divide(a: int, b: int) -> float:
    """Divides two numbers."""
    return a / b

# This will break on zero division
# With AI enabled, it will auto-add error handling!
result = safe_divide(10, 0)
# AI healer detects the error, generates a fix, tests it, and applies it
# Result: safely returns None or raises a better error
```

---

## Clear Configuration

```python
import synapticbricks
config = synapticbricks.get_config()
config.clear()
```

---

## FAQ

**Q: Do I need AI healing?**  
A: No! Security auditing, testing, and monitoring work without it.

**Q: What does AI healing cost?**  
A: Gemini API is free for personal use (1M tokens/month). Commercial use may require billing.

**Q: Is my API key safe?**  
A: Yes! It's stored locally in `~/.synapticbricks/config.json`. Never committed to git (in .gitignore).

**Q: Can I use different models?**  
A: Yes! Supported models:
- `gemini-2.5-flash` (fast, cheap)
- `gemini-2.5-pro` (smarter, slower)
- `gemini-2.0-flash-exp` (experimental)

**Q: Does it work offline?**  
A: Core features yes, AI healing no (needs internet for API calls).

---

**That's it! You now have the full power of self-healing code.** 🚀
