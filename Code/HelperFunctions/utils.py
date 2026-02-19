import torch


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def to_tensor(x, device=None, dtype=torch.float32):
    if device is None:
        device = get_device()
    return torch.as_tensor(x, dtype=dtype, device=device)
