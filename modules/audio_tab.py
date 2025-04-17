
import streamlit as st
from modules.simulation_tab.impulse_response import create_impulse_response_section
from modules.simulation_tab.compare_export import create_impulse_comparison_and_export

def create_audio_tab():
    st.title("🎧 Audio & Impulse Response")
    st.caption("Run time-domain simulations and audition impulse responses.")
    
    create_impulse_response_section()
    create_impulse_comparison_and_export()
