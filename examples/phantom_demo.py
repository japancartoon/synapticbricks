"""
Phantom Demo — Demonstrates the Predictive Failure Engine.

Creates bricks with varying fragility levels, runs Phantom analysis,
and displays full reports for each.
"""

import sys
import os

# Ensure aegis_brick is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapticbricks.core.brick import Brick, brick
from synapticbricks.core.phantom import PhantomEngine, EdgeCaseGenerator
from synapticbricks.core.sensory import SensoryMonitor
from synapticbricks.core.genetic import GeneticMemory


# ---------------------------------------------------------------------------
# Brick 1: ROBUST — Handles everything gracefully
# ---------------------------------------------------------------------------
@brick("robust_divider", description="Robust division with full input validation")
def robust_divider(a: float, b: float) -> float:
    """Safely divides a by b with full edge case handling."""
    if a is None or b is None:
        return 0.0
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return 0.0
    import math
    if math.isnan(a) or math.isnan(b):
        return 0.0
    if math.isinf(a) or math.isinf(b):
        return 0.0
    if b == 0 or b == -0.0:
        return 0.0
    try:
        result = a / b
        if math.isnan(result) or math.isinf(result):
            return 0.0
        return result
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Brick 2: FRAGILE — Crashes on almost anything unexpected
# ---------------------------------------------------------------------------
@brick("fragile_parser", description="Fragile JSON key extractor with no validation")
def fragile_parser(data: str) -> str:
    """Extracts a key from JSON string. No error handling at all."""
    import json
    parsed = json.loads(data)
    return parsed["name"].upper().strip()


# ---------------------------------------------------------------------------
# Brick 3: MEDIUM — Handles some cases but not all
# ---------------------------------------------------------------------------
@brick("medium_processor", description="Processes a list of numbers with partial validation")
def medium_processor(numbers: list, factor: int) -> list:
    """Multiplies each number by factor. Some validation."""
    if not numbers:
        return []
    if factor is None:
        raise ValueError("Factor cannot be None")
    return [n * factor for n in numbers]


# ---------------------------------------------------------------------------
# Brick 4: NUMERIC — Pure math brick
# ---------------------------------------------------------------------------
@brick("sqrt_brick", description="Computes square root")
def sqrt_brick(value: float) -> float:
    """Computes the square root of a value."""
    import math
    if value is None:
        raise TypeError("Cannot compute sqrt of None")
    return math.sqrt(value)


# ---------------------------------------------------------------------------
# Main Demo
# ---------------------------------------------------------------------------
def main():
    print()
    print("=" * 60)
    print("  PHANTOM — Predictive Failure Engine Demo")
    print("  BrickLang / Aegis-Brick")
    print("=" * 60)
    print()

    # Set up integrations (optional)
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    sensory = SensoryMonitor(
        data_path=os.path.join(data_dir, "phantom_sensory_logs.json")
    )
    genetic = GeneticMemory(
        data_path=os.path.join(data_dir, "phantom_genetic_memory.json")
    )

    # Create the Phantom Engine
    phantom = PhantomEngine(sensory=sensory, genetic=genetic)

    # Bricks to analyze
    bricks = [robust_divider, fragile_parser, medium_processor, sqrt_brick]

    for b in bricks:
        # Show edge case count
        edge_cases = EdgeCaseGenerator.generate(b)
        print(f"  Generating {len(edge_cases)} edge cases for [{b.meta.id}]...")

        # Run full analysis
        report = phantom.analyze(b)

        # Print the report
        print(PhantomEngine.generate_report(report))
        print()

    # Summary comparison
    print()
    print("=" * 60)
    print("  FRAGILITY COMPARISON")
    print("=" * 60)
    print()
    print(f"  {'Brick':<25} {'Score':<10} {'Pass/Fail':<15} {'Verdict'}")
    print(f"  {'-'*25} {'-'*10} {'-'*15} {'-'*15}")

    for b in bricks:
        report = phantom.analyze(b)
        score = report.fragility_score
        pf = f"{report.passed}/{report.failed}"

        if score == 0:
            verdict = "\u2705 BULLETPROOF"
        elif score < 0.2:
            verdict = "\U0001f7e2 ROBUST"
        elif score < 0.5:
            verdict = "\U0001f7e1 MODERATE"
        elif score < 0.8:
            verdict = "\U0001f7e0 FRAGILE"
        else:
            verdict = "\U0001f534 CRITICAL"

        print(f"  {b.meta.id:<25} {score:<10.4f} {pf:<15} {verdict}")

    print()
    print("  Phantom analysis complete.")
    print()


if __name__ == "__main__":
    main()
