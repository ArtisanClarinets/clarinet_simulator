
import streamlit as st
import pandas as pd
import numpy as np
from config import PRELOADED_MATERIALS, get_current_bore_data
from ui_components.bore_viewer_3d import render_bore_vtk, display_vtk_in_streamlit

def create_thermo_viscous_section():
    st.subheader("2. Thermo-Viscous Loss Modeling")
    st.markdown("*(Feature 1.3)*")

    st.session_state.use_thermoviscous_model = st.toggle(
        "Enable Thermo-Viscous Loss Effects",
        value=st.session_state.get("use_thermoviscous_model", True),
        help="Enable OpenWind's realistic loss models like 'diffusive' or 'WebsterLokshin'."
    )

    if not st.session_state.use_thermoviscous_model:
        st.info("Thermo-viscous effects are disabled. Simulation assumes ideal physics.")
