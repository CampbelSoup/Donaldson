library(opendatatoronto)
library(dplyr)
library(here)
library(glue)

# Create the directory for the output data 
project_dir <- here::here()
output_dir <- file.path(project_dir, "data", "raw_data")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)


resources <- list_package_resources("ec1f8fbb-0296-4eaf-a10d-c58adc0d4245")
# Select the six yearly reports from 2021 through 2026.
relevant_rows <- resources %>%
  filter(grepl("^202[1-6]_Monthly_Report", name))

# Loop to grab the name and slug then save the corresponding year of data from
for (i in seq_len(nrow(relevant_rows))){
  name <- relevant_rows$name[i]
  year <- substr(name, 1,4)
  slug <- relevant_rows$id[i]

  excel_sheets <- get_resource(slug)
  data_path <- file.path(output_dir, glue("raw_data_{year}.csv"))
  write.csv(data, data_path, row.names = FALSE)
  message("Saved ", nrow(data), " rows to: ", data_path)
}
