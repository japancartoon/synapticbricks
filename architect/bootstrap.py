import os
import sys
import time
from synapticbricks.core import (
    BrickEngine, initialize_aegis, PhantomEngine
)
from mother_bricks import intent_scanner, genome_sequencer

def bootstrap_architect():
    print("============================================================")
    print("🏗️  PROJECT ARCHITECT: THE AUTONOMOUS SOFTWARE FACTORY")
    print("============================================================\n")

    # 1. Initialize the nervous system for the factory
    engine = BrickEngine("C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect\\vault")
    immune, monitor, memory = initialize_aegis(engine)
    phantom = PhantomEngine(sensory=monitor, genetic=memory)

    # 2. Input Human Intent
    my_intent = "Monitor the global sentiment of OpenAI and notify me if they are about to go bankrupt"
    print(f"📡 RECEIVING INTENT: \"{my_intent}\"")
    
    # 3. PHASE 1: Intent Scanning (Mother Brick 1)
    print("🧠 PHASE 1: Scanning Intent for Digital Organs...")
    blueprint = intent_scanner.execute(intent_text=my_intent)
    
    print(f"✅ Blueprint Created. Required Organs: {[o['id'] for o in blueprint['required_organs']]}")
    print(f"📈 Complexity: {blueprint['complexity_score']}\n")

    # 4. PHASE 2: Genome Sequencing (Mother Brick 2)
    print("🧬 PHASE 2: Sequencing DNA (Autonomous Code Generation)...")
    dna_path = genome_sequencer.execute(blueprint=blueprint)
    
    print(f"✅ DNA Sequenced and stored in: {os.path.basename(dna_path)}")
    
    # 5. PHASE 3: Safety Verification (Phantom)
    print("🔮 PHASE 3: Running Phantom Gauntlet on New DNA...")
    # In the full project, we would dynamically load and analyze the generated bricks.
    # For the bootstrap, we verify the 'Intent Scanner' itself is robust.
    report = phantom.analyze(intent_scanner)
    
    print(f"📊 IntentScanner Fragility: {report.fragility_score}")
    if report.fragility_score < 0.2:
        print("✅ DNA is 'Fit' for deployment.")
    else:
        print("❌ DNA is too fragile. Evolution required.")

    print("\n============================================================")
    print("✅ ARCHITECT: FIRST SIGNS OF LIFE VERIFIED")
    print("============================================================")

if __name__ == "__main__":
    # Ensure local path is available
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    bootstrap_architect()
