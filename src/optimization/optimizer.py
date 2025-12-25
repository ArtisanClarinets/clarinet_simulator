
import numpy as np
from src.models.clarinet import Clarinet
from src.simulation.physics import SimulationEngine
from scipy.optimize import minimize_scalar

class Optimizer:
    def __init__(self, clarinet: Clarinet, simulation_engine: SimulationEngine):
        self.clarinet = clarinet
        self.sim = simulation_engine

    def tune_hole_position(self, target_frequency: float, hole_index: int, search_range: float = 0.05):
        """
        Adjusts the position of a specific hole to match the first resonance to target_frequency.
        search_range: +/- meters to search around current position.
        """
        if hole_index >= len(self.clarinet.holes):
            raise ValueError("Invalid hole index")

        # Get the specific hole object to modify
        hole_to_optimize = self.clarinet.holes[hole_index]
        original_pos = hole_to_optimize.position

        def objective(pos_shift):
            # Apply shift to the specific hole object
            # Note: We do NOT re-sort the holes list here.
            # OpenWind might expect holes to be sorted for correct physics,
            # but if we just shift slightly, order likely remains.
            # However, if order changes, we must handle it.
            # Ideally, we sort before simulation if needed, but we keep track of our hole by object reference.

            new_pos = original_pos + pos_shift
            hole_to_optimize.position = new_pos

            # We sort a COPY of the holes list for the simulation, or
            # we rely on the fact that Clarinet.get_holes_list() might need to return sorted data.
            # But Clarinet stores holes in self.holes.
            # If we sort self.holes, the index `hole_index` becomes invalid.
            # But `hole_to_optimize` is a reference to the object, so we are safe modifying it.
            # The only risk is if `self.clarinet.holes` is re-ordered, does it affect anything else?

            # Let's ensure the clarinet provides sorted data to the simulation
            # WITHOUT changing the order of the objects in the list if possible,
            # OR we accept that the list order changes but we hold the object ref.

            # Current `Clarinet` implementation:
            # get_holes_list() iterates over self.holes.
            # So we SHOULD sort self.holes so the physics engine gets them in order.

            self.clarinet.holes.sort(key=lambda h: h.position)

            # Run simulation
            freqs, impedance = self.sim.run_impedance_simulation(self.clarinet)
            peaks = self.sim.detect_peaks(freqs, impedance)

            if not peaks:
                return 1e6 # Penalty if no peaks found

            # Find the peak closest to target
            closest_peak = min(peaks, key=lambda p: abs(p[0] - target_frequency))
            return abs(closest_peak[0] - target_frequency)

        # Optimize
        result = minimize_scalar(objective, bounds=(-search_range, search_range), method='bounded')

        # Apply best result
        best_pos = original_pos + result.x
        hole_to_optimize.position = best_pos
        self.clarinet.holes.sort(key=lambda h: h.position)

        return {
            "success": result.success,
            "new_position": best_pos,
            "error": result.fun
        }
