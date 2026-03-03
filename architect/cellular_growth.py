import os
import sys
import time
import importlib.util
from synapticbricks.core import (
    BrickEngine, initialize_aegis, PhantomEngine
)
from mother_bricks import intent_scanner, genome_sequencer

def cellular_growth_demo():
    print("============================================================")
    print("🏗️  PROJECT ARCHITECT: PHASE 4 - CELLULAR GROWTH")
    print("============================================================\n")

    # 1. Initialize the Factory Nervous System
    engine = BrickEngine("C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect\\vault")
    immune, monitor, memory = initialize_aegis(engine)

    # 2. Receiving Intent
    my_intent = "Scrape the news and analyze sentiment for stocks"
    print(f"📡 INTENT: \"{my_intent}\"")
    
    # 3. Sequencing (Mother Bricks at work)
    blueprint = intent_scanner.execute(intent_text=my_intent)
    dna_path = genome_sequencer.execute(blueprint=blueprint)
    dna_filename = os.path.basename(dna_path)
    print(f"🧬 DNA Sequenced: {dna_filename}\n")

    # 4. CELLULAR GROWTH: Dynamic Loading and Integration
    print("🌱 Phase 4: Triggering Cellular Growth (Dynamic Integration)...")
    
    # Load the generated DNA module dynamically
    spec = importlib.util.spec_from_file_location("dynamic_dna", dna_path)
    dna_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dna_module)
    
    # Register the new bricks into the living engine
    new_bricks = []
    for organ in blueprint["required_organs"]:
        brick_obj = getattr(dna_module, organ["id"])
        engine.register(brick_obj)
        new_bricks.append(brick_obj)
    
    print(f"✅ Bricks Registered: {[b.meta.id for b in new_bricks]}")
    
    # Build the organism's nervous system (The Pipeline)
    organism = dna_module.build_organism(engine)
    print(f"✅ Nervous System (Pipeline) Connected: {organism.name}\n")
    
    # 5. FIRST BREATH: Running the autonomous software
    print("🌬️  Organism's First Breath: Executing Pipeline...")
    results = organism.run({"raw_input": "Breaking Market News: Stocks are rising!"})
    
    if results["success"]:
        print("✅ Pipeline Success!")
        print(f"📊 Final Data Tail: {results['result']}\n")
    else:
        print(f"❌ Pipeline Failed: {results['error']}")

    print("============================================================")
    print("✅ PHASE 4 COMPLETE: ARCHITECT CAN GROW SOFTWARE AUTONOMOUSLY")
    print("============================================================")

if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    cellular_growth_demo()
