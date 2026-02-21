"""Penalty helpers for evaluation or ranking."""


def apply_ts_guess_penalty(score: float, used_ts_guess: bool, penalty: float = 0.1) -> float:
    """Apply an additive penalty if a transition-state guess was used."""
    if used_ts_guess:
        return score + penalty
    return score
