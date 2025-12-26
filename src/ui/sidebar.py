
import streamlit as st
from src.models.clarinet import Clarinet
import json
import pandas as pd

def init_session_state():
    """Initialize session state variables for geometry if they don't exist."""
    if 'temp' not in st.session_state:
        st.session_state['temp'] = 25.0

    # Bore is now a list of dicts for the data editor
    if 'bore_config' not in st.session_state:
        st.session_state['bore_config'] = [
            {"position": 0.0, "radius": 0.0075},
            {"position": 0.6, "radius": 0.0075}
        ]

    # Initialize holes
    if 'holes_config' not in st.session_state:
        st.session_state['holes_config'] = [
            {"pos": 0.5, "rad": 0.002, "chim": 0.005, "label": "Hole 1"},
            {"pos": 0.55, "rad": 0.002, "chim": 0.005, "label": "Hole 2"}
        ]

    # Tracking for file upload to avoid loops
    if 'last_loaded_file' not in st.session_state:
        st.session_state['last_loaded_file'] = None

def load_design_callback():
    """Callback for file uploader."""
    uploaded_file = st.session_state.get('uploaded_file')
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)

            # Update Bore
            if 'bore' in data:
                # Expecting [[pos, rad], ...]
                new_bore = [{"position": b[0], "radius": b[1]} for b in data['bore']]
                st.session_state['bore_config'] = new_bore

            # Update Holes
            if 'holes' in data:
                new_holes = []
                for i, h in enumerate(data['holes']):
                    # Format: [pos, rad, chim, label]
                    label = h[3] if len(h) > 3 else f"Hole {i+1}"
                    new_holes.append({
                        "pos": h[0],
                        "rad": h[1],
                        "chim": h[2],
                        "label": label
                    })
                st.session_state['holes_config'] = new_holes

        except Exception as e:
            st.error(f"Failed to load design: {e}")

def render_sidebar():
    """
    Renders the sidebar interface for geometry configuration.
    Returns:
        tuple: (Clarinet object, float temperature)
    """
    init_session_state()

    st.sidebar.markdown("## ⚙️ Configuration")

    # File Operations
    with st.sidebar.expander("📂 File Operations"):
        st.file_uploader(
            "Load Design (JSON)",
            type="json",
            key='uploaded_file',
            on_change=load_design_callback,
            help="Upload a previously saved .json design file."
        )

    # Material
    st.sidebar.markdown("### 🌡️ Environment")
    st.session_state['temp'] = st.sidebar.number_input(
        "Temperature (°C)",
        value=st.session_state['temp'],
        min_value=0.0, max_value=50.0,
        key="temp_input",
        help="Ambient temperature affects the speed of sound and pitch. Standard is 25°C."
    )

    # Geometry Controls
    st.sidebar.markdown("### 📐 Bore Geometry")
    st.sidebar.caption("Define the main air column profile.")

    # Use Data Editor for Bore
    edited_bore = st.data_editor(
        st.session_state['bore_config'],
        num_rows="dynamic",
        column_config={
            "position": st.column_config.NumberColumn(
                "Position (m)", format="%.4f", min_value=0.0, max_value=2.0,
                help="Distance from the mouthpiece end."
            ),
            "radius": st.column_config.NumberColumn(
                "Radius (m)", format="%.4f", min_value=0.001, max_value=0.1,
                help="Internal radius of the bore at this position."
            )
        },
        key="bore_editor",
        use_container_width=True
    )
    # Ensure bore is sorted by position immediately to avoid confusion
    edited_bore_sorted = sorted(edited_bore, key=lambda x: x['position'])
    st.session_state['bore_config'] = edited_bore_sorted

    # Hole Controls
    st.sidebar.markdown("### 🔘 Tone Holes")
    st.sidebar.caption("Configure the lattice of tone holes.")

    edited_holes = st.data_editor(
        st.session_state['holes_config'],
        num_rows="dynamic",
        column_config={
            "pos": st.column_config.NumberColumn(
                "Position (m)", format="%.4f",
                help="Distance from the mouthpiece end."
            ),
            "rad": st.column_config.NumberColumn(
                "Radius (m)", format="%.4f",
                help="Radius of the tone hole."
            ),
            "chim": st.column_config.NumberColumn(
                "Chimney (m)", format="%.4f",
                help="Height of the tone hole chimney."
            ),
            "label": st.column_config.TextColumn(
                "Label",
                help="Unique name for identification (e.g., 'Register Key')."
            )
        },
        key="holes_editor",
        use_container_width=True
    )

    # CRITICAL: Always keep holes config sorted by position.
    edited_holes_sorted = sorted(edited_holes, key=lambda x: x['pos'])
    st.session_state['holes_config'] = edited_holes_sorted

    # Construct Clarinet Object from State
    clar = Clarinet(name="Custom Prototype")

    # Add Bore (already sorted)
    for b in st.session_state['bore_config']:
        clar.add_bore_point(b['position'], b['radius'])

    # Add Holes (already sorted)
    for h in st.session_state['holes_config']:
        clar.add_hole(h["pos"], h["rad"], h["chim"], h.get("label", ""))

    # Prepare download data
    design_data = {
        "name": clar.name,
        "bore": clar.get_bore_list(),
        "holes": [[h.position, h.radius, h.chimney, h.label] for h in clar.holes]
    }
    st.sidebar.download_button(
        label="💾 Save Design (JSON)",
        data=json.dumps(design_data, indent=4),
        file_name="clarinet_design.json",
        mime="application/json",
        help="Export the current geometry configuration to a JSON file."
    )

    return clar, st.session_state['temp']
