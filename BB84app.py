import streamlit as st
import random
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

# 1. Sidebar Configurations
with st.sidebar:
    st.header("🎛️ Simulator Settings")
    num_photons = st.slider("Total Photons to Transmit", min_value=3, max_value=12, value=5)
    enable_eve = st.checkbox("🕵️‍♀️ Deploy Eve (Eavesdropper Intercept)", value=True)

# Generate values instantly on click to feed the smooth animation canvas
if st.button("🚀 Run Live Physics Simulation", type="primary"):
    history_data = []
    js_photon_array = []

    # Pre-calculate the entire stream data
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

        # Pack row data for the historical table matrix
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

        # Structure precise JSON dictionary configurations explicitly for the JavaScript engine
        js_photon_array.append({
            "id": i + 1,
            "a_arrow": a_arrow, "a_base": a_base, "a_bit": a_bit,
            "e_arrow": e_arrow_log, "e_base": e_base_log, "e_bit": str(e_bit_log),
            "b_arrow": b_arrow, "b_base": b_base, "b_bit": b_bit
        })

    # --- 2. THE HIGH PERFORMANCE SMOOTH CANVAS FRAME ---
    # High framerate calculations handled inside an embedded window frame context
    html_canvas = f"""
    <div style="background:#111; padding:20px; border-radius:12px; font-family:sans-serif; color:white;">
        <div style="text-align:center; font-size:18px; margin-bottom:15px; color:#aaa;">
            Live Transmission Pipeline: Photon <span id="photon-id" style="color:#00c0f2; font-weight:bold;">1</span> of {num_photons}
        </div>
        <canvas id="quantumArena" width="900" height="200" style="display:block; margin:0 auto; max-width:100%; background:#1a1a1a; border-radius:8px; border:1px solid #333;"></canvas>
    </div>

    <script>
    const data = {str(js_photon_array)};
    const showEve = {str(enable_eve).lower()};
    const canvas = document.getElementById('quantumArena');
    const ctx = canvas.getContext('2d');
    
    let currentIdx = 0;
    let pX = 80; 
    let state = 'alice'; // alice -> transit1 -> eve -> transit2 -> bob
    let frame = 0;

    function drawBox(x, y, w, h, title, arrow, label1, label2, color, active) {{
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
    }}

    function animate() {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        frame++;
        
        let p = data[currentIdx];
        document.getElementById('photon-id').innerText = p.id;
        
        // Define clean stationary component bounds
        let aX = 40, eX = 360, bX = 680;
        if (!showEve) bX = 520;

        // Render channel conduit paths
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 4;
        ctx.beginPath();
        if (showEve) {{
            ctx.moveTo(190, 100); ctx.lineTo(360, 100);
            ctx.moveTo(510, 100); ctx.lineTo(680, 100);
        }} else {{
            ctx.moveTo(190, 100); ctx.lineTo(520, 100);
        }}
        ctx.stroke();

        // High frequency position translation loops
        if (state === 'alice') {{
            pX = aX + 75;
            if (frame > 30) {{ state = 'transit1'; frame = 0; }}
        }} else if (state === 'transit1') {{
            let target = showEve ? eX : bX;
            pX += (target - pX) * 0.15;
            if (Math.abs(pX - target) < 5) {{
                state = showEve ? 'eve' : 'bob';
                frame = 0;
            }}
        }} else if (state === 'eve') {{
            pX = eX + 75;
            if (frame > 30) {{ state = 'transit2'; frame = 0; }}
        }} else if (state === 'transit2') {{
            pX += (bX - pX) * 0.15;
            if (Math.abs(pX - bX) < 5) {{ state = 'bob'; frame = 0; }}
        }} else if (state === 'bob') {{
            pX = bX + 75;
            if (frame > 40) {{
                currentIdx++;
                if (currentIdx >= data.length) currentIdx = 0; // Seamless looping visualization
                state = 'alice';
                frame = 0;
            }}
        }}

        // Draw lab hardware boxes
        drawBox(aX, 30, 150, 140, "ALICE'S BOX", p.a_arrow, "Base: " + p.a_base, "Bit Sent: " + p.a_bit, '#00c0f2', state === 'alice');
        if (showEve) {{
            let arr = (state === 'alice' || state === 'transit1') ? '❓' : p.e_arrow;
            let readBit = (state === 'alice' || state === 'transit1') ? '—' : p.e_bit;
            drawBox(eX, 30, 150, 140, "EVE'S BOX", arr, "Base: " + p.e_base, "Read: " + readBit, '#ff4b4b', state === 'eve');
        }}
        let bArrow = (state === 'bob') ? p.b_arrow : '❓';
        let bBit = (state === 'bob') ? p.b_bit : '—';
        drawBox(bX, 30, 150, 140, "BOB'S BOX", bArrow, "Guess: " + p.b_base, "Output: " + bBit, '#28a745', state === 'bob');

        // Draw active trailing quantum photon sphere
        if (state === 'transit1' || state === 'transit2') {{
            ctx.fillStyle = (state === 'transit1') ? '#00c0f2' : (showEve ? '#ff4b4b' : '#00c0f2');
            ctx.shadowBlur = 10;
            ctx.shadowColor = ctx.fillStyle;
            ctx.beginPath();
            ctx.arc(pX, 100, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0; // Reset canvas glow states
        }}

        requestAnimationFrame(animate);
    }}
    animate();
    </script>
    """
    st.components.v1.html(html_canvas, height=270)

    # --- 3. FINAL HISTORICAL LOG EXTRACTION MATRIX ---
    st.markdown("---")
    st.subheader("📋 Quantum Transmission Tracking Matrix")
    df = pd.DataFrame(history_data)
    st.dataframe(df.set_index("Photon #"), use_container_width=True)

    st.subheader("🔑 Final Sifted Key Extraction")
    sifted_rows = [r for r in history_data if r["Bases Match?"] == "Yes"]
    
    a_key = [str(r["Alice Bit"]) for r in sifted_rows]
    b_key = [str(r["Bob Bit"]) for r in sifted_rows]
    
    k1, k2 = st.columns(2)
    k1.info(f"**Alice's Sifted Key:** `{' '.join(a_key) if a_key else 'Empty'}`")
    k2.success(f"**Bob's Sifted Key:** `{' '.join(b_key) if b_key else 'Empty'}`")
    
    if a_key == b_key and len(a_key) > 0:
        st.success("🔒 Keys match perfectly! Secure quantum pipeline finalized.")
    elif len(a_key) == 0:
        st.warning("No bases matched by random chance. Run the simulation again!")
    else:
        st.error("🚨 Key eavesdropping signature detected! The communication path is insecure.")
