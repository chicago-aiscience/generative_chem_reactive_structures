# Dataset

## File
- Current dataset file: `train_rpsb_all.pkl`

## Key Structure
Top-level keys include:
- `reactant`
- `product`
- `transition_state`
- `single_fragment`
- `use_ind`
- `ts_guess_*`

Each of `reactant`/`product`/`transition_state` includes fields like:
- `num_atoms`, `charges`, `fragments`, `positions`, `rxn`
- `wB97x_6-31G(d).energy`, `wB97x_6-31G(d).atomization_energy`, `wB97x_6-31G(d).forces`
- `formula`, `xtb_positions`

## Baseline Subset
Baseline uses fixed atom count (most common = 10) with no masking.

## Split Strategy
Random split (train/val/test).

## Notes
Participants are encouraged to extend the baseline to variable-length inputs.
