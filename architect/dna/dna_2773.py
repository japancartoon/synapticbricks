import time
from typing import Any, Dict, List
from synapticbricks.core import brick, sensory, Pipeline
# DNA Genome for intent: Monitor stock prices and notify me if they crash
# This DNA is sensory-aware and follows the Synaptic nervous system protocol.

@brick('watcher', description='Continuous data acquisition')
def watcher(data: Any) -> dict:
    """Autonomously generated living organ."""
    return {'raw_stream': str(data), 'timestamp': time.time()}

@brick('messenger', description='External alert dispatch')
def messenger(data: Any) -> dict:
    """Autonomously generated living organ."""
    print(f'Sending alert: {data}')
    return {'delivered': True, 'organ': 'messenger'}

def build_organism(engine, monitor=None):
    """Assembles the sequenced bricks into a functional pipeline."""
    pipeline = Pipeline('organism_dna_2773', engine)
    pipeline.add_step('watcher', input_map={'data': 'raw_input'}, output_key='last_output')
    pipeline.add_step('messenger', input_map={'data': 'last_output'}, output_key='last_output')
    return pipeline