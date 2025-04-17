
import pandas as pd
import numpy as np
from openwind.impedance_computation import ImpedanceComputation
from core_logic.openwind_geometry import load_geometry_from_dataframe

def run_openwind_simulation(bore_nodes_df, material_props, env_params, freq_min, freq_max, excitation='Volume Flow', defect_info=None):
    geom = load_geometry_from_dataframe(bore_nodes_df, unit='mm')
    geom.set_air_properties(temp=env_params['temp'], humidity=env_params['humidity'])

    if material_props.get("model") == "thermoviscous":
        geom.set_losses_model("diffusive")
    else:
        geom.set_losses_model("lossless")

    sim = ImpedanceComputation(geometry=geom)

    if excitation == 'Volume Flow':
        sim.set_excitation_flow()
    elif excitation == 'Pressure':
        sim.set_excitation_pressure()

    sim.compute_impedance(freq_min, freq_max)
    return sim.get_pressure_flow()
