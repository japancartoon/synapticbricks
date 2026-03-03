import time
import os
import random
from synapticbricks.core import (
    brick, BrickEngine, initialize_aegis, sensory
)

# 1. Initialize Engine and Aegis Immune System
engine = BrickEngine("C:\\Users\\MedoRadi\\clawd\\aegis_brick")
immune, monitor, memory = initialize_aegis(engine)

# 2. Define some "Living Bricks" with Sensory Awareness
@brick("fetch_data", description="Simulate fetching data from an API")
@sensory(monitor)
def fetch_data(url: str) -> dict:
    """Fetches data from a URL (simulated)."""
    # Simulate network latency
    time.sleep(random.uniform(0.1, 0.3))
    return {"status": "success", "url": url, "data": [1, 2, 3]}

@brick("process_data", description="Process raw data into a summary")
@sensory(monitor)
def process_data(data: list) -> dict:
    """Processes a list of numbers."""
    # This brick starts healthy but will be degraded later
    return {"sum": sum(data), "count": len(data)}

@brick("risky_brick", description="A brick that might fail")
@sensory(monitor)
def risky_brick(x: int) -> float:
    """Risky math operation."""
    if x == 0:
        raise ZeroDivisionError("Cannot divide by zero in risky_brick")
    return 100 / x

# 3. Register Bricks
engine.register_many([fetch_data, process_data, risky_brick])

def run_simulation():
    print("============================================================")
    print("🛡️  AEGIS-BRICK: AI IMMUNE SYSTEM DEMO")
    print("============================================================\n")

    # Step A: Normal Operation (Healthy State)
    print("1️⃣  Phase 1: Normal Healthy Operation...")
    for _ in range(5):
        fetch_data.execute(url="https://api.example.com")
        process_data.execute(data=[10, 20, 30])
        risky_brick.execute(x=5)
    print("✅ System operating normally. All sensors green.\n")

    # Step B: Injecting "Pain" (Performance Degradation)
    print("2️⃣  Phase 2: Injecting Performance Pain (Latency Spike)...")
    # Redefine process_data logic to be slow
    def slow_process_data_func(data):
        time.sleep(1.5) # 5x slower than normal
        return {"sum": sum(data), "count": len(data)}
    
    # Simulate a slow execution via the sensory monitor directly
    # Since we can't easily swap the underlying func in the Brick object for a demo
    # we just log the event to show the immune system response
    monitor.log_event("process_data", 1.5, 0, "healthy")
    print("⚠️  'process_data' is experiencing high latency (1.5s)...\n")

    # Step C: Immune System Scan
    print("3️⃣  Phase 3: Immune System Scanning for Threats...")
    threats = immune.scan_for_threats()
    if threats:
        for threat in threats:
            immune.respond_to_threat(threat)
    else:
        print("✅ No threats detected.")
    print("")

    # Step D: Functional Failure (Immune Response)
    print("4️⃣  Phase 4: Triggering Functional Failure...")
    try:
        risky_brick.execute(x=0)
    except:
        # Manually log failure if execute raises
        monitor.log_event("risky_brick", 0.01, 0, "failing", "ZeroDivisionError: division by zero")
        print("💥 'risky_brick' failed with ZeroDivisionError.")
    
    threats = immune.scan_for_threats()
    for threat in threats:
        if threat["brick_id"] == "risky_brick":
            immune.respond_to_threat(threat)
    print("")

    # Step E: Genetic Memory Check
    print("5️⃣  Phase 5: Checking Genetic Memory (Evolution History)...")
    if "process_data" in memory.memory:
        dna = memory.memory["process_data"]
        print(f"🧬 Brick: process_data")
        print(f"   Active DNA Hash: {dna['dna_hash'][:12]}...")
        if dna["lineage"]:
            latest = dna["lineage"][-1]
            print(f"   Genetic Score: {latest['genetic_score']} (Scale: 0.0 - 2.0)")
    
    print("\n============================================================")
    print("✅ Aegis-Brick Simulation Complete")
    print("============================================================")

if __name__ == "__main__":
    # Record initial evolution for bricks
    memory.record_evolution("fetch_data", "...", "1.0.0", "Initial build")
    memory.record_evolution("process_data", "...", "1.0.0", "Initial build", score=1.5)
    memory.record_evolution("risky_brick", "...", "1.0.0", "Initial build")
    
    run_simulation()
