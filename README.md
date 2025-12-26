# Clarinet R&D Prototyping Lab

A Fortune-1000 grade computational physics environment for designing, simulating, and optimizing clarinet-family instruments. This application leverages the INRIA `openwind` library to provide accurate acoustic simulations and wraps them in a polished, interactive Streamlit interface.

## 🌟 Key Features

*   **Advanced Geometry Designer**: Create complex bore profiles (e.g., bells, barrel tapers) and precise tone hole configurations using interactive data editors.
*   **Physics Simulation**: Compute the input impedance of your design using Finite Element Method (FEM) solvers. Detect resonance peaks automatically.
*   **Automated Optimization**: Utilize numerical optimization (`scipy.optimize`) to automatically tune tone hole positions to match specific target frequencies.
*   **Interactive Visualization**: Real-time 2D visualization of instrument geometry and interactive Plotly charts for acoustic impedance analysis.
*   **Design Persistence**: Save and load your instrument prototypes via JSON to iterate on designs over time.

---

## 🚀 Installation

### Prerequisites
*   Python 3.10+ (Tested on 3.12)
*   `pip` package manager

### Setup
1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd clarinet-rd-lab
    ```

2.  **Install Dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

---

## 🖥️ Usage Guide

Run the application using Streamlit:
```bash
streamlit run app.py
```

### 1. Geometry Design
The **Sidebar** provides full control over the physical parameters of the instrument.
*   **Environment**: Set the simulation temperature (defaults to 25°C), which affects the speed of sound.
*   **Bore Geometry**:
    *   Use the **Bore Profile** data editor to define the main air column.
    *   Add points as `(Position, Radius)` pairs.
    *   The engine supports complex shapes; add multiple points to create tapers, bells, or perturbations.
*   **Tone Holes**:
    *   Use the **Tone Holes** data editor to configure the lattice.
    *   For each hole, specify:
        *   `Position`: Distance from the input end (meters).
        *   `Radius`: Radius of the hole (meters).
        *   `Chimney`: Height of the hole chimney (meters).
        *   `Label`: A unique identifier (e.g., "Register Key", "Hole 1").

### 2. Simulation & Analysis
1.  Click the **Run Simulation** button in the main dashboard.
2.  The application calculates the Input Impedance curve ($Z_{in}$).
3.  **Results**:
    *   **Impedance Plot**: Interactive graph showing Magnitude (dB) vs Frequency (Hz). Zoom and pan to inspect details.
    *   **Resonance Peaks**: A table lists detected resonance frequencies and their magnitudes. These correspond to the notes the instrument can play.

### 3. Automated Optimization
Use the **Optimization** module to tune your design:
1.  Run a simulation first to detect current peaks.
2.  **Target Frequency**: Input the desired frequency for a specific resonance (e.g., tuning the fundamental).
3.  **Select Hole**: Choose which tone hole to move to achieve this target.
4.  Click **Optimize Hole Position**.
    *   The system uses an iterative solver to adjust the hole position.
    *   Upon success, the Geometry and UI update automatically to the new optimal position.

### 4. File Operations
*   **Save Design**: Download your current configuration as a `clarinet_design.json` file.
*   **Load Design**: Upload a previously saved JSON file to restore the entire instrument state (Bore, Holes, Environment).

---

## 📂 Project Structure

The codebase is organized as a modular Python package in `src/`.

```text
.
├── app.py                      # Application Entry Point
├── requirements.txt            # Python dependencies
├── tests/                      # Unit Tests (pytest)
│   ├── test_core.py            # Tests for simulation logic
│   └── test_optimization.py    # Tests for optimizer convergence
└── src/                        # Source Code
    ├── models/                 # Domain Models
    │   └── clarinet.py         # Clarinet class: Manages bore/hole state & validation
    ├── simulation/             # Physics Engine
    │   └── physics.py          # SimulationEngine: Wraps `openwind` API, handles FEM solver & Peak Detection
    ├── optimization/           # Algorithms
    │   └── optimizer.py        # Optimizer: Implements feedback loop for geometry tuning
    └── ui/                     # User Interface
        ├── sidebar.py          # Sidebar render logic, state management, and file I/O
        └── visualization.py    # Plotly/Matplotlib chart generation
```

### Key Modules

*   **`src.models.clarinet.Clarinet`**: The source of truth for the instrument. It manages lists of `BoreSection` and `Hole` objects and ensures data is formatted correctly for the physics engine.
*   **`src.simulation.physics.SimulationEngine`**: The bridge to INRIA's `openwind`. It constructs the `InstrumentGeometry`, instantiates the `FrequentialSolver` with a `UNITARY_FLOW` source, and processes the impedance results.
*   **`src.ui.sidebar.render_sidebar`**: Handles the complex state synchronization required for the interactive Data Editors (`st.data_editor`). It ensures that file uploads, manual edits, and optimization updates all sync correctly to the session state.

---

## 🧪 Testing

The project uses `pytest` for automated testing. Tests cover model integrity, simulation execution, and optimizer convergence.

Run the test suite:
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest tests/
```

---

## 📚 Dependencies

*   **`openwind`**: Computational acoustics library (FEM).
*   **`streamlit`**: Web application framework.
*   **`scipy`**: Optimization algorithms.
*   **`numpy`**: Numerical computing.
*   **`plotly`**: Interactive charting.
