
import streamlit as st

def create_sidebar():
    st.sidebar.title("🎵 Clarinet Simulator")
    st.sidebar.markdown("---")

    st.sidebar.header("Modules")
    st.session_state.acoustic_module_enabled = st.sidebar.toggle(
        "Acoustic Simulation",
        value=st.session_state.get("acoustic_module_enabled", True),
        help="Enable real-time acoustic analysis using OpenWind."
    )
    st.session_state.cnc_module_enabled = st.sidebar.toggle(
        "CNC Toolpath Gen",
        value=st.session_state.get("cnc_module_enabled", False),
        help="Enable G-code generation for manufacturing."
    )
    st.session_state.playtest_module_enabled = st.sidebar.toggle(
        "Virtual Play Test",
        value=st.session_state.get("playtest_module_enabled", False),
        help="Run time-domain simulation with impulse or reed input."
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Simulation Settings")
    st.session_state.simulation_mode = st.sidebar.radio(
        "Simulation Mode",
        options=["Real-Time", "Historical"],
        help="Switch between designing live or matching historical impedance measurements."
    )
