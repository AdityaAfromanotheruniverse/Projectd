import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(layout="wide")

st.title("🌌 Real-Time Animated BB84 Protocol Simulator")
st.write("Watch individual photons physically travel through the quantum channel from box to box.")

# Standard polarization arrow map
ARROW_MAP = {
    ('+', 0): "→",
    ('+', 1): "↑",
    ('X', 0): "↖",
    ('X', 1): "↗"
}

# 1. User Dashboard Settings
with st.sidebar:
    st.header("🎛️ Simulator Settings")
    num_photons = st.slider("Total Photons to Transmit", min_value=3, max_value=12, value=5)
    enable_eve = st.checkbox("🕵️‍♀️ Deploy Eve (Eavesdropper Intercept)", value=True)
    sim_speed = st.slider("Travel Pacing (Seconds per step)", min_value=0.2, max_value=1.5, value=0.5)

# Initialize background metrics data logging
if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = False

# 2. Control Layout
c_start, c_reset = st.columns(2)
with c_start:
    start_sim = st.button("🚀 Start Live Particle Simulation", type="primary")
with c_reset:
    if st.button("🔄 Clear Lab Logs"):
        st.session_state.history = []
        st.session_state.running = False
        st.rerun()

if start_sim:
    st.session_state.history = []  
    st.session_state.running = True

# Helper to render the entire continuous lab channel layout frame
def render_arena(photon_position, current_arrow, a_val, e_val, b_val, show_eve):
    # Active element highlight styles
    active_alice = "border: 3px solid #00c0f2; box-shadow: 0 0 15px #00c0f2; background: #f0f9ff;" if photon_position == "alice" else "border: 2px solid #ccc; background: #fafafa;"
    active_eve = "border: 3px solid #ff4b4b; box-shadow: 0 0 15px #ff4b4b; background: #fff5f5;" if photon_position == "eve" else "border: 2px dashed #aaa; background: #fafafa;"
    active_bob = "border: 3px solid #28a745; box-shadow: 0 0 15px #28a745; background: #f4fff6;" if photon_position == "bob" else "border: 2px solid #ccc; background: #fafafa;"
    
    # Render traveling pathway steps
    t1 = f"<b style='color:#00c0f2; font-size:24px;'>●───</b>" if photon_position == "transit1_a" else "────"
    t2 = f"<b style='color:#00c0f2; font-size:24px;'>──●─</b>" if photon_position == "transit1_b" else "────"
    t3 = f"<b style='color:#ff4b4b; font-size:24px;'>───●</b>" if photon_position == "transit1_c" else "────"
    
    t4 = f"<b style='color:#ff4b4b; font-size:24px;'>●───</b>" if photon_position == "transit2_a" else "────"
    t5 = f"<b style='color:#ff4b4b; font-size:24px;'>──●─</b>" if photon_position == "transit2_b" else "────"
    t6 = f"<b style='color:#28a745; font-size:24px;'>───●</b>" if photon_position == "transit2_c" else "────"

    if show_eve:
        return f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 25px; border-radius: 12px; background: #f9f9f9; border: 1px solid #ddd; font-family: sans-serif; color: #333;">
            <!-- ALICE -->
            <div style="width: 26%; text-align: center; padding: 15px; border-radius: 8px; {active_alice}">
                <h4 style="margin: 0; color: #00c0f2;">👩‍💻 Alice's Box</h4>
                <h1 style="margin: 10px 0; font-size: 42px; color: #00c0f2;">{a_val['arrow']}</h1>
                <p style="margin: 0; font-size: 13px;">Base: <b>{a_val['base']}</b> | Bit: <b>{a_val['bit']}</b></p>
            </div>
            <!-- FIBER LINE 1 -->
            <div style="flex-grow: 1; text-align: center; letter-spacing: 2px; font-family: monospace; color: #bbb;">
                {t1}{t2}{t3}
            </div>
            <!-- EVE -->
            <div style="width: 26%; text-align: center; padding: 15px; border-radius: 8px; {active_eve}">
                <h4 style="margin: 0; color: #ff4b4b;">🕵️‍♀️ Eve's Box</h4>
                <h1 style="margin: 10px 0; font-size: 42px; color: #ff4b4b;">{e_val['arrow']}</h1>
                <p style="margin: 0; font-size: 13px;">Base: <b>{e_val['base']}</b> | Read: <b>{e_val['bit']}</b></p>
            </div>
            <!-- FIBER LINE 2 -->
            <div style="flex-grow: 1; text-align: center; letter-spacing: 2px; font-family: monospace; color: #bbb;">
                {t4}{t5}{t6}
            </div>
            <!-- BOB -->
            <div style="width: 26%; text-align: center; padding: 15px; border-radius: 8px; {active_bob}">
                <h4 style="margin: 0; color: #28a745;">👨‍💻 Bob's Box</h4>
                <h1 style="margin: 10px 0; font-size: 42px; color: #28a745;">{b_val['arrow']}</h1>
                <p style="margin: 0; font-size: 13px;">Base: <b>{b_val['base']}</b> | Output: <b>{b_val['bit']}</b></p>
            </div>
        </div>
        """
    else:
        # Layout structure optimized for direct 2-box connection
        return f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 25px; border-radius: 12px; background: #f9f9f9; border: 1px solid #ddd; font-family: sans-serif; color: #333;">
            <div style="width: 40%; text-align: center; padding: 15px; border-radius: 8px; {active_alice}">
                <h4 style="margin: 0; color: #00c0f2;">👩‍💻 Alice's Box</h4>
                <h1 style="margin: 10px 0; font-size: 45px; color: #00c0f2;">{a_val['arrow']}</h1>
                <p style="margin: 0;">Base: <b>{a_val['base']}</b> | Bit: <b>{a_val['bit']}</b></p>
            </div>
            <div style="flex-grow: 1; text-align: center; letter-spacing: 4px; font-family: monospace; color: #bbb; font-size: 20px;">
                {t1}{t2}{t3}{t4}{t5}{t6}
            </div>
            <div style="width: 40%; text-align: center; padding: 15px; border-radius: 8px; {active_bob}">
                <h4 style="margin: 0; color: #28a745;">👨‍💻 Bob's Box</h4>
                <h1 style="margin: 10px 0; font-size: 45px; color: #28a745;">{b_val['arrow']}</h1>
                <p style="margin: 0;">Base: <b>{b_val['base']}</b> | Output: <b>{b_val['bit']}</b></p>
            </div>
        </div>
        """

# 3. Active Real-Time Animation Loop
if st.session_state.running:
    st.markdown("---")
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # FIX: Initialize with st.empty() placeholder container instead of an unparameterized st.html()
    arena_canvas = st.empty()

    for i in range(num_photons):
        progress_bar.progress((i + 1) / num_photons)
        status_text.markdown(f"### ⚡ Simulating Photon **#{i+1}** of {num_photons}...")

        # Setup initial telemetry vectors
        a_bit = random.randint(0, 1)
        a_base = random.choice(['+', 'X'])
        a_arrow = ARROW_MAP[(a_base, a_bit)]
        
        current_bit = a_bit
        current_base = a_base
        current_arrow = a_arrow
        
        e_base_log, e_arrow_log, e_bit_log = "—", "—", "—"

        if enable_eve:
            eve_base = random.choice(['+', 'X'])
            eve_bit = a_bit if eve_base == a_base else random.randint(0, 1)
            eve_arrow = ARROW_MAP[(eve_base, eve_bit)]
            
            current_bit = eve_bit
            current_base = eve_base
            current_arrow = eve_arrow
            
            e_base_log, e_arrow_log, e_bit_log = eve_base, eve_arrow, eve_bit

        b_base = random.choice(['+', 'X'])
        b_bit = current_bit if current_base == b_base else random.randint(0, 1)
        b_arrow = ARROW_MAP[(b_base, b_bit)]

        # --- STEP 1: Photon is created inside Alice's Box ---
        a_data = {"arrow": a_arrow, "base": a_base, "bit": a_bit}
        e_data = {"arrow": "❓", "base": "—", "bit": "—"}
        b_data = {"arrow": "❓", "base": "—", "bit": "—"}
        
        arena_canvas.html(render_arena("alice", a_arrow, a_data, e_data, b_data, enable_eve))
        time.sleep(sim_speed)

        # --- STEP 2: Photon crawls down channel 1 ---
        arena_canvas.html(render_arena("transit1_a", a_arrow, a_data, e_data, b_data, enable_eve))
        time.sleep(sim_speed)
        arena_canvas.html(render_arena("transit1_b", a_arrow, a_data, e_data, b_data, enable_eve))
        time.sleep(sim_speed)
        arena_canvas.html(render_arena("transit1_c", a_arrow, a_data, e_data, b_data, enable_eve))
        time.sleep(sim_speed)

        # --- STEP 3: Photon processed by Eve's Box ---
        if enable_eve:
            e_data = {"arrow": eve_arrow, "base": eve_base, "bit": eve_bit}
            arena_canvas.html(render_arena("eve", eve_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)

            # --- STEP 4: Photon crawls down channel 2 ---
            arena_canvas.html(render_arena("transit2_a", eve_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)
            arena_canvas.html(render_arena("transit2_b", eve_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)
            arena_canvas.html(render_arena("transit2_c", eve_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)
        else:
            # Continues crawling smoothly across channel if channel is empty
            arena_canvas.html(render_arena("transit2_a", a_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)
            arena_canvas.html(render_arena("transit2_b", a_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)
            arena_canvas.html(render_arena("transit2_c", a_arrow, a_data, e_data, b_data, enable_eve))
            time.sleep(sim_speed)

        # --- STEP 5: Photon lands in Bob's Box ---
        b_data = {"arrow": b_arrow, "base": b_base, "bit": b_bit}
        arena_canvas.html(render_arena("bob", current_arrow, a_data, e_data, b_data, enable_eve))
        time.sleep(sim_speed)

        # --- PROCESS MATRIX LOG ROW ---
        is_sifted = (a_base == b_base)
        outcome = "🗑️ Discarded"
        if is_sifted:
