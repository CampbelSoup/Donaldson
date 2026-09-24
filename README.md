# Communicable Disease Trends in Toronto

This project explores trends in reported communicable diseases in the City of Toronto. The planned study period is 2021–2026, with an exploratory comparison between vaccine-preventable disease trends and vaccination coverage using Toronto Open Data.

## Dataset

- **Source:** [Monthly Communicable Disease Surveillance Data](https://open.toronto.ca/dataset/monthly-communicable-disease-surveillance-data/), published by Toronto Public Health through Toronto Open Data.
- **Geographic scope:** City of Toronto, rather than the entire Greater Toronto Area.
- **Format:** Annual Excel workbooks containing a `Monthly Report` sheet and accompanying `Data Notes`.
- **Contents:** Disease names and categories, monthly reported case counts, and comparison measures such as year-to-date counts, previous-year totals and rates, and historical averages. Available columns may vary by workbook.
- **Current download:** `scripts/01-download_data.R` retrieves the 2026 report using the R package `opendatatoronto` and saves it as `data/raw_data/raw_data_2026.csv`. The current local report includes January–July, so 2026 is an incomplete year.

## Combined Annual Data

Run `python scripts/03-data_cleaning.py` to create the single dataset
`data/processed/yearly_cases_2021_2025.csv`. Rows are grouped by disease category,
disease, and year, with January?December counts followed by `Yearly Cases`,
`Yearly Rate`, and `Year`. Disease titles containing COVID and unavailable
Encephalitis/Meningitis reports are excluded. Footnote 10 of the
[2024 raw report](data/raw_data/raw_data_2024.csv) states that Encephalitis/Meningitis
reports from January 2021 onwards were not entered into iPHIS because of
operational constraints related to the COVID-19 response.

The 2026 report supplies revised **2025** full-year totals and rates; no 2026
observations are included. The 2025 monthly counts remain as originally reported,
so some revised annual totals differ from their monthly sums. See
[data notes and deviations](data/processed/yearly_cases_README.md) for these
changes, missing-value handling, and CSV quoting conventions.

## Simulated data and reusable checks

Run `python scripts/00-simulate_data.py` to generate
`data/synthetic_data/synthetic_yearly_cases_2021_2025.csv`.
The scripts use only the Python standard library. `scripts/validate_data.py`
hardcodes the six category names and 79 allowed disease labels; the simulator
imports these shared definitions. Each disease appears in every year from
2021 through 2025, producing 395 rows with the cleaned CSV's columns except `Yearly Rate`.
Monthly counts are arbitrary integers from 0 to 10,000 inclusive; annual counts
are their sums. Yearly rates are not included in the simulated dataset.
These data are for testing, not a realistic model of disease patterns. The
default random seed is 42; use `--seed 123` to generate another reproducible sample.

Four separate functions in `scripts/validate_data.py` check years, disease/category membership, annual sums,
and nonnegative counts. Each accepts a list of row dictionaries and returns
a list of findings (empty means pass). To apply them to the real dataset:

```sh
python scripts/validate_data.py data/processed/yearly_cases_2021_2025.csv
```

Checking never modifies the input. Missing or invalid counts are flagged, not
changed to zero. Real data may fail the annual-sum check because published totals
were revised or counts are unavailable; a nonnegative-check finding can mean a
missing value, not necessarily a negative count. The command exits with status 1
if any check fails. The 10,000 bound applies only to simulation, not validation
of actual disease counts.

## Initial Analysis Plan

1. Download the yearly reports for 2021–2026 and combine them into a consistent table by disease, year, and month.
2. Explore changes over time and seasonal patterns in reported cases.
3. Identify a suitable vaccination coverage dataset from Toronto Open Data. This second dataset has not yet been selected.
4. Compare relevant vaccine-preventable diseases with coverage for their corresponding vaccines, matching time periods, geography, and population groups where possible.

The comparison will examine associations, not establish that changes in vaccination coverage caused changes in reported disease. Before analysis, review each workbook's data notes, handle missing values and entries such as `<1` explicitly, and compare matching months when a year is incomplete. Case counts and population-based rates should be kept distinct.
