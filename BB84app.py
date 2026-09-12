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

        # Organize structural rows explicitly
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
