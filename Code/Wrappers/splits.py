"""Dataset split helpers."""

from typing import Dict, Iterable, Tuple

import numpy as np

from .io import subset_dataset


def random_split_indices(
    n: int, seed: int = 0, ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1)
) -> Dict[str, Iterable[int]]:
    """Create randomized train/val/test index splits."""
    if abs(sum(ratios) - 1.0) > 1e-6:
        raise ValueError("ratios must sum to 1.0")
    # Shuffle indices deterministically for reproducibility.
    rng = np.random.default_rng(seed)
    indices = np.arange(n)
    rng.shuffle(indices)
    # Allocate slices for each split.
    n_train = int(ratios[0] * n)
    n_val = int(ratios[1] * n)
    train_idx = indices[:n_train]
    val_idx = indices[n_train : n_train + n_val]
    test_idx = indices[n_train + n_val :]
    return {"train": train_idx, "val": val_idx, "test": test_idx}


def build_splits(dataset, split_indices: Dict[str, Iterable[int]]):
    """Materialize split datasets using the index dictionary."""
    return {k: subset_dataset(dataset, v) for k, v in split_indices.items()}
