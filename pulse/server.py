"""
SynapticPulse — Real-Time Dashboard Server for SynapticBricks
Serves a live web UI showing brick health, pain, immune responses, and evolution.
"""
import sys, os, json, time, glob
sys.path.insert(0, r"C:\Users\MedoRadi\clawd")

from flask import Flask, render_template_string, jsonify, request
from synapticbricks.core import (
    BrickEngine, SensoryMonitor, initialize_aegis, PhantomEngine, AIHealer, BrickHealer, BrickTester
)

app = Flask(__name__)

# --- Globals: loaded on demand ---
VAULT_PATH = None
ENGINE = None
IMMUNE = None
MONITOR = None
MEMORY = None
PHANTOM = None
AI_HEALER = None  # Optional: requires API key

def load_engine(vault_path, gemini_api_key=None):
    global VAULT_PATH, ENGINE, IMMUNE, MONITOR, MEMORY, PHANTOM, AI_HEALER
    VAULT_PATH = vault_path
    ENGINE = BrickEngine(vault_path)
    IMMUNE, MONITOR, MEMORY = initialize_aegis(ENGINE)
    MONITOR.set_mode("light")
    PHANTOM = PhantomEngine(sensory=MONITOR, genetic=MEMORY)
    
    # Optional: Initialize AIHealer if API key provided
    if gemini_api_key:
        tester = BrickTester(ENGINE)
        healer = BrickHealer(ENGINE, tester)
        AI_HEALER = AIHealer(gemini_api_key, engine=ENGINE, healer=healer)

# ═══════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════

@app.route("/api/health")
def api_health():
    if not ENGINE:
        return jsonify({"status": "no_engine", "message": "No project loaded"})
    report = ENGINE.health_report()
    report["vault_path"] = VAULT_PATH
    report["monitor_mode"] = MONITOR.mode
    return jsonify(report)

@app.route("/api/bricks")
def api_bricks():
    if not ENGINE:
        return jsonify([])
    return jsonify(ENGINE.list_bricks())

@app.route("/api/sensory")
def api_sensory():
    if not MONITOR:
        return jsonify({})
    # Return last 20 events per brick
    trimmed = {}
    for brick_id, logs in MONITOR.logs.items():
        trimmed[brick_id] = logs[-20:]
    return jsonify(trimmed)

@app.route("/api/genetic")
def api_genetic():
    if not MEMORY:
        return jsonify({})
    # Return lineage summary (no full source code to keep payload small)
    summary = {}
    for brick_id, data in MEMORY.memory.items():
        summary[brick_id] = {
            "active_version": data.get("active_version"),
            "lineage": [{
                "version": v["version"],
                "ts": v["ts"],
                "reason": v["reason"],
                "status": v["status"],
                "genetic_score": v["genetic_score"],
                "dependencies": v.get("dependencies", [])
            } for v in data.get("lineage", [])]
        }
    return jsonify(summary)

@app.route("/api/immune/scan")
def api_immune_scan():
    if not IMMUNE:
        return jsonify({"threats": []})
    threats = IMMUNE.scan_for_threats()
    return jsonify({"threats": threats, "count": len(threats)})

@app.route("/api/phantom/<brick_id>")
def api_phantom(brick_id):
    if not ENGINE or not PHANTOM:
        return jsonify({"error": "No engine loaded"})
    brick = ENGINE.get(brick_id)
    if not brick:
        return jsonify({"error": f"Brick '{brick_id}' not found"})
    report = PHANTOM.analyze(brick)
    return jsonify({
        "brick_id": report.brick_id,
        "fragility_score": report.fragility_score,
        "total_cases": report.total_cases,
        "passed": report.passed,
        "failed": report.failed,
        "dangerous_patterns": report.dangerous_patterns,
        "recommendations": report.recommendations,
        "avg_duration_ms": report.avg_duration_ms
    })

@app.route("/api/codemap")
def api_codemap():
    if not ENGINE:
        return jsonify({"map": ""})
    return jsonify({"map": ENGINE.get_code_map()})

@app.route("/api/healing/stats")
def api_healing_stats():
    """Get AIHealer statistics (if enabled)"""
    if not AI_HEALER:
        return jsonify({"enabled": False, "message": "AIHealer not initialized (no API key)"})
    
    stats = AI_HEALER.get_stats()
    stats["enabled"] = True
    return jsonify(stats)

@app.route("/api/healing/heal/<brick_id>", methods=["POST"])
def api_healing_heal(brick_id):
    """Trigger autonomous healing for a brick"""
    if not AI_HEALER:
        return jsonify({"success": False, "error": "AIHealer not initialized"})
    
    result = AI_HEALER.auto_heal(brick_id, apply=True)
    return jsonify(result)

# ═══════════════════════════════════════════════
# DASHBOARD HTML
# ═══════════════════════════════════════════════

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SynapticPulse</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  
  :root {
    --bg-primary: #0a0e17;
    --bg-secondary: #111827;
    --bg-card: rgba(17, 24, 39, 0.7);
    --bg-glass: rgba(255, 255, 255, 0.03);
    --border: rgba(255, 255, 255, 0.06);
    --text-primary: #e5e7eb;
    --text-secondary: #9ca3af;
    --text-muted: #6b7280;
    --accent-green: #10b981;
    --accent-green-glow: rgba(16, 185, 129, 0.15);
    --accent-red: #ef4444;
    --accent-red-glow: rgba(239, 68, 68, 0.15);
    --accent-amber: #f59e0b;
    --accent-amber-glow: rgba(245, 158, 11, 0.15);
    --accent-blue: #3b82f6;
    --accent-blue-glow: rgba(59, 130, 246, 0.15);
    --accent-purple: #8b5cf6;
    --accent-purple-glow: rgba(139, 92, 246, 0.15);
    --accent-cyan: #06b6d4;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }
  
  body {
    font-family: 'Inter', sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Animated background */
  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: 
      radial-gradient(ellipse at 20% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, rgba(59, 130, 246, 0.04) 0%, transparent 50%),
      radial-gradient(ellipse at 50% 80%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
  }

  .container { max-width: 1400px; margin: 0 auto; padding: 20px; position: relative; z-index: 1; }

  /* Header */
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 0 30px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
  }
  .header h1 {
    font-size: 28px; font-weight: 700;
    background: linear-gradient(135deg, var(--accent-green), var(--accent-cyan));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
  }
  .header .subtitle { color: var(--text-muted); font-size: 13px; margin-top: 4px; }
  .header .status-badge {
    display: flex; align-items: center; gap: 8px;
    background: var(--bg-glass); border: 1px solid var(--border);
    padding: 8px 16px; border-radius: 100px; font-size: 13px;
  }
  .pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--accent-green);
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(16,185,129,0); }
  }

  /* Stats row */
  .stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
  .stat-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
  }
  .stat-card:hover { border-color: rgba(255,255,255,0.12); transform: translateY(-2px); }
  .stat-card .label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-card .value { font-size: 32px; font-weight: 700; margin-top: 8px; font-family: 'JetBrains Mono', monospace; }
  .stat-card .sub { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
  .stat-card.green .value { color: var(--accent-green); }
  .stat-card.red .value { color: var(--accent-red); }
  .stat-card.blue .value { color: var(--accent-blue); }
  .stat-card.purple .value { color: var(--accent-purple); }

  /* Grid layout */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 24px; }

  /* Cards */
  .card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
    backdrop-filter: blur(10px);
  }
  .card h2 {
    font-size: 14px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.5px; color: var(--text-secondary); margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
  }
  .card h2 .icon { font-size: 16px; }

  /* Brick list */
  .brick-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; border-radius: 8px;
    background: var(--bg-glass); border: 1px solid var(--border);
    margin-bottom: 8px;
    transition: all 0.2s ease;
    cursor: pointer;
  }
  .brick-item:hover { border-color: rgba(255,255,255,0.12); background: rgba(255,255,255,0.05); }
  .brick-item .name { font-weight: 500; font-size: 14px; }
  .brick-item .meta { font-size: 12px; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }
  .brick-item .badge {
    font-size: 11px; padding: 3px 10px; border-radius: 100px;
    font-weight: 500;
  }
  .badge.healthy { background: var(--accent-green-glow); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.2); }
  .badge.broken { background: var(--accent-red-glow); color: var(--accent-red); border: 1px solid rgba(239,68,68,0.2); }
  .badge.fragile { background: var(--accent-amber-glow); color: var(--accent-amber); border: 1px solid rgba(245,158,11,0.2); }

  /* Threat list */
  .threat-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 8px;
    margin-bottom: 8px;
    border-left: 3px solid var(--accent-red);
    background: var(--accent-red-glow);
  }
  .threat-item.high { border-left-color: var(--accent-amber); background: var(--accent-amber-glow); }
  .threat-item .threat-text { font-size: 13px; }
  .threat-item .threat-brick { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted); }

  .no-threats {
    text-align: center; padding: 30px; color: var(--text-muted);
    font-size: 14px;
  }

  /* Latency chart (CSS bars) */
  .latency-chart { display: flex; flex-direction: column; gap: 8px; }
  .latency-row { display: flex; align-items: center; gap: 12px; }
  .latency-row .label { width: 140px; font-size: 12px; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .latency-row .bar-bg { flex: 1; height: 22px; background: var(--bg-glass); border-radius: 4px; overflow: hidden; position: relative; }
  .latency-row .bar {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    transition: width 0.6s ease;
    display: flex; align-items: center; justify-content: flex-end; padding-right: 8px;
    font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--bg-primary);
    font-weight: 600; min-width: 40px;
  }
  .latency-row .bar.warn { background: linear-gradient(90deg, var(--accent-amber), #f97316); }
  .latency-row .bar.danger { background: linear-gradient(90deg, var(--accent-red), #dc2626); }

  /* Evolution timeline */
  .evo-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid var(--border);
  }
  .evo-item:last-child { border-bottom: none; }
  .evo-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--accent-purple); margin-top: 4px; flex-shrink: 0;
    box-shadow: 0 0 8px var(--accent-purple-glow);
  }
  .evo-dot.healthy { background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green-glow); }
  .evo-dot.fragile { background: var(--accent-amber); box-shadow: 0 0 8px var(--accent-amber-glow); }
  .evo-version { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 500; }
  .evo-reason { font-size: 12px; color: var(--text-muted); }
  .evo-score { font-size: 12px; color: var(--accent-cyan); font-family: 'JetBrains Mono', monospace; }

  /* Phantom modal */
  .modal-overlay {
    display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.7); z-index: 100;
    justify-content: center; align-items: center;
    backdrop-filter: blur(4px);
  }
  .modal-overlay.show { display: flex; }
  .modal {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 16px; padding: 32px; max-width: 600px; width: 90%;
    max-height: 80vh; overflow-y: auto;
  }
  .modal h2 { font-size: 18px; margin-bottom: 20px; color: var(--text-primary); text-transform: none; }
  .modal .close-btn {
    float: right; background: none; border: none; color: var(--text-muted);
    font-size: 20px; cursor: pointer;
  }

  /* Fragility gauge */
  .gauge-container { text-align: center; margin: 20px 0; }
  .gauge-value { font-size: 48px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
  .gauge-label { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
  .gauge-bar { width: 100%; height: 8px; background: var(--bg-glass); border-radius: 4px; margin-top: 12px; overflow: hidden; }
  .gauge-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }

  /* Refresh button */
  .refresh-btn {
    background: var(--bg-glass); border: 1px solid var(--border);
    color: var(--text-secondary); padding: 8px 16px; border-radius: 8px;
    cursor: pointer; font-size: 13px; font-family: 'Inter', sans-serif;
    transition: all 0.2s ease;
  }
  .refresh-btn:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }

  .empty-state { text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px; }

  /* Responsive */
  @media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <div>
      <h1>SynapticPulse</h1>
      <div class="subtitle">Real-time nervous system monitor for SynapticBricks</div>
    </div>
    <div style="display:flex;gap:12px;align-items:center">
      <button class="refresh-btn" onclick="refreshAll()">Refresh</button>
      <div class="status-badge">
        <div class="pulse-dot"></div>
        <span id="status-text">Connecting...</span>
      </div>
    </div>
  </div>

  <!-- Stats Row -->
  <div class="stats-row">
    <div class="stat-card green">
      <div class="label">Total Bricks</div>
      <div class="value" id="stat-total">-</div>
      <div class="sub" id="stat-total-sub"></div>
    </div>
    <div class="stat-card blue">
      <div class="label">Healthy</div>
      <div class="value" id="stat-healthy">-</div>
      <div class="sub" id="stat-healthy-sub"></div>
    </div>
    <div class="stat-card red">
      <div class="label">Active Threats</div>
      <div class="value" id="stat-threats">-</div>
      <div class="sub" id="stat-threats-sub"></div>
    </div>
    <div class="stat-card purple">
      <div class="label">Total Fixes</div>
      <div class="value" id="stat-fixes">-</div>
      <div class="sub" id="stat-fixes-sub"></div>
    </div>
  </div>

  <!-- Main Grid -->
  <div class="grid-2">
    <!-- Brick Registry -->
    <div class="card">
      <h2><span class="icon">&#x1F9F1;</span> Brick Registry</h2>
      <div id="brick-list"><div class="empty-state">Loading...</div></div>
    </div>

    <!-- Immune System -->
    <div class="card">
      <h2><span class="icon">&#x1F6E1;</span> Immune System</h2>
      <div id="threat-list"><div class="empty-state">Scanning...</div></div>
    </div>
  </div>

  <div class="grid-2">
    <!-- Latency Monitor -->
    <div class="card">
      <h2><span class="icon">&#x1F4C8;</span> Latency Monitor (Nervous System)</h2>
      <div id="latency-chart" class="latency-chart"><div class="empty-state">No sensory data yet</div></div>
    </div>

    <!-- Genetic Evolution -->
    <div class="card">
      <h2><span class="icon">&#x1F9EC;</span> Genetic Evolution Timeline</h2>
      <div id="evo-timeline"><div class="empty-state">No evolution history</div></div>
    </div>
  </div>
</div>

<!-- Phantom Modal -->
<div class="modal-overlay" id="phantom-modal">
  <div class="modal">
    <button class="close-btn" onclick="closeModal()">&times;</button>
    <h2 id="modal-title">Phantom Analysis</h2>
    <div id="modal-content"></div>
  </div>
</div>

<script>
const API = '';

async function fetchJSON(url) {
  try {
    const res = await fetch(API + url);
    return await res.json();
  } catch(e) {
    console.error('Fetch error:', url, e);
    return null;
  }
}

async function refreshAll() {
  await Promise.all([loadHealth(), loadBricks(), loadThreats(), loadSensory(), loadGenetic()]);
}

async function loadHealth() {
  const data = await fetchJSON('/api/health');
  if (!data) { document.getElementById('status-text').textContent = 'Offline'; return; }
  
  document.getElementById('status-text').textContent = data.status === 'no_engine' ? 'No Project' : 'Online';
  document.getElementById('stat-total').textContent = data.total_bricks || 0;
  document.getElementById('stat-healthy').textContent = data.healthy || 0;
  document.getElementById('stat-fixes').textContent = data.total_fixes || 0;
  document.getElementById('stat-total-sub').textContent = `${data.broken || 0} broken`;
  document.getElementById('stat-healthy-sub').textContent = `${data.total_bricks ? Math.round((data.healthy/data.total_bricks)*100) : 0}% uptime`;
  document.getElementById('stat-fixes-sub').textContent = `${data.total_errors || 0} total errors`;
}

async function loadBricks() {
  const bricks = await fetchJSON('/api/bricks');
  const el = document.getElementById('brick-list');
  if (!bricks || bricks.length === 0) { el.innerHTML = '<div class="empty-state">No bricks registered</div>'; return; }
  
  el.innerHTML = bricks.map(b => `
    <div class="brick-item" onclick="runPhantom('${b.id}')">
      <div>
        <div class="name">${b.name}</div>
        <div class="meta">v${b.version} &middot; ${b.label_code || b.id} &middot; ${b.tests} tests</div>
      </div>
      <span class="badge ${b.status}">${b.status}</span>
    </div>
  `).join('');
}

async function loadThreats() {
  const data = await fetchJSON('/api/immune/scan');
  const el = document.getElementById('threat-list');
  if (!data || data.count === 0) {
    el.innerHTML = '<div class="no-threats">&#x2705; No threats detected. System is healthy.</div>';
    document.getElementById('stat-threats').textContent = '0';
    document.getElementById('stat-threats-sub').textContent = 'All clear';
    return;
  }
  
  document.getElementById('stat-threats').textContent = data.count;
  document.getElementById('stat-threats-sub').textContent = `${data.threats.filter(t=>t.severity==='CRITICAL').length} critical`;
  
  el.innerHTML = data.threats.map(t => `
    <div class="threat-item ${t.severity === 'HIGH' ? 'high' : ''}">
      <div>
        <div class="threat-text">[${t.severity}] ${t.type}: ${t.reason}</div>
        <div class="threat-brick">${t.brick_id}</div>
      </div>
    </div>
  `).join('');
}

async function loadSensory() {
  const data = await fetchJSON('/api/sensory');
  const el = document.getElementById('latency-chart');
  if (!data || Object.keys(data).length === 0) { el.innerHTML = '<div class="empty-state">No sensory data yet</div>'; return; }
  
  const entries = Object.entries(data).filter(([k]) => !k.startsWith('phantom:'));
  if (entries.length === 0) { el.innerHTML = '<div class="empty-state">No sensory data yet</div>'; return; }
  
  // Get avg latency per brick
  const avgs = entries.map(([id, logs]) => {
    const latencies = logs.map(l => l.latency_ms);
    const avg = latencies.reduce((a,b) => a+b, 0) / latencies.length;
    return { id, avg, last: latencies[latencies.length - 1] || 0, count: logs.length };
  }).sort((a,b) => b.avg - a.avg);
  
  const maxLatency = Math.max(...avgs.map(a => a.avg), 1);
  
  el.innerHTML = avgs.map(a => {
    const pct = Math.min(100, (a.avg / maxLatency) * 100);
    const cls = a.avg > 100 ? 'danger' : a.avg > 20 ? 'warn' : '';
    return `
      <div class="latency-row">
        <div class="label" title="${a.id}">${a.id}</div>
        <div class="bar-bg">
          <div class="bar ${cls}" style="width:${Math.max(pct, 8)}%">${a.avg.toFixed(1)}ms</div>
        </div>
      </div>
    `;
  }).join('');
}

async function loadGenetic() {
  const data = await fetchJSON('/api/genetic');
  const el = document.getElementById('evo-timeline');
  if (!data || Object.keys(data).length === 0) { el.innerHTML = '<div class="empty-state">No evolution history</div>'; return; }
  
  let items = [];
  for (const [brickId, info] of Object.entries(data)) {
    for (const v of (info.lineage || [])) {
      items.push({ ...v, brick_id: brickId });
    }
  }
  items.sort((a,b) => new Date(b.ts) - new Date(a.ts));
  items = items.slice(0, 15);
  
  if (items.length === 0) { el.innerHTML = '<div class="empty-state">No evolution history</div>'; return; }
  
  el.innerHTML = items.map(v => `
    <div class="evo-item">
      <div class="evo-dot ${v.status}"></div>
      <div style="flex:1">
        <div class="evo-version">${v.brick_id} v${v.version}</div>
        <div class="evo-reason">${v.reason}</div>
        <div class="evo-score">Score: ${v.genetic_score} &middot; Deps: ${(v.dependencies||[]).join(', ') || 'none'}</div>
      </div>
    </div>
  `).join('');
}

async function runPhantom(brickId) {
  const modal = document.getElementById('phantom-modal');
  const title = document.getElementById('modal-title');
  const content = document.getElementById('modal-content');
  
  title.textContent = `Phantom Analysis: ${brickId}`;
  content.innerHTML = '<div class="empty-state">Running ghost executions...</div>';
  modal.classList.add('show');
  
  const data = await fetchJSON(`/api/phantom/${brickId}`);
  if (!data || data.error) {
    content.innerHTML = `<div class="empty-state">${data?.error || 'Analysis failed'}</div>`;
    return;
  }
  
  const score = data.fragility_score;
  const label = score === 0 ? 'BULLETPROOF' : score < 0.2 ? 'ROBUST' : score < 0.5 ? 'MODERATE' : score < 0.8 ? 'FRAGILE' : 'CRITICAL';
  const color = score === 0 ? 'var(--accent-green)' : score < 0.3 ? 'var(--accent-green)' : score < 0.6 ? 'var(--accent-amber)' : 'var(--accent-red)';
  
  content.innerHTML = `
    <div class="gauge-container">
      <div class="gauge-value" style="color:${color}">${score.toFixed(4)}</div>
      <div class="gauge-label">${label}</div>
      <div class="gauge-bar">
        <div class="gauge-fill" style="width:${score*100}%;background:${color}"></div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:20px 0;text-align:center">
      <div><div style="font-size:24px;font-weight:700;color:var(--accent-green)">${data.passed}</div><div style="font-size:12px;color:var(--text-muted)">Passed</div></div>
      <div><div style="font-size:24px;font-weight:700;color:var(--accent-red)">${data.failed}</div><div style="font-size:12px;color:var(--text-muted)">Failed</div></div>
      <div><div style="font-size:24px;font-weight:700;color:var(--accent-blue)">${data.avg_duration_ms.toFixed(1)}ms</div><div style="font-size:12px;color:var(--text-muted)">Avg Duration</div></div>
    </div>
    ${data.dangerous_patterns.length > 0 ? `
      <h3 style="font-size:13px;color:var(--text-secondary);margin:16px 0 8px">Dangerous Patterns</h3>
      ${data.dangerous_patterns.map(p => `
        <div style="background:var(--bg-glass);padding:10px 14px;border-radius:8px;margin-bottom:6px;font-size:13px">
          <strong>${p.pattern}</strong> (${p.failure_count} failures)
        </div>
      `).join('')}
    ` : ''}
    ${data.recommendations.length > 0 ? `
      <h3 style="font-size:13px;color:var(--text-secondary);margin:16px 0 8px">Recommendations</h3>
      ${data.recommendations.map(r => `<div style="font-size:13px;color:var(--text-muted);margin-bottom:6px">• ${r}</div>`).join('')}
    ` : ''}
  `;
}

function closeModal() {
  document.getElementById('phantom-modal').classList.remove('show');
}

document.getElementById('phantom-modal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});

// Initial load + auto-refresh every 10s
refreshAll();
setInterval(refreshAll, 10000);
</script>
</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


# ═══════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════

def main():
    """CLI entry point for synaptic-pulse command."""
    import argparse
    parser = argparse.ArgumentParser(description="SynapticPulse Dashboard")
    parser.add_argument("--vault", default=None, help="Path to project vault")
    parser.add_argument("--port", type=int, default=7700, help="Server port")
    parser.add_argument("--demo", action="store_true", help="Load NeuralGuard demo data")
    parser.add_argument("--gemini-key", default=None, help="Gemini API key for AIHealer (optional)")
    args = parser.parse_args()

    # Check for API key in environment if not provided
    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY")

    if args.demo:
        vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\pulse_demo"
        os.makedirs(vault, exist_ok=True)
        load_engine(vault, gemini_api_key=gemini_key)
        
        sys.path.insert(0, r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard")
        import bricks as ng
        ENGINE.register_many([ng.source_parser, ng.complexity_analyzer,
                              ng.antipattern_detector, ng.quality_scorer,
                              ng.report_generator])
        
        from synapticbricks.core import Pipeline
        pipe = Pipeline("NeuralGuard", ENGINE)
        pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
        pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
        pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
        pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
        pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                      "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

        sample = 'def hello(name: str) -> str:\n    """Greet someone."""\n    return f"Hello {name}"\n'
        for _ in range(5):
            pipe.run({"code": sample})
        
        MEMORY.record_evolution("source_parser", ng.source_parser.source, "1.0.0", "initial", score=1.0)
        MEMORY.record_evolution("antipattern_detector", ng.antipattern_detector.source, "1.0.0", "initial", score=0.95)
        
        print(f"Demo loaded: 5 bricks, sensory data, genetic history")
    elif args.vault:
        load_engine(args.vault, gemini_api_key=gemini_key)
    else:
        print("No vault specified. Use --demo for demo mode or --vault <path>")

    print(f"\n{'='*50}")
    print(f"  SynapticPulse Dashboard")
    print(f"  http://localhost:{args.port}")
    if AI_HEALER:
        print(f"  AIHealer: ENABLED ✅")
    else:
        print(f"  AIHealer: disabled (no API key)")
    print(f"{'='*50}\n")
    
    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SynapticPulse Dashboard")
    parser.add_argument("--vault", default=None, help="Path to project vault")
    parser.add_argument("--port", type=int, default=7700, help="Server port")
    parser.add_argument("--demo", action="store_true", help="Load NeuralGuard demo data")
    parser.add_argument("--gemini-key", default=None, help="Gemini API key for AIHealer (optional)")
    args = parser.parse_args()

    gemini_key = args.gemini_key or os.environ.get("GEMINI_API_KEY")

    if args.demo:
        # Load NeuralGuard as demo project
        vault = r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard\vault\pulse_demo"
        os.makedirs(vault, exist_ok=True)
        load_engine(vault, gemini_api_key=gemini_key)
        
        # Register NeuralGuard bricks
        sys.path.insert(0, r"C:\Users\MedoRadi\clawd\synapticbricks\projects\neuralguard")
        import bricks as ng
        ENGINE.register_many([ng.source_parser, ng.complexity_analyzer,
                              ng.antipattern_detector, ng.quality_scorer,
                              ng.report_generator])
        
        # Run a few cycles to generate sensory data
        from synapticbricks.core import Pipeline
        pipe = Pipeline("NeuralGuard", ENGINE)
        pipe.add_step("source_parser", input_map={"code": "code"}, output_key="parsed")
        pipe.add_step("complexity_analyzer", input_map={"parsed": "parsed"}, output_key="complexity")
        pipe.add_step("antipattern_detector", input_map={"code": "code"}, output_key="antipatterns")
        pipe.add_step("quality_scorer", input_map={"complexity": "complexity", "antipatterns": "antipatterns"}, output_key="quality")
        pipe.add_step("report_generator", input_map={"parsed": "parsed", "complexity": "complexity",
                      "antipatterns": "antipatterns", "quality": "quality"}, output_key="report")

        sample = 'def hello(name: str) -> str:\n    """Greet someone."""\n    return f"Hello {name}"\n'
        for _ in range(5):
            pipe.run({"code": sample})
        
        # Record some genetic evolution for demo
        MEMORY.record_evolution("source_parser", ng.source_parser.source, "1.0.0", "initial", score=1.0)
        MEMORY.record_evolution("antipattern_detector", ng.antipattern_detector.source, "1.0.0", "initial", score=0.95)
        
        print(f"Demo loaded: 5 bricks, sensory data, genetic history")
    elif args.vault:
        load_engine(args.vault, gemini_api_key=gemini_key)
    else:
        print("No vault specified. Use --demo for demo mode or --vault <path>")
        print("Starting with empty engine...")

    print(f"\n{'='*50}")
    print(f"  SynapticPulse Dashboard")
    print(f"  http://localhost:{args.port}")
    if AI_HEALER:
        print(f"  AIHealer: ENABLED ✅")
    else:
        print(f"  AIHealer: disabled (no API key)")
    print(f"{'='*50}\n")
    
    app.run(host="0.0.0.0", port=args.port, debug=False)
