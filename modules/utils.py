# clarinet_simulator/modules/utils.py
import streamlit as st
from config import PRELOADED_MATERIALS # Import from config.py

# Callback function to update properties when material selection changes
def update_material_properties():
    """
    Updates session state values for density, damping, and humidity
    coefficient based on the selected material name. Does not override
    custom values if 'Custom' is selected.
    """
    material_name = st.session_state.selected_material_name # Get the newly selected name
    if material_name != "Custom":
        st.session_state.material_density = PRELOADED_MATERIALS[material_name]['density']
        st.session_state.material_damping = PRELOADED_MATERIALS[material_name]['damping']
        st.session_state.material_humidity_coeff = PRELOADED_MATERIALS[material_name]['humidity_coeff']
    # If "Custom" is selected, we DON'T override the density/damping/coeff fields,
    # allowing the user to edit them in the expander.




# --- NOTE-FREQUENCY MAP UTILS ---
# clarinet_simulator/modules/utils.py (add this section or place in new module if needed)
import numpy as np

NOTE_NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
A4_FREQ = 440.0
A4_INDEX = 9 + 12 * 4  # Index of A4 in 12-tone system

TRANSPOSITION_OFFSETS = {
    "Bb": -2,
    "A": -3,
    "C": 0,
    "D": -5,
    "Eb": -1
}

def frequency_to_note_name(freq, transposition="Bb"):
    """Map frequency to nearest note name with optional transposition."""
    if freq <= 0:
        return "-"
    half_steps_from_a4 = int(round(12 * np.log2(freq / A4_FREQ)))
    note_index = (half_steps_from_a4 + A4_INDEX + TRANSPOSITION_OFFSETS.get(transposition, 0)) % 12
    octave = (half_steps_from_a4 + A4_INDEX + TRANSPOSITION_OFFSETS.get(transposition, 0)) // 12
    return f"{NOTE_NAMES_SHARP[note_index]}{octave}"

def generate_note_ticks(freq_array, transposition="Bb"):
    """Return a dict mapping frequency to note name labels on the plot."""
    ticks = {}
    for freq in freq_array:
        note = frequency_to_note_name(freq, transposition)
        if note not in ticks.values():
            ticks[freq] = note
    return ticks
