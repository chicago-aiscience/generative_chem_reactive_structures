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

### Example: Train and evaluate the EGNN baseline script

If you used `uv`, you can then run python commands and jupyter notebooks this way:

```bash
uv run python Code/Examples/train_and_eval_egnn.py \
  --pkl Data/train_rpsb_all.pkl \
  --atom-count 10 \
  --epochs 3 \
  --train-samples 200 \
  --eval-samples 100 \
  --out-dir outputs_xyz
```

If needed, install notebook library:

```bash
uv sync --extra jupyter
```

```bash
uv run jupyter notebook Notebooks/example_baseline.ipynb
```
