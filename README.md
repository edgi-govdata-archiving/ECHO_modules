===============================
ECHO_modules
===============================

.. image:: https://img.shields.io/pypi/v/wayback.svg
        :target: https://pypi.python.org/pypi/wayback
        :alt: Download Latest Version from PyPI

.. image:: https://img.shields.io/badge/%E2%9D%A4-code%20of%20conduct-blue.svg?style=flat
        :target: https://github.com/edgi-govdata-archiving/overview/blob/main/CONDUCT.md
        :alt: Code of Conduct


*ECHO_modules* is a Python package repository for analyzing a copy of the US Environmental Protection Agency's (EPA) Enforcement and Compliance History Online (ECHO) database.

Background
--------------------------
The US EPA collects a wide variety of data concerning environmental pollution and makes this available through several portals. The ECHO database collates information on industrial facilities' compliance with environmental protection laws like the Clean Water Act and regulatory agencies' enforcement of those laws. ECHO records reported violations, agency inspections of facilities, penalties paid by companies for infractions. It also incorporates information from other sources, such as reported pollutant releases from the Toxics Release Inventory and socio-economic information from EJScreen.

Unfortunately, both the web portal for ECHO (echo.epa.gov) and its API have a number of limitations. First, EPA generally only makes the past 3-5 years worth of data available through these services. Second, EPA typically does not allow aggregating information into meaningful views, such as reports of inspections by Census tract or ZIP code. Instead, searches on echo.epa.gov are usually facility-oriented. This makes it hard to understand the state of environmental enforcement and compliance across an entire geography, company, or industry sector. 

In response, we make regular copies of the full set of historical records in ECHO by scraping echo.epa.gov [here](https://echo.epa.gov/files/echodownloads/). We load a select number of specific tables into a [Postgresql database](https://github.com/sunggheel/edgipgdb) hosted at Stony Brook University (SBU). These tables are then linked through various lookups and materialized views.

`ECHO_modules` provides a set of convenient dataset definitions and pre-defined queries that enable users to retrieve information from the SBU database and to visualize it as tables, maps, and charts. It also supports user-defined queries. With `ECHO_modules`, users can easily access summaries of EPA's records for specific geographies (e.g. a set of ZIP codes) and examine these records in relation to EPA's measures of environmental inequalities (from EJScreen).

Learn more about the SBU copy of ECHO and how it is used by ECHO_modules [here](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/main/SBU-db.md). EDGI's Environmental Enforcement Watch (EEW) works with `ECHO_modules` extensively. For more on the EEW project, visit [here](https://environmentalenforcementwatch.org/) or check out project-specific repositories in the EDGI organization on GitHub.

Installation & Basic Usage
--------------------------
For a more complete set of examples, see the Jupyter Notebook [here](https://colab.research.google.com/drive/1EqbWz1KqBqlMc1IYMcOPbI_8Equ2Jwmr?usp=sharing) or notebooks in project-specific repositories in the EDGI organization on GitHub.

Command line installation:

`pip install ECHO_modules`

Retrieve records of reported violations of the Clean Water Act for Snohomish County in Washington state:

```
from ECHO_modules.make_data_sets import make_data_sets # Import relevant module
ds = make_data_sets(["CWA Violations"]) # Create a DataSet for handling the data
snohomish_cwa_violations = ds["CWA Violations"].store_results(region_type="County", region_value=("SNOHOMISH",) state="WA") # Store results for this DataSet as a DataSetResults object
snohomish_cwa_violations.dataframe # Show the results as a dataframe
```

|   YEARQTR | HLRNC | NUME90Q | NUMCVDT | NUMSVCD | NUMPSCH | FAC_NAME |                 FAC_STREET |                      FAC_CITY | FAC_STATE | ... | FAC_LAT |  FAC_LONG | FAC_DERIVED_WBD | FAC_DERIVED_CD113 | FAC_PERCENT_MINORITY | FAC_POP_DEN | FAC_DERIVED_HUC | FAC_SIC_CODES | FAC_NAICS_CODES | DFR_URL |                                                   |
|----------:|------:|--------:|--------:|--------:|--------:|---------:|---------------------------:|------------------------------:|----------:|----:|--------:|----------:|----------------:|------------------:|---------------------:|------------:|----------------:|--------------:|----------------:|--------:|---------------------------------------------------|
|  NPDES_ID |       |         |         |         |         |          |                            |                               |           |     |         |           |                 |                   |                      |             |                 |               |                 |         |                                                   |
| WAR126958 | 20144 |       U |       0 |       0 |       0 |        0 |           SOUTHGATE RETAIL |                SOUTH REGAL ST |   SPOKANE |  WA |     ... | 47.609302 |     -117.368209 |      1.701031e+11 |                  5.0 |      12.803 |         2038.02 |    17010306.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20112 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20113 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20114 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |                 |         |                                                   |
`...`

Show the results in chart form:

`snohomish_cwa_violations.show_chart()`

Map the results:

```
from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules
aggregated_results = aggregate_by_facility(snohomish_cwa_violations, snohomish_cwa_violations.dataset.name, other_records=True) # Aggregate each entry using this function. In the case of CWA violations, it will summarize each type of violation (permit, schedule, effluent, etc.) and then aggregate them for each facility over time. By setting other_records to True, we also get CWA-regulated facilities in the county without records of violations.
point_mapper(agg["data"], snohomish_cwa_violations.dataset.agg_col, quartiles=True, other_fac=agg["diff"]) # Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.
```

Export the results:
```
from ECHO_modules.utilities import write_dataset
write_dataset( snohomish_cwa_violations.dataframe, "CWAViolations", snohomish_cwa_violations.region_type, snohomish_cwa_violations.state, snohomish_cwa_violations.region_value )
```

Code of Conduct
--------------------------
This repository falls under EDGI’s `Code of Conduct <https://github.com/edgi-govdata-archiving/overview/blob/main/CONDUCT.md>`. Please take a moment to review it before commenting on or creating issues and pull requests.

Contributors
--------------------------
- `Steve Hansen <https://github.com/shansen5>` (Code, Tests, Documentation, Reviews)
- `Eric Nost <https://github.com/ericnost>` (Code, Tests, Documentation, Reviews)
- `Kelsey Breseman <https://github.com/frijol>` (Code, Tests, Documentation, Reviews)
- `Lourdes Vera <https://github.com/lourdesvera>` (Project Management, Events, Documentation)
- `Sara Wylie <https://github.com/@saraannwylie>` (Project Management, Events, Documentation)
- `Sung-Gheel Jang <https://github.com/@sunggheel>` (Code, Database)
- `Paul St. Denis <https://github.com/@pstdenis>` (Code, Database)
- `Megan Raisle <https://github.com/@mraisle>` (Code)
- `Olivia Chang <https://github.com/@oliviachang29>` (Code)

A more complete list of contributors to EEW is [here](https://github.com/edgi-govdata-archiving/Environmental_Enforcement_Watch?tab=readme-ov-file#people-of-eew)	

License & Copyright
--------------------------
Copyright (C) 2019-2024 Environmental Data and Governance Initiative (EDGI)

This program is free software: you can redistribute it and/or modify it under the terms of the 3-Clause BSD License. See the `LICENSE <https://github.com/edgi-govdata-archiving/wayback/blob/master/LICENSE>` file for details.