# clarinet_simulator/modules/design_tab/material_selector.py
import streamlit as st
from config import PRELOADED_MATERIALS, MATERIAL_NAMES # Import data from config
from modules.utils import update_material_properties # Import the callback

def create_material_selector_section():
    """Creates the UI section for material selection."""
    st.subheader("2. Material Selection")

    # Dropdown for selecting material
    st.selectbox(
        "Select Material",
        options=MATERIAL_NAMES,
        key='selected_material_name', # Link to session state key
        on_change=update_material_properties, # Use imported callback
        help="Choose a preloaded material or select 'Custom' to define your own."
    )

    # Display description for the selected material
    selected_desc = PRELOADED_MATERIALS[st.session_state.selected_material_name]['description']
    st.caption(f"Description: {selected_desc}")

    # Expander for custom material input
    with st.expander("Custom Material Properties", expanded=(st.session_state.selected_material_name == "Custom")):
        st.text_input(
            "Custom Material Name",
            key='custom_material_name',
            disabled=(st.session_state.selected_material_name != "Custom"),
            help="Give your custom material a unique name."
        )
        st.session_state.material_density = st.number_input(
            "Density (g/cm³)",
            min_value=0.1, max_value=10.0,
            value=st.session_state.material_density,
            step=0.01, format="%.3f",
            disabled=(st.session_state.selected_material_name != "Custom"),
            help="Mass per unit volume. Influences vibration and potentially timbre."
        )
        st.session_state.material_damping = st.number_input(
            "Damping Factor",
            min_value=0.0001, max_value=0.1,
            value=st.session_state.material_damping,
            step=0.0001, format="%.4f",
            disabled=(st.session_state.selected_material_name != "Custom"),
            help="How quickly vibrations dissipate in the material. Affects resonance and brightness."
        )
        st.session_state.material_humidity_coeff = st.number_input(
            "Humidity Coefficient",
            min_value=0.0, max_value=0.1,
            value=st.session_state.material_humidity_coeff,
            step=0.0001, format="%.4f",
            disabled=(st.session_state.selected_material_name != "Custom"),
            help="How much material dimensions might change with humidity (used in advanced FEA)."
        )

    # Display current effective properties (read-only display for clarity)
    st.markdown("---")
    st.markdown("**Current Effective Material Properties:**")
    current_name = st.session_state.custom_material_name if st.session_state.selected_material_name == "Custom" else st.session_state.selected_material_name
    st.text(f"Name: {current_name}")
    st.text(f"Density: {st.session_state.material_density:.3f} g/cm³")
    st.text(f"Damping: {st.session_state.material_damping:.4f}")
    st.text(f"Humidity Coeff: {st.session_state.material_humidity_coeff:.4f}")
