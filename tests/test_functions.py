# -*- coding: utf-8 -*-
"""
ECHO_modules tests

The following are lines from the ECHO_modules tutorials, but we can run them in a development environment to ensure there are no errors.

Maps and charts and the like won't display, but that's ok.
"""


"""# Basic Usage
## Analyze Currently Active Facilities in a County

In the following example, we retrieve all of the currently active facilities (according to EPA) in Erie County in New York.
"""

from ECHO_modules.utilities import get_active_facilities # Use the get_active_facilities function

erie = get_active_facilities("NY", "County", ["ERIE"])
erie

"""## Save this Data to CSV Format

This will export the above dataframe as a CSV. If running this notebook in Google Colab, the CSV can be found by clicking on the folder on the left-hand side of the screen and then opening the CSV sub-folder, right-clicking on the "Facilities-NY-County-Erie.csv" file and choosing Download.

First you are able to customize the name of the file we will be creating.
"""

## You may enter a name to use for the file, or use the one provided.
from ECHO_modules.utilities import dataset_filename, write_dataset

filename_widget = dataset_filename(base='Facilities',
               type='County', state='NY', regions=['Erie'])

"""...and now you can write the file."""

from ECHO_modules.utilities import write_dataset
write_dataset(erie, filename_widget.value)

"""## Find and Chart the 10 Facilities Least Compliant with the Resource and Conservation Recovery Act (RCRA) over the Past 12 Quarters in this County

EPA provides summary data on inspections, violations, and penalties under various environmental protection laws. In the following example, we access that summary data for RCRA-regulated facilities in Erie County, sort it, and then chart it.
"""

# Next, we enter the dataframe of Erie County facilities into the get_top_violators() function, then use chart_top_violators to visualize the result
# Use get_top_violators and chart_top_violators
from ECHO_modules.utilities import get_top_violators, chart_top_violators

erie_top_violators = get_top_violators( erie, flag = 'RCRA_FLAG',
                                       noncomp_field = 'RCRA_3YR_COMPL_QTRS_HISTORY',
                                        action_field = 'RCRA_FORMAL_ACTION_COUNT',
                                        num_fac=10 )
chart_top_violators(erie_top_violators, state = 'NY', selections = "Erie County",
                    epa_pgm = "RCRA" )

"""## Map these Top 10 RCRA Violators"""

import geopandas # Import a Python package for creating spatial dataframes
from ECHO_modules.get_data import get_spatial_data # Module for getting spatial data from the SBU database
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries
from ECHO_modules.utilities import bivariate_map, map_style # Use this function and variable to make our map

# Query and return spatial data
county, state = get_spatial_data( region_type = "County", states = ["NY"],
                                 spatial_tables = spatial_tables, region_filter = "Erie")
bivariate_map(regions = county,
              points = geopandas.GeoDataFrame(erie_top_violators,
                                              geometry=geopandas.points_from_xy(
                                                  erie_top_violators['FAC_LONG'],
                                                  erie_top_violators['FAC_LAT']),
                                                  crs=4269
                                              )
              ) # Use Geopandas to create a spatial version of this dataframe so that it can be mapped

"""## Create DataSet templates for all the types of ECHO records

EPA not only produces summary information on environmental enforcement and compliance programs (in its ECHO_EXPORTER records), it provides access to "raw" historical records. These can be accessed through our DataSet collections. Here we will create all of the types of DataSet. These won't hold any records yet. They are just the containers for the types of data. We will populate some of these data_sets later.
"""

from ECHO_modules.make_data_sets import make_data_sets

## List of datasets to choose from
data_sets = make_data_sets([
    "RCRA Violations",
    "RCRA Inspections",
    "RCRA Penalties",
    "CAA Violations",
    "CAA Penalties",
    "CAA Inspections",
    "Combined Air Emissions",
    "Greenhouse Gas Emissions",
    "Toxic Releases",
    "CWA Violations",
    "CWA Inspections",
    "CWA Penalties",
    "SDWA Site Visits",
    "SDWA Enforcements",
    "SDWA Public Water Systems",
    "SDWA Violations",
    "SDWA Serious Violators",
    "2022 Discharge Monitoring",
    "Effluent Violations",
])
## These are described in more detail here: https://github.com/edgi-govdata-archiving/ECHO_modules/blob/main/ECHO_modules/data_set_presets.py
## and here: https://echo.epa.gov/tools/data-downloads#downloads

"""## Get Historical Records of RCRA Violations in this County

Here we will populate one of the DataSet containers, the one for "RCRA Violations", with a request for specific data. We use the DataSet's store_results() function to get the data from the database and keep it in a DatSetResults container owned by the DataSet.

EPA says records prior to 2001 are unreliable. First we'll let you select your years of interest...
"""

from ECHO_modules.utilities import show_year_range_widget
## Slide the endpoints to the desired years
year_range = show_year_range_widget()

"""...and now we can populate the RCRA Violations DataSet for those years."""

# Store results for this DataSet as a DataSetResults object
erie_rcra_violations = data_sets["RCRA Violations"].store_results(
    region_type="County", region_value=["ERIE"], state="NY", years=year_range.value)
erie_rcra_violations.dataframe # Show the results as a dataframe

"""## Show RCRA Violations Over Time in a Chart"""

erie_rcra_violations.show_chart()

"""## Map Facilities in this County with Recorded RCRA Violations"""

from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules

erie_rcra_violations.region_value=["ERIE"] # (re)set the region_value as a list
# Aggregate each entry using this function. In the case of RCRA violations,
# it will summarize each type of violation (permit, schedule, effluent, etc.)
# and then aggregate them for each facility over time.
# By setting other_records to True, we also get RCRA-regulated facilities in the
# county without records of violations.
aggregated_results = aggregate_by_facility(
    erie_rcra_violations, erie_rcra_violations.dataset.name, other_records=True)
# Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.
point_mapper(aggregated_results["data"], aggregated_results["aggregator"],
             quartiles=True, other_fac=aggregated_results["diff"])

"""# Advanced Usage

## Select an area of interest using a map
Administrative boundaries like counties are only so meaningful when it comes to understanding environmental pollution, enforcement, and compliance trends near you. You might want to draw your own neighborhood - this utility lets you do that, and then retrieve records for facilities within those boundaries.

Run the following cell, use the tools in the left part of the map to create a shape, and then run the cell that follows to retrieve Clean Air Act violations for the area.
"""

from ECHO_modules.utilities import polygon_map
area_of_interest = polygon_map()
area_of_interest[0]

# Populate the CAA Violations DataSet that was created earlier.
# Store results for this DataSet as a DataSetResults object
try:
    aoi_caa_violations = data_sets["CAA Violations"].store_results( region_type="Neighborhood",
                            region_value=list(area_of_interest[1])[0], years=[2020,2024] )
    display(aoi_caa_violations.dataframe)
except:
    print("There are no records in that region for this data set.")

"""## Watersheds
Many people may not know the formal name of the watershed they live in (and since watersheds are nested within each other, people live in several watersheds of various sizes, each of which likely has a different name, compounding the challenge).

Most people do, however, know which ZIP code or county they live in. To get ECHO data on a watershed basis, first we query the database for the watersheds intersecting a more well-known geography. (Note: technically, we look up watersheds *within* a more well-known geography. Unfortunately, this means some watersheds will never be selected because they are not fully contained by a state. This is an issue to be fixed.)

In the following example, we get the watersheds that intersect with a state and then look up "serious violators' of the Safe Drinking Water Act within one of those watersheds.

Note: Watershed geographies do not require setting the `state` variable to retrieve data/store results.
"""

from ECHO_modules.get_data import get_spatial_data
from ECHO_modules.geographies import spatial_tables
from ECHO_modules.utilities import show_regions

# We look up intersecting watersheds on a state(s) basis.
watersheds, state = get_spatial_data(region_type = "Watershed", states = ["NY"],
                                     spatial_tables = spatial_tables)
# Map out the watersheds to make it clearer which one we want
show_regions(regions = watersheds, states = state, region_type = "Watershed",
             spatial_tables = spatial_tables)

watershed = watersheds.loc[watersheds["name"] == "Seneca"] # Filter to the watershed we're interested in
ds = make_data_sets(["SDWA Serious Violators"]) # Create a DataSet for handling that watershed's data
# Store results for this DataSet as a DataSetResults object.
# In some cases we have to add a "0" back on to the watershed id when it gets
# convereted to an integer.
seneca_sdwa = ds["SDWA Serious Violators"].store_results(
    region_type="Watershed", region_value=["0"+str(watershed["huc8"].iloc[0])])
seneca_sdwa.dataframe

"""## Ways of Selecting Records on Facilities

A user may have facility IDs obtained, perhaps, from outside of the ECHO data. As examples, RCRA data uses a field called ID_NUMBER and CAA uses PGM_. The database has mapped program-specific IDs to the REGISTRY_IDs that are used in the ECHO_EXPORTER table. Because of that mapping, we can generally work with the REGISTRY_ID to identify a facility. But we could also get to the same data, in the case of RCRA, by asking for the facilities by their ID_NUMBER.

Here we show the two ways of requesting data on facilities, again using RCRA Violations as our example.

### Select Records by Facility Program IDs

We'll use some data we acquired earlier, erie_rcra_violations, to get some of the RCRA program-specific ID_NUMBERs. Then we'll ask the database for records using those ID_NUMBERS and show that the number of records is the same
"""

print(f'The RCRA Violations data contains {len(erie_rcra_violations.dataframe)} records.')

## Even though we already have the same data, we'll get the list of ID_NUMBER values
## and get the data another way. We should get the same data.
ids = erie_rcra_violations.dataframe.index.unique().to_list()
## Pretend we were given this list of facility ID_NUMBERS and asked to get the RCRA Violation
## records for the selected years.
second_results = data_sets['RCRA Violations'].store_results_by_ids(ids, region_type="Facilities",
                                              use_registry_id=False, years=year_range.value)
print(f'second_results contains {len(second_results.dataframe)} records.')

"""### Select Records by REGISTRY_ID

Now we'll go the other direction--we'll take the REGISTRY_IDs from our second_results and ask the database for the matching records. We should again get the same records.
"""

ids = second_results.dataframe['REGISTRY_ID'].unique().tolist()
## This time, pretend we were given this list of facility REGISTRY_IDs and asked to get the RCRA Violation
## records for the selected years.
third_results = data_sets['RCRA Violations'].store_results_by_ids(ids, region_type="Facilities",
                                              use_registry_id=True, years=year_range.value)
print(f'third_results contains {len(third_results.dataframe)} records.')

"""## Multiple Geographies
A DataSetResults object can only store one kind of geography (e.g. ZIP codes OR Counties) but it can store multiple values of that geography (e.g. ZIPs: 53703, 52358, 04345, etc.)

Notes: ZIP Code geographies do not require setting the `state` variable to retrieve data/store results. Also, unlike with counties, which we look retrieve data for using a list like `region_value = ["ERIE"]`, for ZIP codes and watersheds we provide values in a string like `region_value = '14201,14202,14203'`
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant module
from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules

ds = make_data_sets(["CWA Inspections"]) # Create a DataSet for handling the data
# Store results for this DataSet as a DataSetResults object
buffalo_cwa_inspections = ds["CWA Inspections"].store_results(
    region_type="Zip Code", region_value='14201,14202,14203')
aggregated_results = aggregate_by_facility(
    records = buffalo_cwa_inspections,
    program = buffalo_cwa_inspections.dataset.name,
    other_records=True) # Aggregate each entry using this function
# Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.
point_mapper(aggregated_results["data"], aggregated_results["aggregator"],
             quartiles=True, other_fac=aggregated_results["diff"])

"""## Multiple Programs

We can load as many programs as we like for each set of geographies (in DataSetResults objects).

Information about available programs can be found in [here](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/v0-1-0/SBU-db.md).

The following produces charts that summarize inspections, violations, and penalties under the Clean Air Act for two of New York's Congressional Districts - #25 and #26.
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant modules
from ECHO_modules.utilities import aggregate_by_facility, point_mapper

ny_cds_caa_inspections = data_sets["CAA Inspections"].store_results(
    region_type="Congressional District", region_value=["25", "26"], state = "NY",
    years=[2016,2024])
ny_cds_caa_violations = data_sets["CAA Violations"].store_results(
    region_type="Congressional District", region_value=["25", "26"], state = "NY",
    years=[2016,2024])
ny_cds_caa_penalties = data_sets["CAA Penalties"].store_results(
    region_type="Congressional District", region_value=["25", "26"], state = "NY",
    years=[2016,2024])

ny_cds_caa_inspections.show_chart()
ny_cds_caa_violations.show_chart()
ny_cds_caa_penalties.show_chart()

"""## GHGs and other Air Emissions
Beyond enforcement and compliance information, the ECHO database - and our copy of it at Stony Brook University - contains records of industry's self-report releases of various pollutants. These records originate from the Greenhouse Gas Reporting Program and the Toxics Release Inventory (TRI).

The following code returns these records for New York state. If you are interested in a specific GHG or TRI pollutant, some analysis would have to be written outside existing ECHO_modules - we haven't developed specific code to filter these tables to a pollutant(s). An example of this extra code is shown below, however - `ny_tri.dataframe.loc[ny_tri.dataframe['POLLUTANT_NAME'].str.lower().str.contains("mercury")]`
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant modules
from ECHO_modules.utilities import aggregate_by_facility, point_mapper

ny_ghg = data_sets["Greenhouse Gas Emissions"].store_results(
    region_type="State", region_value = "NY", state = "NY",
    years=[2016,2024])
ny_ghg.show_chart() # Total reported emissions in lbs (normalized to CO2e)
ny_tri = data_sets["Toxic Releases"].store_results(
    region_type="State", region_value = "NY", state = "NY",
    years=[2016,2024])
ny_tri.show_chart() # Total emissions in lbs

# Filter NY_TRI records to just ones where the pollutant is mercury
ny_tri.dataframe = ny_tri.dataframe.loc[
    ny_tri.dataframe['POLLUTANT_NAME'].str.lower().str.contains("mercury")]
ny_tri.show_chart() # Chart total mercury emissions in lbs

"""## Discharge Monitoring Reports (DMRs)

Facilities regulated under the Clean Water Act are required to submit monitoring reports directly to EPA. These represent extensive records of levels of pollutants discharged into waterbodies. We currently provide access to reports from Fiscal Year 2022.

The following code maps facilities with DMRs across two watersheds (note: watershed IDs currently have to be looked up separately. See "Watersheds" section above).
"""

from ECHO_modules.get_data import get_spatial_data # Module for getting spatial data from the SBU database
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries
from ECHO_modules.utilities import bivariate_map, map_style # Use this function and variable to make our map

dmrs = data_sets["2022 Discharge Monitoring"].store_results(region_type="Watershed",
                                                     region_value = '04120103, 04120102')
# The facilities in this watershed
dmrs.dataframe = dmrs.dataframe.drop_duplicates(subset=["FAC_NAME"])
# Query and return spatial data
watersheds, state = get_spatial_data(region_type = "Watershed", states = ["NY"],
                                     spatial_tables = spatial_tables,
                                     region_filter = ["04120103", "04120102"])
# Map each unique DMR-reporting facility in these watersheds
# We only keep the columns we need (name, geometry) and use them for pop-ups
# with the fields/aliases parameters
bivariate_map(regions = watersheds[["name", "geometry"]],
              points = geopandas.GeoDataFrame(dmrs.dataframe,
                                              geometry=geopandas.points_from_xy(
                                                  dmrs.dataframe['FAC_LONG'],
                                                  dmrs.dataframe['FAC_LAT']),
                                                  crs=4269
                                              )[["FAC_NAME", "geometry"]],
              region_fields=["name",],
              region_aliases=["Watershed Name: ",],
              points_fields=["FAC_NAME",],
              points_aliases=["Facility Name: "],
              )

"""## Mapping
We can symbolize inspections, violations, and so on for areas such as ZIP Codes and Congressional Districts using the `choropleth()` function.
"""

# Function for aggregating data by spatial unit and mapping data values by that unit (e.g. ZIP code)
from ECHO_modules.utilities import aggregate_by_geography, choropleth
from ECHO_modules.get_data import get_spatial_data # Function for getting zip code boundaries
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries

zips = '14201, 14202, 14203, 14204, 14205, 14206, 14207, 14208, 14209, 14210, 14211, \
14212, 14213, 14214, 14215, 14216, 14217, 14218, 14219, 14220, 14221, 14222, \
14223, 14224, 14225, 14226, 14227, 14228, 14231, 14233, 14240, 14241, 14260, \
14261, 14263, 14264, 14265, 14267, 14269, 14270, 14272, 14273, 14276, 14280'
# Create a duplicate but differently formatted list for the get_spatial_data function
zips_list = [str(z) for z in zips.split(", ")]

# Get attribute data
ny_zips_cwa_inspections = data_sets["CWA Violations"].store_results(region_type="Zip Code",
                                                             region_value=zips, state = "NY",
                                                             years=[2020,2024]) # Store results for this DataSet as a DataSetResults object


# Aggregate attribute data
ny_zips_aggregated = aggregate_by_geography(ny_zips_cwa_inspections,
                                            agg_type="sum",
                                            spatial_tables=spatial_tables)
# Reset the index to make the zip codes available to the choropleth function
ny_zips_aggregated.reset_index(inplace=True)

# Map
choropleth(polygons = ny_zips_aggregated,
           attribute = "NUME90Q",
           key_id = "FAC_ZIP",
           legend_name = "Map")

"""## Custom Queries: EJScreen

Records from EPA's EJScreen (2021) are available through custom SQL queries.

For example, the following returns EJScreen information for the state of New York and where the % of the population defined as a racial minority is greater than 75% and the % of the population defined as low-income is greater than 50%.

For more information about EJScreen, see the [documentation](https://gaftp.epa.gov/EJScreen/2021/2021_EJSCREEEN_columns-explained.xlsx) (.xlsx file).
"""

from ECHO_modules.get_data import get_echo_data

# This query selects Census Block Group records from EJScreen for the state of New York and where the % of the population defined as a racial minority is greater than 75% and the % of the population defined as low-income is greater than 50%
sql = 'SELECT * FROM "EJSCREEN_2021_USPR" WHERE "ST_ABBREV" = \'NY\' ' +\
'AND "MINORPCT" > .75 AND "LOWINCPCT" > .5'
results = get_echo_data(sql)
results
