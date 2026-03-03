# 🧬 SynapticBricks

**Autonomous Living Code Ecosystem: Self-Healing, Security-First Python Framework**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)]()

> "Code that heals itself, learns from failures, and blocks malware before execution."

---

## 🌟 What is SynapticBricks?

SynapticBricks is a **self-healing Python framework** that treats code like living organisms. Instead of crashing when things break, it:

- 🔧 **Self-heals** using AI-powered repair
- 🛡️ **Blocks malware** with AST-based security analysis  
- 🧬 **Evolves** through genetic learning from failures
- 📊 **Monitors** health in real-time
- 🌐 **Shares cures** across a global healing network

Think of it as **an immune system for your code**.

---

## ⚡ Quick Start

### Installation

```bash
pip install git+https://github.com/japancartoon/synapticbricks.git
```

Or install from source:
```bash
git clone https://github.com/japancartoon/synapticbricks.git
cd synapticbricks
pip install -e .
```

### Hello World (No API Required!)

```python
from synapticbricks.core import brick

@brick("hello", description="A self-healing greeting")
def hello(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Name must be a string")
    return f"Hello, {name}!"

# Add a test (auto-validates on execution)
hello.add_test(
    inputs={"name": "World"},
    expected_output="Hello, World!",
    label="test_greeting"
)

# Run it - works immediately, no config needed!
result = hello("World")
print(result)  # "Hello, World!"
```

**✅ Works instantly - no API keys, no configuration!**

### Optional: AI-Powered Healing

For **autonomous LLM-powered repair**, enable AI features with one line:

```python
import synapticbricks

# One-time setup (saves config to ~/.synapticbricks/config.json)
synapticbricks.configure(api_key="YOUR_GEMINI_API_KEY")
# ✅ AI healing enabled!
```

**Get a free API key:** https://ai.google.dev/

After configuration, all your bricks get AI-powered self-healing automatically!

```python
from synapticbricks.core import brick

@brick("divide")
def divide(a: int, b: int) -> float:
    return a / b

# This breaks on divide(5, 0)
# With AI enabled, it will attempt to add zero-division handling!
result = divide(5, 0)  # Auto-heals and returns a safe result
```

**Environment variables (alternative):**
```bash
export SYNAPTICBRICKS_API_KEY="your-key-here"
export SYNAPTICBRICKS_MODEL="gemini-2.5-flash"  # optional
```

**Check if AI is enabled:**
```python
import synapticbricks
if synapticbricks.is_ai_enabled():
    print("AI healing is active!")
```

**Note:** AI healing is **optional**. All core features (security, testing, monitoring) work without any API.

---

## 🔥 Key Features

### 1. **Security Auditing** (No API Required)
Every brick is automatically scanned for:
- Dangerous code patterns (`eval`, `exec`, `os.system`)
- Input validation issues
- Security vulnerabilities

Scored 0-100 across 5 dimensions. **Works immediately, no configuration!**

### 2. **Self-Testing** (No API Required)
Add tests to your bricks:
```python
my_brick.add_test(inputs={...}, expected_output=..., label="test")
```
Tests run automatically and validate your code.

### 3. **Genetic Evolution** (No API Required)
Failed executions create "genetic memory":
- Stores failure patterns
- Learns edge cases
- Evolves better code over time

### 4. **AI-Powered Healing** (Optional - Requires API Key)
When code breaks, SynapticBricks can attempt automatic repair using LLMs:
- Analyzes the error
- Generates a fix
- Tests the fix
- Applies if successful

**This is OPTIONAL** - You can use SynapticBricks without any API keys!

### 5. **Global Healing Network** (Coming Soon)
When one instance heals a brick, the cure spreads to all users.

---

## 📚 Core Concepts

### Bricks
A **brick** is a self-aware function:
- Knows its own health
- Can test itself
- Heals when broken
- Learns from failures

### Security Scoring
Multi-dimensional security analysis:
- **Code Patterns** (40 pts) - Dangerous operations
- **Input Validation** (20 pts) - Type hints, sanitization
- **Output Safety** (15 pts) - Error handling
- **Dependencies** (15 pts) - Module trust
- **Test Coverage** (10 pts) - Edge case testing

**Minimum score:** 60/100 to be considered "safe"

---

## 🛡️ Security First

SynapticBricks was built to solve a real problem: **malware in agent marketplaces**.

**Existing marketplaces:**
- ❌ Distribute malicious code
- ❌ No pre-publication checks
- ❌ Manual reviews (slow & incomplete)

**SynapticBricks:**
- ✅ Auto-blocks dangerous code
- ✅ AST-based pattern detection
- ✅ Pre-execution security scoring
- ✅ Transparent security reports

Try it yourself: https://synapticbricks-marketplace.onrender.com

---

## 🚀 Examples

### Example 1: Safe Data Processing

```python
from synapticbricks.core import brick

@brick("process_data", description="Process user data safely")
def process_data(data: list) -> dict:
    if not isinstance(data, list):
        raise TypeError("Data must be a list")
    
    return {
        "count": len(data),
        "items": [str(x) for x in data]
    }

# This brick scores 85/100 (trusted)
```

### Example 2: Malware Detection

```python
from synapticbricks.core import brick

@brick("evil", description="This will be rejected")
def evil(code: str):
    eval(code)  # ❌ BLOCKED!

# This brick scores 45/100 (rejected)
```

### Example 3: Self-Healing

```python
from synapticbricks.core import BrickEngine

engine = BrickEngine()

@engine.brick("divide", description="Division with auto-heal")
def divide(a: int, b: int) -> float:
    return a / b

# This breaks on divide(5, 0)
# The healer will attempt to add zero-division handling
```

---

## 📦 Architecture

```
synapticbricks/
├── core/
│   ├── brick.py          # Brick decorator & wrapper
│   ├── engine.py         # BrickEngine orchestrator
│   ├── security.py       # SecurityAuditor (AST analysis)
│   ├── healer.py         # BrickHealer (self-repair)
│   ├── ai_healer.py      # AIHealer (LLM-powered)
│   ├── immune.py         # Immune system (Aegis)
│   └── phantom.py        # Edge case generator
├── pulse/                # Real-time monitoring dashboard
├── architect/            # Autonomous brick evolution
└── examples/             # Usage examples
```

---

## 🌐 SynapticBricks Marketplace

We built a live marketplace to demonstrate the security system:

**URL:** https://synapticbricks-marketplace.onrender.com

**Features:**
- Browse secure skills
- Publish your own (auto-scanned)
- Install with confidence
- View security reports

**GitHub:** https://github.com/japancartoon/synapticbricks-marketplace

---

## 🧪 Testing

Run the security demo:

```bash
python demo_security_enforcement.py
```

This will:
1. Test a safe brick (should pass)
2. Test an evil brick with `eval()` (should fail)
3. Show security scores

---

## 📊 Real-World Use Cases

1. **AI Agent Skills** - Secure, self-healing agent capabilities
2. **Data Pipelines** - Resilient ETL with auto-recovery
3. **Microservices** - Services that heal from failures
4. **Testing Frameworks** - Code that generates its own edge cases
5. **Educational Tools** - Teach secure coding practices

---

## 🤝 Contributing

We welcome contributions! This is an open source project.

**Areas we need help:**
- [ ] More security patterns
- [ ] Healing strategies
- [ ] Frontend for marketplace
- [ ] Documentation
- [ ] Test coverage

**To contribute:**
1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

**TL;DR:** Use it, modify it, distribute it. Just don't blame us if it breaks. (But it probably won't - it heals itself!)

---

## 🙏 Credits

**Built by:** Medo & Neura  
**Inspired by:** The need for secure, resilient code  
**Powered by:** Python, AST analysis, and a lot of coffee ☕

---

## 📞 Links

- **Marketplace:** https://synapticbricks-marketplace.onrender.com
- **GitHub (Framework):** https://github.com/japancartoon/synapticbricks
- **GitHub (Marketplace):** https://github.com/japancartoon/synapticbricks-marketplace
- **Documentation:** *(Coming soon)*
- **Discord:** *(Coming soon)*

---

## ⚠️ Current Status

**Version:** 1.4.1 (Beta)  
**Stability:** Production-ready for non-critical systems  
**Tested on:** Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.14  

**Known limitations:**
- AI healing requires API access (optional)
- Phantom executor has edge cases (ironic, we know)
- Dashboard (Pulse) is early alpha

---

## ❓ FAQ

### Do I need an API key to use SynapticBricks?

**No!** All core features work without any API keys:
- ✅ Security auditing
- ✅ Self-testing
- ✅ Genetic evolution
- ✅ Health monitoring

**Optional:** AI-powered healing requires a Gemini API key, but you can skip this feature entirely.

### How do I enable AI healing?

**Super easy - one line:**
```python
import synapticbricks
synapticbricks.configure(api_key="YOUR_GEMINI_API_KEY")
```

Get a free API key at: https://ai.google.dev/

The config is saved to `~/.synapticbricks/config.json` and works across all projects!

### How do I install it?

```bash
pip install git+https://github.com/japancartoon/synapticbricks.git
```

No configuration needed. It works immediately!

### Is it free?

Yes! MIT License - use it for anything, commercial or personal.

### Does it send data anywhere?

**No.** Unless you enable AI healing (optional), SynapticBricks runs 100% locally. No telemetry, no tracking.

### Can I use it in production?

Yes, but it's in beta. Test thoroughly. The security features are production-ready; AI healing is experimental.

---

## 🌟 Star History

If you find this useful, give us a star! ⭐

It helps others discover secure, self-healing code.

---

**Built with ❤️ for a safer AI future.**

*"Code that refuses to die."*
