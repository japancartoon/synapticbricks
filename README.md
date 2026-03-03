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
pip install synapticbricks
```

### Hello World (Self-Healing Edition)

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

# Run it - if it breaks, it attempts to self-heal!
result = hello("World")
print(result)  # "Hello, World!"
```

---

## 🔥 Key Features

### 1. **Self-Healing**
When code breaks, SynapticBricks attempts automatic repair:
- Analyzes the error
- Generates a fix
- Tests the fix
- Applies if successful

### 2. **Security Auditing**
Every brick is automatically scanned for:
- Dangerous code patterns (`eval`, `exec`, `os.system`)
- Input validation issues
- Security vulnerabilities

Scored 0-100 across 5 dimensions.

### 3. **Genetic Evolution**
Failed executions create "genetic memory":
- Stores failure patterns
- Learns edge cases
- Evolves better code over time

### 4. **Global Healing Network** (Coming Soon)
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

## 🌟 Star History

If you find this useful, give us a star! ⭐

It helps others discover secure, self-healing code.

---

**Built with ❤️ for a safer AI future.**

*"Code that refuses to die."*
