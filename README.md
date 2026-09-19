# Communicable Disease Trends in Toronto

This project explores trends in reported communicable diseases in the City of Toronto. The planned study period is 2021–2026, with an exploratory comparison between vaccine-preventable disease trends and vaccination coverage using Toronto Open Data.

## Dataset

- **Source:** [Monthly Communicable Disease Surveillance Data](https://open.toronto.ca/dataset/monthly-communicable-disease-surveillance-data/), published by Toronto Public Health through Toronto Open Data.
- **Geographic scope:** City of Toronto, rather than the entire Greater Toronto Area.
- **Format:** Annual Excel workbooks containing a `Monthly Report` sheet and accompanying `Data Notes`.
- **Contents:** Disease names and categories, monthly reported case counts, and comparison measures such as year-to-date counts, previous-year totals and rates, and historical averages. Available columns may vary by workbook.
- **Current download:** `scripts/01-download_data.R` retrieves the 2026 report using the R package `opendatatoronto` and saves it as `data/raw_data/raw_data_2026.csv`. The current local report includes January–July, so 2026 is an incomplete year.

## Initial Analysis Plan

1. Download the yearly reports for 2021–2026 and combine them into a consistent table by disease, year, and month.
2. Explore changes over time and seasonal patterns in reported cases.
3. Identify a suitable vaccination coverage dataset from Toronto Open Data. This second dataset has not yet been selected.
4. Compare relevant vaccine-preventable diseases with coverage for their corresponding vaccines, matching time periods, geography, and population groups where possible.

The comparison will examine associations, not establish that changes in vaccination coverage caused changes in reported disease. Before analysis, review each workbook's data notes, handle missing values and entries such as `<1` explicitly, and compare matching months when a year is incomplete. Case counts and population-based rates should be kept distinct.
