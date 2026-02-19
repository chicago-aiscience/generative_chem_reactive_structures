from typing import Iterable, Optional

import numpy as np


def write_xyz(path: str, positions: np.ndarray, elements: Optional[Iterable[str]] = None, comment: str = ""):
    n = positions.shape[0]
    if elements is None:
        elements = ["C"] * n
    with open(path, "w") as f:
        f.write(f"{n}\n")
        f.write(f"{comment}\n")
        for elem, pos in zip(elements, positions):
            x, y, z = pos
            f.write(f"{elem} {x:.6f} {y:.6f} {z:.6f}\n")


def write_xyz_pair(
    path: str,
    reactant_pos: np.ndarray,
    product_pos: np.ndarray,
    pred_ts_pos: np.ndarray,
    comment: str = "",
):
    n = reactant_pos.shape[0]
    elements = ["C"] * n
    with open(path, "w") as f:
        for label, pos in [("reactant", reactant_pos), ("product", product_pos), ("pred_ts", pred_ts_pos)]:
            f.write(f"{n}\n")
            f.write(f"{label} {comment}\n")
            for elem, p in zip(elements, pos):
                x, y, z = p
                f.write(f"{elem} {x:.6f} {y:.6f} {z:.6f}\n")


def write_xyz_dir(output_dir: str, positions_list: Iterable[np.ndarray]):
    import os

    os.makedirs(output_dir, exist_ok=True)
    for i, pos in enumerate(positions_list):
        path = os.path.join(output_dir, f"ts_{i:05d}.xyz")
        write_xyz(path, pos, comment=f"pred_ts_{i}")
