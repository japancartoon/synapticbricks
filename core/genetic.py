import json
import os
import re
import hashlib
from datetime import datetime

class GeneticMemory:
    def __init__(self, data_path="C:\\Users\\MedoRadi\\clawd\\synapticbricks\\data\\genetic_memory.json"):
        self.data_path = data_path
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_memory(self):
        with open(self.data_path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def _extract_imports(self, source_code):
        """Extract import names from source code for dependency manifest."""
        imports = set()
        for line in source_code.split("\n"):
            line = line.strip()
            # "import foo" or "import foo.bar"
            m = re.match(r'^import\s+([\w.]+)', line)
            if m:
                imports.add(m.group(1).split('.')[0])
            # "from foo import bar"
            m = re.match(r'^from\s+([\w.]+)\s+import', line)
            if m:
                imports.add(m.group(1).split('.')[0])
        # Remove builtins
        builtins = {'os', 'sys', 'time', 'json', 'math', 'random', 'hashlib',
                     'datetime', 'collections', 'functools', 'typing', 'copy',
                     'inspect', 're', 'io', 'pathlib', 'dataclasses', 'abc',
                     'itertools', 'enum', 'traceback', 'contextlib', 'textwrap'}
        return list(imports - builtins)

    def check_dependencies(self, deps_list):
        """Check if all dependencies in a list are importable. Returns (ok, missing)."""
        missing = []
        for dep in deps_list:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        return len(missing) == 0, missing

    def record_evolution(self, brick_id, source_code, version, reason, status="healthy", score=1.0):
        dna_hash = hashlib.sha256(source_code.encode()).hexdigest()
        deps = self._extract_imports(source_code)
        
        if brick_id not in self.memory:
            self.memory[brick_id] = {
                "lineage": [],
                "active_version": None,
                "dna_hash": None
            }
        
        evolution_step = {
            "version": version,
            "ts": datetime.now().isoformat(),
            "reason": reason,
            "dna_hash": dna_hash,
            "status": status,
            "genetic_score": score,
            "source": source_code,
            "dependencies": deps
        }
        
        # Check if we're actually changing DNA
        if self.memory[brick_id]["dna_hash"] != dna_hash or version != self.memory[brick_id]["active_version"]:
            self.memory[brick_id]["lineage"].append(evolution_step)
            self.memory[brick_id]["active_version"] = version
            self.memory[brick_id]["dna_hash"] = dna_hash
            self._save_memory()
            return True, f"Evolution recorded: {version}"
        
        return False, "DNA unchanged"

    def get_best_version(self, brick_id, min_score_diff=0.0):
        if brick_id not in self.memory or not self.memory[brick_id]["lineage"]:
            return None
        
        # Find healthy version with highest score
        lineage = self.memory[brick_id]["lineage"]
        healthy_versions = [v for v in lineage if v["status"] == "healthy"]
        
        if not healthy_versions:
            return None
            
        best = max(healthy_versions, key=lambda x: x["genetic_score"])
        return best

    def update_score(self, brick_id, version, delta):
        if brick_id in self.memory:
            for v in self.memory[brick_id]["lineage"]:
                if v["version"] == version:
                    v["genetic_score"] = round(max(0, min(2.0, v["genetic_score"] + delta)), 2)
                    self._save_memory()
                    return True
        return False
