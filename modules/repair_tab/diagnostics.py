# clarinet_simulator/modules/repair_tab/diagnostics.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from core_logic.impedance import run_openwind_simulation
from config import get_current_bore_data
from modules.utils import frequency_to_note_name  # new import


def create_diagnostics_section():
    """Creates the UI for advanced repair diagnostics."""
    st.subheader("2. Advanced Repair Diagnostics")
    st.markdown("*(Feature 1.5)*")

    if not st.session_state.repair_module_enabled:
        st.warning("Repair Diagnostics module is not enabled.")
        return

    col1, col2 = st.columns(2)

    # --- Column 1: Defect Simulation UI ---
    with col1:
        st.markdown("**Simulate Defect Impact**")
        defect_options = ["None", "Crack (Barrel Top)", "Worn Pad (Register Key)",
                          "Misaligned Joint (Barrel-Upper)", "Bore Obstruction"]
        st.session_state.selected_defect = st.selectbox(
            "Select Defect to Simulate:", defect_options, key="sb_defect",
            help="Choose a defect type to simulate its effect on impedance."
        )

        defect_info_to_sim = None
        if st.session_state.selected_defect != "None":
            st.session_state.defect_severity = st.slider(
                f"Severity/Size of {st.session_state.selected_defect}",
                min_value=0.1, max_value=1.0, value=st.session_state.get("defect_severity", 0.5), step=0.1,
                key="slider_defect_severity",
                help="Adjust how severe or large the defect is."
            )

            defect_position_map = {
                "Crack (Barrel Top)": 5.0,
                "Worn Pad (Register Key)": 150.0,
                "Misaligned Joint (Barrel-Upper)": 65.0,
                "Bore Obstruction": 100.0
            }

            defect_info_to_sim = {
                'type': st.session_state.selected_defect,
                'position': defect_position_map.get(st.session_state.selected_defect, 0),
                'severity': st.session_state.defect_severity
            }

            st.caption(f"🛠️ Simulating defect at approx. position {defect_info_to_sim['position']:.1f} mm")

        if st.button("Simulate Pre- vs. Post-Repair Acoustics", type="primary",
                     disabled=(st.session_state.selected_defect == "None")):
            st.info(f"Simulating baseline vs. defect impact: '{st.session_state.selected_defect}'...")

            bore_data = get_current_bore_data()
            if bore_data.empty:
                st.error("Bore data is empty. Please define in the Design tab.")
                return

            material_props = {
                "density": st.session_state.material_density,
                "damping": st.session_state.material_damping
            }
            env_params = {
                "temp": st.session_state.sim_temperature,
                "humidity": st.session_state.sim_humidity
            }
            freq_min = st.session_state.sim_freq_min
            freq_max = st.session_state.sim_freq_max

            sim_results = {}

            with st.spinner("Running baseline simulation..."):
                baseline_result = run_openwind_simulation(
                    bore_data, material_props, env_params, freq_min, freq_max, defect_info=None
                )

            if not baseline_result.empty:
                sim_results['pre_repair'] = baseline_result
                st.success("✅ Baseline simulation complete.")

                with st.spinner(f"Running simulation with defect '{st.session_state.selected_defect}'..."):
                    defect_result = run_openwind_simulation(
                        bore_data, material_props, env_params, freq_min, freq_max, defect_info=defect_info_to_sim
                    )

                if not defect_result.empty:
                    sim_results['post_repair_sim'] = defect_result
                    st.success("✅ Defect simulation complete.")
                else:
                    st.warning("⚠️ Defect simulation failed or returned no data.")
            else:
                st.error("❌ Baseline simulation failed. Cannot proceed.")

            st.session_state.repair_simulation_results = sim_results
            st.rerun()

        st.divider()
        st.markdown("**📚 Defect Library & Suggestions**")
        st.button("Load Common Defects from Library", help="Feature 1.5 - Not Implemented")
        st.info("🔍 Predictive adjustments based on defect database (Not Implemented)")


    # --- Column 2: Visualization ---
    with col2:
        st.markdown("**📈 Diagnostic Visualization**")

        # Add transposition dropdown
        transposition_choice = st.selectbox("Note Display Transposition", ["Bb", "A", "C", "D", "Eb"], index=0)

        sim_data = st.session_state.get("repair_simulation_results", {})
        if 'pre_repair' in sim_data and 'post_repair_sim' in sim_data:
            pre_data = sim_data['pre_repair']
            post_data = sim_data['post_repair_sim']

            pre_mag_db = 20 * np.log10(np.maximum(pre_data['magnitude_ohm'], 1e-8) / 2e-5)
            post_mag_db = 20 * np.log10(np.maximum(post_data['magnitude_ohm'], 1e-8) / 2e-5)

            # Map frequency to note names
            hover_note_labels = [frequency_to_note_name(f, transposition_choice) for f in pre_data['frequency_hz']]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pre_data['frequency_hz'], y=pre_mag_db,
                mode='lines+markers',
                name='Baseline (Pre-Repair)',
                text=hover_note_labels, hoverinfo='text+y'
            ))
            fig.add_trace(go.Scatter(
                x=post_data['frequency_hz'], y=post_mag_db,
                mode='lines+markers',
                name=f'Simulated Defect ({st.session_state.selected_defect})',
                line=dict(dash='dot', color='red'),
                text=hover_note_labels, hoverinfo='text+y'
            ))
            fig.update_layout(
                title="Acoustic Impact of Simulated Defect (Impedance Magnitude)",
                xaxis_title="Frequency (Hz)",
                yaxis_title="Magnitude (dB re 20µPa)",
                height=400, margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("**📊 Comparison with Field Data**")
            if 'repair_uploaded_data' in st.session_state and st.session_state.repair_uploaded_data:
                st.info("🧪 Comparison logic with uploaded field data will appear here. [Feature 1.5]")
            else:
                st.info("📂 Upload field data in Section 1 to enable acoustic validation.")
        else:
            st.info("Run a defect simulation to see comparison plots.")
