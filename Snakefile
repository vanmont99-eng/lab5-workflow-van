# Lab 5: Scalable Analysis Workflow
#
# STAGE 2 of 3: branches linked and merged. Report comes next.
#
#   messy_samples.csv --clean_samples--> samples_clean.csv --+
#                                                            +--make_crosswalk--> crosswalk.tsv
#   cohort.db --build_feature_table--> feature_table.tsv ----+          |
#                                            |                          v
#                                            +-----------------> merge_tables --> combined_table.tsv
#                                                                                       |
#                                                                  make_report --> report.md + summary_figure.png
#
# Every script and .sql file a rule uses is listed under input:, so editing
# one of them reruns that rule and everything downstream. Nothing is read
# that the workflow doesn't know about.

configfile: "config.yaml"


rule all:
    input:
        "results/combined_table.tsv",


# ---------- raw data (downloaded, not committed) ----------

rule get_messy_samples:
    input:
        script="scripts/get_data.py",
    output:
        "data/raw/messy_samples.csv",
    params:
        url=config["messy_samples_url"],
    log:
        "logs/get_messy_samples.log",
    shell:
        "python {input.script} --url {params.url} --output {output} > {log} 2>&1"


rule get_cohort_db:
    input:
        script="scripts/get_data.py",
    output:
        "data/raw/cohort.db",
    params:
        url=config["cohort_db_url"],
    log:
        "logs/get_cohort_db.log",
    shell:
        "python {input.script} --url {params.url} --output {output} > {log} 2>&1"


# ---------- stage 1: clean the messy samples (Lab 3 regex) ----------

rule clean_samples:
    input:
        script="scripts/clean_samples.py",
        raw="data/raw/messy_samples.csv",
    output:
        "results/samples_clean.csv",
    log:
        "logs/clean_samples.log",
    shell:
        "python {input.script} {input.raw} {output} > {log} 2>&1"


# ---------- stage 2: query cohort.db (Lab 4 SQL) ----------

rule build_feature_table:
    input:
        script="scripts/build_feature_table.py",
        db="data/raw/cohort.db",
        features_sql="sql/q3_patient_features.sql",
        genes_sql="sql/q1_gene_counts.sql",
    output:
        "results/feature_table.tsv",
    log:
        "logs/build_feature_table.log",
    shell:
        "python {input.script} --db {input.db}"
        " --features-sql {input.features_sql} --genes-sql {input.genes_sql}"
        " --output {output} > {log} 2>&1"


# ---------- stage 3: link and merge ----------

rule make_crosswalk:
    input:
        script="scripts/make_crosswalk.py",
        samples="results/samples_clean.csv",
        patients="results/feature_table.tsv",
    output:
        "results/crosswalk.tsv",
    params:
        seed=config["crosswalk_seed"],
    log:
        "logs/make_crosswalk.log",
    shell:
        "python {input.script} --samples {input.samples} --patients {input.patients}"
        " --seed {params.seed} --output {output} > {log} 2>&1"


rule merge_tables:
    input:
        script="scripts/merge_tables.py",
        samples="results/samples_clean.csv",
        crosswalk="results/crosswalk.tsv",
        features="results/feature_table.tsv",
    output:
        "results/combined_table.tsv",
    log:
        "logs/merge_tables.log",
    shell:
        "python {input.script} --samples {input.samples} --crosswalk {input.crosswalk}"
        " --features {input.features} --output {output} > {log} 2>&1"
