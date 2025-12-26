import numpy as np
from openwind import ImpedanceComputation, InstrumentGeometry, Player
from src.models.clarinet import Clarinet
import matplotlib.pyplot as plt
import streamlit as st

class SimulationEngine:
    """
    Wrapper around the OpenWind physics engine for clarinet acoustic simulation.
    Handles geometry construction, mesh generation, and FEM solving.
    """

    def __init__(self):
        # Configuration could be moved to parameters
        self.frequencies = np.arange(20, 2500, 2) # Extended range and finer resolution
        self.temperature = 25 # degrees Celsius

    @st.cache_data(show_spinner=False)
    def run_impedance_simulation(_self, clarinet: Clarinet):
        """
        Runs impedance simulation for the given clarinet.
        Returns frequencies and complex impedance.

        Using st.cache_data to improve performance on re-runs with identical geometry.
        Note: We use _self to exclude 'self' from hashing if it doesn't change state relevant to the calc.
        But 'clarinet' is a mutable object. Streamlit hashes it by value.
        """
        # We need to recreate the frequency array inside or pass it, as 'self' is excluded from hashing
        # if we follow the pattern strictly. However, let's keep it simple.
        # Ideally, we move the logic out of the class or pass all params explicitly for caching.
        # For now, let's assume 'clarinet' state is the key driver.

        bore_data = clarinet.get_bore_list()
        holes_data = clarinet.get_holes_list()

        try:
            # Create the geometry object explicitly.
            inst = InstrumentGeometry(bore_data, holes_data)

            # Use lower-level classes for maximum control and correctness
            from openwind import InstrumentPhysics, FrequentialSolver

            # For impedance computation, we typically want Unitary Flow input
            player = Player("UNITARY_FLOW")

            # Create Physics Object
            # We can expose losses and other params here for advanced users later
            phys = InstrumentPhysics(inst, _self.temperature, player, losses=True)

            # Create Solver
            solver = FrequentialSolver(phys, _self.frequencies)
            solver.solve()

            # Return frequencies and COMPLEX impedance (for Phase calculation)
            return _self.frequencies, solver.impedance

        except Exception as e:
            raise RuntimeError(f"Simulation failed: {e}")

    def detect_peaks(self, frequencies, impedance):
        """
        Detects impedance peaks which correspond to resonance frequencies.
        Returns a list of tuples: (Frequency, Magnitude_dB).
        """
        # Simple peak detection
        peaks = []
        mag = 20 * np.log10(np.abs(impedance))

        # Basic algorithm: point is higher than neighbors
        # Can be improved with scipy.signal.find_peaks for robustness
        for i in range(1, len(mag)-1):
            if mag[i] > mag[i-1] and mag[i] > mag[i+1]:
                # Filter out very small peaks (noise)
                if mag[i] > -20: # arbitrary threshold, maybe expose this?
                    peaks.append((frequencies[i], mag[i]))
        return peaks
