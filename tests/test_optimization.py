
import pytest
from src.models.clarinet import Clarinet
from src.simulation.physics import SimulationEngine
from src.optimization.optimizer import Optimizer
import numpy as np

def test_optimization():
    # Setup a simple clarinet
    clar = Clarinet.default_clarinet()
    # Let's say we want to tune the first hole (index 0)
    # Current pos is 0.5.

    sim = SimulationEngine()
    # Speed up sim for test
    sim.frequencies = np.arange(100, 600, 10)

    optimizer = Optimizer(clar, sim)

    # Let's try to tune to a frequency slightly different from what it naturally is.
    # First run to see natural freq
    freqs, imp = sim.run_impedance_simulation(clar)
    peaks = sim.detect_peaks(freqs, imp)
    natural_freq = peaks[0][0] # e.g. 140Hz

    target_freq = natural_freq + 20 # Try to shift it up

    result = optimizer.tune_hole_position(target_freq, 0, search_range=0.1)

    assert result['success']
    assert result['new_position'] != 0.5
    # Frequency should be closer (due to discrete freq steps in sim, might not be exact 0 error)
    # But new pos should be different.
