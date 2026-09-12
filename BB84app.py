import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(layout="wide")

st.title("🌌 Real-Time BB84 Quantum Photon Simulator")
st.write("Watch individual photons emerge from Alice's box, polarize, travel across the channel, and enter Bob's measuring box.")

# Dictionary to convert base and bit into standard polarization arrows
ARROW_MAP = {
    ('+', 0): "→ (Horizontal)",
    ('+', 1): "↑ (Vertical)",
    ('X', 0): "↖ (Diagonal 135°)",
    ('X', 1): "↗ (Diagonal 45°)"
}

# 1. User Setup
with st.sidebar:
    st.header("🎛️ Simulator Settings")
    num_photons = st.slider("Total Photons to Transmit", min_value=5, max_value=20, value=8)
    enable_eve = st.checkbox("🕵️‍♀️ Deploy Eve (Eavesdropper Intercept)")
    sim_speed = st.slider("Step Duration (Seconds per phase)", min_value=1.0, max_value=4.0, value=2.0)

# Initialize Session States to keep historical table data across frames
if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = False

# 2. Controls to start or reset
c_start, c_reset = st.columns(2)
with c_start:
    start_sim = st.button("🚀 Run Live Simulation", type="primary")
with c_reset:
    if st.button("🔄 Reset Logs"):
        st.session_state.history = []
        st.session_state.running = False
        st.rerun()

if start_sim:
    st.session_state.history = []  # Clear previous run data
    st.session_state.running = True

# 3. Active Real-Time Animation Loop
if st.session_state.running:
    st.subheader("📦 Live Lab Setup")
    
    # Establish stationary visual slots across the screen layout
    box_cols = st.columns(3) if enable_eve else st.columns(3)
    alice_box = box_cols[0].empty()
    middle_box = box_cols[1].empty()
    bob_box = box_cols[-1].empty()
    
    # Progress tracking tools
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_photons):
        progress_bar.progress((i + 1) / num_photons)
        status_text.markdown(f"### ⚡ Transmitting Photon **#{i+1}** of {num_photons}...")

        # Precompute values immediately so they remain internally consistent across animation steps
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_orient = ARROW_MAP[(a_base, a_bit)]
        a_arrow = a_orient.split()[0]

        current_bit = a_bit
        current_base = a_base
        eve_base_log = "—"
        eve_orient_log = "—"

        if enable_eve:
            eve_base = random.choice(['+', 'X'])
            eve_bit = a_bit if eve_base == a_base else random.randint(0, 1)
            current_bit = eve_bit
            current_base = eve_base
            eve_orient_log = ARROW_MAP[(eve_base, eve_bit)].split()[0]

        b_base = random.choice(['+', 'X'])
        b_bit = current_bit if current_base == b_base else random.randint(0, 1)
        b_orient = ARROW_MAP[(b_base, b_bit)]
        b_arrow = b_orient.split()[0]

        # ----------------------------------------------------
        # --- VISUAL PHASE 1: Alice Fires Photon ---
        # ----------------------------------------------------
        alice_box.markdown(f"""
        <div style="border:3px solid #00c0f2; padding:20px; border-radius:10px; background-color:#f0f9ff; text-align:center; box-shadow: 0 0 15px #00c0f2;">
            <h3>👩‍💻 Alice's Box</h3>
            <h1 style="color:#00c0f2; font-size: 55px; margin: 10px 0;">{a_arrow}</h1>
            <p><b>Base Selected:</b> [ {a_base} ]</p>
            <p><b>Bit Input:</b> {a_bit}</p>
            <span style="background-color:#00c0f2; color:white; padding:4px 8px; border-radius:5px; font-weight:bold;">FIRED 🔥</span>
        </div>
        """, unsafe_allowed_html=True)
        
        if enable_eve:
            middle_box.markdown("<div style='text-align:center; margin-top:60px; font-size:16px; color:#aaa;'>🌌 Waiting for intercept...</div>", unsafe_allowed_html=True)
        else:
            middle_box.markdown("<div style='text-align:center; margin-top:60px; font-size:24px; color:#00c0f2;'>● ──▶</div>", unsafe_allowed_html=True)
            
        bob_box.markdown("<div style='border:3px dashed #ccc; padding:20px; border-radius:10px; text-align:center; color:#aaa;'><h3>👨‍💻 Bob's Box</h3><br><p>Waiting for photon...</p></div>", unsafe_allowed_html=True)
        
        time.sleep(sim_speed)

        # ----------------------------------------------------
        # --- VISUAL PHASE 2: Mid-Transit (Eve Intercept) ---
        # ----------------------------------------------------
        if enable_eve:
            middle_box.markdown(f"""
            <div style="border:3px solid #ff4b4b; padding:20px; border-radius:10px; background-color:#fff5f5; text-align:center; box-shadow: 0 0 15px #ff4b4b;">
                <h3>🕵️‍♀️ Eve's Box (Intercepted!)</h3>
                <h1 style="color:#ff4b4b; font-size: 55px; margin: 10px 0;">{eve_orient_log}</h1>
                <p><b>Base Used:</b> [ {eve_base} ]</p>
                <p><b>Measured Bit:</b> {eve_bit}</p>
                <span style="background-color:#ff4b4b; color:white; padding:4px 8px; border-radius:5px; font-weight:bold;">RE-SENT 🔄</span>
            </div>
            """, unsafe_allowed_html=True)
            time.sleep(sim_speed)

        # ----------------------------------------------------
        # --- VISUAL PHASE 3: Bob Receives & Measures ---
        # ----------------------------------------------------
        if enable_eve:
            middle_box.markdown(f"""
            <div style="border:3px solid #ff4b4b; padding:20px; border-radius:10px; background-color:#fff5f5; text-align:center; opacity: 0.6;">
                <h3>🕵️‍♀️ Eve's Box</h3>
                <h1 style="color:#ff4b4b; font-size: 55px; margin: 10px 0;">{eve_orient_log}</h1>
                <p><b>Base Used:</b> [ {eve_base} ]</p>
                <p><b>Measured Bit:</b> {eve_bit}</p>
                <span style="background-color:#777; color:white; padding:4px 8px; border-radius:5px;">FORWARDED ➡️</span>
            </div>
            """, unsafe_allowed_html=True)

        bob_box.markdown(f"""
        <div style="border:3px solid #28a745; padding:20px; border-radius:10px; background-color:#f4fff6; text-align:center; box-shadow: 0 0 15px #28a745;">
            <h3>👨‍💻 Bob's Box</h3>
            <h1 style="color:#28a745; font-size: 55px; margin: 10px 0;">{b_arrow}</h1>
            <p><b>Base Guessed:</b> [ {b_base} ]</p>
            <p><b>Bit Read:</b> {b_bit}</p>
            <span style="background-color:#28a745; color:white; padding:4px 8px; border-radius:5px; font-weight:bold;">MEASURED 🎯</span>
        </div>
        """, unsafe_allowed_html=True)

        # Evaluate final key metrics matching criteria
        is_sifted = (a_base == b_base)
        outcome = "🗑️ Discarded"
        if is_sifted:
            outcome = "✅ Match" if (a_bit == b_bit) else "🚨 Mismatch (Tampered!)"

        # Organize structural log tracking arrays
        if enable_eve:
            row_data = {
                "Photon #": i + 1,
                "Alice Orientation": a_arrow,
                "Eve Orientation": eve_orient_log,
                "Bob Orientation": b_arrow,
                "Outcome": outcome,
                "Alice Bit": a_bit,
                "Bob Bit": b_bit,
                "Bases Match?": "Yes" if is_sifted else "No"
            }
        else:
            row_data = {
                "Photon #": i + 1,
                "Alice Orientation": a_arrow,
                "Bob Orientation": b_arrow,
                "Outcome": outcome,
                "Alice Bit": a_bit,
                "Bob Bit": b_bit,
                "Bases Match?": "Yes" if is_sifted else "No"
            }

        st.session_state.history.append(row_data)
        time.sleep(sim_speed)

    st.session_state.running = False
    status_text.markdown("### 🎉 Simulation Completed!")

# 4. Display Historical Matrix Summary
if len(st.session_state.history) > 0:
    st.markdown("---")
    st.subheader("📋 Quantum Transmission Tracking Matrix")
    
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df.set_index("Photon #"), use_container_width=True)

    st.subheader("🔑 Final Sifted Key Extraction")
    sifted_rows = [r for r in st.session_state.history if r["Bases Match?"] == "Yes"]
    
    a_key = [str(r["Alice Bit"]) for r in sifted_rows]
    b_key = [str(r["Bob Bit"]) for r in sifted_rows]
    
    k1, k2 = st.columns(2)
    k1.info(f"**Alice's Key:** `{' '.join(a_key) if a_key else 'Empty'}`")
    k2.success(f"**Bob's Key:** `{' '.join(b_key) if b_key else 'Empty'}`")
    
    if a_key == b_key and len(a_key) > 0:
        st.balloons()
        st.success("🔒 Keys match perfectly! Secure quantum pipeline finalized.")
    elif len(a_key) == 0:
        st.warning("No bases matched by random chance. Run the simulation again with more photons!")
    else:
        st.error("🚨 Key eavesdropping signature detected! The communication path is insecure.")
