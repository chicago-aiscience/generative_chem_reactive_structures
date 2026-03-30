# TODO

1. Evaluation metric RMSD at the end.
2. Modify code to use these test/train/validation split datasets. Maybe have some out of distribution?
3. Provide more information about the different guesses. Maybe we just remove all guesses?
4. Remove atom count from `train_and_eval_egnn.py` - make it more general
5. Include masking example.
6. Provide context for what the dataset are and what format they are in - how they were created and how to work with them. - add figures for what these datasets are.
7. Identify where participants should make modifications or how they can integrate the baseline with their solution. Add to the codes.
8. Provide an example of how to evaluate solution, I think there is a evaluation script that shows improvement but I am not sure where it is.
9. Include a bonus folder with the Halo8 dataset - include
10. Add more comments on the parameters in both the notebook and python files.

# Generative Chem Reaction Structures Hackathon

AI Schmidt Hackathon 2026 project on predicting 3D transition-state (TS) geometries from reactant and product structures.

## Environment Setup

- This repo uses a small Python stack: `numpy`, `torch`, `ipykernel`
- Additional libraries for visualization: `ase`, `py3dmol`
- To run notebooks: `jupyterlab`

### Midway3 (RCC Cluster) — Recommended for Hackathon

The hackathon base environment is pre-installed on Midway3 at `/project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base`. Rather than duplicating the full environment, you'll create a lightweight personal virtual environment that builds on top of it.

#### One-Time Shell Configuration

The very first time you log in, you need to initialize conda for your shell. You only need to do this once:

```bash
module load python/miniforge-25.3.0
conda init
source ~/.bashrc
```

#### Setting Up Your Personal Environment

Run these commands once after the shell configuration above to create a virtual environment (`venv`) from the base `conda` environment:

```bash
# 1. Load conda
module load python/miniforge-25.3.0

# 2. Activate the shared hackathon conda environment
conda activate /project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base

# 3. Create your personal virtual environment in your home directory
python -m venv --system-site-packages ~/my-hack-venv

# 4. Activate your personal environment
source ~/my-hack-venv/bin/activate
```

#### Every Subsequent Session

Run these commands to load and activate your virtual environment that references the base `conda` environment:

```bash
module load python/miniforge-25.3.0
conda activate /project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base
source ~/my-hack-venv/bin/activate
```

#### Installing Additional Packages

Make sure your personal venv is active first, then:

```bash
pip install <package-name>
```

This installs only into your personal environment — the shared base is not affected. To see only the packages you've added (vs. what's inherited from the base):

```bash
pip list --local
```

#### Troubleshooting

If you run into a package conflict or something breaks, you can delete and recreate your personal `venv` without touching the shared environment:

```bash
rm -rf ~/my-hack-venv
module load python/miniforge-25.3.0
conda activate /project/ai4s-hackathon/ai-sci-hackathon-2026/hackathon-base
python -m venv --system-site-packages ~/my-hack-venv
source ~/my-hack-venv/bin/activate
```

---

### `uv` (recommended for local development on your laptop)

**1. Install uv: https://docs.astral.sh/uv/getting-started/installation/**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**2. Sync (install) project dependencies (from project root)**

```bash
cd /path/to/gh/repo/generative_chem_reactive_structures
uv sync
```

### Conda (alternative for local development)

```bash
conda env create -f environment.yaml
conda activate generative-chem
```

If the environment already exists and `environment.yaml` changes:

```bash
conda env update -f environment.yaml --prune
```

### Pip (alternative for local development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy torch ipykernel
```

### Note on `uv` vs. `conda`

`uv` is a fast, modern Python package manager written in Rust. It resolves and installs dependencies significantly faster than conda (often 10–100×), and uses a `pyproject.toml`-based lockfile that makes environments reproducible without the overhead of conda's solver. If you're working on a fresh machine or just need to run the code quickly, `uv` is the recommended path — a single `uv sync` handles everything.

Conda is a better fit if you're working in an existing conda-based environment, need non-Python dependencies (e.g., system-level libraries or CUDA toolkits managed through conda channels), or are on an HPC cluster where `conda` is already the standard.

> Note that the `uv`-managed environment will not interfere with any existing conda setup.

## Quick Start: Example Runs

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

### Dataset Summary

This project dataset is organized around reaction triples:
- reactant structure (`reactant`)
- product structure (`product`)
- transition-state (TS) reference (`transition_state`)

Current local files include:
- `Data/train_rpsb_all.pkl`
- `Data/halo8_rpsb_like_all.pkl`
- split files under `Data/Halo8/` and `Data/transition1x/` (`train.pkl`, `val.pkl`, `test.pkl`)

The Halo8 dataset is a modification of the transition1x by adding in halogenated groups to the molecules.

For `transition1x`, some entries include TS guess structures generated from prior QM-based workflows (for example `ts_guess_*`-style fields).

What you find in each reaction entry (as used in notebooks/scripts):
- top-level keys: `reactant`, `product`, `transition_state`, `single_fragment`, `use_ind`, `ts_guess`, `ts_guess_sbv1`, `ts_guess_true`, `ts_guess_NEBCI-xtb`
- per-structure keys (inside `reactant`/`product`/`transition_state`): `positions`, `charges` (or `atomic_numbers`), `num_atoms`, `fragments`, `rxn`, and optional quantum properties (`wB97x_6-31G(d).energy`, forces, atomization energy)
- `positions` is the main supervised signal: an `N x 3` coordinate array for one structure

What this means for modeling:
- input condition: reactant + product coordinates (and atom identities)
- prediction target: transition-state coordinates for the same atoms
- standard baseline initialization: midpoint `x0 = 0.5 * (xR + xP)`
- evaluation question: does the predicted TS geometry reduce RMSD vs the midpoint baseline?

Concrete examples from the notebooks:
- `Notebooks/example_baseline_reactOT.ipynb`:
  - shows keys like `dict_keys(['reactant', 'transition_state', 'product', ...])`
  - picks a fixed atom-count subset (example run: most common `N=10`)
  - reports sample RMSD comparison (example run): midpoint->TS `0.4242`, predicted->TS `0.2174`
- `Notebooks/example_halo8_reactOT_rmsd.ipynb`:
  - uses `Data/halo8_rpsb_like_all.pkl`
  - evaluates on held-out data with summary stats (mean/median/p90 and `% improved vs midpoint`)

Expected output from code (what "good output" looks like):
- training/eval logs from `Code/Examples/train_and_eval_egnn.py`:
  - epoch losses, then aggregate metrics such as:
  - `model RMSD: ...`
  - `midpoint RMSD: ...`
  - optional `energy MAE (mean baseline): ...`
- generated structures:
  - predicted TS files are written to `outputs_xyz/ts_00000.xyz`, `ts_00001.xyz`, ...
  - each file is a single XYZ frame with comment `pred_ts_i` (see `Code/Wrappers/xyz.py`)
  - sample files are included in `sample_outputs_xyz/`

<img src="figures/transition1x.png" width="600">

Figure X from the Transition1x paper: (a) is an example reaction from reactant to product through the transition state.

<img src="figures/halo8.png" width="600">

Figure X from Halo8 paper: Reaction path sampling from single reactant to multiple products.


Source papers / dataset links (to be added):
- Transition1x: Paper: [https://doi.org/10.1038/s41597-022-01870-w] Dataset:[https://doi.org/10.6084/m9.figshare.19614657.v4]
- Halo8: Paper: [https://doi.org/10.1038/s41597-025-05944-3] Dataset: [https://doi.org/10.5281/zenodo.16737590.]

Fair-use / evaluation note:
- Using these "smarter" TS guesses as training inputs or features is allowed only with a competition penalty.
- For fair model comparisons, report clearly whether your method uses any TS guess (`ts_guess-*` in `transition1x`) information beyond reactant/product inputs.

TODO: Talk about why the Halo8 has more reactions.

## Visualization

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

## Methods: Conditional Flow Matching example

There are several methods of predicting these transition-state (TS) structures. Some generative examples are diffusion models and conditional flow matching. Participants can also test non-generative methods to make predictions.

This repository uses conditional flow matching (CFM) to generate a TS geometry from reactant and product structures. Rather than predicting the TS in one step, the model learns a continuous update rule for coordinates over time.

Let `x_R`, `x_P`, and `x_TS` denote reactant, product, and transition-state coordinates. At time `t in [0,1]`, the model predicts a vector field

$$v_\theta(x_t, t \mid x_R, x_P)$$

and evolves the structure by

$$\frac{d x_t}{dt} = v_\theta(x_t, t \mid x_R, x_P)$$

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


## Evaluation (How your model is scored)

- **Metric:** RMSD between predicted TS and ground-truth TS
- **Baseline:** midpoint initialization

`x_mid = 0.5 * (x_R + x_P)`

- **What matters:** improvement over baseline

`Δ = RMSD(midpoint, TS) − RMSD(model, TS)`

- **We report:**
  - Mean RMSD (lower is better)
  - % of reactions improved vs midpoint

- **Goal:** outperform the midpoint baseline consistently


## Repository Structure and How To Use Each Folder

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

### `rcc.submit/`
Example RCC / Midway job-submission files.

Use this folder when you want to run training or inference on UChicago RCC resources with Slurm; it includes a sample `sub.sbatch`, a small example Python script, and brief setup notes in `rcc.submit/README.md`.

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

## Notes

- Current baseline workflow is fixed-atom-count oriented (default atom count: 10).
- Primary metric is TS coordinate RMSD; optional energy MAE is supported where energies exist.