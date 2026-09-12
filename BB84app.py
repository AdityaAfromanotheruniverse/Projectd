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
    
    # Establish distinct, stationary column placeholders
    if enable_eve:
        col1, col2, col3 = st.columns(3)
        alice_box = col1.empty()
        middle_box = col2.empty()
        bob_box = col3.empty()
    else:
        col1, col2 = st.columns(2)
        alice_box = col1.empty()
        bob_box = col2.empty()
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_photons):
        progress_bar.progress((i + 1) / num_photons)
        status_text.markdown(f"### ⚡ Transmitting Photon **#{i+1}** of {num_photons}...")

        # --- PHASE 1: Alice configures her box and fires ---
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_orient = ARROW_MAP[(a_base, a_bit)]

        alice_box.markdown(f"""
        <div style="border:3px solid #00c0f2; padding:20px; border-radius:10px; background-color:#f0f9ff; text-align:center;">
            <h3>👩‍💻 Alice's Box</h3>
            <h1 style="color:#00c0f2; font-size: 40px;">{a_orient}</h1>
            <p><b>Base Selected:</b> [ {a_base} ]</p>
            <p><b>Bit Input:</b> {a_bit}</p>
            <span style="background-color:#00c0f2; color:white; padding:4px 8px; border-radius:5px;">FIRED 🔥</span>
        </div>
        """, unsafe_allowed_html=True)
        
        if enable_eve:
            middle_box.markdown("<div style='text-align:center; margin-top:50px;'>✨ 🌌 Photon leaving Alice...</div>", unsafe_allowed_html=True)
        bob_box.markdown("<div style='border:3px dashed #ccc; padding:20px; border-radius:10px; text-align:center; color:#aaa; margin-top:10px;'><h3>👨‍💻 Bob's Box</h3><br><p>Waiting for photon...</p></div>", unsafe_allowed_html=True)
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
    
    # Establish distinct placeholders
    if enable_eve:
        col1, col2, col3 = st.columns(3)
        alice_box = col1.empty()
        middle_box = col2.empty()
        bob_box = col3.empty()
    else:
        col1, col2 = st.columns(2)
        alice_box = col1.empty()
        bob_box = col2.empty()
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(num_photons):
        progress_bar.progress((i + 1) / num_photons)
        status_text.markdown(f"### ⚡ Transmitting Photon **#{i+1}** of {num_photons}...")

        # --- PHASE 1: Alice configures her box and fires ---
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_orient = ARROW_MAP[(a_base, a_bit)]

        # Use clean markdown layout without styling blocks inside empty containers
        alice_box.markdown(
            f"### 👩‍💻 Alice's Box\n"
            f"**State:** `FIRED 🔥`\n\n"
            f"## {a_orient}\n\n"
            f"* **Base:** `[ {a_base} ]`\n"
            f"* **Bit Input:** `{a_bit}`"
        )
        
        if enable_eve:
            middle_box.markdown("\n\n### 🌌 Mid-Channel\n\n✨ Photon traveling from Alice...")
        
        bob_box.markdown(
            f"### 👨‍💻 Bob's Box\n"
            f"**State:** `Waiting... ⏳`\n\n"
            f"## ❓\n\n"
            f"* **Base:** `Selecting...`\n"
            f"* **Bit Read:** `—`"
        )
        
        time.sleep(sim_speed)

        # --- PHASE 2: Mid-transit (Eve's box action if active) ---
        current_bit = a_bit
        current_base = a_base
        current_orient = a_orient
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
            eve_orient_log = current_orient

            middle_box.markdown(
                f"### 🕵️‍♀️ Eve's Box\n"
                f"**State:** `INTERCEPTED 🚨`\n\n"
                f"## {eve_orient_log}\n\n"
                f"* **Base Used:** `[ {eve_base} ]`\n"
                f"* **Bit Read:** `{eve_bit}`"
            )
            time.sleep(sim_speed)

        # --- PHASE 3: Bob's Box receives and measures ---
        b_base = random.choice(['+', 'X'])
        
        if current_base == b_base:
            b_bit = current_bit
        else:
            b_bit = random.randint(0, 1)
            
        b_orient = ARROW_MAP[(b_base, b_bit)]

        bob_box.markdown(
            f"### 👨‍💻 Bob's Box\n"
            f"**State:** `MEASURED 🎯`\n\n"
            f"## {b_orient}\n\n"
            f"* **Base Guessed:** `[ {b_base} ]`\n"
            f"* **Bit Output:** `{b_bit}`"
        )
        
        is_sifted = (a_base == b_base)
        outcome = "🗑️ Discarded"
        if is_sifted:
            outcome = "✅ Match" if (a_bit == b_bit) else "🚨 Mismatch"

        # Organize row data according to parameters
        if enable_eve:
            row_data = {
                "Photon #": i + 1,
                "Alice Orientation": a_orient,
                "Eve Orientation": eve_orient_log,
                "Bob Orientation": b_orient,
                "Outcome": outcome,
                "Alice Bit": a_bit,
                "Bob Bit": b_bit,
                "Bases Match?": "Yes" if is_sifted else "No"
            }
        else:
            row_data = {
                "Photon #": i + 1,
                "Alice Orientation": a_orient,
                "Bob Orientation": b_orient,
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
        st.success("🔒 Keys match perfectly! Secure quantum pipeline finalized.")
    elif len(a_key) == 0:
        st.warning("No bases matched by random chance. Run the simulation again with more photons!")
    else:
        st.error("🚨 Key eavesdropping signature detected! The communication path is insecure.")
