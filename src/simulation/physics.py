import numpy as np
from openwind import ImpedanceComputation, InstrumentGeometry, Player
from src.models.clarinet import Clarinet
import matplotlib.pyplot as plt

class SimulationEngine:
    def __init__(self):
        self.frequencies = np.arange(20, 2000, 2)
        self.temperature = 25 # degrees Celsius

    def run_impedance_simulation(self, clarinet: Clarinet):
        """
        Runs impedance simulation for the given clarinet.
        Returns frequencies and impedance magnitude.
        """
        bore_data = clarinet.get_bore_list()
        holes_data = clarinet.get_holes_list()

        try:
            # Create the geometry object explicitly.
            inst = InstrumentGeometry(bore_data, holes_data)

            # Use lower-level classes for maximum control and correctness
            from openwind import InstrumentPhysics, FrequentialSolver

            # For impedance computation, we typically want Unitary Flow input
            # The available defaults were listed in the error:
            # ['FLUTE', 'SOPRANO_RECORDER', ... 'UNITARY_FLOW', ...]
            player = Player("UNITARY_FLOW")

            phys = InstrumentPhysics(inst, self.temperature, player, losses=True)
            solver = FrequentialSolver(phys, self.frequencies)
            solver.solve()

            return self.frequencies, np.abs(solver.impedance)

        except Exception as e:
            raise RuntimeError(f"Simulation failed: {e}")

    def plot_impedance(self, frequencies, impedance):
        """
        Generates a plot of Impedance vs Frequency.
        Returns a matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(frequencies, 20 * np.log10(impedance))
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Impedance Magnitude (dB)")
        ax.set_title("Input Impedance")
        ax.grid(True)
        return fig

    def detect_peaks(self, frequencies, impedance):
        """
        Detects impedance peaks which correspond to resonance frequencies.
        """
        # Simple peak detection
        peaks = []
        # basic algorithm: point is higher than neighbors
        mag = 20 * np.log10(impedance)
        for i in range(1, len(mag)-1):
            if mag[i] > mag[i-1] and mag[i] > mag[i+1]:
                # Threshold check could be added
                peaks.append((frequencies[i], mag[i]))
        return peaks
