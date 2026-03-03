# SynapticBricks v1.4.0 — Security Auditor Release

## 🛡️ What's New

### SecurityAuditor — Autonomous Vulnerability Detection
The world's first **self-auditing code framework**. Every brick gets a security score (0-100) and automatic hardening.

**How it works:**
1. **AST-based code analysis** — scans for dangerous patterns (eval, exec, os.system, pickle)
2. **Multi-dimensional scoring:**
   - Code patterns (40 pts) — dangerous operations detection
   - Input validation (20 pts) — type checking, sanitization
   - Output safety (15 pts) — error handling, return validation
   - Dependency risk (15 pts) — risky module usage
   - Test coverage (10 pts) — edge case quality
3. **Risk classification:**
   - 80-100: ✅ **Trusted** (no action)
   - 60-79: ⚠️ **Moderate** (add validation)
   - 40-59: 🔶 **Risky** (sandbox execution)
   - 0-39: 🔴 **Dangerous** (auto-regenerate)
4. **Automatic hardening** — integrates with AIHealer for regeneration

### Features
- ✅ Static code analysis via Python AST
- ✅ Pattern-based vulnerability detection
- ✅ Detailed security reports with recommendations
- ✅ Audit history tracking
- ✅ Batch auditing (scan entire codebase)
- ✅ Vulnerability threshold filtering
- ✅ Security summary dashboard

## 📊 Demo Results

Tested on 4 intentionally vulnerable bricks:

| Brick | Score | Risk Level | Issues Detected |
|-------|-------|------------|-----------------|
| dangerous_calc | 43/100 | RISKY | eval(), os.system() |
| file_reader | 70/100 | MODERATE | File ops, weak error handling |
| divide | 83/100 | TRUSTED | Bare except clause |
| safe_add | 93/100 | TRUSTED | Nearly perfect |

**Average security score:** 72.2/100  
**Vulnerable bricks detected:** 1/4 (dangerous_calc)

## 🚀 Usage

```python
from synapticbricks.core import BrickEngine, SecurityAuditor

engine = BrickEngine()
auditor = SecurityAuditor(engine)

# Audit single brick
report = auditor.audit_brick("my_brick")
print(f"Score: {report.score}/100 ({report.risk_level})")
print(f"Issues: {report.critical_issues}")

# Audit all bricks
results = auditor.audit_all()

# Find vulnerable bricks
vulnerable = auditor.get_vulnerable_bricks(threshold=60)

# Get security summary
summary = auditor.get_security_summary()
print(f"Average score: {summary['avg_score']:.1f}/100")
```

## 🔄 Integration with AIHealer

```python
from synapticbricks.core import SecurityAuditor, AIHealer

auditor = SecurityAuditor(engine, ai_healer=healer)

# Auto-harden based on score
result = auditor.auto_harden("dangerous_brick")
# - Score 60-79: Adds validation wrapper
# - Score 40-59: Enables sandbox mode
# - Score 0-39: Triggers AIHealer regeneration
```

## 📦 Installation

```bash
pip install -e .
```

**New in this version:** No new dependencies (uses stdlib AST module)

## 🧪 Run the Demo

```bash
# Security audit demo
python synapticbricks\demo_security_audit.py

# Autonomous healing demo (requires API key)
set GEMINI_API_KEY=your_key
python synapticbricks\demo_autonomous_healing.py
```

## 🏗️ System Architecture

**10 Core Systems** (SecurityAuditor is #10):
1. **Brick** — Foundation with contracts & tests
2. **Engine** — Registry with auto-test generation
3. **Pipeline** — Data flow orchestration
4. **Tester** — Isolated testing with daemon threads
5. **Healer** — Repair prompt generation
6. **Sensory** — Tiered monitoring (light/full)
7. **Genetic** — DNA versioning + dependencies
8. **Immune** — Threat detection & rollback
9. **AIHealer** — Autonomous LLM repair
10. **SecurityAuditor** — Vulnerability scanning & hardening ⭐ NEW

## 🔐 Security Detection Capabilities

**Critical Patterns (instant low score):**
- Arbitrary code execution: `eval()`, `exec()`, `compile()`
- System commands: `os.system()`, `subprocess.Popen()`
- Unsafe serialization: `pickle.loads()`
- Dynamic imports: `__import__()`, `importlib`

**Risky Patterns (score penalties):**
- File operations without validation: `open()`, `os.remove()`
- Network calls: `requests`, `urllib`, `socket`
- Environment access: `os.environ`, `sys.argv`

**Good Patterns (score bonuses):**
- Type hints and validation
- Specific exception handling
- Input sanitization
- Comprehensive test coverage
- Pure functions (no side effects)

## 🎯 Next Steps

- [ ] Dashboard UI for security scores
- [ ] Real-time scanning on brick modification
- [ ] Integration with marketplace (pre-install audits)
- [ ] Sandbox execution enforcement
- [ ] Security regression tracking

---

**Version:** 1.4.0  
**Authors:** Medo & Neura  
**Date:** March 3, 2026  
**Tagline:** The world's first self-auditing code framework
