"""Combine the raw annual reports into one disease-by-year CSV.

Run from any directory: python scripts/03-data_cleaning.py
Uses only Python's standard library; the original files are never modified.
"""

import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_data"
OUTPUT = ROOT / "data" / "processed" / "yearly_cases_2021_2025.csv"
YEARS = range(2021, 2026)  # Output years; 2026 supplies only 2025 annual figures.
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
COLUMNS = ["Disease Category", "Disease", *MONTHS,
           "Yearly Cases", "Yearly Rate", "Year"]
MISSING = {"", "NA", "N/A", "-"}

# Older reports use short section headings instead of a category column.
CATEGORIES = {
    "Sexually Transmitted and Bloodborne": "Sexually Transmitted and Bloodborne Infections",
    "Enteric, Food and Waterborne": "Enteric Food and Waterborne Diseases",
    "Vaccine Preventable": "Vaccine Preventable Diseases",
    "Direct Contact and Respiratory": "Diseases Transmitted by Direct Contact and Respiratory Routes",
    "Vectorborne and Zoonotics": "Vectorborne and Zoonotic Diseases",
    "Other": "Other Diseases",
    "Encephalitis/Meningitis": "Encephalitis/Meningitis",
}

# Explicit aliases avoid accidentally combining distinct diseases/subtypes.
ALIASES = {
    "Hepatitis B - cases": "Hepatitis B cases",
    "Hepatitis B - carriers": "Hepatitis B carriers",
    "Hepatitis B - unclassified": "Hepatitis B unclassified reports",
    "Chickenpox": "Chickenpox (Varicella)",
    "Haemophilus influenzae, invasive": "Haemophilus influenzae, invasive (all types)",
    "Influenza - sporadic": "Influenza",
    "Influenza - outbreak associated": "Influenza",
    "Monkeypox": "Mpox",
    "Pertussis": "Pertussis (Whooping Cough)",
    "Rubella, congenital syndrome": "Rubella, congenital syndrome (CRS)",
    "Meningococcal disease, invasive": "Meningococcal disease, invasive (IMD)",
    "Group A Streptococcal disease, invasive": "Group A Streptococcal disease, invasive (iGAS)",
    "Group B Streptococcal disease, neonatal": "Group B Streptococcal disease, neonatal (GBS)",
    "Pneumococcal disease, invasive": "Pneumococcal disease, invasive (IPD)",
    "Verotoxin-producing E. coli infection": "Verotoxin-producing E. coli infection (VTEC)",
    "Echinoccoccus multilocularis infection": "Echinococcus multilocularis infection",
    "West Nile Virus": "West Nile Virus (WNV)",
    "Carbapenamase-producing Enterobacteriaceae": "Carbapenemase-producing Enterobacteriaceae (CPE)",
    "Transmissible spongiform encephalopathy: Creutzfeldt-Jakob disease": "Creutzfeldt-Jakob disease (CJD)",
}


def excluded_disease(name):
    """Exclude COVID titles and unavailable encephalitis/meningitis reports."""
    # Footnote 10 in raw_data_2024.csv states that Encephalitis/Meningitis
    # reports from January 2021 onwards were not entered into iPHIS because
    # of operational constraints related to the COVID-19 response.
    title = name.casefold()
    return "covid" in title or title.startswith("encephalitis/meningitis")


def clean_name(name):
    # In the older files, trailing digits are footnote markers, e.g. Mpox7.
    # COVID is filtered BEFORE this step so that COVID-19 is not altered.
    name = re.sub(r"\d+$", "", name).strip()
    return ALIASES.get(name, name)


def read_report(path):
    """Find the actual header below any spreadsheet title/blank rows."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [[cell.strip() for cell in row] for row in csv.reader(handle)]
    for index, header in enumerate(rows):
        if "Disease" in header and all(month in header for month in MONTHS):
            return [dict(zip(header, row)) for row in rows[index + 1:]]
    raise ValueError(f"{path.name}: no header containing all twelve months")


def case_count(value):
    """Keep unavailable counts as None, not zero; reject unexpected values."""
    if value in MISSING:
        return None
    if not value.isdigit():
        raise ValueError(f"Expected a whole case count, found {value!r}")
    return int(value)


def rate_value(value):
    """Preserve censored rates such as <0.1 instead of inventing an exact rate."""
    if value in MISSING:
        return None
    if value.startswith("<"):
        float(value[1:])  # Validate the threshold while retaining the '<'.
        return value
    return float(value)


def complete_sum(values):
    """A missing component makes the total unknown, not a partial total."""
    return None if any(value is None for value in values) else sum(values)


def clean_report(year, reference_categories):
    rows = read_report(RAW_DIR / f"raw_data_{year}.csv")
    category = None
    diseases = {}
    original_names = {}

    for row in rows:
        name = row["Disease"]
        if name.startswith("Source:"):
            break  # All subsequent rows are explanatory notes.
        if name in MISSING or name == "Disease":
            continue
        if name == "Outbreaks":
            break  # These rows count outbreaks, not individual disease cases.
        if "Disease Category" not in row and name in CATEGORIES:
            category = CATEGORIES[name]
            continue
        if excluded_disease(name):
            continue

        original_name = re.sub(r"\d+$", "", name).strip()
        disease = clean_name(name)
        # Use 2025 category membership, including diseases that changed category.
        disease_category = reference_categories.get(
            disease, row.get("Disease Category", category)
        )
        if not disease_category:
            raise ValueError(f"{year}: no category for {name!r}")

        # Select only a rate for THIS year. A prior-year comparison is not valid.
        rate_columns = [key for key in row if re.fullmatch(
            rf"{year} (?:YTD|Total) Rate\d*", key
        )]
        rate = rate_value(row[rate_columns[0]]) if rate_columns else None
        record = {
            "Disease Category": disease_category,
            "Disease": disease,
            **{month: case_count(row[month]) for month in MONTHS},
            "Yearly Rate": rate,
            "Year": year,
        }

        if disease in diseases:
            # The older influenza rows count disjoint sets of CASES. Together
            # they form the single Influenza row used in the newer layout.
            influenza_parts = {"Influenza - sporadic", "Influenza - outbreak associated"}
            if (disease != "Influenza" or
                    {original_names[disease], original_name} != influenza_parts):
                raise ValueError(f"{year}: unexpected duplicate disease {disease!r}")
            previous = diseases[disease]
            for month in MONTHS:
                record[month] = complete_sum([previous[month], record[month]])
            rates = [previous["Yearly Rate"], rate]
            # These influenza rates use the same population denominator.
            record["Yearly Rate"] = (
                sum(rates) if all(isinstance(r, (int, float)) for r in rates)
                else None
            )

        # Calculate monthly sums here; revised 2025 totals are applied below.
        record["Yearly Cases"] = complete_sum([record[m] for m in MONTHS])
        diseases[disease] = record
        original_names[disease] = original_name

    return list(diseases.values())


def update_2025_totals(records):
    """Read only 2025 full-year comparison fields from the partial 2026 report."""
    with (RAW_DIR / "raw_data_2026.csv").open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"Disease", "2025 Total Cases", "2025 Total Rate"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("2026 report is missing required 2025 annual fields")
        annual = {}
        for row in reader:
            name = row["Disease"].strip()
            if excluded_disease(name):
                continue
            disease = clean_name(name)
            if disease in annual:
                raise ValueError(f"2026 report: duplicate disease {disease!r}")
            annual[disease] = row

    differences = []
    for record in records:
        if record["Year"] != 2025:
            continue
        disease = record["Disease"]
        if disease not in annual:
            raise ValueError(f"2026 report: missing 2025 comparison for {disease!r}")
        source = annual[disease]
        total = case_count(source["2025 Total Cases"].strip())
        if total != record["Yearly Cases"]:
            differences.append((disease, record["Yearly Cases"], total))
        record["Yearly Cases"] = total
        record["Yearly Rate"] = rate_value(source["2025 Total Rate"].strip())
    return differences



def main():
    # The 2025 file provides the standard category labels and membership.
    reference = read_report(RAW_DIR / "raw_data_2025.csv")
    reference_categories = {
        row["Disease"]: row["Disease Category"].replace(
            "Enteric, Food and Waterborne Diseases", "Enteric Food and Waterborne Diseases"
        ) for row in reference
    }
    records = []
    for year in YEARS:
        records.extend(clean_report(year, reference_categories))
    category_order = {name: index for index, name in enumerate(dict.fromkeys(reference_categories.values()))}
    records.sort(key=lambda row: (
        category_order.get(row["Disease Category"], len(category_order)),
        row["Disease Category"], row["Disease"], row["Year"],
    ))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)  # None becomes an empty CSV cell.
    
    print(f"Wrote {len(records)} disease-year rows to {OUTPUT}")
    print(f"Rows per year: {dict(sorted(Counter(r['Year'] for r in records).items()))}")
    print(f"Rows with unavailable annual totals: {sum(r['Yearly Cases'] is None for r in records)}")


if __name__ == "__main__":
    main()
