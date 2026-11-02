"""Make a SYNTHETIC crosswalk linking each Lab 3 sample to one Lab 4 patient.

Why this exists: messy_samples.csv (S0001...) and cohort.db (TCGA barcodes)
share no ID, so there is no real way to join them. This script makes up a
link so the pipeline has something to merge on. It is NOT real linkage and
nothing downstream should be read as a finding.

Rules:
- Samples with known sex (M/F) get a patient of the same sex.
- Samples with Unknown sex get a patient of any recorded sex.
- Patients with no recorded sex in cohort.db are never used.
- No patient is used twice.
- Seeded, so the same inputs + seed always give the same crosswalk.

Usage:
    python scripts/make_crosswalk.py --samples results/samples_clean.csv \
        --patients results/feature_table.tsv --seed 6854 \
        --output results/crosswalk.tsv
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--samples", required=True)
p.add_argument("--patients", required=True)
p.add_argument("--seed", type=int, required=True)
p.add_argument("--output", required=True)
a = p.parse_args()

rng = np.random.default_rng(a.seed)
samples = pd.read_csv(a.samples).sort_values("sample_id")
patients = pd.read_csv(a.patients, sep="\t", keep_default_na=False, na_values=["NA"])
patients = patients[patients["sex"].isin(["male", "female"])].sort_values("patient_id")

# shuffle each sex's patient pool once, then hand patients out in order
pools = {
    "M": list(rng.permutation(patients.loc[patients.sex == "male", "patient_id"])),
    "F": list(rng.permutation(patients.loc[patients.sex == "female", "patient_id"])),
}

rows = []
# known-sex samples first so they get first pick from their own pool
for sex in ["M", "F"]:
    for sid in samples.loc[samples.sex == sex, "sample_id"]:
        rows.append({"sample_id": sid, "patient_id": pools[sex].pop(),
                     "match_basis": f"same sex ({sex})"})

# Unknown-sex samples draw from whatever is left in both pools
leftover = list(rng.permutation(pools["M"] + pools["F"]))
for sid in samples.loc[~samples.sex.isin(["M", "F"]), "sample_id"]:
    rows.append({"sample_id": sid, "patient_id": leftover.pop(),
                 "match_basis": "sample sex unknown, any patient"})

xw = pd.DataFrame(rows).sort_values("sample_id")
assert len(xw) == len(samples), "every sample should get exactly one patient"
assert xw["sample_id"].is_unique and xw["patient_id"].is_unique

out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
xw.to_csv(out, sep="\t", index=False)
print(f"wrote {out}: {len(xw)} synthetic sample-patient links")
print(xw["match_basis"].value_counts().to_string())
