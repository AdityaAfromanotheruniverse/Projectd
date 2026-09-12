import streamlit as st
import random
import json
import pandas as pd

st.set_page_config(layout="wide")

st.title("🌌 Smooth Real-Time BB84 Protocol Simulator")
st.write("Watch individual photons travel smoothly through the quantum channel via high-performance hardware rendering.")

# Dictionary to map states to arrows for the logs
ARROW_MAP = {
    ('+', 0): "→",
    ('+', 1): "↑",
    ('X', 0): "↖",
    ('X', 1): "↗"
}


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
        outcome = "🗑️ Discarded"
        if is_sifted:
            outcome = "✅ Match" if (a_bit == b_bit) else "🚨 Mismatch"

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


# 1. Sidebar Configurations
with st.sidebar:
    st.header("🎛️ Simulator Settings")
    num_photons = st.slider("Total Photons to Transmit", min_value=3, max_value=20, value=8)
    speed = st.slider("⚡ Animation Speed", min_value=0.5, max_value=3.0, value=1.5, step=0.25,
                       help="Higher = faster photon travel and shorter dwell time in each box")
    threshold_pct = st.slider("🚨 Abort Threshold (QBER %)", min_value=5, max_value=25, value=11, step=1,
                               help="Real BB84 implementations abort the key if the estimated error rate "
                                    "among sifted bits exceeds roughly this much (~11% is the standard bound)")
    enable_eve = st.checkbox("🕵️‍♀️ Deploy Eve (Eavesdropper Intercept)", value=True)
    st.caption("Photon count and the Eve toggle reshuffle the run automatically. Speed and threshold apply instantly to the current run.")
    shuffle_clicked = st.button("🎲 Shuffle New Random Run", type="primary")

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

# Visible confirmation of exactly what's driving the current render — if this line doesn't
# match your sliders, the browser/tab is showing a stale copy of the app and needs a restart.
st.info(
    f"▶ Currently simulating **{num_photons} photons** at **{speed}×** speed, "
    f"abort threshold **{threshold_pct}%** QBER, Eve **{'ON' if enable_eve else 'OFF'}**."
)

# --- 2. THE HIGH PERFORMANCE SMOOTH CANVAS FRAME (table + sifted key + QBER all update live) ---
# Data is injected via plain string substitution (not an f-string) so the JS below can use
# normal single braces without needing to be doubled everywhere.
html_template = """
<div style="background:#111; padding:20px; border-radius:12px; font-family:sans-serif; color:white;">
    <div style="text-align:center; font-size:18px; margin-bottom:4px; color:#aaa;">
        Live Transmission Pipeline: Photon <span id="photon-id" style="color:#00c0f2; font-weight:bold;">1</span> of __NUM__
    </div>
    <div id="statusLine" style="text-align:center; font-size:13px; margin-bottom:11px; color:#666; height:16px;"></div>
    <canvas id="quantumArena" width="900" height="200" style="display:block; margin:0 auto; max-width:100%; background:#1a1a1a; border-radius:8px; border:1px solid #333;"></canvas>

    <div style="margin-top:16px; max-height:320px; overflow-y:auto; border-radius:8px; border:1px solid #333;">
        <table style="width:100%; border-collapse:collapse; font-family:sans-serif; font-size:13px; color:#ddd;">
            <thead>
                <tr id="tableHeader" style="position:sticky; top:0; background:#1a1a1a;"></tr>
            </thead>
            <tbody id="tableBody"></tbody>
        </table>
    </div>

    <div style="margin-top:16px; background:#0d1b12; border:1px solid #234; border-radius:8px; padding:14px;">
        <div style="font-size:14px; color:#aaa; margin-bottom:8px;">🔑 Sifted Key (builds live as matching bases land)</div>
        <div style="font-family:monospace; font-size:14px; margin-bottom:4px;"><span style="color:#00c0f2;">Alice:</span> <span id="aliceKeyDisplay" style="color:#eee;">(none yet)</span></div>
        <div style="font-family:monospace; font-size:14px; margin-bottom:10px;"><span style="color:#28a745;">Bob:</span> <span id="bobKeyDisplay" style="color:#eee;">(none yet)</span></div>
        <div id="qberDisplay" style="font-size:12px; color:#888; margin-bottom:6px;">Error rate (QBER): 0.0% (0 sifted bits so far)</div>
        <div id="keyStatus" style="font-size:13px; color:#888;">Waiting for first matching basis…</div>
    </div>
</div>

<script>
const data = __DATA__;
const showEve = __SHOW_EVE__;
const speed = __SPEED__;
const threshold = __THRESHOLD__;
const canvas = document.getElementById('quantumArena');
const ctx = canvas.getContext('2d');

let currentIdx = 0;
let pX = 80;
let state = 'alice'; // alice -> transit1 -> eve -> transit2 -> bob
let frame = 0;
let finished = false;

let aliceKeyBits = [];
let bobKeyBits = [];
let siftedCount = 0;
let errorCount = 0;
const addedToKey = new Set();

// Dwell / speed settings, scaled by the speed slider (clamped so it never gets unreadable)
const dwellAliceEve = Math.max(6, Math.round(30 / speed));
const dwellBob = Math.max(8, Math.round(40 / speed));
const lerpRate = Math.min(0.5, 0.15 * speed);

function drawBox(x, y, w, h, title, arrow, label1, label2, color, active) {
    ctx.fillStyle = active ? '#223' : '#111';
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = active ? color : '#444';
    ctx.lineWidth = active ? 3 : 1;
    ctx.strokeRect(x, y, w, h);

    ctx.fillStyle = color;
    ctx.font = 'bold 12px sans-serif';
    ctx.fillText(title, x + 10, y + 25);

    ctx.fillStyle = active ? '#fff' : '#888';
    ctx.font = '32px sans-serif';
    ctx.fillText(arrow, x + w/2 - 12, y + 70);

    ctx.fillStyle = '#aaa';
    ctx.font = '11px sans-serif';
    ctx.fillText(label1, x + 10, y + 105);
    ctx.fillText(label2, x + 10, y + 120);
}

// --- Build the live tracking table: starts as placeholders, fills in as each photon lands ---
function buildTable() {
    const header = document.getElementById('tableHeader');
    let headerHtml = '<th style="padding:8px; text-align:left; color:#00c0f2;">#</th>' +
        '<th style="padding:8px; text-align:left; color:#00c0f2;">Alice</th>';
    if (showEve) headerHtml += '<th style="padding:8px; text-align:left; color:#ff4b4b;">Eve</th>';
    headerHtml += '<th style="padding:8px; text-align:left; color:#28a745;">Bob</th>' +
        '<th style="padding:8px; text-align:left;">Outcome</th>';
    header.innerHTML = headerHtml;

    const body = document.getElementById('tableBody');
    let bodyHtml = '';
    data.forEach(function(p) {
        bodyHtml += '<tr id="row-' + p.id + '" style="border-bottom:1px solid #222; transition:background 0.3s;">' +
            '<td style="padding:8px; color:#888;">' + p.id + '</td>' +
            '<td style="padding:8px; color:#555;" id="a-' + p.id + '">—</td>';
        if (showEve) bodyHtml += '<td style="padding:8px; color:#555;" id="e-' + p.id + '">—</td>';
        bodyHtml += '<td style="padding:8px; color:#555;" id="b-' + p.id + '">—</td>' +
            '<td style="padding:8px; color:#555;" id="o-' + p.id + '">pending…</td>' +
            '</tr>';
    });
    body.innerHTML = bodyHtml;
}
buildTable();

// --- Update the current row's cells (and the live key + QBER) as its photon passes each stage.
// Takes p as a parameter rather than re-reading data[currentIdx], so it stays valid even
// on the final frame after currentIdx has already advanced past the end of the array. ---
function updateTable(p) {
    const rowEl = document.getElementById('row-' + p.id);
    rowEl.style.background = '#1c2733';

    const aCell = document.getElementById('a-' + p.id);
    aCell.innerText = p.a_arrow + '  (base ' + p.a_base + ', bit ' + p.a_bit + ')';
    aCell.style.color = '#ddd';

    if (showEve) {
        const eCell = document.getElementById('e-' + p.id);
        if (state === 'eve' || state === 'transit2' || state === 'bob') {
            eCell.innerText = p.e_arrow + '  (base ' + p.e_base + ', bit ' + p.e_bit + ')';
            eCell.style.color = '#ddd';
        }
    }

    if (state === 'bob') {
        const bCell = document.getElementById('b-' + p.id);
        bCell.innerText = p.b_arrow + '  (base ' + p.b_base + ', bit ' + p.b_bit + ')';
        bCell.style.color = '#ddd';

        const match = (p.a_base === p.b_base);
        const oCell = document.getElementById('o-' + p.id);
        if (!match) {
            oCell.innerText = '🗑️ Discarded';
            oCell.style.color = '#888';
        } else if (p.a_bit === p.b_bit) {
            oCell.innerText = '✅ Match';
            oCell.style.color = '#28a745';
        } else {
            oCell.innerText = '🚨 Mismatch';
            oCell.style.color = '#ff4b4b';
        }
        rowEl.style.background = '#152018';

        // Only fold this photon into the running key/QBER once, the first frame it lands on Bob
        if (!addedToKey.has(p.id)) {
            addedToKey.add(p.id);
            if (match) {
                aliceKeyBits.push(p.a_bit);
                bobKeyBits.push(p.b_bit);
                siftedCount++;
                if (p.a_bit !== p.b_bit) errorCount++;

                document.getElementById('aliceKeyDisplay').innerText = aliceKeyBits.join(' ');
                document.getElementById('bobKeyDisplay').innerText = bobKeyBits.join(' ');

                const qber = (errorCount / siftedCount) * 100;
                document.getElementById('qberDisplay').innerText =
                    'Error rate (QBER): ' + qber.toFixed(1) + '%  (' + errorCount + ' of ' + siftedCount + ' sifted bits mismatched)';

                const statusEl = document.getElementById('keyStatus');
                if (qber > threshold) {
                    statusEl.innerText = '🚨 Error rate above the ' + threshold + '% threshold — possible eavesdropper!';
                    statusEl.style.color = '#ff4b4b';
                } else {
                    statusEl.innerText = '✅ Error rate within the ' + threshold + '% threshold — channel looks secure so far';
                    statusEl.style.color = '#28a745';
                }
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    frame++;

    let p = data[currentIdx];
    document.getElementById('photon-id').innerText = p.id;

    let aX = 40, eX = 360, bX = 680;
    if (!showEve) bX = 520;

    ctx.strokeStyle = '#333';
    ctx.lineWidth = 4;
    ctx.beginPath();
    if (showEve) {
        ctx.moveTo(190, 100); ctx.lineTo(360, 100);
        ctx.moveTo(510, 100); ctx.lineTo(680, 100);
    } else {
        ctx.moveTo(190, 100); ctx.lineTo(520, 100);
    }
    ctx.stroke();

    if (state === 'alice') {
        pX = aX + 75;
        if (frame > dwellAliceEve) { state = 'transit1'; frame = 0; }
    } else if (state === 'transit1') {
        let target = showEve ? eX : bX;
        pX += (target - pX) * lerpRate;
        if (Math.abs(pX - target) < 5) {
            state = showEve ? 'eve' : 'bob';
            frame = 0;
        }
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
            if (currentIdx >= data.length) {
                finished = true;
            } else {
                state = 'alice';
                frame = 0;
            }
        }
    }

    updateTable(p); // uses the p captured above, so it's safe even on the finishing frame

    drawBox(aX, 30, 150, 140, "ALICE'S BOX", p.a_arrow, "Base: " + p.a_base, "Bit Sent: " + p.a_bit, '#00c0f2', state === 'alice');
    if (showEve) {
        let arr = (state === 'alice' || state === 'transit1') ? '❓' : p.e_arrow;
        let readBit = (state === 'alice' || state === 'transit1') ? '—' : p.e_bit;
        drawBox(eX, 30, 150, 140, "EVE'S BOX", arr, "Base: " + p.e_base, "Read: " + readBit, '#ff4b4b', state === 'eve');
    }
    let bArrow = (state === 'bob') ? p.b_arrow : '❓';
    let bBit = (state === 'bob') ? p.b_bit : '—';
    drawBox(bX, 30, 150, 140, "BOB'S BOX", bArrow, "Guess: " + p.b_base, "Output: " + bBit, '#28a745', state === 'bob');

    if (state === 'transit1' || state === 'transit2') {
        ctx.fillStyle = (state === 'transit1') ? '#00c0f2' : (showEve ? '#ff4b4b' : '#00c0f2');
        ctx.shadowBlur = 10;
        ctx.shadowColor = ctx.fillStyle;
        ctx.beginPath();
        ctx.arc(pX, 100, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    if (finished) {
        document.getElementById('statusLine').innerText = '✅ Transmission complete — shuffle a new random run to try again';
        const statusEl = document.getElementById('keyStatus');
        if (siftedCount === 0) {
            statusEl.innerText = '⚠️ Final: no bases matched by chance — shuffle a new run!';
            statusEl.style.color = '#f5a623';
        } else {
            const finalQber = (errorCount / siftedCount) * 100;
            if (finalQber > threshold) {
                statusEl.innerText = '🚨 Final QBER ' + finalQber.toFixed(1) + '% exceeds ' + threshold + '% threshold — ABORT, key discarded!';
                statusEl.style.color = '#ff4b4b';
            } else {
                statusEl.innerText = '🔒 Final QBER ' + finalQber.toFixed(1) + '% — within threshold, secure key accepted!';
                statusEl.style.color = '#28a745';
            }
        }
        return; // stop the loop, leave the final frame + fully-populated table/key on screen
    }

    requestAnimationFrame(animate);
}
animate();
</script>
"""

html_canvas = (html_template
    .replace("__DATA__", json.dumps(js_photon_array))
    .replace("__SHOW_EVE__", str(enable_eve).lower())
    .replace("__SPEED__", str(speed))
    .replace("__THRESHOLD__", str(threshold_pct))
    .replace("__NUM__", str(num_photons)))

st.components.v1.html(html_canvas, height=780, scrolling=True)

with st.expander("📋 Raw data table"):
    df = pd.DataFrame(history_data)
    st.dataframe(df.set_index("Photon #"), use_container_width=True)
