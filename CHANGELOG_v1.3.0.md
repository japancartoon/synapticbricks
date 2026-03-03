# SynapticBricks v1.3.0 — Autonomous Healing Update

## 🚀 What's New

### AIHealer — Autonomous LLM-Powered Repair
The world's first truly self-healing code system.

**How it works:**
1. Brick breaks (detected via test failures)
2. System generates repair prompt with context
3. Calls Gemini API to generate fix
4. **Tests fix BEFORE applying** (safety gate)
5. Only applies if ALL tests pass
6. Verifies post-application

**Features:**
- ✅ Tiered healing (Flash → Pro fallback)
- ✅ Pre-apply test validation
- ✅ Success rate tracking
- ✅ Token usage monitoring
- ✅ No hardcoded API keys (env var or arg)

### SynapticPulse Dashboard Updates
- ✅ New API endpoints: `/api/healing/stats`, `/api/healing/heal/<brick_id>`
- ✅ Optional AIHealer integration (requires API key)
- ✅ Real-time healing stats display

## 📦 Installation

```bash
pip install -e .
```

**Dependencies:**
- `psutil` (system monitoring)
- `flask>=2.0` (dashboard)
- `requests>=2.25` (AI API calls)

## 🔑 API Key Setup

**Never hardcode API keys!**

### Option 1: Environment Variable (Recommended)
```bash
set GEMINI_API_KEY=your_api_key_here
python demo_autonomous_healing.py
```

### Option 2: Command Line Argument
```bash
python demo_autonomous_healing.py your_api_key_here
```

### Option 3: Dashboard Integration
```bash
python -m synapticbricks.pulse.server --demo --gemini-key your_key
# Or with env var:
set GEMINI_API_KEY=your_key
python -m synapticbricks.pulse.server --demo
```

## 🧪 Demo

```bash
# Set API key
set GEMINI_API_KEY=your_key

# Run autonomous healing demo
python synapticbricks\demo_autonomous_healing.py

# Or launch dashboard with healing enabled
python -m synapticbricks.pulse.server --demo
```

## 📊 Stats

**First real test:**
- Model: Gemini 2.5 Flash (free tier)
- Bug: `ZeroDivisionError` in calculator
- Fix time: 3.4 seconds
- Pre-apply tests: 3/3 passed ✅
- Post-apply tests: 3/3 passed ✅
- Success rate: 100%

## 🔒 Security Notes

- ✅ No API keys in source code
- ✅ Environment variables or CLI args only
- ✅ Pre-apply test validation prevents bad fixes
- ✅ All healing attempts logged for audit

## 🎯 What's Next

- Dashboard UI for healing stats
- More complex bug tests
- Escalation to reasoning models for hard bugs
- Multi-model comparison benchmarks

## 🧠 System Architecture

**9 Core Systems:**
1. **Brick** — Foundation with contracts & tests
2. **Engine** — Registry with auto-test generation
3. **Pipeline** — Data flow orchestration
4. **Tester** — Isolated testing with daemon threads
5. **Healer** — Repair prompt generation
6. **Sensory** — Tiered monitoring (light/full)
7. **Genetic** — DNA versioning + dependencies
8. **Immune** — Threat detection & rollback
9. **AIHealer** — Autonomous LLM repair ⭐ NEW

---

**Version:** 1.3.0  
**Authors:** Medo & Neura  
**Date:** March 3, 2026
