"""Metric utilities for comparing predictions."""

import numpy as np


def compute_rmsd(pred_pos: np.ndarray, true_pos: np.ndarray) -> float:
    """Compute RMSD between predicted and true positions."""
    diff = pred_pos - true_pos
    return float(np.sqrt(np.mean(np.sum(diff * diff, axis=-1))))


def compute_energy_mae(pred_energy: float, true_energy: float) -> float:
    """Compute mean absolute error between energies."""
    return float(np.abs(pred_energy - true_energy))
