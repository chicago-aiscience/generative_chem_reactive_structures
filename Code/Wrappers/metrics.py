"""Metric utilities for comparing predictions."""

import numpy as np


def kabsch_align(mobile_pos: np.ndarray, reference_pos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Center and rotate ``mobile_pos`` onto ``reference_pos`` with Kabsch alignment."""
    mobile_centered = mobile_pos - mobile_pos.mean(axis=0, keepdims=True)
    reference_centered = reference_pos - reference_pos.mean(axis=0, keepdims=True)

    cov = mobile_centered.T @ reference_centered
    u, _, vh = np.linalg.svd(cov)
    det_sign = np.sign(np.linalg.det(u @ vh))
    corr = np.diag([1.0, 1.0, det_sign])
    rot = u @ corr @ vh
    mobile_aligned = mobile_centered @ rot
    return mobile_aligned, reference_centered


def compute_rmsd(pred_pos: np.ndarray, true_pos: np.ndarray) -> float:
    """Compute Kabsch-aligned RMSD between predicted and true positions."""
    pred_aligned, true_centered = kabsch_align(pred_pos, true_pos)
    diff = pred_aligned - true_centered
    return float(np.sqrt(np.mean(np.sum(diff * diff, axis=-1))))


def compute_energy_mae(pred_energy: float, true_energy: float) -> float:
    """Compute mean absolute error between energies."""
    return float(np.abs(pred_energy - true_energy))