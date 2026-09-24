# Communicable Diseases in Toronto: Trends and Implications for Prevention

## Overview
Communicable disease surveillance programs help public health agencies understand how infectious disease patterns change over time and provide evidence for targeted population health initiatives. This report analyzes Toronto’s Monthly Communicable Disease Surveillance Data between 2021 and 2025 using monthly case totals across six disease categories and population-adjusted rates to examine seasonal patterns. Vaccine-preventable diseases showed clear winter seasonality, with influenza accounting for 81.4% to 94.1% of reported cases in the category between 2022 and 2025 and reaching an annual rate of 387.0 cases per 100,000 in 2025. These findings highlight influenza as an important target for seasonal prevention efforts and show how surveillance data can be used alongside vaccination coverage to provide evidence in support of public health programming. 

## Structure

The repo is structured in the following way: 

**Scripts:** 
- Contains all code required to collect, clean and validate data. 
- Provides Jupyter notebook to replicate exploratory data analysis that was performed. 

**Data:**
- */raw_data:* Folder containing the raw dataset that was downloaded from Open Data Toronto 
- */processed:* Folder containing the cleaned dataset. One row represents one disease and year. 
- */synthetic_data:* Folder containing the synthetic data that was created to simluate the cleaned dataset used for analysis. 

**Paper:**
- Contains files related to the produced report including quarto document and references.S

## Disclosure
Apects of the analysis code were written with support from OpenAI Codex. Similarily, Chat-GPT was used to assist in the editing and reviewing of the writing material. A history of the chats is provided in `other/llm/usage.txt`. All final code and written material was reviewed and tested by author.  