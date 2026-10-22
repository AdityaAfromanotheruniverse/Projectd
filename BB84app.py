import json
import random

import pandas as pd
import streamlit as st

# Requires Streamlit >= 1.40 (multipage navigation with st.navigation / st.Page).
st.set_page_config(
    page_title="BB84 Quantum Key Distribution Simulator",
    layout="wide",
)

# Dictionary to map states to arrows for the logs
ARROW_MAP = {
    ('+', 0): "→",
    ('+', 1): "↑",
    ('X', 0): "↖",
    ('X', 1): "↗"
}

# ---------------------------------------------------------------------------------------
# Glossary: single source of truth for hover definitions (used by the simulator canvas/table
# via JavaScript, and by the article page via CSS tooltips).
# ---------------------------------------------------------------------------------------
GLOSSARY = {
    "alice": {
        "title": "Alice (sender)",
        "text": "The party who prepares and sends the photons. For each photon she randomly chooses "
                "a bit (0 or 1) and a basis, and encodes the bit in the photon's polarization.",
    },
    "bob": {
        "title": "Bob (receiver)",
        "text": "The party who measures each incoming photon in a randomly chosen basis. When his "
                "basis matches Alice's he reads her bit correctly; otherwise his result is a coin flip.",
    },
    "eve": {
        "title": "Eve (eavesdropper)",
        "text": "An attacker tapping the quantum channel. Here she uses an intercept-resend attack: "
                "she measures each photon in a random basis and sends a replacement on to Bob. "
                "Whenever she guesses the basis wrong she disturbs the photon, and that disturbance "
                "later shows up as errors.",
    },
    "photon": {
        "title": "Photon",
        "text": "A single particle of light. Here each photon carries one qubit in its polarization. "
                "Quantum mechanics forbids making a perfect copy of an unknown photon state, so Eve "
                "cannot simply duplicate it and measure the copy.",
    },
    "qubit": {
        "title": "Qubit (quantum bit)",
        "text": "The quantum version of a bit. Besides 0 and 1 it can exist in superpositions, and "
                "measuring it forces a definite 0 or 1 and destroys the original state. In BB84 each "
                "photon's polarization is a qubit.",
    },
    "polarization": {
        "title": "Polarization (the arrows)",
        "text": "The direction in which a photon's light wave oscillates, drawn here as an arrow. "
                "In the + basis: → means bit 0 and ↑ means bit 1. In the X basis: ↖ means bit 0 "
                "and ↗ means bit 1.",
    },
    "basis": {
        "title": "Basis",
        "text": "The angle at which a polarization is prepared or measured: rectilinear (+) or "
                "diagonal (X). Measuring in the matching basis returns the exact bit; measuring in "
                "the other basis gives a random result.",
    },
    "bit": {
        "title": "Bit",
        "text": "A classical binary digit, 0 or 1. This is the raw information Alice wants to share "
                "with Bob.",
    },
    "channel": {
        "title": "Quantum channel",
        "text": "The physical path the photons travel along, such as an optical fibre or free space. "
                "It is assumed that an eavesdropper may tap it. Real systems also use a separate public "
                "classical channel so Alice and Bob can compare bases.",
    },
    "sifting": {
        "title": "Sifting",
        "text": "After transmission, Alice and Bob publicly compare which bases they used (never the "
                "bit values) and discard every photon where the bases differ. On average about half "
                "of the photons survive.",
    },
    "sifted_key": {
        "title": "Sifted key",
        "text": "The bits left after sifting. If nobody interfered, Alice's and Bob's sifted keys are "
                "identical and can become a shared secret key.",
    },
    "qber": {
        "title": "QBER (quantum bit error rate)",
        "text": "The fraction of sifted bits where Alice and Bob disagree. Ordinary noise gives a small "
                "QBER; a full intercept-resend attack pushes it toward 25%.",
    },
    "threshold": {
        "title": "Abort threshold",
        "text": "If the QBER rises above this limit the key is thrown away. Around 11% is the commonly "
                "quoted security bound for BB84; above it a secure key can no longer be guaranteed.",
    },
    "outcome": {
        "title": "Outcome",
        "text": "What happened to each photon after sifting: Match, Mismatch, or Discarded.",
    },
    "match": {
        "title": "Match",
        "text": "Alice and Bob used the same basis and obtained the same bit. This bit joins the sifted key.",
    },
    "mismatch": {
        "title": "Mismatch",
        "text": "Same basis, but different bits. With perfect equipment and no eavesdropper this never "
                "happens, so it signals noise or an interception.",
    },
    "discarded": {
        "title": "Discarded",
        "text": "Alice and Bob used different bases, so Bob's result carries no reliable information. "
                "The photon is dropped during sifting.",
    },
    "no_cloning": {
        "title": "No-cloning theorem",
        "text": "A law of quantum mechanics: an unknown quantum state cannot be copied perfectly. It "
                "stops an eavesdropper from keeping a copy of each photon.",
    },
}


def T(key, label=None):
    """Inline term with a CSS hover definition (for markdown content on the article page)."""
    g = GLOSSARY[key]
    label = label or g["title"].split(" (")[0]
    return (f'<span class="term">{label}<span class="tip"><span class="tip-t">{g["title"]}</span>'
            f'{g["text"]}</span></span>')


# ---------------------------------------------------------------------------------------
# Global look and feel
# ---------------------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
.stApp, [data-testid="stAppViewContainer"] { background:#0b1220; }
[data-testid="stHeader"] { background:rgba(11,18,32,.92); }
[data-testid="stSidebar"] { background:#0d1527; border-right:1px solid #1e293b; }
.stApp h1 { font-size:1.85rem; font-weight:650; letter-spacing:-.01em; color:#f1f5f9; padding-top:.2rem; }
.stApp h2, .stApp h3, .stApp h4 { color:#f1f5f9; font-weight:600; letter-spacing:-.005em; }
.stApp p, .stApp li, .stApp label { color:#b6c2d4; }
.stApp [data-testid="stCaptionContainer"] { color:#8091a7; }
.stApp [data-testid="stSidebar"] h2, .stApp [data-testid="stSidebar"] h3 { font-size:1.05rem; }

.stApp button[kind="primary"], .stApp [data-testid="stBaseButton-primary"] {
    background:#2563eb; border:1px solid #2563eb; color:#fff; border-radius:6px; font-weight:500;
}
.stApp button[kind="primary"]:hover, .stApp [data-testid="stBaseButton-primary"]:hover {
    background:#1d4ed8; border-color:#1d4ed8;
}
.stApp button[kind="primary"] p, .stApp [data-testid="stBaseButton-primary"] p { color:#fff; }

.chips { display:flex; flex-wrap:wrap; gap:8px; margin:.1rem 0 .6rem; }
.chip { background:#111a2e; border:1px solid #1e293b; border-radius:6px; padding:6px 12px;
        font-size:.8rem; color:#94a3b8; }
.chip b { color:#e2e8f0; font-weight:600; margin-left:6px; }

/* Hover definitions for terms used in page content (the simulator iframe has its own) */
.term { border-bottom:1px dotted #64748b; cursor:help; position:relative; color:inherit; }
.term .tip { visibility:hidden; opacity:0; position:absolute; z-index:99999;
    bottom:calc(100% + 8px); left:50%; transform:translateX(-50%); width:290px;
    background:#0b1220; border:1px solid #334155; border-radius:8px; padding:10px 12px;
    font-size:.78rem; line-height:1.5; font-weight:400; color:#cbd5e1; text-align:left;
    box-shadow:0 10px 30px rgba(0,0,0,.5); transition:opacity .12s; pointer-events:none; }
.term:hover .tip { visibility:visible; opacity:1; }
.tip-t { display:block; font-weight:600; color:#f1f5f9; margin-bottom:3px; font-size:.84rem; }

.raw-wrap { overflow-x:auto; border:1px solid #1e293b; border-radius:8px; }
.raw-table { width:100%; border-collapse:collapse; font-size:.82rem; }
.raw-table th, .raw-table td { text-align:left !important; padding:7px 12px; border-bottom:1px solid #1e293b; }
.raw-table th { background:#111a2e; color:#94a3b8; font-weight:600; }
.raw-table td { color:#cbd5e1; }

.article-note { background:#111a2e; border:1px solid #1e293b; border-left:3px solid #38bdf8;
    border-radius:6px; padding:12px 16px; color:#b6c2d4; font-size:.92rem; }
</style>
"""

# Keep sidebar widget values when the user switches pages and comes back.
for _k in ("num_photons", "speed", "threshold_pct", "enable_eve"):
    if _k in st.session_state:
        st.session_state[_k] = st.session_state[_k]


def generate_photon_stream(num_photons, enable_eve):
    """Roll fresh random Alice/Eve/Bob bits+bases for a new run."""
    history_data = []
    js_photon_array = []

    for i in range(num_photons):
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_arrow = ARROW_MAP[(a_base, a_bit)]

        current_bit = a_bit
        current_base = a_base

        e_base_log, e_arrow_log, e_bit_log = "—", "—", "—"

        if enable_eve:
            eve_base = random.choice(['+', 'X'])
            eve_bit = a_bit if eve_base == a_base else random.randint(0, 1)
            eve_arrow = ARROW_MAP[(eve_base, eve_bit)]
            current_bit = eve_bit
            current_base = eve_base
            e_base_log, e_arrow_log, e_bit_log = eve_base, eve_arrow, eve_bit

        b_base = random.choice(['+', 'X'])
        b_bit = current_bit if current_base == b_base else random.randint(0, 1)
        b_arrow = ARROW_MAP[(b_base, b_bit)]

        is_sifted = (a_base == b_base)
        outcome = "Discarded"
        if is_sifted:
            outcome = "Match" if (a_bit == b_bit) else "Mismatch"

        row = {
            "Photon #": i + 1,
            "Alice Orientation": a_arrow,
            "Bob Orientation": b_arrow,
            "Outcome": outcome,
            "Alice Bit": a_bit,
            "Bob Bit": b_bit,
            "Bases Match?": "Yes" if is_sifted else "No"
        }
        if enable_eve:
            row["Eve Orientation"] = e_arrow_log
        history_data.append(row)

        js_photon_array.append({
            "id": i + 1,
            "a_arrow": a_arrow, "a_base": a_base, "a_bit": a_bit,
            "e_arrow": e_arrow_log, "e_base": e_base_log, "e_bit": str(e_bit_log),
            "b_arrow": b_arrow, "b_base": b_base, "b_bit": b_bit
        })

    return history_data, js_photon_array


# ---------------------------------------------------------------------------------------
# The animated simulator (HTML canvas inside a Streamlit component).
# Data is injected via plain string substitution (not an f-string) so the JS below can use
# normal single braces.
# ---------------------------------------------------------------------------------------
HTML_TEMPLATE = """
<style>
  * { box-sizing:border-box; }
  body { margin:0; background:transparent; }
  .shell { font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; color:#e2e8f0;
           background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:20px; }
  .toolbar { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; }
  .heading { font-size:17px; font-weight:600; color:#f1f5f9; }
  .heading b { color:#38bdf8; font-variant-numeric:tabular-nums; font-weight:600; }
  .btns { display:flex; gap:8px; }
  button.ctl { font:inherit; font-size:13px; font-weight:500; color:#cbd5e1; background:#162033;
               border:1px solid #2a3a56; border-radius:6px; padding:7px 16px; cursor:pointer;
               transition:background .15s, border-color .15s; }
  button.ctl:hover { background:#1e2b45; border-color:#3b82f6; color:#fff; }
  button.ctl:focus-visible { outline:2px solid #38bdf8; outline-offset:2px; }
  button.ctl.primary { background:#2563eb; border-color:#2563eb; color:#fff; }
  button.ctl.primary:hover { background:#1d4ed8; }
  button.ctl.attn { animation:pulse 1.8s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { box-shadow:0 0 0 0 rgba(37,99,235,.55); } 50% { box-shadow:0 0 0 7px rgba(37,99,235,0); } }
  @media (prefers-reduced-motion: reduce) { button.ctl.attn { animation:none; } }
  .progress { height:3px; background:#1e293b; border-radius:2px; margin:14px 0 10px; overflow:hidden; }
  .progress > div { height:100%; width:0%; background:#38bdf8; transition:width .25s; }
  #statusLine { font-size:12.5px; color:#94a3b8; min-height:18px; margin-bottom:8px; }
  canvas { display:block; margin:0 auto; width:100%; max-width:900px; height:auto; background:#0b1220;
           border-radius:8px; border:1px solid #1e293b; }
  .legend { font-size:12px; color:#8091a7; margin:8px 2px 0; text-align:center; }
  .legend b { color:#cbd5e1; font-weight:500; }

  .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:16px 0; }
  .card { background:#111a2e; border:1px solid #1e293b; border-radius:8px; padding:10px 14px; }
  .card .k { font-size:12px; color:#8091a7; }
  .card .v { font-size:22px; font-weight:600; color:#f1f5f9; margin-top:2px; font-variant-numeric:tabular-nums; }
  @media (max-width:640px) { .cards { grid-template-columns:repeat(2,1fr); } }

  #tableWrap { position:relative; max-height:290px; overflow-y:auto; border:1px solid #1e293b; border-radius:8px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { position:sticky; top:0; background:#111a2e; text-align:left; padding:9px 14px; font-weight:600;
       color:#94a3b8; font-size:12.5px; border-bottom:1px solid #1e293b; }
  td { padding:8px 14px; border-bottom:1px solid #162033; color:#cbd5e1; }
  td.idx { color:#64748b; width:48px; }
  td.pend { color:#4b5a73; }
  tr.active { background:#16233a; }
  tr.done { background:#0f1b2c; }
  .arr { font-size:17px; display:inline-block; width:24px; color:#f1f5f9; }
  .meta { color:#8091a7; font-size:12px; }

  .badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; }
  .b-ok { background:rgba(52,211,153,.14); color:#34d399; }
  .b-bad { background:rgba(248,113,113,.14); color:#f87171; }
  .b-warn { background:rgba(245,166,35,.14); color:#f5a623; }
  .b-idle { background:rgba(148,163,184,.14); color:#94a3b8; }

  .keybox { margin-top:16px; background:#0c1626; border:1px solid #1e293b; border-radius:8px; padding:16px; }
  .kt { font-size:14px; font-weight:600; color:#e2e8f0; margin-bottom:10px; }
  .kt .hint { font-weight:400; color:#64748b; font-size:12px; margin-left:8px; }
  .keyrow { display:flex; gap:12px; align-items:baseline; margin-bottom:5px; font-family:ui-monospace,Menlo,Consolas,monospace; font-size:14px; }
  .keyrow .who { width:52px; font-family:-apple-system,'Segoe UI',Roboto,sans-serif; font-size:13px; font-weight:600; }
  .keyrow .bits { color:#e2e8f0; letter-spacing:.04em; word-break:break-all; }
  #qberDisplay { font-size:12.5px; color:#8091a7; margin:12px 0 8px; }
  #keyStatus { font-size:13px; color:#94a3b8; }
  #keyStatus .stxt { margin-left:10px; }

  .term { border-bottom:1px dotted #64748b; cursor:help; }
  #tooltip { position:fixed; display:none; max-width:290px; background:#0b1220; border:1px solid #334155;
             border-radius:8px; padding:10px 12px; box-shadow:0 10px 30px rgba(0,0,0,.5);
             z-index:1000; pointer-events:none; }
  .tt-title { font-size:12.5px; font-weight:600; color:#f1f5f9; margin-bottom:3px; }
  .tt-body { font-size:12px; line-height:1.5; color:#cbd5e1; }
</style>

<div class="shell">
  <div class="toolbar">
    <div class="heading">Live transmission: photon <b id="photon-id">1</b> of __NUM__</div>
    <div class="btns">
      <button class="ctl" id="btnPause" type="button">Pause</button>
      <button class="ctl primary" id="btnReplay" type="button">Replay this run</button>
    </div>
  </div>
  <div class="progress"><div id="progressBar"></div></div>
  <div id="statusLine"></div>

  <canvas id="quantumArena"></canvas>
  <div class="legend">
    Hover over any box, the photon or the channel for a definition.
    <span class="term" data-term="polarization">Polarization</span> key:
    <b>+ basis</b> → is 0, ↑ is 1; <b>X basis</b> ↖ is 0, ↗ is 1.
  </div>

  <div class="cards">
    <div class="card"><div class="k"><span class="term" data-term="photon">Photons</span> received</div><div class="v" id="cPhotons">0 / __NUM__</div></div>
    <div class="card"><div class="k"><span class="term" data-term="sifting">Sifted</span> bits</div><div class="v" id="cSifted">0</div></div>
    <div class="card"><div class="k">Mismatched bits</div><div class="v" id="cErrors">0</div></div>
    <div class="card"><div class="k"><span class="term" data-term="qber">QBER</span></div><div class="v" id="cQber">—</div></div>
  </div>

  <div id="tableWrap">
    <table>
      <thead><tr id="tableHeader"></tr></thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>

  <div class="keybox">
    <div class="kt"><span class="term" data-term="sifted_key">Sifted key</span><span class="hint">grows as matching bases land</span></div>
    <div class="keyrow"><span class="who term" data-term="alice" style="color:#38bdf8;">Alice</span><span class="bits" id="aliceKeyDisplay">(none yet)</span></div>
    <div class="keyrow"><span class="who term" data-term="bob" style="color:#34d399;">Bob</span><span class="bits" id="bobKeyDisplay">(none yet)</span></div>
    <div id="qberDisplay">QBER: 0.0% (0 sifted bits so far)</div>
    <div id="keyStatus"></div>
  </div>
</div>
<div id="tooltip"><div class="tt-title" id="ttTitle"></div><div class="tt-body" id="ttBody"></div></div>

<script>
const data = __DATA__;
const GLOSSARY = __GLOSSARY__;
const showEve = __SHOW_EVE__;
const speed = __SPEED__;
const threshold = __THRESHOLD__;
const N = data.length;
const $ = function(id) { return document.getElementById(id); };

// ---------- Canvas setup (sharp on high-DPI screens) ----------
const W = 900, H = 200;
const canvas = $('quantumArena');
const ctx = canvas.getContext('2d');
const dpr = window.devicePixelRatio || 1;
canvas.width = W * dpr;
canvas.height = H * dpr;
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

const FONT = '-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
const COL = { alice: '#38bdf8', eve: '#f87171', bob: '#34d399' };
const BOX_W = 150, BOX_Y = 30, BOX_H = 140, LINE_Y = 100;
const aX = showEve ? 40 : 150;
const eX = 360;
const bX = showEve ? 680 : 600;

// ---------- Simulation state ----------
let currentIdx, pX, state, frame, finished, paused, rafId;
let aliceKeyBits, bobKeyBits, siftedCount, errorCount, landed, stage, lastRow;

// Dwell / speed settings, scaled by the speed slider (clamped so it never gets unreadable)
const dwellAliceEve = Math.max(6, Math.round(30 / speed));
const dwellBob = Math.max(8, Math.round(40 / speed));
const lerpRate = Math.min(0.5, 0.15 * speed);

// ---------- Hover definitions ----------
const tip = $('tooltip');
let shownKey = null;
function showTip(key) {
    const g = GLOSSARY[key];
    if (!g) return false;
    $('ttTitle').textContent = g.title;
    $('ttBody').textContent = g.text;
    tip.style.display = 'block';
    shownKey = key;
    return true;
}
function hideTip() { tip.style.display = 'none'; shownKey = null; canvas.style.cursor = 'default'; }
function positionTip(x, y) {
    const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
    let left = x + pad, top = y + pad;
    if (left + w > window.innerWidth - 8) left = x - w - pad;
    if (top + h > window.innerHeight - 8) top = y - h - pad;
    tip.style.left = Math.max(8, left) + 'px';
    tip.style.top = Math.max(8, top) + 'px';
}
function hitTest(e) {
    const r = canvas.getBoundingClientRect();
    const k = W / r.width;
    const x = (e.clientX - r.left) * k, y = (e.clientY - r.top) * k;
    // the photon in flight
    if ((state === 'transit1' || state === 'transit2') && Math.hypot(x - pX, y - LINE_Y) < 14) return 'photon';
    const boxes = [['alice', aX], ['bob', bX]];
    if (showEve) boxes.push(['eve', eX]);
    for (let i = 0; i < boxes.length; i++) {
        const who = boxes[i][0], bx = boxes[i][1];
        if (x >= bx && x <= bx + BOX_W && y >= BOX_Y && y <= BOX_Y + BOX_H) {
            const dy = y - BOX_Y;
            if (dy > 40 && dy < 92) return 'polarization';
            if (dy >= 94 && dy < 112) return 'basis';
            if (dy >= 112 && dy < 132) return 'bit';
            return who;
        }
    }
    // the channel between boxes
    const segs = showEve ? [[aX + BOX_W, eX], [eX + BOX_W, bX]] : [[aX + BOX_W, bX]];
    for (let j = 0; j < segs.length; j++) {
        if (x >= segs[j][0] && x <= segs[j][1] && Math.abs(y - LINE_Y) < 18) return 'channel';
    }
    return null;
}
document.addEventListener('mousemove', function(e) {
    let key = null;
    const t = e.target && e.target.closest ? e.target.closest('[data-term]') : null;
    if (t) key = t.getAttribute('data-term');
    else if (e.target === canvas) key = hitTest(e);
    if (key) {
        if (key !== shownKey) showTip(key);
        canvas.style.cursor = (e.target === canvas) ? 'help' : 'default';
        positionTip(e.clientX, e.clientY);
    } else if (shownKey) {
        hideTip();
    }
});
document.documentElement.addEventListener('mouseleave', hideTip);

// ---------- Canvas drawing ----------
function rr(x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
}

function drawBox(x, title, arrow, label1, label2, color, active) {
    rr(x, BOX_Y, BOX_W, BOX_H, 10);
    ctx.fillStyle = active ? '#16233a' : '#0e1829';
    ctx.fill();
    ctx.strokeStyle = active ? color : '#2a3a56';
    ctx.lineWidth = active ? 2 : 1;
    ctx.stroke();

    ctx.textAlign = 'left';
    ctx.fillStyle = color;
    ctx.font = '600 12px ' + FONT;
    ctx.fillText(title, x + 14, BOX_Y + 24);

    ctx.textAlign = 'center';
    ctx.fillStyle = active ? '#f1f5f9' : '#64748b';
    ctx.font = '34px ' + FONT;
    ctx.fillText(arrow, x + BOX_W / 2, BOX_Y + 78);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px ' + FONT;
    ctx.fillText(label1, x + 14, BOX_Y + 108);
    ctx.fillText(label2, x + 14, BOX_Y + 126);
}

function drawChannel() {
    ctx.lineWidth = 2;
    ctx.strokeStyle = '#2a3a56';
    ctx.setLineDash([6, 5]);
    ctx.beginPath();
    const segs = showEve ? [[aX + BOX_W, eX], [eX + BOX_W, bX]] : [[aX + BOX_W, bX]];
    segs.forEach(function(s) { ctx.moveTo(s[0], LINE_Y); ctx.lineTo(s[1], LINE_Y); });
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#4b5a73';
    ctx.font = '11px ' + FONT;
    ctx.textAlign = 'center';
    segs.forEach(function(s) { ctx.fillText('Quantum channel', (s[0] + s[1]) / 2, LINE_Y - 12); });
    ctx.textAlign = 'left';
}

// ---------- Live tracking table ----------
function term(key, label) { return '<span class="term" data-term="' + key + '">' + label + '</span>'; }
function cellHtml(arrow, base, bit) {
    return '<span class="arr">' + arrow + '</span><span class="meta">basis ' + base + ', bit ' + bit + '</span>';
}
function outcomeBadge(kind) {
    if (kind === 'disc') return '<span class="badge b-idle" data-term="discarded">Discarded</span>';
    if (kind === 'match') return '<span class="badge b-ok" data-term="match">Match</span>';
    return '<span class="badge b-bad" data-term="mismatch">Mismatch</span>';
}
function buildTable() {
    let h = '<th>#</th><th>' + term('alice', 'Alice') + '</th>';
    if (showEve) h += '<th>' + term('eve', 'Eve') + '</th>';
    h += '<th>' + term('bob', 'Bob') + '</th><th>' + term('outcome', 'Outcome') + '</th>';
    $('tableHeader').innerHTML = h;
    let b = '';
    data.forEach(function(p) {
        b += '<tr id="row-' + p.id + '"><td class="idx">' + p.id + '</td><td class="pend" id="a-' + p.id + '">—</td>' +
            (showEve ? '<td class="pend" id="e-' + p.id + '">—</td>' : '') +
            '<td class="pend" id="b-' + p.id + '">—</td><td class="pend" id="o-' + p.id + '">pending</td></tr>';
    });
    $('tableBody').innerHTML = b;
    $('tableWrap').scrollTop = 0;
}

function setKeyStatus(kind, label, text) {
    $('keyStatus').innerHTML = '<span class="badge b-' + kind + '">' + label + '</span><span class="stxt">' + text + '</span>';
}

function updateCards() {
    $('cPhotons').textContent = landed + ' / ' + N;
    $('cSifted').textContent = siftedCount;
    $('cErrors').textContent = errorCount;
    const q = siftedCount ? (errorCount / siftedCount) * 100 : 0;
    const el = $('cQber');
    el.textContent = siftedCount ? q.toFixed(1) + '%' : '—';
    el.style.color = siftedCount ? (q > threshold ? '#f87171' : '#34d399') : '#f1f5f9';
    $('progressBar').style.width = (landed / N * 100) + '%';
}

// Fills in each cell as the photon passes that stage. Takes p as a parameter so it stays valid
// even on the final frame after currentIdx has advanced past the end of the array.
function updateTable(p) {
    const rowEl = $('row-' + p.id);
    let s = stage[p.id] || 0;

    if (s < 1) {
        const c = $('a-' + p.id);
        c.innerHTML = cellHtml(p.a_arrow, p.a_base, p.a_bit);
        c.className = '';
        s = 1;
    }
    if (showEve && s < 2 && (state === 'eve' || state === 'transit2' || state === 'bob')) {
        const c = $('e-' + p.id);
        c.innerHTML = cellHtml(p.e_arrow, p.e_base, p.e_bit);
        c.className = '';
        s = 2;
    }
    if (state === 'bob' && s < 3) {
        const c = $('b-' + p.id);
        c.innerHTML = cellHtml(p.b_arrow, p.b_base, p.b_bit);
        c.className = '';

        const match = (p.a_base === p.b_base);
        const o = $('o-' + p.id);
        o.className = '';
        if (!match) o.innerHTML = outcomeBadge('disc');
        else if (p.a_bit === p.b_bit) o.innerHTML = outcomeBadge('match');
        else o.innerHTML = outcomeBadge('miss');
        s = 3;
        landed++;

        // Fold this photon into the running key/QBER exactly once, the first frame it lands on Bob
        if (match) {
            aliceKeyBits.push(p.a_bit);
            bobKeyBits.push(p.b_bit);
            siftedCount++;
            if (p.a_bit !== p.b_bit) errorCount++;
            $('aliceKeyDisplay').textContent = aliceKeyBits.join(' ');
            $('bobKeyDisplay').textContent = bobKeyBits.join(' ');
            const qber = (errorCount / siftedCount) * 100;
            $('qberDisplay').textContent = 'QBER: ' + qber.toFixed(1) + '% (' + errorCount + ' of ' +
                siftedCount + ' sifted bits mismatched, abort threshold ' + threshold + '%)';
            if (qber > threshold) setKeyStatus('bad', 'Above threshold', 'Error rate exceeds ' + threshold + '%: possible eavesdropper.');
            else setKeyStatus('ok', 'Within threshold', 'Error rate is below ' + threshold + '%: channel looks secure so far.');
        }
        updateCards();
    }
    stage[p.id] = s;
    rowEl.className = (s < 3) ? 'active' : 'done';

    if (lastRow !== p.id) {
        lastRow = p.id;
        const wrap = $('tableWrap');
        wrap.scrollTop = Math.max(0, rowEl.offsetTop - wrap.clientHeight / 2 + rowEl.offsetHeight / 2);
    }
}

function finish() {
    $('statusLine').textContent = 'Transmission complete. Replay runs these same photons again; use "Run new random simulation" above the diagram for fresh random data.';
    $('btnReplay').classList.add('attn');
    $('btnPause').textContent = 'Pause';
    if (siftedCount === 0) {
        setKeyStatus('warn', 'No key', 'No bases matched by chance. Replay or start a new random run.');
    } else {
        const q = (errorCount / siftedCount) * 100;
        if (q > threshold) setKeyStatus('bad', 'Key discarded', 'Final QBER ' + q.toFixed(1) + '% exceeds the ' + threshold + '% threshold. Protocol aborted.');
        else setKeyStatus('ok', 'Key accepted', 'Final QBER ' + q.toFixed(1) + '% is within the ' + threshold + '% threshold.');
    }
}

// ---------- Main loop ----------
function animate() {
    if (paused) { rafId = requestAnimationFrame(animate); return; }

    ctx.clearRect(0, 0, W, H);
    frame++;

    const p = data[currentIdx];
    $('photon-id').textContent = p.id;

    drawChannel();

    if (state === 'alice') {
        pX = aX + 75;
        if (frame > dwellAliceEve) { state = 'transit1'; frame = 0; }
    } else if (state === 'transit1') {
        const target = showEve ? eX : bX;
        pX += (target - pX) * lerpRate;
        if (Math.abs(pX - target) < 5) { state = showEve ? 'eve' : 'bob'; frame = 0; }
    } else if (state === 'eve') {
        pX = eX + 75;
        if (frame > dwellAliceEve) { state = 'transit2'; frame = 0; }
    } else if (state === 'transit2') {
        pX += (bX - pX) * lerpRate;
        if (Math.abs(pX - bX) < 5) { state = 'bob'; frame = 0; }
    } else if (state === 'bob') {
        pX = bX + 75;
        if (frame > dwellBob) {
            currentIdx++;
            if (currentIdx >= data.length) finished = true;
            else { state = 'alice'; frame = 0; }
        }
    }

    updateTable(p);

    drawBox(aX, 'ALICE (SENDER)', p.a_arrow, 'Basis: ' + p.a_base, 'Bit sent: ' + p.a_bit, COL.alice, state === 'alice');
    if (showEve) {
        const pre = (state === 'alice' || state === 'transit1');
        drawBox(eX, 'EVE (EAVESDROPPER)', pre ? '?' : p.e_arrow, 'Basis: ' + p.e_base,
                'Bit read: ' + (pre ? '—' : p.e_bit), COL.eve, state === 'eve');
    }
    const atBob = (state === 'bob');
    drawBox(bX, 'BOB (RECEIVER)', atBob ? p.b_arrow : '?', 'Basis guess: ' + p.b_base,
            'Output bit: ' + (atBob ? p.b_bit : '—'), COL.bob, atBob);

    if (state === 'transit1' || state === 'transit2') {
        const c = (state === 'transit2' && showEve) ? COL.eve : COL.alice;
        ctx.fillStyle = c;
        ctx.shadowBlur = 12;
        ctx.shadowColor = c;
        ctx.beginPath();
        ctx.arc(pX, LINE_Y, 7, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    if (finished) {
        finish();
        return; // stop the loop, leave the final frame + fully-populated table/key on screen
    }
    rafId = requestAnimationFrame(animate);
}

// ---------- (Re)start ----------
function resetSim() {
    cancelAnimationFrame(rafId);
    currentIdx = 0; pX = aX + 75; state = 'alice'; frame = 0;
    finished = false; paused = false;
    aliceKeyBits = []; bobKeyBits = []; siftedCount = 0; errorCount = 0; landed = 0;
    stage = {}; lastRow = -1;
    buildTable();
    $('aliceKeyDisplay').textContent = '(none yet)';
    $('bobKeyDisplay').textContent = '(none yet)';
    $('qberDisplay').textContent = 'QBER: 0.0% (0 sifted bits so far)';
    $('keyStatus').innerHTML = '<span class="badge b-idle">Waiting</span><span class="stxt">Waiting for the first matching basis.</span>';
    $('statusLine').textContent = '';
    $('btnPause').textContent = 'Pause';
    $('btnReplay').classList.remove('attn');
    updateCards();
    rafId = requestAnimationFrame(animate);
}

$('btnReplay').addEventListener('click', resetSim);
$('btnPause').addEventListener('click', function() {
    if (finished) return;
    paused = !paused;
    this.textContent = paused ? 'Resume' : 'Pause';
});

resetSim();
</script>
"""


# ---------------------------------------------------------------------------------------
# Page: Simulator
# ---------------------------------------------------------------------------------------
def simulator_page():
    # 1. Sidebar configuration
    with st.sidebar:
        st.subheader("Simulation settings")
        num_photons = st.slider("Total photons to transmit", min_value=3, max_value=20, value=8,
                                key="num_photons")
        speed = st.slider("Animation speed", min_value=0.5, max_value=3.0, value=1.5, step=0.25,
                          key="speed",
                          help="Higher = faster photon travel and shorter dwell time in each box")
        threshold_pct = st.slider("Abort threshold (QBER %)", min_value=5, max_value=25, value=11, step=1,
                                  key="threshold_pct",
                                  help="Real BB84 implementations abort the key if the estimated error rate "
                                       "among sifted bits exceeds roughly this much (~11% is the standard bound)")
        enable_eve = st.checkbox("Deploy Eve (eavesdropper intercept)", value=True, key="enable_eve",
                                 help="Eve intercepts every photon, measures it in a random basis and "
                                      "resends it to Bob.")
        st.caption("Photon count and the Eve toggle reshuffle the run automatically. Speed and threshold "
                   "apply instantly to the current run.")

    # 2. Page header
    st.title("BB84 Quantum Key Distribution Simulator")
    st.caption("Watch individual photons travel from Alice to Bob, with an optional eavesdropper "
               "on the line, and see how the shared key is built.")
    st.page_link(article_page, label="New to quantum key distribution? Read the BB84 guide",
                 icon=":material/menu_book:")

    left, right = st.columns([4, 1.4], vertical_alignment="center")
    with right:
        shuffle_clicked = st.button("Run new random simulation", type="primary", use_container_width=True)

    # --- Decide whether we need a fresh random photon stream, or can reuse the cached one ---
    current_settings = (num_photons, enable_eve)
    need_new_data = (
        "photon_data" not in st.session_state
        or st.session_state.get("sim_settings") != current_settings
        or shuffle_clicked
    )
    if need_new_data:
        history_data, js_photon_array = generate_photon_stream(num_photons, enable_eve)
        st.session_state.photon_data = js_photon_array
        st.session_state.history_data = history_data
        st.session_state.sim_settings = current_settings

    js_photon_array = st.session_state.photon_data
    history_data = st.session_state.history_data

    # Visible confirmation of exactly what's driving the current render
    with left:
        st.markdown(
            '<div class="chips">'
            f'<div class="chip">Photons<b>{num_photons}</b></div>'
            f'<div class="chip">Speed<b>{speed}×</b></div>'
            f'<div class="chip">Abort threshold<b>{threshold_pct}% QBER</b></div>'
            f'<div class="chip">Eavesdropper<b>{"Present" if enable_eve else "Absent"}</b></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # 3. The high performance smooth canvas frame (table + sifted key + QBER all update live)
    html_canvas = (HTML_TEMPLATE
                   .replace("__DATA__", json.dumps(js_photon_array))
                   .replace("__GLOSSARY__", json.dumps(GLOSSARY))
                   .replace("__SHOW_EVE__", str(enable_eve).lower())
                   .replace("__SPEED__", str(speed))
                   .replace("__THRESHOLD__", str(threshold_pct))
                   .replace("__NUM__", str(num_photons)))
    st.components.v1.html(html_canvas, height=980, scrolling=True)

    with st.expander("Raw data table"):
        df = pd.DataFrame(history_data)
        table_html = df.to_html(index=False, border=0, classes="raw-table")
        st.markdown(f'<div class="raw-wrap">{table_html}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------------------
# Page: Learn - What is BB84?
# ---------------------------------------------------------------------------------------
def article_pg():
    st.markdown("<style>.block-container { max-width: 900px; }</style>", unsafe_allow_html=True)
    st.title("Understanding BB84 quantum key distribution")
    st.caption("A plain-language introduction to the first quantum cryptography protocol, "
               "and a guide to reading the simulator.")
    st.page_link(sim_page, label="Open the simulator", icon=":material/science:")

    st.markdown(f"""
<div class="article-note">Underlined terms show a short definition when you hover over them, the same way they do in the simulator.</div>

## The problem: sharing a secret key

Almost all secure communication works by encrypting data with a secret key. Strong ciphers such as AES are practically unbreakable, but both people must first hold the *same* key, and sending that key over an ordinary channel lets an eavesdropper copy it without anyone noticing. Several widely used key-exchange methods also depend on mathematical problems that a large future quantum computer could solve.

Quantum key distribution (QKD) takes a different route. It uses the laws of physics so that any attempt to listen in on the key leaves a detectable trace.

## BB84 in one paragraph

BB84 was proposed in 1984 by Charles Bennett and Gilles Brassard, which is where the name comes from. {T('alice')} sends a stream of single {T('photon')}s to {T('bob')}, each carrying one bit of information in its {T('polarization')}. Afterwards they compare notes in public about *how* each photon was prepared and measured, but never about the bit values, and keep only the results where they happened to agree. If {T('eve')} tried to listen in, she unavoidably disturbed some photons, and Alice and Bob can see this as an unusually high error rate.

## Building blocks

### Photons and qubits

Each photon carries one {T('qubit')}. Measuring a qubit forces it to give a definite answer and wipes out the information about how it was prepared. Because of the {T('no_cloning')}, Eve also cannot make a perfect copy of a photon and measure the copy later while forwarding the original untouched.

### Two bases

Alice can encode a bit in two different ways, called {T('basis', 'bases')}. This simulator draws them as arrows:

| Basis | Bit 0 | Bit 1 |
|---|---|---|
| + (rectilinear) | → | ↑ |
| X (diagonal) | ↖ | ↗ |

The key rule of BB84: if Bob measures in the *same* basis Alice used, he gets her bit every time. If he measures in the *other* basis, his result is random, a 50/50 coin flip, and the original information is lost.

## The protocol step by step

1. **Preparation.** For every photon, Alice picks a random bit and a random basis and sends a photon polarized accordingly.
2. **Transmission.** The photons travel along the {T('channel')} to Bob.
3. **Measurement.** Bob does not know Alice's bases, so he picks a random basis for each photon and records what he measures.
4. **{T('sifting', 'Sifting')}.** Over a public channel, Alice and Bob announce their bases (not their bits) and discard every photon where the bases differ. About half the photons remain, and these form the {T('sifted_key')}.
5. **Error check.** They compare some or all of the sifted bits and compute the {T('qber')}. If it is above the {T('threshold')}, they assume someone interfered and discard the key.
6. **Key distillation.** If the check passes, classical post-processing (error correction and privacy amplification) turns the sifted bits into a final, shorter secret key.

The simulator compares *every* sifted bit to compute the QBER so you can see each error. Real systems sacrifice only a random sample of the sifted bits for this check.

## Why Eve gets caught

Suppose Eve intercepts every photon, measures it, and sends a new photon on to Bob (an *intercept-resend* attack). She does not know Alice's basis, so she guesses:

- **Half the time she guesses right.** She reads the correct bit, resends an identical photon, and leaves no trace.
- **Half the time she guesses wrong.** Her measurement randomizes the photon. When she resends it, Bob gets a random result in Alice's basis, so he is wrong half of the time.

Among the sifted bits, that works out to 0.5 × 0.5 = **25% errors**. Without an eavesdropper, a good system sees close to 0%. The gap between the two is what Alice and Bob detect.

The {T('threshold')} is the line they draw between "ordinary noise" and "somebody is listening". About 11% is the figure usually quoted as the security bound for BB84.

## How to read the simulator

- **The three boxes.** Alice's box shows the polarization she sent and the basis and bit behind it. Eve's box shows what she measured. Bob's box shows the basis he guessed and the bit he got. The glowing dot is a single photon in flight.
- **The table.** One row per photon, filling in as the photon moves along. The outcome column reads *Match*, *Mismatch* or *Discarded* (see the definitions by hovering over them).
- **The sifted key.** Only photons where Alice's and Bob's bases matched end up here, so Alice's and Bob's rows should be identical when nobody interferes.
- **QBER and status.** The error rate updates after every sifted bit and is compared against the abort threshold from the sidebar.
- **Replay controls.** "Replay this run" plays the same photons again. "Run new random simulation" rolls fresh random bits and bases with the same settings.

One thing to keep in mind: with only a handful of photons there are very few sifted bits. If Eve is present and there are *n* sifted bits, the chance that she causes no error at all is (3/4)<sup>n</sup>, so with 4 sifted bits she slips through about 32% of the time. Increase the photon count, or run several simulations, to see the 25% pattern emerge.

## Real-world limits

- The protocol assumes ideal single-photon sources, no photon loss and perfect detectors. Real fibre and free-space links lose most photons over long distances, and real devices have flaws that attackers can exploit (so-called side-channel attacks).
- Alice and Bob need a public classical channel that is *authenticated*: Eve may listen to it but must not be able to impersonate either party.
- BB84 only distributes keys. The final secret key is then used with a conventional cipher to encrypt the actual message.
""", unsafe_allow_html=True)

    with st.expander("Glossary"):
        for g in GLOSSARY.values():
            st.markdown(f"**{g['title']}**  \n{g['text']}")

    st.markdown("""
#### Further reading

- [BB84 on Wikipedia](https://en.wikipedia.org/wiki/BB84)
- [Quantum key distribution on Wikipedia](https://en.wikipedia.org/wiki/Quantum_key_distribution)
- C. H. Bennett and G. Brassard, "Quantum cryptography: Public key distribution and coin tossing" (1984), the original paper.
""")


# ---------------------------------------------------------------------------------------
# Navigation (pages appear in the left sidebar)
# ---------------------------------------------------------------------------------------
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

sim_page = st.Page(simulator_page, title="Simulator", icon=":material/science:",
                   url_path="simulator", default=True)
article_page = st.Page(article_pg, title="Learn: What is BB84?", icon=":material/menu_book:",
                       url_path="learn-bb84")

pg = st.navigation([sim_page, article_page])
pg.run()
