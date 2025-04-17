
import streamlit as st
import numpy as np
import pandas as pd
import scipy.io.wavfile as wavfile
import tempfile
import os
from config import get_current_bore_data
from core_logic.temporal_simulation import generate_impulse_response
from core_logic.session_manager import save_bore_with_impulse, list_saved_impulses, load_saved_impulse

def create_impulse_response_section():
    st.subheader("🎧 Impulse Response & Audio Synthesis")
    st.markdown("*(Feature 1.6)*")

    # --- REED PARAMETERS ---
    st.markdown("**Reed Settings**")
    with st.expander("Advanced Reed Parameters"):
        reed_params = {
            "mass": st.slider("Reed Mass (g)", 0.01, 0.3, 0.05, 0.01),
            "stiffness": st.slider("Reed Stiffness (N/m)", 100, 10000, 2000, 100),
            "damping": st.slider("Reed Damping", 0.1, 5.0, 0.8, 0.1),
        }
    duration = st.slider("Simulation Duration (s)", 0.01, 0.2, 0.05, 0.01)
    fs = st.selectbox("Sample Rate (Hz)", [22050, 44100, 48000], index=1)

    # --- RUN SIMULATION ---
    if st.button("Generate Impulse Response"):
        bore_nodes_df = get_current_bore_data()
        time, response = generate_impulse_response(bore_nodes_df, reed_params, duration, fs)

        st.success("Impulse Response Generated!")
        st.line_chart(pd.DataFrame({"Time (s)": time, "Pressure (Pa)": response}))

        # Normalize to 16-bit PCM range
        norm_response = np.int16((response / np.max(np.abs(response))) * 32767)

        # Save to temporary WAV file
        tmp_wav_path = os.path.join(tempfile.gettempdir(), "clarinet_impulse.wav")
        wavfile.write(tmp_wav_path, fs, norm_response)

        # AUDIO PLAYER
        st.audio(tmp_wav_path, format="audio/wav")

        # DOWNLOAD LINK
        with open(tmp_wav_path, "rb") as file:
            st.download_button("Download WAV", data=file, file_name="clarinet_impulse.wav", mime="audio/wav")

        # SAVE SESSION
        if st.button("Save This Result"):
            save_bore_with_impulse(bore_nodes_df, response, time, label="My Latest Test")
            st.success("Saved to session!")

    # --- LOAD & VIEW PREVIOUS RESULTS ---
    st.markdown("### 📁 Load Saved Impulse Responses")
    labels = list_saved_impulses()
    if labels:
        selected = st.selectbox("Choose a Saved Response:", labels, index=0)
        if st.button("View Saved Result"):
            idx = labels.index(selected)
            saved = load_saved_impulse(idx)
            st.line_chart(pd.DataFrame({"Time (s)": saved["time_vector"], "Pressure (Pa)": saved["impulse_response"]}))
