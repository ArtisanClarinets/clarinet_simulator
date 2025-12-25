import pytest
import numpy as np
from src.models.clarinet import Clarinet
from src.simulation.physics import SimulationEngine

def test_clarinet_creation():
    clar = Clarinet.default_clarinet()
    assert len(clar.bore) == 2
    assert len(clar.holes) == 2
    assert clar.bore[0].radius == 0.0075

def test_simulation_run():
    clar = Clarinet.default_clarinet()
    sim = SimulationEngine()

    # Use a smaller frequency range for speed in testing
    sim.frequencies = np.arange(100, 500, 10)

    freqs, impedance = sim.run_impedance_simulation(clar)

    assert len(freqs) == len(impedance)
    assert len(freqs) > 0
    assert not np.isnan(impedance).any()

def test_peak_detection():
    sim = SimulationEngine()
    freqs = np.array([100, 200, 300, 400, 500])
    # Create artificial impedance with a peak at 300
    impedance = np.array([0.1, 0.5, 1.0, 0.5, 0.1]) # magnitude, not dB for input, but helper converts to dB
    # wait, helper converts to dB. log10(1) = 0. log10(0.1) = -1.
    # So 300 is indeed a peak.

    peaks = sim.detect_peaks(freqs, impedance)
    assert len(peaks) == 1
    assert peaks[0][0] == 300
