# AI Usage

**Model:** Claude 

## Key prompts

 "lets do the same think for lab 5 really take. deep dive into rubric and then even go into lectures and demos to get a better ideas then we start"
 "can you explain to me what lab 5 is doing first and make sure you are explaining throughout waht each step of the process is doing keeping a data base for the final read me while reminding me to push constantly"

After that it was step by step. Claude explained each file, I predicted the job count, ran it, and sent back the output, as well as checked the outputs and code was giving me to make sure nothing was missing as well to strenghthen my knowledge in what was going on. This helped me a lot because I do not have a ton of expierence in coding and Snakemake, so by using AI I got to finish the assignment as well as learn a lot about how I can utilize these commands in other scenarios and in future projects that may utilize Snakemake. 

AI did help me write most of the code but I made sure to stick with it line by line to understand what was going on. I had it draft the read me and I read through it making sure that I could follow every step that it was giving, tweaking it by hand if something needed to be clarified, go in more detail, or made more concise for people trying to run my code. 

## How I built it

We built the Snakefile in 3 stages, like the Week 10 demo (`Snakefile.1` -> `.2` -> `.3`), and I committed after each one.

| Step | My job-count prediction | Actual | Notes |
|---|---|---|---|
| Stage 1: downloads, clean, feature table | 3 | 5 | I forgot the 2 download rules count as jobs. The downloads ran in parallel. Feature table log matched my Lab 4 numbers (566 patients, 2830 gene rows). |
| Stage 2: crosswalk + merge | 4 | 3 | I thought rule all counted twice because it lists 2 files. It's one job no matter how many files it lists. |
| Stage 3: report | 2 | 2 | |
| Clean run from nothing | | 8 | |
| Partial rerun (edit S0001 glucose) | 5 | 5 | clean_samples, make_crosswalk, merge_tables, make_report, all. The SQL branch didn't rerun. |

## Things the AI got wrong, and how they got caught

1. There was a bug where the first version did not have the 'scripts/get_data.py' as an input. I caught it the outputs were not matching what was expected and we rebuilt the stag 1 Snakfile and fixed it. Downloads were rerun 
2. The file AI sent me was the old version. During stage 2 when I ran it i got an output of "nothing to be done" and no merges. AI checked my repo and found the Snakfile was still the stage 1 version, so my stage 2 commit was broken. I asked AI to help me with this and at first it blamed VS Code, but I checked and the file was not even open so it could not have rewrote it. The problem was the file was a cahced older copy and it fixed it by mkaing a new file, which then happened again in stage 3 as well.
3. My explanation was wrong as

## Things I checked for because the course warned about them

The Week 10 practical slides show an AI-written Snakefile with 2 bugs that still run without errors: I made sure that the config was used and rule all asks for the final report in figure. 

## Snags that weren't the AI's fault

- **Forgot to activate the environment** in a new terminal the next day. zsh said `snakemake: command not found`. Fixed with `conda activate lab5`.
- **Ran the partial-rerun block twice.** The second `sed` had nothing to replace but rewrote the file with a new timestamp, and Snakemake said "Nothing to be done" because the content hadn't changed. The second `tee` overwrote my evidence files. I re-downloaded the original with `snakemake --cores 2 -R get_messy_samples`


## What I verified myself

- Job counts for each run 
- Clean run started from an empty state: every `reason:` line in `evidence/01_clean_run.txt` says "Missing output files"
- The partial rerun has no `get_cohort_db` or `build_feature_table` jobs
- Made sure the data in the freeature table matches my lab 4/
- Double checked cross walk and 
- S0001 (F) is linked to a female patient
- The restored data gives the same results as before the edit
- Opened the rule graph and summary figure
