"""Simulate disease-year records and validate simulated or real CSV data.

Run: python scripts/00-simulate_data.py
Check a real file: python scripts/00-simulate_data.py --check data/processed/yearly_cases_2021_2025.csv

Uses only the Python standard library. This is arbitrary test data, not a
realistic disease model. Every allowed disease appears in every study year.
"""

import argparse
import csv
import random
from pathlib import Path

# Share the allowed labels and validation functions with the standalone checker.
from validate_data import MONTHS, DISEASES_BY_CATEGORY, validate_data

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "synthetic_data" / "synthetic_yearly_cases_2021_2025.csv"
COLUMNS = ["Disease Category", "Disease", *MONTHS,
           "Yearly Cases", "Year"]
MAX_MONTHLY_CASES = 10_000  # Inclusive upper bound; change here if needed.



def simulate_data(seed=42):
    """Create one row per allowed disease per year, with reproducible randomness."""
    rng = random.Random(seed)
    rows = []
    for category, diseases in DISEASES_BY_CATEGORY.items():
        for disease in diseases:
            for year in range(2021, 2026):
                counts = {month: rng.randint(0, MAX_MONTHLY_CASES) for month in MONTHS}
                rows.append({
                    "Disease Category": category,
                    "Disease": disease,
                    **counts,
                    "Yearly Cases": sum(counts.values()),
                    "Year": year,
                })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="Validate an existing CSV without changing it.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for simulation (default: 42).")
    args = parser.parse_args()

    if args.check:
        with args.check.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        # Real data can fail because of missing counts or revised annual totals.
        # Findings are reported without filling gaps or overwriting the source.
        return 0 if validate_data(rows) else 1

    rows = simulate_data(args.seed)
    if not validate_data(rows):
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} simulated rows to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
