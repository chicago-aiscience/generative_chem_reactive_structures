"""Utility helpers for device selection and tensor conversion."""

import torch


def get_device():
    """Pick the best available torch device (MPS, CUDA, then CPU)."""
    # Prefer Apple Silicon MPS, then CUDA, otherwise default to CPU.
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def to_tensor(x, device=None, dtype=torch.float32):
    """Convert input to a torch Tensor on the chosen device/dtype."""
    if device is None:
        device = get_device()
    return torch.as_tensor(x, dtype=dtype, device=device)
