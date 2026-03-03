import time
import os
import random
import unittest
import sys
from synapticbricks.core import (
    brick, BrickEngine, initialize_aegis, sensory, ImmuneSystem, SensoryMonitor, GeneticMemory, BrickTester
)

class TestAegisLogic(unittest.TestCase):
    def setUp(self):
        # Fresh isolated engine for logic testing
        self.test_id = random.randint(1000, 9999)
        self.project_dir = f"C:\\Users\\MedoRadi\\clawd\\aegis_brick\\test_workspace_{self.test_id}"
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)
        self.engine = BrickEngine(self.project_dir)
        
        # Use unique paths for each test run to avoid cross-talk
        monitor_path = os.path.join(self.project_dir, "sensory_logs.json")
        genetic_path = os.path.join(self.project_dir, "genetic_memory.json")
        
        self.monitor = SensoryMonitor(monitor_path)
        self.memory = GeneticMemory(genetic_path)
        self.immune = ImmuneSystem(self.engine, BrickTester(self.engine), self.monitor, self.memory)

    def test_sensory_latency_logging(self):
        """Logic Test: Does the sensory system accurately record latency?"""
        @brick("test_latency", "Test")
        @sensory(self.monitor)
        def test_latency():
            time.sleep(0.1)
            return True
        
        self.engine.register(test_latency)
        test_latency.execute()
        
        logs = self.monitor.logs.get("test_latency")
        self.assertIsNotNone(logs)
        self.assertGreaterEqual(logs[0]["latency_ms"], 100)
        print("✅ Logic: Sensory latency recording verified.")

    def test_immune_pain_detection(self):
        """Logic Test: Does the immune system detect a 3x latency spike?"""
        brick_id = "pain_test"
        # Simulate healthy baseline (10ms)
        for _ in range(10):
            self.monitor.log_event(brick_id, 0.01, 0, "healthy")
            
        # Simulate a sudden spike (100ms = 10x spike)
        self.monitor.log_event(brick_id, 0.1, 0, "healthy")
        
        threats = self.immune.scan_for_threats()
        pain_threats = [t for t in threats if t["brick_id"] == brick_id and t["type"] == "performance_pain"]
        
        self.assertTrue(len(pain_threats) > 0)
        print(f"✅ Logic: Immune system detected pain ({pain_threats[0]['reason']})")

    def test_genetic_memory_lineage(self):
        """Logic Test: Does genetic memory track DNA evolution?"""
        brick_id = "dna_test"
        code_v1 = "def x(): return 1"
        code_v2 = "def x(): return 2"
        
        self.memory.record_evolution(brick_id, code_v1, "1.0.0", "Genesis")
        self.memory.record_evolution(brick_id, code_v2, "1.1.0", "Evolution")
        
        dna = self.memory.memory.get(brick_id)
        self.assertEqual(len(dna["lineage"]), 2)
        self.assertEqual(dna["active_version"], "1.1.0")
        print("✅ Logic: Genetic lineage tracking verified.")

    def test_immune_response_to_failure(self):
        """Logic Test: Does the immune system respond to functional failure?"""
        brick_id = "fail_test"
        # Log 5 failures
        for _ in range(5):
            self.monitor.log_event(brick_id, 0.01, 0, "failing", "TestError")
            
        threats = self.immune.scan_for_threats()
        failure_threats = [t for t in threats if t["brick_id"] == brick_id and t["type"] == "functional_failure"]
        
        self.assertTrue(len(failure_threats) > 0)
        print(f"✅ Logic: Immune response to functional failure verified.")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAegisLogic)
    unittest.TextTestRunner(verbosity=1).run(suite)
