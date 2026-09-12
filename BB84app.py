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
    sim_speed = st.slider("Transmission Speed (Seconds per phase)", min_value=0.2, max_value=2.0, value=0.6)

# Initialize Session States to keep historical table data across frames
if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = False

# 2. Controls to start or reset
c_start, c_reset = st.columns([1, 5])
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
    # Set up layout containers for the active "Boxes"
    st.subheader("📦 Live Lab Setup")
    box_cols = st.columns([3, 4, 3]) if enable_eve else st.columns([4, 2, 4])
    
    alice_box = box_cols[0].empty()
    middle_box = box_cols[1].empty()
    bob_box = box_cols[-1].empty()
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_photons):
        # Update progress tracking
        progress_bar.progress((i + 1) / num_photons)
        status_text.markdown(f"### ⚡ Transmitting Photon **#{i+1}** of {num_photons}...")

        # --- PHASE 1: Alice configures her box and fires ---
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_orient = ARROW_MAP[(a_base, a_bit)]

        alice_box.markdown(f"""
        <div style="border:3px solid #00c0f2; padding:20px; border-radius:10px; background-color:#f0f9ff; text-align:center;">
            <h3>👩‍💻 Alice's Box</h3>
            <h1 style="color:#00c0f2; font-size: 50px;">{a_orient.split()[0]}</h1>
            <p><b>Base Selected:</b> [ {a_base} ]</p>
            <p><b>Bit Input:</b> {a_bit}</p>
            <span style="background-color:#00c0f2; color:white; padding:4px 8px; border-radius:5px;">FIRED 🔥</span>
        </div>
        """, unsafe_allowed_html=True)
        
        middle_box.markdown("<div style='text-align:center; margin-top:50px;'>✨ 🌌 Photon leaving Alice...</div>", unsafe_allowed_html=True)
        bob_box.markdown("<div style='border:3px dashed #ccc; padding:20px; border-radius:10px; text-align:center; color:#aaa;'><h3>👨‍💻 Bob's Box</h3><br><p>Waiting for photon...</p></div>", unsafe_allowed_html=True)
        
        time.sleep(sim_speed)

        # --- PHASE 2: Mid-transit (Eve's box action if active) ---
        current_bit = a_bit
        current_base = a_base
        current_orient = a_orient
        eve_base_log = "—"
        eve_orient_log = "—"

        if enable_eve:
            eve_base = random.choice(['+', 'X'])
            if eve_base == a_base:
                eve_bit = a_bit
            else:
                eve_bit = random.randint(0, 1)
                
            current_bit = eve_bit
            current_base = eve_base
            current_orient = ARROW_MAP[(eve_base, eve_bit)]
            eve_base_log = eve_base
            eve_orient_log = current_orient.split()[0]

            middle_box.markdown(f"""
            <div style="border:3px solid #ff4b4b; padding:20px; border-radius:10px; background-color:#fff5f5; text-align:center;">
                <h3>🕵️‍♀️ Eve's Box (Intercepted!)</h3>
                <h1 style="color:#ff4b4b; font-size: 50px;">{eve_orient_log}</h1>
                <p><b>Base Used:</b> [ {eve_base} ]</p>
                <p><b>Measured Bit:</b> {eve_bit}</p>
                <span style="background-color:#ff4b4b; color:white; padding:4px 8px; border-radius:5px;">RE-SENT 🔄</span>
            </div>
            """, unsafe_allowed_html=True)
            time.sleep(sim_speed)
        else:
            middle_box.markdown("<div style='text-align:center; margin-top:50px; font-size:30px; color:#4caf50;'>➡️ ➡️ ➡️</div>", unsafe_allowed_html=True)
            time.sleep(sim_speed / 2)

        # --- PHASE 3: Bob's Box receives and measures ---
        b_base = random.choice(['+', 'X'])
        
        # Physics simulation check for outcome
        if current_base == b_base:
            b_bit = current_bit
        else:
            b_bit = random.randint(0, 1)
            
        b_orient = ARROW_MAP[(b_base, b_bit)]

        bob_box.markdown(f"""
        <div style="border:3px solid #28a745; padding:20px; border-radius:10px; background-color:#f4fff6; text-align:center;">
            <h3>👨‍💻 Bob's Box</h3>
            <h1 style="color:#28a745; font-size: 50px;">{b_orient.split()[0]}</h1>
            <p><b>Base Guessed:</b> [ {b_base} ]</p>
            <p><b>Bit Read:</b> {b_bit}</p>
            <span style="background-color:#28a745; color:white; padding:4px 8px; border-radius:5px;">MEASURED 🎯</span>
        </div>
        """, unsafe_allowed_html=True)
        
        # Evaluate sifted key criteria
        is_sifted = (a_base == b_base)
        outcome = "🗑️ Discarded"
        if is_sifted:
            outcome = "✅ Match" if (a_bit == b_bit) else "🚨 Mismatch (Tampered!)"

        # Record this row to history logs
        row_data = {
            "Photon #": i + 1,
            "Alice Orientation": a_orient.split()[0],
            "Bob Orientation": b_orient.split()[0],
            "Outcome": outcome,
            "Alice Bit": a_bit,
            "Bob Bit": b_bit,
            "Bases Match?": "Yes" if is_sifted else "No"
        }
        
        if enable_eve:
            # Inject Eve's column into the middle structure if active
            row_data = {
                "Photon #": i + 1,
                "Alice Orientation": a_orient.split()[0],
                "Eve Orientation": eve_orient_log,
                "Bob Orientation": b_orient.split()[0],
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
    
    # Construct a clean dataframe matrix out of state logs
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df.set_index("Photon #"), use_container_width=True)

    # Output Key analysis summaries
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
