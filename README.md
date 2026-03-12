# TODO

1. Modify code to use these test/train/validation split datasets. Maybe have some out of distribution? 
2. Provide more information about the different guesses. Maybe we just remove all guesses? 
3. Remove atom count from `train_and_eval_egnn.py` - make it more general
4. Include masking example.
5. Provide context for what the dataset are and what format they are in - how they were created and how to work with them. - add figures for what these datasets are.
6. Add bonus for the full reaction pathway from Halo8
7. Identify where participants should make modifications or how they can integrate the baseline with their solution. Add to the codes.
8. Provide an example of how to evaluate solution, I think there is a evaluation script that shows improvement but I am not sure where it is.
9. RMSD evaluation metric in README
10. Include a bonus folder with the Halo8 dataset - include

# Generative Chem Reaction Structures Hackathon

AI Schmidt Hackathon 2026 project on predicting 3D transition-state (TS) geometries from reactant and product structures.

## 1) Environment Setup

- This repo uses a small Python stack: `numpy`, `torch`, `ipykernel`
- Additional libraries for visualization: `ase`, `py3dmol`
- To run notebooks: `jupyterlab`

### `uv` (recommended)

**1. Install uv: https://docs.astral.sh/uv/getting-started/installation/**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Sync (install) project dependencies (from project root)**

```bash
cd /path/to/gh/repo/generative_chem_reactive_structures
uv sync
```

### Conda (alternative)

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
uv run python Code/Examples/train_and_eval_egnn.py \
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
uv run jupyter notebook Notebooks/example_baseline.ipynb
```

Other notebook examples:
- `Notebooks/example_baseline_reactOT.ipynb`
- `Notebooks/example_halo8_reactOT_rmsd.ipynb`

If needed, install notebook library:

```bash
uv sync --extra jupyter
```

## 2.5) Dataset Summary

This project dataset is organized around reaction triples:
- reactant structure
- product structure
- transition-state (TS) structure

Current local files include:
- `Data/train_rpsb_all.pkl`
- `Data/halo8_rpsb_like_all.pkl`
- split files under `Data/Halo8/` and `Data/transition1x/` (`train.pkl`, `val.pkl`, `test.pkl`)

For `transition1x`, some entries include TS guess structures generated from prior QM-based workflows (for example `ts_guess_*`-style fields).

<img src="figures/halo8.png" width="600">

<img src="figures/transition1x.png" width="600">

Source papers / dataset links (to be added):
- Transition1x: Paper: [https://doi.org/10.1038/s41597-022-01870-w] Dataset:[https://doi.org/10.6084/m9.figshare.19614657.v4]
- Halo8: Paper: [https://doi.org/10.1038/s41597-025-05944-3] Dataset: [https://doi.org/10.5281/zenodo.16737590.]

Fair-use / evaluation note:
- Using these "smarter" TS guesses as training inputs or features is allowed only with a competition penalty.
- For fair model comparisons, report clearly whether your method uses any TS guess (`ts_guess-*` in `transition1x`) information beyond reactant/product inputs.

TODO: Add how the two datsets differ. Explain the figures a little.

## 3) Visualization

Use the notebook below to inspect generated `.xyz` structures interactively:

```bash
uv run jupyter notebook Notebooks/xyz_visualization.ipynb
```

Notebook highlights (from `Notebooks/xyz_visualization.ipynb`):
- Discovers `.xyz` files (or lets you set a specific file path like `outputs_xyz/ts_00000.xyz`)
- Loads single-frame or multi-frame XYZ data with ASE
- Supports inline visualization with ASE (`viewer='x3d'`)
- Supports inline `py3Dmol` rendering (single frame and animation)
- Supports optional desktop viewer launch via `ase gui`

If needed, install visualization extras:

```bash
uv sync --extra visualize
```

## 3.5) Conditional Flow Matching

This project uses conditional flow matching (CFM) to generate a transition-state (TS) geometry from reactant and product structures. Rather than predicting the TS in one step, the model learns a continuous update rule for coordinates over time.

Let `x_R`, `x_P`, and `x_TS` denote reactant, product, and transition-state coordinates. At time `t in [0,1]`, the model predicts a vector field

$$v_\theta(x_t, t \mid x_R, x_P)$$

and evolves the structure by

$$\frac{d x_t}{dt} = v_\theta(x_t, t \mid x_R, x_P)$$.

For a simple baseline, the trajectory starts from the coordinate-wise midpoint

$$x_0 = \frac{x_R + x_P}{2}$$

During training, the model matches a linear path from `x_0` to the true TS:

$$x_t = (1 - t)x_0 + t x_{TS}, \qquad$$
$$u_t = x_{TS} - x_0$$

with loss


$$
\mathcal{L} =
\mathbb{E}_{t,x_t}
\| v_\theta(x_t, t \mid x_R, x_P) - u_t \|^2
$$

In short: reactant and product define the endpoints, the midpoint provides a simple initialization, and the learned flow refines that structure toward the TS.

### Example flow-matching output

The sample animation below uses a simple baseline initialization: the starting structure is the coordinate-wise mean of the reactant and product states. From that baseline, flow matching evolves the geometry toward the transition state (TS).

![Example flow matching trajectory](sample_outputs_xyz/example_flowmatching.gif)

The sample `.xyz` outputs used for inspection live in `sample_outputs_xyz/`.

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
