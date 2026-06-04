<!-- Digital Twin Project - Discrete Event Simulation & Optimization -->

# Digital Twin Mini Project - PhD Thesis Preparation

## Project Overview
Mini project for Digital Twin in surface treatment industries with finite capacity simulation and optimization coupling.

**Aligned with:** PhD Thesis - Digital Twin for Short Term Planning (IMT Mines Albi, INFINITY Project)

## Project Status

- [x] Project directory structure created
- [x] Python environment initialized
- [x] Dependencies installed
- [x] Core simulation module developed
- [x] Optimization service implemented
- [x] Visualization tools created
- [x] Example case study completed
- [x] Documentation finalized

## Quick Start
```bash
cd digital-twin-project
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python examples/simple_surface_treatment.py
```

## Key Components

### 1. Simulation Module (`src/simulation/`)
- Discrete Event Simulation (DES) using SimPy
- Surface treatment workshop model
- Finite capacity constraints
- Order processing and batching

### 2. Optimization Module (`src/optimization/`)
- Scheduling optimization
- Batch grouping algorithms
- Workshop coordination

### 3. Visualization (`src/visualization/`)
- Production timeline charts
- Resource utilization dashboards
- Performance metrics

## Technologies
- **SimPy** - Discrete Event Simulation
- **Python** - Core implementation
- **NumPy/SciPy** - Numerical optimization
- **Pandas** - Data analysis
- **Matplotlib/Plotly** - Visualization

