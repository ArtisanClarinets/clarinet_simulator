
import pandas as pd
import numpy as np
from openwind.temporal.temporal_solver import TemporalSolver
from core_logic.openwind_geometry import load_geometry_from_dataframe

def generate_impulse_response(bore_nodes_df, reed_params=None, duration=0.05, fs=44100):
    """
    Generates a time-domain impulse response using OpenWind's temporal solver.

    Args:
        bore_nodes_df (pd.DataFrame): Bore geometry.
        reed_params (dict, optional): Reed physical parameters.
        duration (float): Simulation duration in seconds.
        fs (int): Sample rate (Hz).

    Returns:
        tuple: (time_vector, pressure_signal)
    """
    geom = load_geometry_from_dataframe(bore_nodes_df, unit='mm')

    # Configure solver
    solver = TemporalSolver(geometry=geom)
    solver.configure_impulse_input(duration=duration, sample_rate=fs)

    if reed_params:
        solver.add_reed(reed_type="scaled", parameters=reed_params)

    solver.run()
    time_vec, pressure_response = solver.get_impulse_response()
    return time_vec, pressure_response
