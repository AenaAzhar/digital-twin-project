# Digital Twin for Surface Treatment Industries

A mini project demonstrating **Discrete Event Simulation (DES) + Optimization coupling** for finite capacity production planning in surface treatment industries.

## 📋 Overview

This project implements core components of a digital twin system for short-term production planning, aligned with the PhD thesis requirements at IMT Mines Albi:

- **Discrete Event Simulation**: SimPy-based model for surface treatment workshops
- **Optimization Services**: Scheduling and batch grouping optimization
- **Finite Capacity Planning**: Multi-workshop coordination with capacity constraints
- **Decision Support**: Timeline visualization and performance metrics

## 🏗️ Project Structure

```
digital-twin-project/
├── src/
│   ├── simulation/              # DES models using SimPy
│   │   ├── __init__.py
│   │   ├── workshop.py          # Workshop simulation model
│   │   ├── order.py             # Order entity
│   │   └── resources.py         # Resource definitions
│   ├── optimization/            # Optimization services
│   │   ├── __init__.py
│   │   ├── scheduler.py         # Scheduling algorithms
│   │   └── batch_grouping.py    # Batch optimization
│   └── visualization/           # Analysis & visualization
│       ├── __init__.py
│       └── dashboards.py        # Performance dashboards
├── config/                      # Configuration files
│   └── workshop_config.yaml     # Workshop parameters
├── examples/                    # Case studies
│   ├── simple_surface_treatment.py
│   └── multi_workshop_scenario.py
├── tests/                       # Unit tests
├── requirements.txt             # Dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows/Linux/Mac

### Installation

```bash
# Clone and navigate to project
cd digital-twin-project

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Example

```bash
python examples/simple_surface_treatment.py
```

## 📚 Key Concepts

### Digital Twin Architecture
- **Physical System**: Surface treatment workshops with multiple stations
- **Cyber System**: Simulation model + optimization services
- **Bidirectional Interaction**: Planning decisions → Production execution

### Finite Capacity Simulation
- Multi-stage surface treatment processes
- Order batching and sequencing
- Resource constraints (machines, operators, material)
- Lead time management

### Optimization Services
- Short-term scheduling (days)
- Medium-term planning (weeks)
- Batch optimization for efficiency
- Operator versatility management

## 🔧 Technologies

| Component | Technology |
|-----------|-----------|
| Simulation | **SimPy** (Discrete Event Simulation) |
| Language | **Python 3.8+** |
| Optimization | **NumPy/SciPy** |
| Data Analysis | **Pandas** |
| Visualization | **Matplotlib, Plotly** |

## 📖 Documentation

See [copilot-instructions.md](.github/copilot-instructions.md) for development guidelines.

## 📝 Surface Treatment Industry Context

**Key Characteristics:**
- Made-to-order production
- Short promised lead times
- High customer diversity
- Highly variable product mix
- Mix of automated and manual processes

**Planning Challenges:**
- Work-in-progress (WIP) regulation
- Capacity agility requirements
- Complex batch compositions
- Multi-workshop coordination

## ✅ What's Included

- [x] SimPy-based simulation framework
- [x] Basic workshop model (single/multi-stage)
- [x] Order and batch management
- [x] Optimization skeleton
- [x] Example scenarios
- [x] Performance metrics

## 🎯 Future Extensions

- [ ] Reinforcement Learning coupling for adaptive scheduling
- [ ] Real-time data collection interface
- [ ] Database integration for order history
- [ ] Web dashboard for visualization
- [ ] Advanced optimization (genetic algorithms, etc.)

## 📧 Research Context

**PhD Program**: Digital Twin for Short Term Planning  
**Institution**: IMT Mines Albi, Industrial Engineering Centre (CGI)  
**Project**: INFINITY - Digital Twin for Surface Treatment Industries  
**Advisor**: FLOWS axis, HOPOPOP scientific program

---

**Created**: June 2026 | **Status**: Initial Mini Project
