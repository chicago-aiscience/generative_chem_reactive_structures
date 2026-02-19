<<<<<<< HEAD
# generative_chem_reactive_structures
AI Schmidt Hackathon 2026. Participants are tasked with predicting the 3D molecular structures of transition states using just reactant and product geometries. 
=======
# Generative Chem Reaction Structures Hackathon

## Overview
Goal: predict transition state (TS) 3D structures (and optionally energies).

Inputs:
- Reactant + product only.

Outputs:
- TS positions (and optionally TS energy).

## Dataset Summary
The dataset is provided as a single `.pkl` file. It contains keys like:
- `reactant`, `product`, `transition_state`, `ts_guess_*`, `use_ind`, etc.

Baseline uses a fixed atom count (most common atom count = 10) with no masking.

## Evaluation
Primary metrics:
- RMSD on TS positions.
- Energy MAE on TS energies (optional).

Penalty:
- If `ts_guess_*` is used as input features, a penalty is applied to the score.

## Baseline
Midpoint baseline (from `reactOT.ipynb`):
- TS prediction = (reactant positions + product positions) / 2
- Fixed atom count only.

## Getting Started
- See `Notebooks/` for the example notebook.
- See `Code/Examples/` for scripts once available.

## Rules / Constraints
- Inputs restricted to reactant + product.
- `ts_guess_*` may be used with a penalty.
- Participants are encouraged to generalize beyond fixed atom count.

## Repo Map
- `Code/Wrappers/`: dataset loading, splitting, baseline, metrics, XYZ writer.
- `Code/HelperFunctions/`: small utilities, EGNN, flow matching.
- `Code/Baselines/`: baseline methods.
- `Code/Visualization/`: XYZ output utilities.
- `Notebooks/`: example notebook.

## Acknowledgements
Inspired by `deepprinciple-react-ot-5184332/reactOT.ipynb`.
>>>>>>> d043c0d (Initial commit)
