import argparse
import os
import re
import sys
from collections import OrderedDict

import numpy as np
from ase.db import connect


ID_PATTERN = re.compile(r"^(?P<prefix>.+)_rxn(?P<rxn>\d+)_(?P<step>\d+)$")


def print_args(args):
    print()
    print("Arguments provided:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")
    print()


def parse_row_id(row):
    data = row.data or {}
    for key in ("unique_id", "dand_id", "old_dand_id"):
        value = data.get(key)
        if value:
            m = ID_PATTERN.match(value)
            if m:
                return {
                    "raw_id": value,
                    "prefix": m.group("prefix"),
                    "rxn": int(m.group("rxn")),
                    "step": int(m.group("step")),
                }
    return None


def get_parser():
    parser = argparse.ArgumentParser(
        description="Translate ASE DB file into HDF5 grouped by reaction trajectories."
    )
    parser.add_argument(
        "-i",
        "--input_path",
        required=True,
        help="Path of the input ASE db file",
    )
    parser.add_argument(
        "-o",
        "--output_path",
        required=True,
        help="Path of the output hdf5 file",
    )
    parser.add_argument(
        "--max_rows",
        type=int,
        default=None,
        help="Optional cap on rows processed (useful for quick validation).",
    )
    parser.add_argument(
        "--max_reactions",
        type=int,
        default=None,
        help="Optional cap on number of reactions to export (based on first-seen order).",
    )
    return parser


def main(args):
    print_args(args)

    try:
        import h5py
    except ModuleNotFoundError:
        sys.exit("Missing dependency: h5py. Install with `pip install h5py` and rerun.")

    input_path = args.input_path
    output_path = args.output_path

    if not os.path.isfile(input_path):
        sys.exit(f"Error: '{input_path}' is not a file.")

    rxn_meta = OrderedDict()
    skipped_rows = 0
    parsed_rows = 0

    # Pass 1: gather per-reaction metadata and max frame index.
    # For max_reactions, we treat "first reactions" as first-seen grouped blocks in DB order.
    with connect(input_path) as db:
        for idx, row in enumerate(db.select(), start=1):
            if args.max_rows is not None and idx > args.max_rows:
                break

            if not hasattr(row, "energy") or not hasattr(row, "forces"):
                skipped_rows += 1
                continue

            parsed = parse_row_id(row)
            if parsed is None:
                skipped_rows += 1
                continue

            key = (parsed["prefix"], parsed["rxn"])
            atoms = row.toatoms()

            if key not in rxn_meta:
                if args.max_reactions is not None and len(rxn_meta) >= args.max_reactions:
                    break
                rxn_meta[key] = {
                    "prefix": parsed["prefix"],
                    "rxn": parsed["rxn"],
                    "max_step": parsed["step"],
                    "natoms": len(atoms),
                    "numbers": atoms.numbers.copy(),
                }
            else:
                rxn_meta[key]["max_step"] = max(rxn_meta[key]["max_step"], parsed["step"])

            parsed_rows += 1

    if not rxn_meta:
        sys.exit("No valid rows found. Could not parse any reaction IDs.")

    # Organize keys for deterministic output.
    selected_keys = list(rxn_meta.keys())

    with h5py.File(output_path, "w") as h5file:
        data_group = h5file.create_group("data")

        # Pre-create all reaction datasets using max_step + 1 shape.
        rxn_groups = {}
        for prefix, rxn in selected_keys:
            meta = rxn_meta[(prefix, rxn)]
            nframes = meta["max_step"] + 1
            natoms = meta["natoms"]

            chem_group = data_group.require_group(prefix)
            rxn_group = chem_group.create_group(f"rxn{rxn:05d}")
            rxn_group.create_dataset("atomic_numbers", data=meta["numbers"])
            rxn_group.create_dataset(
                "wB97x_6-31G(d).energy",
                shape=(nframes,),
                dtype=np.float64,
                fillvalue=np.nan,
            )
            rxn_group.create_dataset(
                "wB97x_6-31G(d).forces",
                shape=(nframes, natoms, 3),
                dtype=np.float64,
                fillvalue=np.nan,
            )
            rxn_group.create_dataset(
                "positions",
                shape=(nframes, natoms, 3),
                dtype=np.float64,
                fillvalue=np.nan,
            )
            rxn_group.create_dataset("valid", shape=(nframes,), dtype=np.bool_, fillvalue=False)

            rxn_groups[(prefix, rxn)] = rxn_group

        # Pass 2: fill frame-indexed datasets.
        selected_set = set(selected_keys)
        started_selected_block = False
        with connect(input_path) as db:
            for idx, row in enumerate(db.select(), start=1):
                if args.max_rows is not None and idx > args.max_rows:
                    break

                if not hasattr(row, "energy") or not hasattr(row, "forces"):
                    continue

                parsed = parse_row_id(row)
                if parsed is None:
                    continue

                key = (parsed["prefix"], parsed["rxn"])
                if key in selected_set:
                    started_selected_block = True
                elif started_selected_block and args.max_reactions is not None:
                    # Stop after leaving the selected grouped reaction block.
                    break

                if key not in rxn_groups:
                    continue

                frame_idx = parsed["step"]
                atoms = row.toatoms()
                grp = rxn_groups[key]
                grp["wB97x_6-31G(d).energy"][frame_idx] = row.energy
                grp["wB97x_6-31G(d).forces"][frame_idx, :, :] = row.forces
                grp["positions"][frame_idx, :, :] = atoms.positions
                grp["valid"][frame_idx] = True

    print(f"Parsed rows: {parsed_rows}")
    print(f"Skipped rows: {skipped_rows}")
    print(f"Reactions written: {len(selected_keys)}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main(get_parser().parse_args())
