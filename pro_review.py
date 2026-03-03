import os
import sys
import unittest
import random
import time
from synapticbricks.core import (
    brick, BrickEngine, initialize_aegis, sensory, 
    PhantomEngine, EdgeCaseGenerator, Pipeline
)

class ProfessionalReviewTests(unittest.TestCase):
    def setUp(self):
        self.test_id = random.randint(1000, 9999)
        self.workspace = f"C:\\Users\\MedoRadi\\clawd\\synapticbricks\\review_ws_{self.test_id}"
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        self.engine = BrickEngine(self.workspace)
        self.immune, self.monitor, self.memory = initialize_aegis(self.engine)
        self.phantom = PhantomEngine(sensory=self.monitor, genetic=self.memory)

    def test_end_to_end_lifecycle(self):
        """Review: Does a brick survive the full Build -> Sense -> Predict -> Heal cycle?"""
        
        # 1. BUILD
        @brick("math_core", description="Core math brick")
        @sensory(self.monitor)
        def math_core(a: int, b: int) -> int:
            return a // b # Intentional fragility (zero division)
        
        math_core.add_test(inputs={"a": 10, "b": 2}, expected_output=5)
        self.engine.register(math_core)
        
        # 2. SENSE
        math_core.execute(a=10, b=5)
        logs = self.monitor.logs.get("math_core")
        self.assertTrue(len(logs) > 0, "Sensory monitoring failed to log execution")
        
        # 3. PREDICT (Phantom)
        report = self.phantom.analyze(math_core)
        self.assertGreater(report.fragility_score, 0, "Phantom failed to detect zero division fragility")
        self.assertTrue(any(p['pattern'] == 'zero_division' for p in report.dangerous_patterns), "Phantom missed zero_division pattern")
        
        # 4. HEAL (Simulated fix)
        def fixed_math(a: int, b: int) -> int:
            return a // b if b != 0 else 0
            
        from synapticbricks.core import BrickHealer, BrickTester
        healer = BrickHealer(self.engine, BrickTester(self.engine))
        res = healer.auto_heal("math_core", fixed_math)
        self.assertTrue(res['success'], "Self-healing pipeline failed to apply/verify fix")
        
        # Verify version bump
        new_brick = self.engine.get("math_core")
        self.assertEqual(new_brick.meta.version, "1.0.1")

    def test_pipeline_data_flow(self):
        """Review: Do pipelines correctly move data between living bricks?"""
        @brick("b1", "B1")
        def b1(x: int) -> int: return x + 1
        
        @brick("b2", "B2")
        def b2(y: int) -> int: return y * 2
        
        self.engine.register_many([b1, b2])
        
        p = Pipeline("test_p", self.engine)
        p.add_step("b1", input_map={"x": "val"}, output_key="mid")
        p.add_step("b2", input_map={"y": "mid"}, output_key="out")
        
        res = p.run({"val": 10})
        self.assertTrue(res["success"], f"Pipeline failed: {res.get('error')}")
        self.assertEqual(res["result"], 22, "Pipeline result corrupted")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(ProfessionalReviewTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
