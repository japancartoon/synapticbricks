import os
import sys
import unittest
import random
import time
from synapticbricks.core import (
    brick, BrickEngine, initialize_aegis, sensory, 
    PhantomEngine, EdgeCaseGenerator, Pipeline,
    ImmuneSystem, SensoryMonitor, GeneticMemory, BrickTester
)

class PerfectionVerification(unittest.TestCase):
    def setUp(self):
        self.test_id = random.randint(10000, 99999)
        self.workspace = f"C:\\Users\\MedoRadi\\clawd\\synapticbricks\\perf_ws_{self.test_id}"
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        self.engine = BrickEngine(self.workspace)
        
        # Use fresh memory objects to avoid persistence issues
        self.monitor = SensoryMonitor(os.path.join(self.workspace, "logs.json"))
        self.memory = GeneticMemory(os.path.join(self.workspace, "gen.json"))
        self.immune = ImmuneSystem(self.engine, BrickTester(self.engine), self.monitor, self.memory)

    def test_blind_brick_rejection(self):
        """Logical Guard: Does the engine reject bricks without type hints?"""
        @brick("blind_brick")
        def blind_brick(data): # No type hint
            return data
        
        self.engine.register(blind_brick)
        self.assertIsNone(self.engine.get("blind_brick"), "Engine accepted a brick without type hints")
        print("✅ Guard: Blind brick rejection verified.")

    def test_autonomous_immune_authority(self):
        """Logical Authority: Does Aegis actually swap code variants?"""
        # 1. Register a 'genetically superior' v1.0.0
        superior_code = "@brick('ev_test')\ndef ev_test(x: int) -> int: return x"
        self.memory.record_evolution("ev_test", superior_code, "1.0.0", "Genesis", score=2.0)
        
        # 2. Register a 'weak' v2.0.0
        @brick("ev_test", version="2.0.0")
        def weak_brick(x: int) -> int:
            return x
        
        self.engine.register(weak_brick)
        
        # Manually seed sensory data with a massive spike
        for _ in range(10):
            self.monitor.log_event("ev_test", 0.01, 0) # Baseline 10ms
        self.monitor.log_event("ev_test", 1.0, 0)    # Spike 1000ms
            
        # 3. Trigger Immune Response
        threats = self.immune.scan_for_threats()
        self.assertTrue(len(threats) > 0, "Immune system failed to detect pain")
        
        pain_threat = next(t for t in threats if t['brick_id'] == 'ev_test')
        
        # Response should trigger ROLLBACK
        self.immune.respond_to_threat(pain_threat)
        
        # 4. Verify rollback happened (version should bump)
        new_brick = self.engine.get("ev_test")
        self.assertEqual(new_brick.meta.version, "2.0.1", "Version didn't bump after rollback")
        print(f"✅ Authority: Autonomous rollback to healthy DNA verified (v{new_brick.meta.version}).")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(PerfectionVerification)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
