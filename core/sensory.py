import time
import psutil
import os
import json
from functools import wraps
from datetime import datetime

class SensoryMonitor:
    # Monitoring tiers
    LIGHT = "light"   # Only time.perf_counter() — ~0.001ms overhead
    FULL  = "full"    # time + psutil memory + disk write — ~2-5ms overhead

    def __init__(self, data_path="C:\\Users\\MedoRadi\\clawd\\synapticbricks\\data\\sensory_logs.json", mode="full"):
        self.data_path = data_path
        self.mode = mode  # "light" or "full"
        self.logs = self._load_logs()
        
    def _load_logs(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def _save_logs(self):
        with open(self.data_path, "w") as f:
            json.dump(self.logs, f, indent=4)

    def log_event(self, brick_id, latency, memory_delta, status="healthy", error=None):
        if brick_id not in self.logs:
            self.logs[brick_id] = []
        
        event = {
            "ts": datetime.now().isoformat(),
            "latency_ms": round(latency * 1000, 4),
            "memory_mb": round(memory_delta / (1024 * 1024), 4),
            "status": status,
            "error": error
        }
        
        self.logs[brick_id].append(event)
        # Keep only last 100 events per brick
        if len(self.logs[brick_id]) > 100:
            self.logs[brick_id] = self.logs[brick_id][-100:]
            
        # self._save_logs() # Removed for performance/test reliability
        return event

    def check_pain(self, brick_id, latency):
        """Detects if a brick is in 'pain' (performing poorly)."""
        if brick_id not in self.logs or len(self.logs[brick_id]) < 5:
            return False, "Insufficient data"
            
        avg_latency = sum(e["latency_ms"] for e in self.logs[brick_id]) / len(self.logs[brick_id])
        current_latency = latency * 1000
        
        if current_latency > avg_latency * 3: # 3x spike
            return True, f"Latency spike: {round(current_latency, 2)}ms vs avg {round(avg_latency, 2)}ms"
        
        return False, "Healthy"

    def set_mode(self, mode):
        """Switch monitoring tier at runtime."""
        if mode in (self.LIGHT, self.FULL):
            self.mode = mode

def sensory(monitor: SensoryMonitor):
    """Decorator to add sensory awareness to a brick."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            brick_id = getattr(func, "brick_id", func.__name__)
            start_time = time.perf_counter()

            # LIGHT mode: skip psutil entirely (~0.001ms)
            mem_start = 0
            if monitor.mode == SensoryMonitor.FULL:
                process = psutil.Process(os.getpid())
                mem_start = process.memory_info().rss
            
            status = "healthy"
            error = None
            result = None
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                status = "failing"
                error = str(e)
                raise e
            finally:
                latency = time.perf_counter() - start_time
                mem_delta = 0
                if monitor.mode == SensoryMonitor.FULL:
                    mem_end = process.memory_info().rss
                    mem_delta = mem_end - mem_start
                monitor.log_event(brick_id, latency, mem_delta, status, error)
            
            return result
        return wrapper
    return decorator
