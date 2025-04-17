# clarinet_simulator/app.py
import streamlit as st

# Import configuration and initialization functions
from config import configure_page, initialize_session_state

# --- Import Module Creation Functions ---
# Sidebar
from modules.sidebar import create_sidebar

# Design Tab Components
from modules.design_tab.bore_editor import create_bore_editor_section
from modules.design_tab.material_selector import create_material_selector_section
from modules.design_tab.reconstruction import create_reconstruction_section

# Simulation Tab Components
from modules.simulation_tab.impedance_analyzer import create_impedance_analyzer_section
from modules.simulation_tab.thermo_viscous import create_thermo_viscous_section

# Repair Tab Components
from modules.repair_tab.measurement_input import create_measurement_input_section
from modules.repair_tab.diagnostics import create_diagnostics_section

# Reports Tab Components
from modules.reports_tab.dashboard import create_dashboard_section
from modules.reports_tab.export import create_export_section

# Collaboration & Community (can be standalone tabs or integrated)
from modules.collaboration import create_collaboration_section
from modules.community import create_community_section

# --- 1. Configure Page ---
configure_page()

# --- 2. Initialize Session State ---
initialize_session_state()

# --- 3. Create Sidebar ---
create_sidebar()

# --- 4. Main Area ---
st.title("🔬 Clarinet Design & Analysis Suite (Module 1)")

# --- 5. Tab View System ---
# Added Collaboration and Community tabs as examples
tab_design, tab_simulation, tab_repair, tab_reports, tab_collab, tab_community = st.tabs([
    "Design Suite", "Simulation Lab", "Repair Diagnostics", "Reports & Export", "Collaboration", "Community Hub"
])

# --- 6. Populate Tabs ---

# == Design Tab ==
with tab_design:
    st.header("Design Suite: Bore Geometry & Materials")
    st.markdown("*(Features 1.1, 1.2)*")
    create_bore_editor_section()
    st.divider()
    create_material_selector_section()
    st.divider()
    create_reconstruction_section()

# == Simulation Tab ==
with tab_simulation:
    st.header("Simulation Lab: Acoustics & Physics")
    st.markdown("*(Features 1.1, 1.3)*")
    create_impedance_analyzer_section()
    st.divider()
    create_thermo_viscous_section()
    # Placeholder for Virtual Play Test (could be another section/file)
    st.divider()
    st.subheader("3. Virtual Play Test (Placeholder)")
    if st.session_state.playtest_module_enabled:
         st.success("Virtual Play Test Module Enabled")
         st.button("Play Scale (Placeholder)", disabled=True)
    else:
         st.warning("Enable Virtual Play Test module in sidebar.")


# == Repair Tab ==
with tab_repair:
    st.header("Repair Diagnostics Workbench")
    st.markdown("*(Feature 1.5)*")
    create_measurement_input_section()
    st.divider()
    create_diagnostics_section()

# == Reports Tab ==
with tab_reports:
    st.header("Dashboards, Reporting & Manufacturing")
    st.markdown("*(Feature 1.4)*")
    create_dashboard_section()
    st.divider()
    create_export_section()

# == Collaboration Tab ==
with tab_collab:
    # Pass the tab object so content appears within this tab
    create_collaboration_section(tab_collab)

# == Community Tab ==
with tab_community:
    # Pass the tab object
    create_community_section(tab_community)


# --- 7. Footer/Status Area ---
st.markdown("---")
status_modules = [
    f"Acoustic: {'ON' if st.session_state.acoustic_module_enabled else 'OFF'}",
    f"CNC: {'ON' if st.session_state.cnc_module_enabled else 'OFF'}",
    f"PlayTest: {'ON' if st.session_state.playtest_module_enabled else 'OFF'}",
    f"Repair: {'ON' if st.session_state.repair_module_enabled else 'OFF'}",
    f"Collab: {'ON' if st.session_state.collaboration_enabled else 'OFF'}"
]
st.caption(f"Status: {' | '.join(status_modules)}")
if st.session_state.collaboration_session_id:
    st.caption(f"Collaboration Session: {st.session_state.collaboration_session_id}")
