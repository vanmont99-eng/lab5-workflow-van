"""Download one raw input file from the course repo.

Adapted from Lab 4's get_data.py so the URL and destination come from the
Snakefile/config instead of being hard-coded.

Usage: python scripts/get_data.py --url URL --output PATH
"""
import argparse
import urllib.request
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--url", required=True)
p.add_argument("--output", required=True)
a = p.parse_args()

dest = Path(a.output)
dest.parent.mkdir(parents=True, exist_ok=True)
print(f"downloading {a.url}")
urllib.request.urlretrieve(a.url, dest)
print(f"saved {dest} ({dest.stat().st_size / 1e6:.2f} MB)")
