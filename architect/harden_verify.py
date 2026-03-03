import os
import sys
import importlib.util
import unittest
import random
from synapticbricks.core import (
    BrickEngine, initialize_aegis, PhantomEngine, BrickTester
)
from synapticbricks.architect.mother_bricks import intent_scanner, genome_sequencer

class ArchitectHardeningTests(unittest.TestCase):
    def setUp(self):
        self.test_id = random.randint(100000, 999999)
        self.workspace = f"C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect_test_{self.test_id}"
        os.makedirs(os.path.join(self.workspace, "vault"), exist_ok=True)
        self.engine = BrickEngine(os.path.join(self.workspace, "vault"))
        self.immune, self.monitor, self.memory = initialize_aegis(self.engine)
        self.phantom = PhantomEngine(sensory=self.monitor, genetic=self.memory)

    def test_dna_robustness_and_growth(self):
        """Advanced Test: Intent -> DNA -> Loading -> Verification"""
        
        # 1. Complex Intent
        intent = "Monitor stock prices and notify me if they crash"
        print(f"\n🔍 Testing Intent: \"{intent}\"")
        
        # 2. Mother Bricks action
        blueprint = intent_scanner.execute(intent_text=intent)
        dna_path = genome_sequencer.execute(blueprint=blueprint)
        self.assertTrue(os.path.exists(dna_path), "DNA file was not generated")
        
        # 3. Dynamic Growth (Loading)
        spec = importlib.util.spec_from_file_location("dynamic_test", dna_path)
        dna_module = importlib.util.module_from_spec(spec)
        dna_module.engine = self.engine # Inject engine
        spec.loader.exec_module(dna_module)
        
        # 4. Verify Organs follow Mandatory Type Hint rules
        for organ in blueprint["required_organs"]:
            brick_obj = getattr(dna_module, organ["id"])
            # Registering should NOT fail because sequencer now generates type hints
            self.engine.register(brick_obj)
            self.assertIsNotNone(self.engine.get(organ["id"]), f"Organ {organ['id']} was rejected or failed registration")
            
            # 5. Phantom Hardening: Check if child bricks are born robust
            report = self.phantom.analyze(brick_obj)
            print(f"📊 Organ [{organ['id']}] initial fragility: {report.fragility_score}")
            self.assertLess(report.fragility_score, 0.5, f"Generated organ {organ['id']} is too fragile at birth!")

        # 6. Nervous System Assembly
        organism = dna_module.build_organism(self.engine)
        res = organism.run({"raw_input": "STOCK_GO_BOOM"})
        
        self.assertTrue(res["success"], f"Generated organism failed its first breath: {res.get('error')}")
        self.assertIn("delivered", str(res["result"]), "Organism logic didn't reach the final stage")
        print("✅ Advanced Life Cycle: Successfully grew a robust, functional organism.")

if __name__ == "__main__":
    # Add architect path for local imports
    sys.path.append("C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect")
    suite = unittest.TestLoader().loadTestsFromTestCase(ArchitectHardeningTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
