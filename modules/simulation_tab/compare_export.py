
import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import io
from core_logic.session_manager import list_saved_impulses, load_saved_impulse
import scipy.io.wavfile as wavfile

def create_impulse_comparison_and_export():
    st.markdown("## 📊 Compare & Export Impulse Responses")

    labels = list_saved_impulses()
    if not labels:
        st.info("No saved impulse responses yet.")
        return

    selected_labels = st.multiselect("Select Responses to Compare", labels, default=labels[:2])
    if selected_labels:
        chart_data = {}
        for lbl in selected_labels:
            idx = labels.index(lbl)
            entry = load_saved_impulse(idx)
            if entry:
                chart_data[lbl] = pd.Series(entry["impulse_response"], index=entry["time_vector"])

        st.line_chart(pd.DataFrame(chart_data))

    # --- EXPORT SECTION ---
    st.markdown("### 📦 Export All Saved Responses (WAV + CSV)")
    if st.button("Download ZIP Archive"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, entry in enumerate(st.session_state.get("saved_impulse_responses", [])):
                base_name = f"impulse_{i+1}_{entry['label'].replace(' ', '_')}_{entry['timestamp']}"
                # Save CSV
                csv_df = pd.DataFrame({
                    "time_s": entry["time_vector"],
                    "pressure_Pa": entry["impulse_response"]
                })
                zip_file.writestr(f"{base_name}.csv", csv_df.to_csv(index=False))

                # Save WAV
                response = entry["impulse_response"]
                norm_response = np.int16((response / np.max(np.abs(response))) * 32767)
                wav_buf = io.BytesIO()
                wavfile.write(wav_buf, 44100, norm_response)
                zip_file.writestr(f"{base_name}.wav", wav_buf.getvalue())

        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer.getvalue(),
            file_name="clarinet_impulse_exports.zip",
            mime="application/zip"
        )
