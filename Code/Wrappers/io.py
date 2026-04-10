"""Dataset loading and slicing helpers."""

import pickle
from typing import Any, Dict, Iterable, List

import numpy as np


def load_dataset(pkl_path: str) -> Dict[str, Any]:
    """Load a pickled dataset from disk."""
    with open(pkl_path, "rb") as f:
        return pickle.load(f)


def _subset_value(value: Any, indices: Iterable[int]) -> Any:
    """Recursively apply a list of indices to nested dataset structures."""
    if isinstance(value, dict):
        return {k: _subset_value(v, indices) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return value[list(indices)]
    if isinstance(value, list):
        return [value[i] for i in indices]
    return value


def subset_dataset(dataset: Dict[str, Any], indices: Iterable[int]) -> Dict[str, Any]:
    """Return a dataset dictionary filtered by the provided indices."""
    return _subset_value(dataset, list(indices))


def filter_by_atom_count(dataset: Dict[str, Any], count: int) -> List[int]:
    """Return indices where the reactant atom count equals the provided count. 
    NOTE:: This is only for testing!!!! Final version should be generalized"""
    num_atoms = dataset["reactant"]["num_atoms"]
    if isinstance(num_atoms, np.ndarray):
        return [i for i, n in enumerate(num_atoms) if int(n) == int(count)]
    return [i for i, n in enumerate(list(num_atoms)) if int(n) == int(count)]
