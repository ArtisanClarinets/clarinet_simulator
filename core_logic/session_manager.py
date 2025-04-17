
import streamlit as st
import datetime

def save_bore_with_impulse(bore_df, impulse_response, time_vector, label="ImpulseTest"):
    """
    Save bore data with impulse response and time vector to session state.

    Args:
        bore_df (pd.DataFrame): Bore geometry.
        impulse_response (np.ndarray): Simulated pressure response.
        time_vector (np.ndarray): Corresponding time vector.
        label (str): User-defined label.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    entry = {
        "label": label,
        "timestamp": timestamp,
        "bore_df": bore_df.copy(),
        "impulse_response": impulse_response.copy(),
        "time_vector": time_vector.copy()
    }

    if "saved_impulse_responses" not in st.session_state:
        st.session_state.saved_impulse_responses = []

    st.session_state.saved_impulse_responses.append(entry)

def list_saved_impulses():
    """Return labels of saved entries for display."""
    if "saved_impulse_responses" not in st.session_state:
        return []
    return [f"{i+1}. {e['label']} ({e['timestamp']})" for i, e in enumerate(st.session_state.saved_impulse_responses)]

def load_saved_impulse(index):
    """Return a saved impulse entry by index."""
    if "saved_impulse_responses" not in st.session_state:
        return None
    return st.session_state.saved_impulse_responses[index] if index < len(st.session_state.saved_impulse_responses) else None
