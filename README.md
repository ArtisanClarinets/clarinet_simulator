# Clarinet R&D Prototyping Lab

This application provides a complete environment for prototyping, simulating, and optimizing clarinet geometries using computational physics. It leverages the `openwind` library for accurate acoustic simulations.

## Features

- **Geometry Designer**: define bore shape and hole placements interactively.
- **Physics Simulation**: compute input impedance and detect resonance frequencies.
- **Optimization**: automatically tune hole positions to match target frequencies.
- **Interactive Visualization**: explore geometry and simulation results with Plotly.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Run the Streamlit application:

```bash
streamlit run app.py
```

## Structure

- `src/models`: Data structures for Clarinet geometry.
- `src/simulation`: Physics engine wrapping `openwind`.
- `src/optimization`: Algorithms for automated design tuning.
- `src/ui`: User interface components.
- `tests`: Automated tests for core logic.
