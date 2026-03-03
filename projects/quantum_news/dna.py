import time
import random
from typing import Any, Dict, List
from synapticbricks.core import brick, sensory, Pipeline

# Global monitor placeholder
class MonitorContainer:
    instance = None

@brick("news_watcher", description="Fetches latest headlines from a news source")
def news_watcher(url: str) -> List[str]:
    # Simulate network variation
    if random.random() < 0.2: time.sleep(0.1) 
    return ["AI growth", "Market shift", "Quantum leap", "Stable stock"]

@brick("sentiment_core", description="Analyzes text sentiment")
def sentiment_core(text_list: List[str]) -> Dict[str, float]:
    scores = [(len(t) % 10) / 10.0 for t in text_list]
    return {"avg_sentiment": sum(scores) / len(scores), "count": len(text_list)}

@brick("decision_matrix", description="Decides on alerts")
def decision_matrix(analysis: Dict[str, Any]) -> str:
    score = analysis.get("avg_sentiment", 0.0)
    return "ALERT: POSITIVE" if score > 0.5 else "STATUS: NEUTRAL"
