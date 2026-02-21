import argparse
import os
import pickle
import re
import sys

import numpy as np
from ase.db import connect


ID_PATTERN = re.compile(r"^(?P<prefix>.+)_rxn(?P<rxn>\d+)_(?P<step>\d+)$")
ENERGY_KEY = "wB97x_6-31G(d).energy"
ATOMIZATION_KEY = "wB97x_6-31G(d).atomization_energy"
FORCES_KEY = "wB97x_6-31G(d).forces"


def get_parser():
    parser = argparse.ArgumentParser(
        description="Convert Halo_8 ASE DB to R/P/TS PKL format similar to train_rpsb_all.pkl."
    )
    parser.add_argument("-i", "--input_path", required=True, help="Input ASE DB path")
    parser.add_argument("-o", "--output_path", required=True, help="Output PKL path")
    parser.add_argument(
        "--max_rows",
        type=int,
        default=None,
        help="Optional cap on rows processed (for quick testing).",
    )
    parser.add_argument(
        "--max_reactions",
        type=int,
        default=None,
        help="Optional cap on reactions retained.",
    )
    return parser


def parse_row_id(row):
    data = row.data or {}
    for key in ("unique_id", "dand_id", "old_dand_id"):
        value = data.get(key)
        if value:
            m = ID_PATTERN.match(value)
            if m:
                return m.group("prefix"), int(m.group("rxn")), int(m.group("step"))
    return None


def snapshot_from_row(row, rxn_name):
    atoms = row.toatoms()
    positions = atoms.positions.copy()
    numbers = atoms.numbers.astype(np.int32)
    natoms = int(len(numbers))
    return {
        "num_atoms": natoms,
        "charges": numbers.tolist(),  # Matches existing PKL convention
        "fragments": [list(range(natoms))],
        "positions": positions,
        "rxn": rxn_name,
        ENERGY_KEY: float(row.energy),
        ATOMIZATION_KEY: float("nan"),
        FORCES_KEY: np.array(row.forces, dtype=np.float64).tolist(),
        "formula": row.formula,
        "xtb_positions": positions.copy(),
    }


def append_entry(section, entry, include_xtb):
    section["num_atoms"].append(entry["num_atoms"])
    section["charges"].append(entry["charges"])
    section["fragments"].append(entry["fragments"])
    section["positions"].append(entry["positions"])
    section["rxn"].append(entry["rxn"])
    section[ENERGY_KEY].append(entry[ENERGY_KEY])
    section[ATOMIZATION_KEY].append(entry[ATOMIZATION_KEY])
    section[FORCES_KEY].append(entry[FORCES_KEY])
    section["formula"].append(entry["formula"])
    if include_xtb:
        section["xtb_positions"].append(entry["xtb_positions"])


def print_args(args):
    print()
    print("Arguments provided:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print()


def main(args):
    print_args(args)

    if not os.path.isfile(args.input_path):
        sys.exit(f"Error: '{args.input_path}' is not a file.")

    rxn_state = {}
    rxn_order = []
    skipped = 0
    processed = 0

    with connect(args.input_path) as db:
        last_selected_rxn = None
        started_selected_block = False
        for idx, row in enumerate(db.select(), start=1):
            if args.max_rows is not None and idx > args.max_rows:
                break

            parsed = parse_row_id(row)
            if parsed is None or not hasattr(row, "energy") or not hasattr(row, "forces"):
                skipped += 1
                continue

            _, rxn_id, step = parsed
            rxn_name = f"rxn{rxn_id}"
            key = rxn_name

            if key not in rxn_state:
                if args.max_reactions is not None and len(rxn_state) >= args.max_reactions:
                    if started_selected_block and key != last_selected_rxn:
                        break
                    continue
                rxn_order.append(key)
                last_selected_rxn = key
                started_selected_block = True
                snap = snapshot_from_row(row, rxn_name)
                rxn_state[key] = {
                    "min_step": step,
                    "max_step": step,
                    "max_energy": float(row.energy),
                    "reactant": snap,
                    "product": snap,
                    "ts": snap,
                }
            else:
                snap = snapshot_from_row(row, rxn_name)
                state = rxn_state[key]
                if step < state["min_step"]:
                    state["min_step"] = step
                    state["reactant"] = snap
                if step > state["max_step"]:
                    state["max_step"] = step
                    state["product"] = snap
                if float(row.energy) > state["max_energy"]:
                    state["max_energy"] = float(row.energy)
                    state["ts"] = snap

            processed += 1

    reactant = {
        "num_atoms": [],
        "charges": [],
        "fragments": [],
        "positions": [],
        "rxn": [],
        ENERGY_KEY: [],
        ATOMIZATION_KEY: [],
        FORCES_KEY: [],
        "formula": [],
        "xtb_positions": [],
    }
    ts = {
        "num_atoms": [],
        "charges": [],
        "fragments": [],
        "positions": [],
        "rxn": [],
        ENERGY_KEY: [],
        ATOMIZATION_KEY: [],
        FORCES_KEY: [],
        "formula": [],
    }
    product = {
        "num_atoms": [],
        "charges": [],
        "fragments": [],
        "positions": [],
        "rxn": [],
        ENERGY_KEY: [],
        ATOMIZATION_KEY: [],
        FORCES_KEY: [],
        "formula": [],
        "xtb_positions": [],
    }

    ts_guess = []
    ts_guess_sbv1 = []
    ts_guess_true = []
    ts_guess_nebci = []
    single_fragment = []
    use_ind = []

    for i, rxn in enumerate(rxn_order):
        state = rxn_state[rxn]
        r = state["reactant"]
        t = state["ts"]
        p = state["product"]

        append_entry(reactant, r, include_xtb=True)
        append_entry(ts, t, include_xtb=False)
        append_entry(product, p, include_xtb=True)

        midpoint = 0.5 * (r["positions"] + p["positions"])
        ts_guess.append(midpoint)
        ts_guess_sbv1.append(midpoint.copy())
        ts_guess_true.append(t["positions"].copy())
        ts_guess_nebci.append(t["positions"].copy())
        single_fragment.append(1)
        use_ind.append(np.int64(i))

    out = {
        "reactant": reactant,
        "transition_state": ts,
        "product": product,
        "single_fragment": single_fragment,
        "use_ind": use_ind,
        "ts_guess": ts_guess,
        "ts_guess_sbv1": ts_guess_sbv1,
        "ts_guess_true": ts_guess_true,
        "ts_guess_NEBCI-xtb": ts_guess_nebci,
    }

    with open(args.output_path, "wb") as f:
        pickle.dump(out, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Processed rows: {processed}")
    print(f"Skipped rows: {skipped}")
    print(f"Reactions saved: {len(rxn_order)}")
    print(f"Saved: {args.output_path}")


if __name__ == "__main__":
    main(get_parser().parse_args())
