import time
import json
import os
import sys
from .sensory import SensoryMonitor
from .genetic import GeneticMemory
from .healer import BrickHealer
from .engine import BrickEngine
from .tester import BrickTester

class ImmuneSystem:
    def __init__(self, engine, tester, monitor, memory):
        self.engine = engine
        self.tester = tester
        self.monitor = monitor
        self.memory = memory
        self.healer = BrickHealer(engine, tester)
        self.alert_threshold = 2.0  # 2x slower than average = alert

    def scan_for_threats(self):
        """Scans sensory data for 'pain' (performance degradation) or failures."""
        threats = []
        # Create a snapshot to avoid modification issues during iteration
        log_snapshot = dict(self.monitor.logs)
        
        for brick_id, logs in log_snapshot.items():
            if not logs: continue
            
            # Check for recent failures
            recent_failures = [e for e in logs[-5:] if e["status"] == "failing"]
            if recent_failures:
                threats.append({
                    "brick_id": brick_id,
                    "type": "functional_failure",
                    "severity": "CRITICAL",
                    "reason": f"Failing: {recent_failures[-1]['error']}"
                })
                continue
            
            # Check for performance degradation (latency)
            if len(logs) >= 5:
                # Use all but the last log to establish baseline
                avg_latency = sum(e["latency_ms"] for e in logs[:-1]) / len(logs[:-1])
                current_latency = logs[-1]["latency_ms"]
                
                # Check for massive spike or establish logic for 0 baseline
                if current_latency > (avg_latency * self.alert_threshold) or (avg_latency <= 0.001 and current_latency > 100):
                    threats.append({
                        "brick_id": brick_id,
                        "type": "performance_pain",
                        "severity": "HIGH",
                        "reason": f"Latency spike: {current_latency}ms (avg: {round(avg_latency, 2)}ms)"
                    })
        
        return threats

    def respond_to_threat(self, threat):
        """Immune response: healing, refactoring, or rollbacks."""
        brick_id = threat["brick_id"]
        brick = self.engine.get(brick_id)
        
        if not brick:
            return False, f"Unknown brick: {brick_id}"

        print(f"🛡️  [IMMUNE RESPONSE] {threat['severity']} - {threat['reason']}")
        
        if threat["type"] == "functional_failure":
            # standard self-healing
            print(f"🩺 Healing functional failure in {brick_id}...")
            # In a real environment, we'd trigger an AI fix here.
            return True, f"Repair initiated for {brick_id}"
            
        elif threat["type"] == "performance_pain":
            # Auto-optimization response
            print(f"🧬 Performance pain detected in {brick_id}. Analyzing Genetic Memory...")
            return self._evolve_brick(brick_id, threat["reason"])
            
        return False, "No strategy found"

    def _evolve_brick(self, brick_id, reason):
        """
        Executes a real evolution:
        1. Find a higher-scoring DNA variant in Genetic Memory.
        2. If found, automatically swap the brick's implementation (Rollback).
        3. If no better DNA exists, mark current as 'weak' and signal for AI Refactor.
        """
        brick = self.engine.get(brick_id)
        best_variant = self.memory.get_best_version(brick_id)
        
        # Calculate current score
        current_score = 1.0 # Default
        for v in self.memory.memory[brick_id]["lineage"]:
            if v["version"] == brick.meta.version:
                current_score = v["genetic_score"]
                break
        
        # 1. ROLLBACK: If a previous version was significantly better (>20% better score)
        # OR if we just established that the current version is bad and there is ANY better one
        if best_variant and (best_variant["genetic_score"] > current_score * 1.1 or best_variant["version"] != brick.meta.version):
            # DEPENDENCY CHECK: Verify all imports are available before rollback
            deps = best_variant.get("dependencies", [])
            if deps:
                ok, missing = self.memory.check_dependencies(deps)
                if not ok:
                    print(f"⛔ ROLLBACK ABORTED: Missing dependencies {missing} for {best_variant['version']}")
                    print(f"   Keeping current version {brick.meta.version}. Install missing packages to enable rollback.")
                    return False, f"Rollback blocked: missing {missing}"

            print(f"♻️  AUTONOMOUS ROLLBACK: Version {best_variant['version']} (Score: {best_variant['genetic_score']}) is healthier than current (Score: {current_score}).")
            print(f"   Swapping {brick_id} logic back to healthy DNA...")
            
            # Real Authority: Swap the function pointer and source
            self.healer.apply_fix(brick_id, self._reconstruct_func(best_variant["source"]))
            return True, f"Autonomous rollback to {best_variant['version']} successful"
            
        # 2. MARK AS WEAK: Reduce score to trigger future AI refactoring
        self.memory.update_score(brick_id, brick.meta.version, -0.3)
        print(f"📉 DNA WEAKENED: {brick_id} v{brick.meta.version} score reduced due to performance pain.")
        
        return True, f"Brick {brick_id} marked as weak. AI Refactor required."

    def _reconstruct_func(self, source_code):
        """Reconstructs a function object from source code safely."""
        namespace = {}
        # Minimal environment for reconstruction
        namespace['time'] = time
        namespace['monitor'] = self.monitor
        
        # Define a mock @brick decorator so the source code can be exec'd
        def mock_brick(*args, **kwargs):
            def wrapper(f): return f
            return wrapper
            
        namespace['brick'] = mock_brick
        namespace['sensory'] = mock_brick # Treat sensory as pass-through during reconstruction
        
        try:
            # Clean the source code string if it's stored with metadata
            cleaned_source = source_code
            if "```python" in cleaned_source:
                cleaned_source = cleaned_source.split("```python")[1].split("```")[0].strip()
            
            exec(cleaned_source, namespace)
            # Find the actual function (the one that isn't the decorator or time)
            for name, item in namespace.items():
                if callable(item) and name not in ('brick', 'sensory', 'mock_brick', 'mock_sensory'):
                    return item
        except Exception as e:
            print(f"❌ RECONSTRUCTION FAILED: {str(e)}")
            
        return None

def initialize_aegis(engine):
    """Factory to set up the Aegis Immune System."""
    tester = BrickTester(engine)
    monitor = SensoryMonitor()
    memory = GeneticMemory()
    immune = ImmuneSystem(engine, tester, monitor, memory)
    return immune, monitor, memory
