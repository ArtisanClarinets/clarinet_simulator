# clarinet_simulator/config.py
import streamlit as st
import pandas as pd # Added for potential data handling

# --- Preloaded Material Data ---
PRELOADED_MATERIALS = {
    "Grenadilla": {"density": 1.25, "damping": 0.005, "humidity_coeff": 0.01, "description": "Traditional dense wood, dark tone."},
    "ABS Plastic": {"density": 1.05, "damping": 0.015, "humidity_coeff": 0.001, "description": "Common student model material, durable, brighter tone."},
    "Resin Composite": {"density": 1.15, "damping": 0.010, "humidity_coeff": 0.005, "description": "Stable alternative to wood, often used in intermediate models."},
    "Carbon Fiber": {"density": 1.50, "damping": 0.002, "humidity_coeff": 0.0001, "description": "Very rigid and stable, potentially brighter/clearer tone, expensive."},
    "Custom": {"density": 1.0, "damping": 0.01, "humidity_coeff": 0.001, "description": "Define your own material properties below."}
}
MATERIAL_NAMES = list(PRELOADED_MATERIALS.keys())

# --- Page Configuration Function ---
def configure_page():
    """Sets the Streamlit page configuration."""
    st.set_page_config(
        page_title="Clarinet Simulator - Module 1",
        page_icon="🔬", # Updated icon
        layout="wide",
        initial_sidebar_state="expanded"
    )

# --- Initialize Session State (Expanded) ---
def initialize_session_state():
    """Initializes required keys in Streamlit's session state."""
    # Sidebar toggles (Module activation)
    if 'acoustic_module_enabled' not in st.session_state: st.session_state.acoustic_module_enabled = True
    if 'cnc_module_enabled' not in st.session_state: st.session_state.cnc_module_enabled = False
    if 'playtest_module_enabled' not in st.session_state: st.session_state.playtest_module_enabled = False
    if 'repair_module_enabled' not in st.session_state: st.session_state.repair_module_enabled = True # Assume enabled
    if 'collaboration_enabled' not in st.session_state: st.session_state.collaboration_enabled = False # Default off

    # == Design Tab States ==
    # Bore Editor (1.1)
    if 'bore_nodes' not in st.session_state: st.session_state.bore_nodes = pd.DataFrame({'position_mm': [0, 10, 30, 65], 'diameter_mm': [14.8, 14.9, 15.0, 15.2]}) # Example initial nodes
    if 'selected_template' not in st.session_state: st.session_state.selected_template = "Custom"
    if 'show_cross_section' not in st.session_state: st.session_state.show_cross_section = False
    if 'snap_to_wavelength' not in st.session_state: st.session_state.snap_to_wavelength = False

    # Material Selector (Existing)
    if 'selected_material_name' not in st.session_state: st.session_state.selected_material_name = MATERIAL_NAMES[0]
    # (density, damping, humidity_coeff, custom_name initialized based on selection)
    # Ensure these are initialized after selected_material_name is set
    default_material = PRELOADED_MATERIALS[st.session_state.selected_material_name]
    if 'material_density' not in st.session_state: st.session_state.material_density = default_material['density']
    if 'material_damping' not in st.session_state: st.session_state.material_damping = default_material['damping']
    if 'material_humidity_coeff' not in st.session_state: st.session_state.material_humidity_coeff = default_material['humidity_coeff']
    if 'custom_material_name' not in st.session_state: st.session_state.custom_material_name = "My Custom Material"


    # Reconstruction (1.2)
    if 'uploaded_measurement_data' not in st.session_state: st.session_state.uploaded_measurement_data = None
    if 'measurement_data_type' not in st.session_state: st.session_state.measurement_data_type = ".csv"
    if 'smoothing_filter' not in st.session_state: st.session_state.smoothing_filter = "None"

    # == Simulation Tab States ==
    # Impedance Analyzer (1.1)
    if 'sim_freq_min' not in st.session_state: st.session_state.sim_freq_min = 20
    if 'sim_freq_max' not in st.session_state: st.session_state.sim_freq_max = 3000
    if 'sim_temperature' not in st.session_state: st.session_state.sim_temperature = 20.0 # Celsius
    if 'sim_humidity' not in st.session_state: st.session_state.sim_humidity = 50.0 # Percent
    if 'impedance_results' not in st.session_state: st.session_state.impedance_results = {} # Store simulation results {scenario_name: data}
    if 'optimization_goal' not in st.session_state: st.session_state.optimization_goal = "Tune A4=440Hz"

    # Thermo-viscous (1.3)
    if 'thermo_viscous_enabled' not in st.session_state: st.session_state.thermo_viscous_enabled = True
    if 'show_loss_overlay' not in st.session_state: st.session_state.show_loss_overlay = False
    if 'loss_comparison_mode' not in st.session_state: st.session_state.loss_comparison_mode = False

    # == Repair Tab States == (1.5)
    if 'selected_defect' not in st.session_state: st.session_state.selected_defect = "None"
    if 'defect_severity' not in st.session_state: st.session_state.defect_severity = 0.5 # Example scale 0-1
    if 'repair_simulation_results' not in st.session_state: st.session_state.repair_simulation_results = {}

    # == Reports Tab States == (1.4)
    if 'export_format' not in st.session_state: st.session_state.export_format = "STL"
    if 'export_tolerance' not in st.session_state: st.session_state.export_tolerance = 0.05 # mm
    if 'generate_support' not in st.session_state: st.session_state.generate_support = False
    if 'cnc_tool_diameter' not in st.session_state: st.session_state.cnc_tool_diameter = 6.0 # mm

    # == Collaboration States == (1.2, 1.5)
    if 'collaboration_session_id' not in st.session_state: st.session_state.collaboration_session_id = None
    if 'user_annotations' not in st.session_state: st.session_state.user_annotations = [] # List of annotation dicts

    # == Community States == (2)
    if 'selected_community_library' not in st.session_state: st.session_state.selected_community_library = "Official Materials"


# --- Placeholder for bore data update logic ---
# In a real app, this would likely involve more complex state management
# or callbacks to ensure data consistency across modules.
def get_current_bore_data():
    """Simple function to retrieve bore data from session state."""
    if 'bore_nodes' in st.session_state:
        return st.session_state.bore_nodes.copy() # Return a copy to prevent accidental modification
    return pd.DataFrame({'position_mm': [], 'diameter_mm': []})
