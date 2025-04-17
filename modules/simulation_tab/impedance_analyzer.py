# clarinet_simulator/modules/simulation_tab/impedance_analyzer.py

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from config import get_current_bore_data
from core_logic.impedance import run_openwind_simulation
from modules.utils.note_utils import freq_to_note, detect_impedance_peaks, TRANSPOSITION_MAP


COLOR_MAP = {
    "in_tune": "#00cc96",
    "slightly_off": "#ffa15a",
    "off": "#ef553b"
}

def create_impedance_analyzer_section():
    st.subheader("1. Impedance Simulation & Analysis")
    st.markdown("*(Feature 1.1)*")

    if not st.session_state.acoustic_module_enabled:
        st.warning("Acoustic Simulation module is disabled in the sidebar.")
        return

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Simulation Parameters**")
        st.session_state.sim_freq_min, st.session_state.sim_freq_max = st.slider(
            "Frequency Range (Hz)", 0, 5000,
            (st.session_state.sim_freq_min, st.session_state.sim_freq_max),
            50, key="slider_freq_range"
        )
        st.session_state.sim_temperature = st.slider(
            "Temperature (°C)", -10.0, 40.0, st.session_state.sim_temperature,
            0.5, format="%.1f", key="slider_temp",
            help="Affects speed of sound and visco-thermal losses."
        )
        st.session_state.sim_humidity = st.slider(
            "Relative Humidity (%)", 0.0, 100.0, st.session_state.sim_humidity,
            1.0, format="%.0f%%", key="slider_humidity",
            help="Affects air density and visco-thermal losses."
        )
        excitation_type = st.selectbox(
            "Excitation Type:", ["Volume Flow", "Pressure"],
            key="sb_excitation", help="Simulation input type"
        )

        st.divider()
        st.markdown("**Run Simulation**")
        current_scenario_name = st.text_input("Scenario Name:", value="Current Design", key="txt_scenario_name")

        if st.button("Run Impedance Simulation", type="primary"):
            st.info(f"Running simulation for '{current_scenario_name}'...")
            bore_data = get_current_bore_data()
            if bore_data.empty:
                st.error("Cannot run simulation: Bore data is empty.")
                return

            material_props = {
                "name": st.session_state.custom_material_name if st.session_state.selected_material_name == "Custom" else st.session_state.selected_material_name,
                "density": st.session_state.material_density,
                "damping": st.session_state.material_damping,
                "humidity_coeff": st.session_state.material_humidity_coeff
            }

            env_params = {
                "temp": st.session_state.sim_temperature,
                "humidity": st.session_state.sim_humidity
            }

            with st.spinner("Calculating impedance..."):
                result_data = run_openwind_simulation(
                    bore_nodes_df=bore_data,
                    material_props=material_props,
                    env_params=env_params,
                    freq_min=st.session_state.sim_freq_min,
                    freq_max=st.session_state.sim_freq_max,
                    excitation=excitation_type,
                    defect_info=None
                )

            if not result_data.empty:
                st.session_state.impedance_results[current_scenario_name] = result_data
                st.success(f"Simulation '{current_scenario_name}' complete.")
                st.rerun()
            else:
                st.error(f"Simulation '{current_scenario_name}' failed or returned no data.")

        st.divider()
        st.markdown("**Analysis & Optimization**")
        st.info("Advanced peak tuning and optimization will be added soon.")

    with col2:
        st.markdown("**Output Visualization**")
        if not st.session_state.impedance_results:
            st.info("Run an impedance simulation to see results.")
            return

        fig_impedance = go.Figure()
        scenarios_to_plot = st.session_state.get('ms_compare_scenarios') or [current_scenario_name]
        plot_phase = st.checkbox("Plot Phase (Secondary Axis)", value=False)
        overlay_harmonics = st.checkbox("Overlay Harmonic Series", value=True)

        for name in scenarios_to_plot:
            if name in st.session_state.impedance_results:
                data = st.session_state.impedance_results[name]
                if data.empty:
                    continue
                mags = data['magnitude_db'].values if 'magnitude_db' in data.columns else 20 * np.log10(data['magnitude_ohm'].values / 2e-5)
                freqs = data['frequency_hz'].values
                fig_impedance.add_trace(go.Scatter(x=freqs, y=mags, mode='lines', name=f'{name} - Magnitude (dB)'))
                if plot_phase and 'phase_deg' in data.columns:
                    fig_impedance.add_trace(go.Scatter(
                        x=freqs, y=data['phase_deg'], mode='lines',
                        name=f'{name} - Phase (°)', yaxis="y2", line=dict(dash='dot')
                    ))
                if overlay_harmonics:
                    fundamental = st.number_input("Fundamental Frequency (Hz)", value=147.0, step=1.0)
                    harmonics = [fundamental * i for i in range(1, 10) if fundamental * i <= st.session_state.sim_freq_max]
                    for i, f in enumerate(harmonics, start=1):
                        fig_impedance.add_shape(type='line', x0=f, x1=f, y0=0, y1=150, line=dict(dash='dot', width=1))
                        fig_impedance.add_annotation(x=f, y=140, text=f"H{i}", showarrow=False, font=dict(size=10))

        fig_impedance.update_layout(
            title="Input Impedance (Simulation Results)",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Impedance Magnitude (dB re 20µPa)",
            yaxis=dict(range=[0, 160] if not fig_impedance.data else None),
            yaxis2=dict(title="Phase (°)", overlaying="y", side="right", range=[-180, 180], showgrid=False, visible=plot_phase),
            height=450,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_impedance, use_container_width=True)

        st.markdown("**Tuning Accuracy (Peak Analysis)**")
        clarinet_type = st.selectbox("Instrument Transposition:", list(TRANSPOSITION_MAP.keys()), index=0)
        transpo_semitones = TRANSPOSITION_MAP[clarinet_type]

        target_notes = st.multiselect("Target Notes (optional):",
            ["D3", "A3", "C4", "E4", "G4", "B4", "D5", "F5", "A5", "C6"], default=["C4", "E4", "G4"])

        data = st.session_state.impedance_results[current_scenario_name]
        freqs = data['frequency_hz'].values
        mags = data['magnitude_db'].values if 'magnitude_db' in data.columns else 20 * np.log10(data['magnitude_ohm'].values / 2e-5)

        peak_freqs = detect_impedance_peaks(freqs, mags)
        result_table = []

        cols = st.columns(min(len(peak_freqs), 8))
        for i, f in enumerate(peak_freqs):
            note, cents = freq_to_note(f, transpo_semitones)
            color = COLOR_MAP["in_tune"] if abs(cents) <= 5 else COLOR_MAP["slightly_off"] if abs(cents) <= 20 else COLOR_MAP["off"]
            cols[i % 8].markdown(f"<div style='color:{color};font-weight:bold'>{note}<br>{cents:+}¢<br>{f:.1f} Hz</div>", unsafe_allow_html=True)
            result_table.append({"Frequency (Hz)": f, "Note": note, "Cents Deviation": cents})

        st.markdown("**\U0001F4C4 Export Peaks as CSV**")
        df_export = pd.DataFrame(result_table)
        st.download_button("Download Peaks", df_export.to_csv(index=False), "impedance_peaks.csv", "text/csv")
