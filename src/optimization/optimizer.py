
import numpy as np
from src.models.clarinet import Clarinet
from src.simulation.physics import SimulationEngine
from scipy.optimize import minimize_scalar

class Optimizer:
    """
    Handles automated optimization of instrument geometry.
    Currently supports tuning hole positions to match target resonance frequencies.
    """
    def __init__(self, clarinet: Clarinet, simulation_engine: SimulationEngine):
        self.clarinet = clarinet
        self.sim = simulation_engine

    def tune_hole_position(self, target_frequency: float, hole_index: int, search_range: float = 0.05):
        """
        Adjusts the position of a specific hole to match the first resonance to target_frequency.

        Args:
            target_frequency (float): The desired frequency in Hz.
            hole_index (int): The index of the hole in the sorted holes list.
            search_range (float): +/- meters to search around current position.

        Returns:
            dict: result with keys 'success', 'new_position', 'error'.
        """
        if hole_index >= len(self.clarinet.holes):
            raise ValueError("Invalid hole index")

        # Get the specific hole object to modify
        hole_to_optimize = self.clarinet.holes[hole_index]
        original_pos = hole_to_optimize.position

        def objective(pos_shift):
            # Apply shift to the specific hole object
            new_pos = original_pos + pos_shift

            # Constraint: Keep within bore bounds (rough check)
            bore_len = self.clarinet.bore[-1].position if self.clarinet.bore else 1.0
            if new_pos < 0 or new_pos > bore_len:
                return 1e6

            hole_to_optimize.position = new_pos

            # Sort holes to maintain physics validity (OpenWind might assume sorted)
            # Note: This changes the order in the list if holes cross!
            # However, our 'hole_to_optimize' variable still points to the correct object instance.
            self.clarinet.holes.sort(key=lambda h: h.position)

            # Run simulation
            # We bypass the cache here because we are modifying geometry in a loop
            # and want fresh results. The simulation engine cache might need to be mindful,
            # but since we modify the object, the cache (if hashing value) should update.
            # Currently our simple cache in physics.py relies on the object reference or value.
            # To be safe, we might need to rely on the physics engine correctly handling it.
            # St.cache_data usually hashes input arguments. If 'clarinet' content changes, hash changes.

            freqs, impedance = self.sim.run_impedance_simulation(self.clarinet)
            peaks = self.sim.detect_peaks(freqs, impedance)

            if not peaks:
                return 1e6 # Penalty if no peaks found

            # Find the peak closest to target
            closest_peak = min(peaks, key=lambda p: abs(p[0] - target_frequency))
            return abs(closest_peak[0] - target_frequency)

        # Optimize
        # bounded method is good for 1D scalar optimization with limits
        result = minimize_scalar(
            objective,
            bounds=(-search_range, search_range),
            method='bounded',
            options={'xatol': 1e-4} # Tolerance of 0.1mm
        )

        # Apply best result final time
        best_pos = original_pos + result.x
        hole_to_optimize.position = best_pos
        self.clarinet.holes.sort(key=lambda h: h.position)

        return {
            "success": result.success,
            "new_position": best_pos,
            "error": result.fun
        }
