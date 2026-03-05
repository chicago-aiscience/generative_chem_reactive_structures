# Generative Chem Reaction Structures Hackathon

AI Schmidt Hackathon 2026 project on predicting 3D transition-state (TS) geometries from reactant and product structures.

## 1) Environment Setup

This repo uses a small Python stack (`numpy`, `torch`, `ipykernel`).

### Conda (recommended)

```bash
conda env create -f environment.yaml
conda activate generative-chem
```

If the environment already exists and `environment.yaml` changes:

```bash
conda env update -f environment.yaml --prune
```

### Pip (alternative)

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy torch ipykernel
```

## 2) Quick Start: Example Runs

### Example A: Train and evaluate the EGNN baseline script

```bash
python Code/Examples/train_and_eval_egnn.py \
  --pkl Data/train_rpsb_all.pkl \
  --atom-count 10 \
  --epochs 3 \
  --train-samples 200 \
  --eval-samples 100 \
  --out-dir outputs_xyz
```

What this does:
- Loads the dataset from `Data/train_rpsb_all.pkl`
- Filters to fixed atom count (default 10)
- Trains a small EGNN baseline
- Reports RMSD (and optional energy MAE)
- Writes predicted TS structures as `.xyz` files into `outputs_xyz/`

### Example B: Run notebook baselines

```bash
jupyter notebook Notebooks/example_baseline.ipynb
```

Other notebook examples:
- `Notebooks/example_baseline_reactOT.ipynb`
- `Notebooks/example_halo8_reactOT_rmsd.ipynb`

## 3) Visualization

Use the notebook below to inspect generated `.xyz` structures interactively:

```bash
jupyter notebook Notebooks/xyz_visualization.ipynb
```

Notebook highlights (from `Notebooks/xyz_visualization.ipynb`):
- Discovers `.xyz` files (or lets you set a specific file path like `outputs_xyz/ts_00000.xyz`)
- Loads single-frame or multi-frame XYZ data with ASE
- Supports inline visualization with ASE (`viewer='x3d'`)
- Supports inline `py3Dmol` rendering (single frame and animation)
- Supports optional desktop viewer launch via `ase gui`

If needed, install visualization extras:

```bash
pip install ase py3Dmol ipywidgets
```

## 4) Repository Structure and How To Use Each Folder

### `Code/`
Core Python code.

- `Code/Wrappers/`
  - Purpose: high-level helpers for data loading, splitting, baseline, metrics, and XYZ writing.
  - Use when: you want reusable building blocks for experiments or scripts.
- `Code/HelperFunctions/`
  - Purpose: model and utility internals (EGNN, flow matching, small data utilities).
  - Use when: implementing new models or extending training logic.
- `Code/Examples/`
  - Purpose: runnable script examples.
  - Use when: you want a script-first starting point (`train_and_eval_egnn.py`).
- `Code/README.md`
  - Purpose: short internal code map.

### `Data/`
Local dataset files in `.pkl` format.

- `train_rpsb_all.pkl`
- `halo8_rpsb_like_all.pkl`

Use this folder as the source for `--pkl` paths in scripts and notebooks.

### `Notebooks/`
Interactive walkthroughs and baseline experimentation.

Use these for quick prototyping, visualization, and exploring baseline behavior before writing scripts.

### `outputs_xyz/`
Generated TS predictions as `.xyz` files.

Use this folder to inspect model outputs in molecular viewers.

### `Slides/`
Presentation material for the project/hackathon.

### Root docs/files
- `ENVIRONMENT.md`: environment setup details.
- `DATASETS.md`: dataset notes/description.
- `environment.yaml`: conda environment spec.
- `README.md`: high-level project entry point.

## 5) Notes

- Current baseline workflow is fixed-atom-count oriented (default atom count: 10).
- Primary metric is TS coordinate RMSD; optional energy MAE is supported where energies exist.
