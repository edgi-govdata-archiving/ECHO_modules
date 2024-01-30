# -*- coding: utf-8 -*-
"""ECHO_modules tests

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

This will export the above dataframe as a CSV.
"""

from ECHO_modules.utilities import write_dataset
write_dataset(erie, base = "Facilities", type = "County", state = "NY", regions = ["Erie"])

"""## Find and Chart the 10 Facilities Least Compliant with the Resource and Conservation Recovery Act (RCRA) over the Past 12 Quarters in this County

EPA provides summary data on inspections, violations, and penalties under various environmental protection laws. In the following example, we access that summary data for RCRA-regulated facilities in Erie County, sort it, and then chart it.
"""

from ECHO_modules.utilities import get_top_violators, chart_top_violators # Use get_top_violators and chart_top_violators
erie_top_violators = get_top_violators( erie, flag = 'RCRA_FLAG', noncomp_field = 'RCRA_3YR_COMPL_QTRS_HISTORY', action_field = 'RCRA_FORMAL_ACTION_COUNT', num_fac=10 )
chart_top_violators(erie_top_violators, state = 'NY', selections = "Erie County", epa_pgm = "RCRA" )

"""## Map these Top 10 RCRA Violators"""

from ECHO_modules.get_data import get_spatial_data # Module for getting spatial data from the SBU database
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries
from ECHO_modules.utilities import bivariate_map, map_style # Use this function and variable to make our map
county, state = get_spatial_data( region_type = "County", states = ["NY"], spatial_tables = spatial_tables, region_filter = "Erie") # Query and return spatial data
bivariate_map(regions = county, points = erie_top_violators)

"""## Get Historical (2001-Present) Records of RCRA Violations in this County

EPA not only produces summary information on environmental enforcement and compliance programs, it provides access to "raw" historical records. We limit these to 2001-Present, since EPA says records prior to 2001 are unreliable.
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant module
ds = make_data_sets(["RCRA Violations"]) # Create a DataSet for handling the data
erie_rcra_violations = ds["RCRA Violations"].store_results(region_type="County", region_value=["ERIE"], state="NY") # Store results for this DataSet as a DataSetResults object
erie_rcra_violations.dataframe # Show the results as a dataframe

"""## Show RCRA Violations Over Time in a Chart"""

erie_rcra_violations.show_chart()

"""## Map Facilities in this County with Recorded RCRA Violations (2001-Present)"""

from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules
erie_rcra_violations.region_value=["ERIE"] # (re)set the region_value as a list
aggregated_results = aggregate_by_facility(erie_rcra_violations, erie_rcra_violations.dataset.name, other_records=True) # Aggregate each entry using this function. In the case of RCRA violations, it will summarize each type of violation (permit, schedule, effluent, etc.) and then aggregate them for each facility over time. By setting other_records to True, we also get RCRA-regulated facilities in the county without records of violations.
point_mapper(aggregated_results["data"], aggregated_results["aggregator"], quartiles=True, other_fac=aggregated_results["diff"]) # Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.

"""# Advanced Usage

## Watersheds
Many people may not know the formal name of the watershed they live in (and since watersheds are nested within each other, people live in several watersheds of various sizes, each of which likely has a different name, compounding the challenge).

Most people do, however, know which ZIP code or county they live in. To get ECHO data on a watershed basis, first we query the database for the watersheds intersecting a more well-known geography. (Note: technically, we look up watersheds *within* a more well-known geography. Unfortunately, this means some watersheds will never be selected because they are not fully contained by a state. This is an issue to be fixed.)

In the following example, we get the watersheds that intersect with a county and then look up "serious violators' of the Safe Drinking Water Act within one of those watersheds.

Note: Watershed geographies do not require setting the `state` variable to retrieve data/store results.
"""

from ECHO_modules.get_data import get_spatial_data
from ECHO_modules.geographies import spatial_tables
from ECHO_modules.utilities import show_regions
from ECHO_modules.make_data_sets import make_data_sets # Import relevant module

watersheds, state = get_spatial_data(region_type = "Watershed", states = ["NY"], spatial_tables = spatial_tables) # We look up intersecting watersheds on a state(s) basis.
show_regions(regions = watersheds, states = state, region_type = "Watershed", spatial_tables = spatial_tables) # Map out the watersheds to make it clearer which one we want
watershed = watersheds.loc[watersheds["name"] == "Seneca"] # Filter to the watershed we're interested in

ds = make_data_sets(["SDWA Serious Violators"]) # Create a DataSet for handling the data
seneca_sdwa = ds["SDWA Serious Violators"].store_results(region_type="Watershed", region_value=["0"+str(watershed["huc8"].iloc[0])]) # Store results for this DataSet as a DataSetResults object. In some cases we have to add a "0" back on to the watershed id when it gets convereted to an integer.
seneca_sdwa.dataframe

"""## Multiple Geographies
A DataSetResults object can only store one kind of geography (e.g. ZIP codes OR Counties) but it can store multiple values of that geography (e.g. ZIPs: 53703, 52358, 04345, etc.)

Note: Zip Code geographies do not require setting the `state` variable to retrieve data/store results.
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant module
from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules

ds = make_data_sets(["CWA Inspections"]) # Create a DataSet for handling the data
buffalo_cwa_inspections = ds["CWA Inspections"].store_results(region_type="Zip Code", region_value=["14201", "14202", "14303"]) # Store results for this DataSet as a DataSetResults object

aggregated_results = aggregate_by_facility(records = buffalo_cwa_inspections, program = buffalo_cwa_inspections.dataset.name, other_records=True) # Aggregate each entry using this function
point_mapper(aggregated_results["data"], aggregated_results["aggregator"], quartiles=True, other_fac=aggregated_results["diff"]) # Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.

"""## Multiple Programs

We can load as many programs as we like for each set of geographies (in DataSetResults objects).

Information about available programs can be found in [here](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/v0-1-0/SBU-db.md).

The following produces charts that summarize inspections, violations, and penalties under the Clean Air Act for two of New York's Congressional Districts - #25 and #26.
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant modules
from ECHO_modules.utilities import aggregate_by_facility, point_mapper

ds = make_data_sets(["CAA Inspections", "CAA Violations", "CAA Penalties"]) # Create a DataSet for handling the data
ny_cds_caa_inspections = ds["CAA Inspections"].store_results(region_type="Congressional District", region_value=["25", "26"], state = "NY") # Store results for this DataSet as a DataSetResults object
ny_cds_caa_violations = ds["CAA Violations"].store_results(region_type="Congressional District", region_value=["25", "26"], state = "NY") # Store results for this DataSet as a DataSetResults object
ny_cds_caa_penalties = ds["CAA Penalties"].store_results(region_type="Congressional District", region_value=["25", "26"], state = "NY") # Store results for this DataSet as a DataSetResults object

ny_cds_caa_inspections.show_chart()
ny_cds_caa_violations.show_chart()
ny_cds_caa_penalties.show_chart()

"""## GHGs and other Air Emissions
Beyond enforcement and compliance information, the ECHO database - and our copy of it at Stony Brook University - contains records of industry's self-report releases of various pollutants. These records originate from the Greenhouse Gas Reporting Program and the Toxics Release Inventory (TRI).

The following code returns these records for New York state. If you are interested in a specific GHG or TRI pollutant, some analysis would have to be written outside existing ECHO_modules - we haven't developed specific code to filter these tables to a pollutant(s). An example of this extra code is shown below, however - `ny_tri.dataframe.loc[ny_tri.dataframe['POLLUTANT_NAME'].str.lower().str.contains("mercury")]`
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant modules
from ECHO_modules.utilities import aggregate_by_facility, point_mapper

ds = make_data_sets(["Greenhouse Gas Emissions", "Toxic Releases"]) # Create a DataSet for handling the data
ny_ghg = ds["Greenhouse Gas Emissions"].store_results(region_type="State", region_value = "NY", state = "NY") # Store results for this DataSet as a DataSetResults object
ny_ghg.show_chart() # Total reported emissions in lbs (normalized to CO2e)
ny_tri = ds["Toxic Releases"].store_results(region_type="State", region_value = "NY", state = "NY")
ny_tri.show_chart() # Total emissions in lbs

ny_tri.dataframe = ny_tri.dataframe.loc[ny_tri.dataframe['POLLUTANT_NAME'].str.lower().str.contains("mercury")] # Filter NY_TRI records to just ones where the pollutant is mercury
ny_tri.show_chart() # Chart total mercury emissions in lbs

"""## Discharge Monitoring Reports (DMRs)

Facilities regulated under the Clean Water Act are required to submit monitoring reports directly to EPA. These represent extensive records of levels of pollutants discharged into waterbodies. We currently provide access to reports from Fiscal Year 2022.

The following code maps facilities with DMRs across two watersheds (note: watershed IDs currently have to be looked up separately. See "Watersheds" section above).
"""

from ECHO_modules.make_data_sets import make_data_sets # Import relevant modules
from ECHO_modules.get_data import get_spatial_data # Module for getting spatial data from the SBU database
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries
from ECHO_modules.utilities import bivariate_map, map_style # Use this function and variable to make our map

ds = make_data_sets(["2022 Discharge Monitoring"]) # Create a DataSet for handling the data
dmrs = ds["2022 Discharge Monitoring"].store_results(region_type="Watershed", region_value = ["04120103", "04120102"]) # Store results for this DataSet as a DataSetResults object
watersheds, state = get_spatial_data(region_type = "Watershed", states = ["NY"], spatial_tables = spatial_tables, region_filter = ["04120103", "04120102"]) # Query and return spatial data
bivariate_map(regions = watersheds, points = dmrs.dataframe.drop_duplicates(subset=["FAC_NAME"])) # Map each unique DMR-reporting facility in these watersheds

"""## Mapping
We can symbolize inspections, violations, and so on for areas such as ZIP Codes and Congressional Districts using the `choropleth()` function. This requires a bit of custom pre-processing code since, at the moment, we have no pre-built function for aggregating facility-level inspections to areal units.
"""

from ECHO_modules.utilities import choropleth # Function for mapping data values by areal unit (e.g. ZIP code)
from ECHO_modules.make_data_sets import make_data_sets
from ECHO_modules.get_data import get_spatial_data # Function for getting zip code boundaries
from ECHO_modules.geographies import spatial_tables # Variables that support spatial queries

zips = ['14201','14202','14203','14204','14205','14206','14207','14208','14209','14210',
'14211','14212','14213','14214','14215','14216','14217','14218','14219','14220','14221','14222','14223','14224','14225',
'14226','14227','14228','14231','14233','14240','14241','14260','14261','14263','14264','14265','14267','14269','14270',
'14272','14273','14276','14280']

# Get attribute data
ds = make_data_sets(["CWA Violations"]) # Create a DataSet for handling the data
ny_zips_cwa_inspections = ds["CWA Violations"].store_results(region_type="Zip Code", region_value=zips, state = "NY") # Store results for this DataSet as a DataSetResults object

# Aggregate attribute data
ny_zips_aggregated = ny_zips_cwa_inspections.dataframe.groupby(by="FAC_ZIP")[["NUME90Q"]].sum() # NUME90Q = effluent violations
ny_zips_aggregated.reset_index(inplace=True)
ny_zips_aggregated.rename(columns = {"FAC_ZIP": "zcta5ce20"}, inplace=True) # Rename column to match the spatial data...

# Get spatial data
zips, states = get_spatial_data(region_type = "Zip Code", states = ["NY"], spatial_tables = spatial_tables, region_filter = zips) # Query and return spatial data # [14272,14273,14276,14280]

# Map
choropleth(polygons = zips, attribute_table = ny_zips_aggregated, attribute = "NUME90Q", key_id = "zcta5ce20", legend_name = "Map")

"""## Custom Queries: EJScreen

Records from EPA's EJScreen (2021) are available through custom SQL queries.

For example, the following returns EJScreen information for the state of New York and where the % of the population defined as a racial minority is greater than 75% and the % of the population defined as low-income is greater than 50%.

For more information about EJScreen, see the [documentation](https://gaftp.epa.gov/EJScreen/2021/2021_EJSCREEEN_columns-explained.xlsx) (.xlsx file).
"""

from ECHO_modules.get_data import get_echo_data

sql = 'SELECT * FROM "EJSCREEN_2021_USPR" WHERE "ST_ABBREV" = \'NY\' AND "MINORPCT" > .75 AND "LOWINCPCT" > .5' # This query selects Census Block Group records from EJScreen for the state of New York and where the % of the population defined as a racial minority is greater than 75% and the % of the population defined as low-income is greater than 50%
results = get_echo_data(sql)
results

