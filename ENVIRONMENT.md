# Environment

This repo uses a small Python stack: `numpy` and `pytorch` (plus `ipykernel` for notebooks).

## Conda (recommended)
Create and activate the environment:

```bash
conda env create -f environment.yaml
conda activate generative-chem
```

If you already created it and want to update it after edits:

```bash
conda env update -f environment.yaml --prune
```

## Pip (alternative)
If you prefer pip, install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy torch ipykernel
```
