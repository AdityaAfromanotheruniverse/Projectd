import streamlit as st
import random
import time
import pandas as pd

st.set_page_config(layout="wide")

st.title("🌌 Graphic BB84 Quantum Photon Simulator")
st.write("Watch actual photons emerge from Alice's box, change states, and enter Bob's measuring box in real time.")

# Dictionary to convert base and bit into standard polarization arrows
ARROW_MAP = {
    ('+', 0): "→",
    ('+', 1): "↑",
    ('X', 0): "↖",
    ('X', 1): "↗"
}

# 1. User Setup
with st.sidebar:
    st.header("🎛️ Simulator Settings")
    num_photons = st.slider("Total Photons to Transmit", min_value=3, max_value=12, value=5)
    enable_eve = st.checkbox("🕵️‍♀️ Deploy Eve (Eavesdropper Intercept)")
    sim_speed = st.slider("Time per phase (seconds)", min_value=1.0, max_value=4.0, value=2.0)

# Initialize Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "running" not in st.session_state:
    st.session_state.running = False

# 2. Controls
c_start, c_reset = st.columns(2)
with c_start:
    start_sim = st.button("🚀 Run Visual Simulation", type="primary")
with c_reset:
    if st.button("🔄 Reset Logs"):
        st.session_state.history = []
        st.session_state.running = False
        st.rerun()

if start_sim:
    st.session_state.history = []  
    st.session_state.running = True

# Helper function to generate beautiful box SVG graphics dynamically
def draw_lab_setup(stage, a_info, e_info, b_info, has_eve):
    alice_color = "#00c0f2"
    eve_color = "#ff4b4b" if has_eve else "#444"
    bob_color = "#28a745"
    
    a_glow = "box-shadow: 0 0 20px #00c0f2; border-width: 4px;" if stage == "alice" else ""
    e_glow = "box-shadow: 0 0 20px #ff4b4b; border-width: 4px;" if stage == "eve" else ""
    b_glow = "box-shadow: 0 0 20px #28a745; border-width: 4px;" if stage == "bob" else ""
    
    a_status = "FIRING... ⚡" if stage == "alice" else "SENT ✅"
    e_status = "IDLE ⏳" if stage == "alice" else ("INTERCEPTING! 🚨" if stage == "eve" else "FORWARDED 🔄")
    b_status = "MEASURING... 🎯" if stage == "bob" else "WAITING... ⏳"
    
    if has_eve:
        html_code = f"""
        <div style="display: flex; justify-content: space-between; align-items: center; background: #111; padding: 30px; border-radius: 15px; min-height: 250px; color: white; font-family: sans-serif;">
            <div style="border: 2px solid {alice_color}; background: #1a2630; padding: 15px; border-radius: 10px; text-align: center; width: 28%; {a_glow}">
                <h4 style="margin: 0; color: {alice_color};">👩‍💻 ALICE'S TRANSMITTER</h4>
                <div style="font-size: 50px; margin: 10px 0; font-weight: bold; color: {alice_color};">{a_info['arrow']}</div>
                <p style="margin: 5px 0; font-size: 13px;">Base: <b>{a_info['base']}</b> | Bit: <b>{a_info['bit']}</b></p>
                <span style="font-size: 11px; color: #aaa;">{a_status}</span>
            </div>
            
            <div style="flex-grow: 1; text-align: center; color: #777;">
                {'<span style="color: #ff4b4b; font-size: 24px;">● ──▶</span>' if stage == "alice" else "──────▶"}
            </div>
            
            <div style="border: 2px dashed {eve_color}; background: #2b1b1b; padding: 15px; border-radius: 10px; text-align: center; width: 28%; {e_glow}">
                <h4 style="margin: 0; color: {eve_color};">🕵️‍♀️ EVE'S INTERCEPTOR</h4>
                <div style="font-size: 50px; margin: 10px 0; font-weight: bold; color: {eve_color};">{e_info['arrow']}</div>
                <p style="margin: 5px 0; font-size: 13px;">Base: <b>{e_info['base']}</b> | Measured: <b>{e_info['bit']}</b></p>
                <span style="font-size: 11px; color: #aaa;">{e_status}</span>
            </div>
            
            <div style="flex-grow: 1; text-align: center; color: #777;">
                {'<span style="color: #28a745; font-size: 24px;">● ──▶</span>' if stage == "eve" else "──────▶"}
            </div>
            
            <div style="border: 2px solid {bob_color}; background: #1b2b1e; padding: 15px; border-radius: 10px; text-align: center; width: 28%; {b_glow}">
                <h4 style="margin: 0; color: {bob_color};">👨‍💻 BOB'S RECEIVER</h4>
                <div style="font-size: 50px; margin: 10px 0; font-weight: bold; color: {bob_color};">{b_info['arrow']}</div>
                <p style="margin: 5px 0; font-size: 13px;">Guess Base: <b>{b_info['base']}</b> | Output: <b>{b_info['bit']}</b></p>
                <span style="font-size: 11px; color: #aaa;">{b_status}</span>
            </div>
        </div>
        """
    else:
        html_code = f"""
        <div style="display: flex; justify-content: space-around; align-items: center; background: #111; padding: 30px; border-radius: 15px; min-height: 250px; color: white; font-family: sans-serif;">
            <div style="border: 2px solid {alice_color}; background: #1a2630; padding: 20px; border-radius: 10px; text-align: center; width: 40%; {a_glow}">
                <h3 style="margin: 0; color: {alice_color};">👩‍💻 ALICE'S TRANSMITTER</h3>
                <div style="font-size: 60px; margin: 15px 0; font-weight: bold; color: {alice_color};">{a_info['arrow']}</div>
                <p style="margin: 5px 0;">Base Filter: <b>{a_info['base']}</b> | Bit Input: <b>{a_info['bit']}</b></p>
                <span style="font-size: 12px; color: #aaa;">{a_status}</span>
            </div>
            
            <div style="width: 15%; text-align: center; color: #00c0f2; font-size: 28px;">
                {'● ────────▶' if stage == "alice" else "─────────▶"}
            </div>
