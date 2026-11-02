"""Regex-based cleaner for messy_samples.csv.

Usage: python clean_regex.py [input_csv] [output_csv]
Defaults: data/raw/messy_samples.csv -> output/regex_clean.csv
"""
import datetime
import os
import re
import sys

import pandas as pd

IN_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/raw/messy_samples.csv"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "output/regex_clean.csv"

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}
THIS_YEAR = datetime.date.today().year


def clean_id(raw):
    # grab the digits, rebuild as S0000
    m = re.search(r"(\d+)", raw)
    return f"S{int(m.group(1)):04d}" if m else None


def clean_name(raw):
    # collapse extra spaces, fix ALL CAPS
    return re.sub(r"\s+", " ", raw).strip().title()


def clean_sex(raw):
    s = raw.strip().lower()
    if re.fullmatch(r"m(ale)?", s):
        return "M"
    if re.fullmatch(r"f(emale)?", s):
        return "F"
    return "Unknown"  # U, unknown, blank


def clean_site(raw):
    # "site" + any spaces/underscores/dashes + the letter
    m = re.fullmatch(r"site[\s_-]*([abc])", raw.strip().lower())
    return m.group(1).upper() if m else None


def clean_dob(raw):
    s = raw.strip()
    flag = ""
    if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s):      # 01/20/1965
        mo, d, y = m.groups()
    elif m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s):        # 1960-10-28
        y, mo, d = m.groups()
    elif m := re.fullmatch(r"(\d{1,2})-([A-Za-z]{3})-(\d{4})", s):  # 06-Feb-1951
        d, mon, y = m.groups()
        mo = MONTHS[mon.lower()]
    elif m := re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{2})", s):  # 11.24.53
        mo, d, yy = m.groups()
        y = 2000 + int(yy)
        if y > THIS_YEAR:  # a birthday can't be in the future
            y -= 100
        flag = "2-digit year inferred"
    else:
        return None, "unparsed date"
    return datetime.date(int(y), int(mo), int(d)).isoformat(), flag


def clean_glucose(raw_val, raw_unit):
    val = raw_val.strip()
    flags = []
    if val == "" or re.fullmatch(r"n/?a", val, re.IGNORECASE):
        return None, "missing in source"
    if val.endswith("*"):
        flags.append("asterisk in source")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\*?", val)
    if not m:
        return None, "unparsed value"
    num = float(m.group(1))

    unit = re.sub(r"\s", "", raw_unit).lower()
    if unit == "mmol/l":
        if num < 50:
            num = round(num * 18, 1)
            flags.append("converted from mmol/L")
        else:
            flags.append("labeled mmol/L but only plausible as mg/dL, not converted")
    elif unit != "mg/dl":
        flags.append("unknown unit")
    return num, "; ".join(flags)


def main():
    raw = pd.read_csv(IN_PATH, dtype=str, keep_default_na=False)
    rows = []
    for _, r in raw.iterrows():
        dob, dob_flag = clean_dob(r["dob"])
        glu, glu_flag = clean_glucose(r["glucose_value"], r["glucose_unit"])
        rows.append({
            "sample_id": clean_id(r["sample_id"]),
            "patient_name": clean_name(r["patient_name"]),
            "dob": dob,
            "dob_flag": dob_flag,
            "sex": clean_sex(r["sex"]),
            "site": clean_site(r["enrollment_site"]),
            "glucose_mg_dl": glu,
            "glucose_flag": glu_flag,
            "notes": r["notes"].strip(),
        })
    clean = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    clean.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(clean)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
