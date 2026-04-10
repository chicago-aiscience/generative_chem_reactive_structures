"""Metric utilities for comparing predictions."""

import numpy as np


def kabsch_align(
    mobile_pos: np.ndarray,
    reference_pos: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Center and rotate ``mobile_pos`` onto ``reference_pos`` with Kabsch alignment. Refer to https://hunterheidenreich.com/posts/kabsch-algorithm/"""
    if mobile_pos.shape != reference_pos.shape:
        raise ValueError("mobile_pos and reference_pos must have the same shape")
    if mobile_pos.ndim != 2 or mobile_pos.shape[1] != 3:
        raise ValueError("Inputs must have shape (N, 3)")

    # Compute centroids
    mobile_centroid = np.mean(mobile_pos, axis=0)
    reference_centroid = np.mean(reference_pos, axis=0)

    # Center coordinates
    mobile_centered = mobile_pos - mobile_centroid
    reference_centered = reference_pos - reference_centroid

    # Covariance matrix
    cov = mobile_centered.T @ reference_centered

    # SVD
    U, _, Vt = np.linalg.svd(cov)

    # Enforce right-handed rotation
    if np.linalg.det(Vt.T @ U.T) < 0.0:
        Vt[-1, :] *= -1.0

    # Optimal rotation
    rot = Vt.T @ U.T

    # Apply rotation
    mobile_aligned = mobile_centered @ rot.T

    return mobile_aligned, reference_centered


def compute_rmsd(pred_pos: np.ndarray, true_pos: np.ndarray) -> float:
    """Compute Kabsch-aligned RMSD between predicted and true positions."""
    pred_aligned, true_centered = kabsch_align(pred_pos, true_pos)
    diff = pred_aligned - true_centered
    return float(np.sqrt(np.sum(diff**2) / pred_pos.shape[0]))


def compute_energy_mae(pred_energy: float, true_energy: float) -> float:
    """Compute mean absolute error between energies."""
    return float(np.abs(pred_energy - true_energy))