import numpy as np


def midpoint_baseline(reactant_pos: np.ndarray, product_pos: np.ndarray) -> np.ndarray:
    return 0.5 * (reactant_pos + product_pos)
