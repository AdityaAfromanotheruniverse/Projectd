import streamlit as st
import random
import time

st.title("Interactive BB84 Protocol Simulation")
st.write("See how Alice and Bob exchange quantum keys, and what happens when Eve spies!")
num_bits = st.slider("Number of Photons Sent per Second", min_value=5, max_value=30, value=10)
enable_eve = st.checkbox("Enable Eve (Eavesdropper)")

if "running" not in st.session_state:
    st.session_state.running = False
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("▶️ Start Simulation"):
        st.session_state.running = True
with col_btn2:
    if st.button("⏸️ Pause Simulation"):
        st.session_state.running = False
display_area = st.empty()
while st.session_state.running:
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(['+', 'X']) for _ in range(num_bits)]
    if enable_eve:
        eve_bases = [random.choice(['+', 'X']) for _ in range(num_bits)]
        eve_bits = [alice_bits[i] if alice_bases[i] == eve_bases[i] else random.randint(0, 1) for i in range(num_bits)
        bob_bases = [random.choice(['+', 'X']) for _ in range(num_bits)]
        bob_bits = [eve_bits[i] if eve_bases[i] == bob_bases[i] else random.randint(0, 1) for i in range(num_bits)]
    else:
        bob_bases = [random.choice(['+', 'X']) for _ in range(num_bits)]
        bob_bits = [alice_bits[i] if alice_bases[i] == bob_bases[i] else random.randint(0, 1) for i in range(num_bits)]
    sifted_alice, sifted_bob = [], []
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_bits[i])
    with display_area.container():
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Alice's Side")
            st.write("**Bits Sent:**", alice_bits)
            st.write("**Bases Used:**", alice_bases)
        with col2:
            st.subheader("Bob's Side")
            st.write("**Bases Guessed:**", bob_bases)
            st.write("**Bits Measured:**", bob_bits)

        st.markdown("---")
        st.subheader("🔑 Final Key Generation")
        st.write("**Alice's Sifted Key:**", sifted_alice)
        st.write("**Bob's Sifted Key:**", sifted_bob)
        
        if sifted_alice == sifted_bob:
            st.success("🎉 Keys Match Perfectly! Secure connection established.")
        else:
            st.error("🚨 Keys Do Not Match! Eve tampered with the signal."
    time.sleep(1)
