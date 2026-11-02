"""Merge cleaned samples + crosswalk + patient features into one table.

One row per Lab 3 sample. validate= makes pandas stop if any join is not
one-to-one, and the asserts check nothing got dropped or duplicated.

Usage:
    python scripts/merge_tables.py --samples results/samples_clean.csv \
        --crosswalk results/crosswalk.tsv --features results/feature_table.tsv \
        --output results/combined_table.tsv
"""
import argparse
from pathlib import Path

import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--samples", required=True)
p.add_argument("--crosswalk", required=True)
p.add_argument("--features", required=True)
p.add_argument("--output", required=True)
a = p.parse_args()

samples = pd.read_csv(a.samples)
xw = pd.read_csv(a.crosswalk, sep="\t")
feats = pd.read_csv(a.features, sep="\t", keep_default_na=False, na_values=["NA"])

# rename overlapping columns so it's obvious which dataset each came from
samples = samples.rename(columns={"sex": "sex_sample", "site": "enrollment_site"})
feats = feats.rename(columns={"sex": "sex_patient"})

combined = (
    samples
    .merge(xw, on="sample_id", how="left", validate="one_to_one")
    .merge(feats, on="patient_id", how="left", validate="one_to_one")
)

assert len(combined) == len(samples), "merge changed the number of rows"
assert combined["patient_id"].notna().all(), "a sample has no linked patient"

# sanity check the crosswalk rule: where sample sex is known, it has to match
known = combined["sex_sample"].isin(["M", "F"])
expected = combined.loc[known, "sex_sample"].map({"M": "male", "F": "female"})
assert (expected == combined.loc[known, "sex_patient"]).all(), "sex mismatch"

out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(out, sep="\t", index=False, na_rep="NA")
print(f"wrote {out}: {len(combined)} rows x {combined.shape[1]} columns")
