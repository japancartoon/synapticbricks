import json
import os
from typing import List, Dict, Any
from synapticbricks.core import brick, sensory

@brick("intent_scanner", description="Translates high-level human intent into a blueprint of digital organs (bricks)")
def intent_scanner(intent_text: str) -> Dict[str, Any]:
    """
    Analyzes human intent and returns a 'Genome Blueprint'.
    In a full system, this would call a high-reasoning LLM (Opus).
    For the bootstrap, we use a semantic pattern matcher.
    """
    blueprint = {
        "intent": intent_text,
        "required_organs": [],
        "complexity_score": 0.0
    }
    
    # Semantic mapping of keywords to 'Living Organs'
    organs_map = {
        "monitor": {"id": "watcher", "type": "io_net", "desc": "Continuous data acquisition"},
        "sentiment": {"id": "analyzer", "type": "math_logic", "desc": "Semantic emotional weight analysis"},
        "notify": {"id": "messenger", "type": "io_net", "desc": "External alert dispatch"},
        "scrape": {"id": "extractor", "type": "parse", "desc": "Unstructured data conversion"},
        "bankrupt": {"id": "risk_engine", "type": "math", "desc": "Financial failure prediction"}
    }
    
    intent_lower = intent_text.lower()
    for keyword, organ in organs_map.items():
        if keyword in intent_lower:
            blueprint["required_organs"].append(organ)
            blueprint["complexity_score"] += 0.2
            
    return blueprint

@brick("genome_sequencer", description="Converts a blueprint into a functional pipeline of synaptic bricks")
def genome_sequencer(blueprint: Dict[str, Any]) -> str:
    """
    Takes a blueprint and 'sequences' the code. 
    Generates ADVANCED DNA including sensory monitoring and contracts.
    """
    dna_id = f"dna_{hash(blueprint['intent']) % 10000}"
    dna_path = f"C:\\Users\\MedoRadi\\clawd\\synapticbricks\\architect\\dna\\{dna_id}.py"
    
    # Advanced Genetic Code Generation
    code = [
        "import time",
        "import random",
        "from typing import Any, Dict, List",
        "from synapticbricks.core import brick, sensory, Pipeline",
        f"# DNA Genome for intent: {blueprint['intent']}",
        "# This DNA is sensory-aware and follows the Synaptic nervous system protocol.",
        ""
    ]
    
    for organ in blueprint["required_organs"]:
        # Generate more 'real' logic based on type
        logic = "    return {'processed': True, 'input': data}"
        if "analyzer" in organ['id']:
            logic = "    time.sleep(random.uniform(0.01, 0.05))\n    score = len(str(data)) % 10 / 10.0\n    return {'sentiment_score': score, 'status': 'analyzed'}"
        elif "watcher" in organ['id']:
            logic = "    return {'raw_stream': str(data), 'timestamp': time.time()}"
        elif "messenger" in organ['id']:
            logic = f"    print(f'Sending alert: {{data}}')\n    return {{'delivered': True, 'organ': '{organ['id']}'}}"

        code.extend([
            f"@brick('{organ['id']}', description='{organ['desc']}')",
            "@sensory(monitor)",
            f"def {organ['id']}(data: Any) -> dict:",
            "    \"\"\"Autonomously generated living organ.\"\"\"",
            logic,
            ""
        ])
    
    # Cellular Growth Logic
    code.extend([
        "def build_organism(engine, monitor):",
        f"    \"\"\"Assembles the sequenced bricks into a functional pipeline.\"\"\"",
        f"    pipeline = Pipeline('organism_{dna_id}', engine)",
    ])
    
    for i, organ in enumerate(blueprint["required_organs"]):
        input_map = "{'data': 'raw_input'}" if i == 0 else "{'data': 'last_output'}"
        code.append(f"    pipeline.add_step('{organ['id']}', input_map={input_map}, output_key='last_output')")
        
    code.append("    return pipeline")
        
    with open(dna_path, "w") as f:
        f.write("\n".join(code))
        
    return dna_path
