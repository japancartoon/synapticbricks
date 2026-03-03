import os
import sys
import time
from synapticbricks.core import (
    BrickEngine, initialize_aegis, PhantomEngine, Pipeline, sensory
)
import dna

def run_project():
    print("============================================================")
    print("🧠 SYNPATICBRICKS PROJECT: QUANTUM NEWS ANALYZER (V2)")
    print("============================================================\n")

    # 1. Initialize Living Environment
    vault_path = "C:\\Users\\MedoRadi\\clawd\\synapticbricks\\projects\\quantum_news\\vault_v2"
    if not os.path.exists(vault_path): os.makedirs(vault_path)
    engine = BrickEngine(vault_path)
    immune, monitor, memory = initialize_aegis(engine)
    phantom = PhantomEngine(sensory=monitor, genetic=memory)

    # 2. Dynamic Wrap with Sensory Nervous System
    # This proves Aegis can be attached to ANY brick logic
    dna.news_watcher.func = sensory(monitor)(dna.news_watcher.func)
    dna.sentiment_core.func = sensory(monitor)(dna.sentiment_core.func)
    dna.decision_matrix.func = sensory(monitor)(dna.decision_matrix.func)

    # 3. Register Organs
    engine.register_many([dna.news_watcher, dna.sentiment_core, dna.decision_matrix])

    # 4. Construct Organism
    organism = Pipeline("QuantumNews_V2", engine)
    organism.add_step("news_watcher", input_map={"url": "source"}, output_key="headlines")
    organism.add_step("sentiment_core", input_map={"text_list": "headlines"}, output_key="analysis")
    organism.add_step("decision_matrix", input_map={"analysis": "analysis"}, output_key="decision")

    # 5. Loop and Monitor
    print("⚡ Starting Autonomous Execution Loop...")
    for i in range(1, 6):
        print(f"\n🌀 Cycle {i}: Processing data...")
        result = organism.run({"source": "https://marketnews.com"})
        
        if result["success"]:
            print(f"✅ Result: {result['result']}")
        else:
            print(f"❌ Crash in {result['failed_brick']}: {result['error']}")

        # Every 3 cycles, let's look at the nervous system health
        if i == 3:
            print("👁️ Checking Aegis Sensory Logs for 'news_watcher'...")
            logs = monitor.logs.get("news_watcher", [])
            print(f"   -> Recorded {len(logs)} nervous signals (latencies).")

    print("\n============================================================")
    print("🏁 V2 MONITORING COMPLETE")
    print("============================================================")

if __name__ == "__main__":
    run_project()
