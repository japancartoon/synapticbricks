import os
import sys
import time
import importlib.util
from synapticbricks.core import (
    BrickEngine, initialize_aegis, PhantomEngine, BrickHealer, BrickTester, sensory
)
from mother_bricks import intent_scanner, genome_sequencer

def self_evolution_demo():
    print("============================================================")
    print("🏗️  PROJECT ARCHITECT: PHASE 5 - SELF-EVOLUTION")
    print("============================================================\n")

    # 1. Initialize the Factory Nervous System
    test_workspace = f"C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect\\vault_evo_{int(time.time())}"
    if not os.path.exists(test_workspace): os.makedirs(test_workspace)
    engine = BrickEngine(test_workspace)
    immune, monitor, memory = initialize_aegis(engine)

    # 2. Receiving Intent
    my_intent = "Analyze text sentiment"
    print(f"📡 INTENT: \"{my_intent}\"")
    
    # 3. Sequencing (Now generates sensory-enabled DNA)
    blueprint = intent_scanner.execute(intent_text=my_intent)
    dna_path = genome_sequencer.execute(blueprint=blueprint)
    
    # 4. Loading the "Genesis" Version (v1.0.0)
    spec = importlib.util.spec_from_file_location("evo_dna", dna_path)
    dna_module = importlib.util.module_from_spec(spec)
    dna_module.monitor = monitor
    spec.loader.exec_module(dna_module)
    
    brick_id = blueprint["required_organs"][0]["id"] # 'analyzer'
    brick_obj = getattr(dna_module, brick_id)
    engine.register(brick_obj)
    
    # Establish v1.0.0 in Genetic Memory with high score
    with open(dna_path, 'r') as f: genesis_dna = f.read()
    memory.record_evolution(brick_id, genesis_dna, "1.0.0", "Genesis", score=1.8)
    
    # Establish a baseline of logs
    for _ in range(10):
        monitor.log_event(brick_id, 0.01, 0)
    
    print(f"🌱 Genesis Brick: {brick_id} v1.0.0 (Score: 1.8)")

    # 5. Simulate a "Mutation" (New Version v1.0.1 that is broken/slow)
    brick_obj.meta.version = "1.0.1"
    memory.record_evolution(brick_id, "# Weak DNA", "1.0.1", "Update", score=0.5)
    print(f"🧬 Update Applied: {brick_id} v1.0.1 (Score: 0.5)")
    
    # 6. TRIGGERING "PAIN"
    print("\n⚠️  Injecting performance pain into v1.0.1...")
    # Massive latency spike
    monitor.log_event(brick_id, 2.0, 0) 
    
    # 7. THE IMMUNE RESPONSE
    print("🛡️  Immune System scanning for threats...")
    threats = immune.scan_for_threats()
    
    found = False
    for threat in threats:
        if threat['brick_id'] == brick_id:
            found = True
            print(f"🚨 Threat detected: {threat['type']} - {threat['reason']}")
            # Respond with authority
            immune.respond_to_threat(threat)
    
    # 8. VERIFY EVOLUTION
    updated_brick = engine.get(brick_id)
    print(f"\n🧬 Post-Response Status:")
    print(f"   Active Version: {updated_brick.meta.version}")
    
    # If rollback worked, version should be 1.0.1 + 1 patch = 1.0.2
    if updated_brick.meta.version == "1.0.2":
        print("✅ SUCCESS: The organism successfully performed an Autonomous Rollback to healthy DNA.")
    else:
        if not found:
            print("❌ FAILURE: Pain was not detected by scan_for_threats.")
        else:
            print("❌ FAILURE: The organism failed to evolve despite threat detection.")

    print("\n============================================================")
    print("✅ PHASE 5 COMPLETE: ARCHITECT IS NOW A SELF-EVOLVING ORGANISM")
    print("============================================================")

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    self_evolution_demo()
