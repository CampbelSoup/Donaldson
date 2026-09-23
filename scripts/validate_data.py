"""Reusable checks for simulated or cleaned disease data.

Run: python scripts/validate_data.py path/to/data.csv
Import individual test functions to check a list of row dictionaries.
The input is never modified; missing values and revised totals are reported.
"""

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Hardcoded allowed labels, matching the cleaned dataset. The simulator does
# not read real observations or derive its categories from an input file.
DISEASES_BY_CATEGORY = {'Diseases Transmitted by Direct Contact and Respiratory Routes': ['Group A Streptococcal disease, '
                                                                   'invasive (iGAS)',
                                                                   'Group B Streptococcal disease, '
                                                                   'neonatal (GBS)',
                                                                   'Legionellosis',
                                                                   'Leprosy',
                                                                   'Mpox',
                                                                   'SARS',
                                                                   'TB: Atypical mycobacterial '
                                                                   'infections',
                                                                   'Tuberculosis',
                                                                   'Tuberculosis infection, latent '
                                                                   '(LTBI)'],
 'Enteric Food and Waterborne Diseases': ['Amebiasis',
                                          'Botulism',
                                          'Campylobacter enteritis',
                                          'Cholera',
                                          'Cryptosporidiosis',
                                          'Cyclosporiasis',
                                          'Food poisoning',
                                          'Giardiasis',
                                          'Hepatitis A',
                                          'Listeriosis',
                                          'Paralytic shellfish poisoning',
                                          'Paratyphoid fever',
                                          'Salmonellosis',
                                          'Shigellosis',
                                          'Trichinosis',
                                          'Typhoid fever',
                                          'Verotoxin-producing E. coli infection (VTEC)',
                                          'Yersiniosis'],
 'Sexually Transmitted and Bloodborne Infections': ['AIDS',
                                                    'Chancroid',
                                                    'Chlamydia',
                                                    'Gonorrhea',
                                                    'HIV',
                                                    'Hepatitis B carriers',
                                                    'Hepatitis B cases',
                                                    'Hepatitis B unclassified reports',
                                                    'Hepatitis C',
                                                    'Ophthalmia neonatorum',
                                                    'Syphilis, early congenital',
                                                    'Syphilis, infectious',
                                                    'Syphilis, late congenital',
                                                    'Syphilis, late latent',
                                                    'Syphilis, other',
                                                    'Syphilitic stillbirth'],
 'Vaccine Preventable Diseases': ['Acute flaccid paralysis',
                                  'Adverse vaccine reactions',
                                  'Chickenpox (Varicella)',
                                  'Diphtheria',
                                  'Haemophilus influenzae, invasive (all types)',
                                  'Influenza',
                                  'Measles',
                                  'Meningococcal disease, invasive (IMD)',
                                  'Mumps',
                                  'Pertussis (Whooping Cough)',
                                  'Pneumococcal disease, invasive (IPD)',
                                  'Poliomyelitis',
                                  'Rubella',
                                  'Rubella, congenital syndrome (CRS)',
                                  'Smallpox',
                                  'Tetanus'],
 'Vectorborne and Zoonotic Diseases': ['Anaplasmosis',
                                       'Anthrax',
                                       'Babesiosis',
                                       'Brucellosis',
                                       'Echinococcus multilocularis infection',
                                       'Hantavirus',
                                       'Hemorrhagic fevers',
                                       'Lassa fever',
                                       'Lyme disease',
                                       'Plague',
                                       'Powassan virus',
                                       'Psittacosis/Ornithosis',
                                       'Q fever',
                                       'Rabies',
                                       'Tularemia',
                                       'West Nile Virus (WNV)'],
 'Other Diseases': ['Blastomycosis',
                    'Candida auris',
                    'Carbapenemase-producing Enterobacteriaceae (CPE)',
                    'Creutzfeldt-Jakob disease (CJD)']}


def number(value):
    """Read a numeric CSV cell; return None for missing or non-finite values."""
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except InvalidOperation:
        return None


def row_name(index, row):
    """Identify an invalid record in a human-readable error message."""
    return f"Row {index}: {row.get('Disease', '?')} ({row.get('Year', '?')})"


# Each test accepts a list of row dictionaries (from simulation or DictReader)
# and returns error messages. An empty list means the test passed.
def test_year_range(rows):
    """Check that every year is a whole number from 2021 through 2025."""
    errors = []
    for index, row in enumerate(rows, start=2):
        year = number(row.get("Year"))
        if year is None or year not in range(2021, 2026):
            errors.append(f"{row_name(index, row)}: year must be an integer in 2021-2025.")
    return errors


def test_disease_category(rows):
    """Check that the disease belongs to its hardcoded, allowed category."""
    errors = []
    for index, row in enumerate(rows, start=2):
        allowed = DISEASES_BY_CATEGORY.get(row.get("Disease Category"), [])
        if row.get("Disease") not in allowed:
            errors.append(f"{row_name(index, row)}: disease/category combination is not allowed.")
    return errors


def test_yearly_sum(rows):
    """Check each annual count equals its twelve monthly counts, with none missing."""
    errors = []
    for index, row in enumerate(rows, start=2):
        monthly = [number(row.get(month)) for month in MONTHS]
        annual = number(row.get("Yearly Cases"))
        if annual is None or any(value is None for value in monthly):
            errors.append(f"{row_name(index, row)}: cannot verify total; missing or invalid count.")
        elif annual != sum(monthly):
            errors.append(
                f"{row_name(index, row)}: annual count {annual} differs from monthly sum {sum(monthly)}."
            )
    return errors


def test_nonnegative_cases(rows):
    """Check monthly and annual counts are numeric and nonnegative; missing is not zero."""
    errors = []
    for index, row in enumerate(rows, start=2):
        for column in [*MONTHS, "Yearly Cases"]:
            value = number(row.get(column))
            if value is None:
                errors.append(f"{row_name(index, row)}: {column} is missing or invalid.")
            elif value < 0:
                errors.append(f"{row_name(index, row)}: {column} is negative ({value}).")
    return errors


def validate_data(rows):
    """Run the four independent tests, print their findings, and return pass/fail."""
    if not rows:
        print("FAIL: dataset is empty.")
        return False
    passed = True
    for test in [test_year_range, test_disease_category, test_yearly_sum, test_nonnegative_cases]:
        errors = test(rows)
        print(f"{'FAIL' if errors else 'PASS'}: {test.__name__} ({len(errors)} findings)")
        for error in errors:
            print(f"  {error}")
        if errors:
            passed = False
    return passed



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path, help="CSV dataset to validate.")
    args = parser.parse_args()
    with args.csv_file.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    return 0 if validate_data(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
