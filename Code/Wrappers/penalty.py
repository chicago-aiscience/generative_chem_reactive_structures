def apply_ts_guess_penalty(score: float, used_ts_guess: bool, penalty: float = 0.1) -> float:
    if used_ts_guess:
        return score + penalty
    return score
