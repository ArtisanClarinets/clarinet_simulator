
import streamlit as st
from config import get_current_bore_data
from core_logic.manufacturing import export_to_openwind_file, generate_stl_content

def create_export_section():
    st.subheader("Export & Manufacturing Preparation")
    st.markdown("*(Feature 1.4)*")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Export Design Files**")
        export_options = ["STL (3D Print)", "OW Geometry (.ow)"]
        st.session_state.export_format = st.selectbox(
            "Select Export Format:", export_options, key="sb_export_format"
        )

        if st.session_state.export_format == "OW Geometry (.ow)":
            if st.button("Export to OpenWind .ow File"):
                path = export_to_openwind_file(get_current_bore_data())
                st.success(f"Saved to: {path}")
