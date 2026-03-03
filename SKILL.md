# SynapticBricks Skill 🧠🧱

**Version:** 1.1.0
**Location:** `C:\Users\MedoRadi\clawd\synapticbricks\`

---

## 🏗️ Core Workflow

### 1. Build a Brick
```python
from synapticbricks.core import brick, sensory

@brick("my_brick")
@sensory(monitor)
def my_function(data: dict) -> str:
    return data["name"]
```

### 2. Predict Failure (Phantom)
```python
from synapticbricks.core import PhantomEngine
phantom = PhantomEngine(sensory=monitor)
report = phantom.analyze(my_brick)
```

### 3. Heal & Evolve (Aegis)
The immune system automatically detects "pain" in sensory logs and triggers rollbacks or AI-powered refactors.

---
*Refer to README.md in the root directory for full documentation.*
