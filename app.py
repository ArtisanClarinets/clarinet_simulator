
import streamlit as st
import numpy as np
import pandas as pd
from src.ui.sidebar import render_sidebar
from src.ui.visualization import plot_geometry, plot_impedance_interactive
from src.simulation.physics import SimulationEngine
from src.optimization.optimizer import Optimizer

st.set_page_config(page_title="Clarinet R&D Lab", layout="wide")

st.title("Clarinet R&D Prototyping Lab")
st.markdown("""
**Fortune 1000 Grade Simulation Environment**
Design, Simulate, and Optimize Clarinet Geometries using `openwind`.
""")

# Sidebar & Model Creation
clarinet, temperature = render_sidebar()

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Geometry Visualization")
    plot_geometry(clarinet)

    with st.expander("Raw Geometry Data"):
        st.write("Bore:", clarinet.get_bore_list())
        st.write("Holes:", clarinet.get_holes_list())

with col2:
    st.subheader("Simulation & Analysis")

    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running Physics Simulation..."):
            sim = SimulationEngine()
            sim.temperature = temperature

            try:
                freqs, imp = sim.run_impedance_simulation(clarinet)

                # Store in session state to persist
                st.session_state['freqs'] = freqs
                st.session_state['imp'] = imp
                st.session_state['sim_done'] = True

            except Exception as e:
                st.error(f"Simulation Failed: {e}")

    if st.session_state.get('sim_done', False):
        freqs = st.session_state['freqs']
        imp = st.session_state['imp']

        plot_impedance_interactive(freqs, imp)

        sim_engine = SimulationEngine() # Re-instantiate for helper methods
        peaks = sim_engine.detect_peaks(freqs, imp)

        st.info(f"Detected {len(peaks)} Resonance Peaks")
        if len(peaks) > 0:
            df_peaks = pd.DataFrame(peaks, columns=["Frequency (Hz)", "Magnitude (dB)"])
            st.dataframe(df_peaks)

            # Optimization Section
            st.markdown("### Optimization")
            target_freq = st.number_input("Target Frequency for 1st Peak", value=float(peaks[0][0]))

            # Identify holes by label for selection
            hole_options = [f"{i}: {h.label}" for i, h in enumerate(clarinet.holes)]
            hole_selection = st.selectbox("Select Hole to Tune", hole_options) if hole_options else None

            if hole_selection and st.button("Optimize Hole Position"):
                hole_idx = int(hole_selection.split(":")[0])

                with st.spinner("Optimizing..."):
                    opt = Optimizer(clarinet, sim_engine)
                    res = opt.tune_hole_position(target_freq, hole_idx)

                    if res['success']:
                        st.success(f"Optimization Successful! New Position: {res['new_position']:.4f} m")
                        st.metric("Error", f"{res['error']:.4f}")

                        # UPDATE SESSION STATE TO PERSIST CHANGE
                        # We rely on the invariant that st.session_state['holes_config'] is sorted
                        # and clarinet.holes is sorted, thus indices match.

                        st.session_state['holes_config'][hole_idx]['pos'] = res['new_position']
                        st.rerun()

                    else:
                        st.error("Optimization failed to converge.")

# Footer
st.markdown("---")
st.markdown("Built with `openwind`, `scipy`, and `streamlit`.")
