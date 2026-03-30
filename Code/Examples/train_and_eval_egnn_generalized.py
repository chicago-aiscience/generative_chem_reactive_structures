"""Train and evaluate a simple EGNN baseline on variable-atom-count reactions."""

import argparse
import os
import sys

import numpy as np
import torch

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)

from Code.Wrappers import (
    load_dataset,
    random_split_indices,
    build_splits,
    midpoint_baseline,
    compute_rmsd,
    compute_energy_mae,
    write_xyz_dir,
)
from Code.HelperFunctions import EGNN, get_device, to_tensor


def parse_args():
    """Parse CLI arguments for training and evaluation."""
    p = argparse.ArgumentParser()
    p.add_argument("--pkl", required=True, help="Path to train_rpsb_all.pkl")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--train-samples", type=int, default=200)
    p.add_argument("--eval-samples", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out-dir", default="outputs_xyz")
    return p.parse_args()


def main():
    """Run a small training loop and report baseline metrics."""
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    # Load full dataset and keep variable atom counts.
    dataset = load_dataset(args.pkl)

    # Build train/val/test splits (we only use train/test here).
    n = len(dataset["reactant"]["positions"])
    split_idx = random_split_indices(n, seed=args.seed)
    splits = build_splits(dataset, split_idx)
    train = splits["train"]
    test = splits["test"]

    # Initialize model and optimizer.
    device = get_device()
    model = EGNN(node_dim=6, hidden_dim=64).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    train_n = min(args.train_samples, len(train["reactant"]["positions"]))
    for epoch in range(args.epochs):
        order = rng.permutation(train_n)
        losses = []
        for i in order:
            # Prepare a single training example.
            r_pos = to_tensor(train["reactant"]["positions"][i], device=device)
            p_pos = to_tensor(train["product"]["positions"][i], device=device)
            ts_true = to_tensor(train["transition_state"]["positions"][i], device=device)

            # Concatenate reactant/product positions as node features.
            h = torch.cat([r_pos, p_pos], dim=-1)
            x = r_pos.clone()

            # Predict and optimize MSE against the true TS coordinates.
            opt.zero_grad()
            x_pred, _ = model(x, h)
            loss = torch.mean((x_pred - ts_true) ** 2)
            loss.backward()
            opt.step()
            losses.append(float(loss.detach().cpu()))
        print(f"epoch={epoch} loss={np.mean(losses):.6f}")

    eval_n = min(args.eval_samples, len(test["reactant"]["positions"]))
    rmsd_model = []
    rmsd_midpoint = []

    # Use mean TS energy as a naive baseline if energies are available.
    if "wB97x_6-31G(d).energy" in train["transition_state"]:
        train_e = train["transition_state"]["wB97x_6-31G(d).energy"]
        mean_energy = float(np.mean(train_e))
    else:
        mean_energy = 0.0

    energy_mae = []
    preds_xyz = []
    for i in range(eval_n):
        r_pos = test["reactant"]["positions"][i]
        p_pos = test["product"]["positions"][i]
        ts_true = test["transition_state"]["positions"][i]

        with torch.no_grad():
            # Run model prediction on a single test example.
            r_t = to_tensor(r_pos, device=device)
            p_t = to_tensor(p_pos, device=device)
            h = torch.cat([r_t, p_t], dim=-1)
            x = r_t.clone()
            x_pred, _ = model(x, h)
            ts_pred = x_pred.detach().cpu().numpy()

        # Compare model vs midpoint baseline.
        rmsd_model.append(compute_rmsd(ts_pred, ts_true))
        ts_mid = midpoint_baseline(r_pos, p_pos)
        rmsd_midpoint.append(compute_rmsd(ts_mid, ts_true))
        preds_xyz.append(ts_pred)

        # Optional energy baseline if energies are present.
        if "wB97x_6-31G(d).energy" in test["transition_state"]:
            true_e = float(test["transition_state"]["wB97x_6-31G(d).energy"][i])
            energy_mae.append(compute_energy_mae(mean_energy, true_e))

    print(f"model RMSD: {np.mean(rmsd_model):.6f}")
    print(f"midpoint RMSD: {np.mean(rmsd_midpoint):.6f}")
    if energy_mae:
        print(f"energy MAE (mean baseline): {np.mean(energy_mae):.6f}")

    # Write predicted TS structures as XYZ files for inspection.
    write_xyz_dir(args.out_dir, preds_xyz)
    print(f"Wrote XYZ predictions to {args.out_dir}")


if __name__ == "__main__":
    main()
