
import streamlit as st
import numpy as np
import pandas as pd
from src.ui.sidebar import render_sidebar
from src.ui.visualization import plot_geometry, plot_impedance_interactive, plot_phase_interactive
from src.simulation.physics import SimulationEngine
from src.optimization.optimizer import Optimizer
import io

# Set page config at the very top
st.set_page_config(
    page_title="Clarinet R&D Lab",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎷"
)

# Custom CSS for Fortune-1000 polish
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 600;
    }
    .stMetric {
        background-color: #F3F4F6;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<div class="main-header">Clarinet R&D Prototyping Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Advanced Acoustic Simulation & Optimization Environment</div>', unsafe_allow_html=True)

    # Sidebar & Model Creation
    clarinet, temperature = render_sidebar()

    # Session State Initialization for Analysis
    if 'freqs' not in st.session_state:
        st.session_state['freqs'] = None
    if 'imp' not in st.session_state:
        st.session_state['imp'] = None
    if 'sim_done' not in st.session_state:
        st.session_state['sim_done'] = False

    # Reference Trace for Comparison
    if 'ref_freqs' not in st.session_state:
        st.session_state['ref_freqs'] = None
    if 'ref_imp' not in st.session_state:
        st.session_state['ref_imp'] = None
    if 'ref_name' not in st.session_state:
        st.session_state['ref_name'] = None

    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔬 Detailed Analysis", "⚖️ Compare Designs"])

    # --- TAB 1: DASHBOARD ---
    with tab1:
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("### Geometry Preview")
            plot_geometry(clarinet)

            with st.expander("View Raw Geometry Data"):
                st.json({
                    "Bore Points": len(clarinet.bore),
                    "Tone Holes": len(clarinet.holes),
                    "Total Length (m)": f"{clarinet.get_bore_list()[-1][0]:.4f}" if clarinet.bore else "0.0000"
                })

        with col2:
            st.markdown("### Simulation Control")

            if st.button("🚀 Run Physics Simulation", type="primary", use_container_width=True):
                with st.spinner("Computing Finite Element Model (FEM)..."):
                    sim = SimulationEngine()
                    sim.temperature = temperature

                    try:
                        freqs, imp = sim.run_impedance_simulation(clarinet)

                        # Store results
                        st.session_state['freqs'] = freqs
                        st.session_state['imp'] = imp
                        st.session_state['sim_done'] = True
                        st.success("Simulation completed successfully.")

                    except Exception as e:
                        st.error(f"Simulation Failed: {e}")

            if st.session_state.get('sim_done'):
                st.markdown("### Key Results")
                freqs = st.session_state['freqs']
                imp = st.session_state['imp']

                # Basic Plot
                plot_impedance_interactive(freqs, imp, title="Input Impedance Magnitude")

                # Peak Detection
                sim_engine = SimulationEngine()
                peaks = sim_engine.detect_peaks(freqs, imp)

                if len(peaks) > 0:
                    st.markdown("#### Detected Resonances")
                    # Display top 3 peaks as metrics
                    cols = st.columns(3)
                    for i, (f, m) in enumerate(peaks[:3]):
                        with cols[i]:
                            st.metric(f"Mode {i+1}", f"{f:.1f} Hz", f"{m:.1f} dB")

    # --- TAB 2: DETAILED ANALYSIS ---
    with tab2:
        if st.session_state.get('sim_done'):
            freqs = st.session_state['freqs']
            imp = st.session_state['imp']
            sim_engine = SimulationEngine()
            peaks = sim_engine.detect_peaks(freqs, imp)

            col_a, col_b = st.columns([2, 1])

            with col_a:
                st.subheader("Acoustic Impedance (Magnitude & Phase)")
                # Magnitude
                plot_impedance_interactive(freqs, imp, show_phase=False)
                # Phase
                plot_phase_interactive(freqs, imp)

            with col_b:
                st.subheader("Resonance Data")
                if len(peaks) > 0:
                    df_peaks = pd.DataFrame(peaks, columns=["Frequency (Hz)", "Magnitude (dB)"])
                    st.dataframe(df_peaks, use_container_width=True)

                    # --- OPTIMIZATION MODULE ---
                    st.divider()
                    st.markdown("### 🎯 Automated Optimization")
                    st.info("Tune a tone hole position to match a target frequency.")

                    target_freq = st.number_input(
                        "Target Frequency (Hz)",
                        value=float(peaks[0][0]),
                        format="%.2f",
                        help="The desired frequency for the selected resonance mode."
                    )

                    hole_options = [f"{i}: {h.label} (@ {h.position:.3f}m)" for i, h in enumerate(clarinet.holes)]
                    if not hole_options:
                        st.warning("No holes available to tune.")
                        hole_selection = None
                    else:
                        hole_selection = st.selectbox("Select Hole to Tune", hole_options)

                    if hole_selection and st.button("Optimize Position"):
                        hole_idx = int(hole_selection.split(":")[0])

                        with st.spinner("Running Optimization Loop..."):
                            opt = Optimizer(clarinet, sim_engine)
                            res = opt.tune_hole_position(target_freq, hole_idx)

                            if res['success']:
                                st.success(f"Converged! New Position: {res['new_position']:.4f} m")
                                st.metric("Frequency Error", f"{res['error']:.4f} Hz")

                                # Update Session State
                                st.session_state['holes_config'][hole_idx]['pos'] = res['new_position']
                                st.rerun()
                            else:
                                st.error("Optimization failed to converge. Try a closer target or different hole.")

                # --- EXPORT ---
                st.divider()
                st.subheader("Data Export")

                # Create DataFrame
                df_export = pd.DataFrame({
                    "Frequency (Hz)": freqs,
                    "Magnitude (Ohm)": np.abs(imp),
                    "Magnitude (dB)": 20 * np.log10(np.abs(imp)),
                    "Phase (rad)": np.angle(imp),
                    "Phase (deg)": np.angle(imp, deg=True)
                })

                csv = df_export.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Simulation Data (CSV)",
                    data=csv,
                    file_name="simulation_results.csv",
                    mime="text/csv"
                )

        else:
            st.info("Run a simulation in the Dashboard to view detailed analysis.")

    # --- TAB 3: COMPARE DESIGNS ---
    with tab3:
        st.subheader("Design Comparison")

        col_c, col_d = st.columns([3, 1])

        with col_d:
            st.markdown("#### Reference Management")
            if st.session_state.get('sim_done'):
                if st.button("Set Current as Reference"):
                    st.session_state['ref_freqs'] = st.session_state['freqs']
                    st.session_state['ref_imp'] = st.session_state['imp']
                    st.session_state['ref_name'] = f"Ref ({clarinet.name})"
                    st.success("Reference trace set!")
            else:
                st.warning("Run simulation to set reference.")

            if st.session_state['ref_imp'] is not None:
                if st.button("Clear Reference"):
                    st.session_state['ref_imp'] = None
                    st.rerun()

        with col_c:
            if st.session_state.get('sim_done'):
                # Prepare comparison plot
                freqs = st.session_state['freqs']
                imp = st.session_state['imp']

                ref_freqs = st.session_state.get('ref_freqs')
                ref_imp = st.session_state.get('ref_imp')
                ref_name = st.session_state.get('ref_name', "Reference")

                plot_impedance_interactive(
                    freqs, imp,
                    title="Impedance Comparison",
                    ref_freqs=ref_freqs,
                    ref_imp=ref_imp,
                    ref_label=ref_name
                )
            else:
                st.info("Run a simulation to compare against reference.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: grey;'>"
        "Clarinet R&D Lab v1.0 | Powered by OpenWind | "
        "Designed for Professional Acoustics Engineering"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
