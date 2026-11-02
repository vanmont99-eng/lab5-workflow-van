"""Build a one-row-per-patient feature table from cohort.db.

Same logic as Lab 4. The only change: every path is now a command-line
argument, so the Snakefile can declare all of them as inputs/outputs
(including the two .sql files this script reads).

Usage:
    python scripts/build_feature_table.py --db data/raw/cohort.db \
        --features-sql sql/q3_patient_features.sql \
        --genes-sql sql/q1_gene_counts.sql \
        --output results/feature_table.tsv
"""
import argparse
import sqlite3
from pathlib import Path

import pandas as pd

p = argparse.ArgumentParser()
p.add_argument("--db", required=True)
p.add_argument("--features-sql", required=True)
p.add_argument("--genes-sql", required=True)
p.add_argument("--output", required=True)
a = p.parse_args()

# must match the VALUES list in sql/q1_gene_counts.sql
GENES = ["TP53", "KRAS", "EGFR", "STK11", "KEAP1"]

con = sqlite3.connect(a.db)

n_patients = con.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
print(f"patients in the patients table: {n_patients}")

# Step 1: clinical + sample features, one row per patient (SQL does the join)
features = pd.read_sql_query(Path(a.features_sql).read_text(), con)
print(f"after joining samples: {len(features)} rows, "
      f"{features['patient_id'].nunique()} distinct patients")
assert len(features) == n_patients
assert features["patient_id"].is_unique

# Step 2: gene counts in long format, one row per patient per gene (Query 1)
gene_long = pd.read_sql_query(Path(a.genes_sql).read_text(), con)
print(f"gene counts (long): {len(gene_long)} rows "
      f"(expected {n_patients} x {len(GENES)} = {n_patients * len(GENES)})")
assert len(gene_long) == n_patients * len(GENES)
assert set(gene_long["gene_symbol"]) == set(GENES), "GENES list and SQL disagree"

# Step 3: reshape to wide, one column per gene.
# pivot() raises an error if any patient/gene pair shows up twice.
gene_wide = gene_long.pivot(
    index="patient_id", columns="gene_symbol", values="n_protein_altering"
)
gene_wide = gene_wide[GENES].add_suffix("_count").reset_index()
gene_wide.columns.name = None
assert len(gene_wide) == n_patients

# Step 4: combine. validate= makes pandas error out if the merge isn't one-to-one.
table = features.merge(gene_wide, on="patient_id", how="left", validate="one_to_one")
table = table.rename(columns={"tmb_nonsynonymous": "tmb"})
assert len(table) == n_patients
assert table["patient_id"].is_unique

# Gene counts should never be missing: no mutation means 0, not NA
count_cols = [f"{g}_count" for g in GENES]
assert table[count_cols].notna().all().all()

out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
table.to_csv(out, sep="\t", index=False, na_rep="NA")
print(f"wrote {out}: {len(table)} rows")
