library(opendatatoronto)
library(dplyr)


package <- show_packages("058236d2-d26e-4622-9665-941b9e7a5229")
package


# get all resources for this package
resources <- list_package_resources("058236d2-d26e-4622-9665-941b9e7a5229")
 
# identify datastore resources; by default, Toronto Open Data sets datastore resource format to CSV for non-geospatial and GeoJSON for geospatial resources
datastore_resources <- filter(resources, tolower(format) %in% c('csv', 'geojson'))
 
# load the first datastore resource as a sample
data <- filter(datastore_resources, row_number()==1) %>% get_resource()
data
