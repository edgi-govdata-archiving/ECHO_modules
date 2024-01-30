ECHO_modules
===============================

.. image:: https://img.shields.io/pypi/v/echo-modules.svg
        :target: https://pypi.python.org/pypi/echo-modules
        :alt: Download Latest Version from PyPI

.. image:: https://img.shields.io/badge/%E2%9D%A4-code%20of%20conduct-blue.svg?style=flat
        :target: https://github.com/edgi-govdata-archiving/overview/blob/main/CONDUCT.md
        :alt: Code of Conduct


*ECHO_modules* is a Python package repository for analyzing a copy of the US Environmental Protection Agency's (EPA) Enforcement and Compliance History Online (ECHO) database.

Background
--------------------------
The US EPA collects a wide variety of data concerning environmental pollution and makes this available through several portals. The ECHO database collates information on industrial facilities' compliance with environmental protection laws like the Clean Water Act and regulatory agencies' enforcement of those laws. ECHO records reported violations, agency inspections of facilities, penalties paid by companies for infractions. It also incorporates information from other sources, such as reported pollutant releases from the Toxics Release Inventory and socio-economic information from EJScreen.

Unfortunately, both the web portal for ECHO (echo.epa.gov) and its API have a number of limitations. First, EPA generally only makes the past 3-5 years worth of data available through these services. Second, EPA typically does not allow aggregating information into meaningful views, such as reports of inspections by Census tract or ZIP code. Instead, searches on echo.epa.gov are usually facility-oriented. This makes it hard to understand the state of environmental enforcement and compliance across an entire geography, company, or industry sector. 

In response, we make regular copies of the full set of historical records in ECHO by scraping echo.epa.gov [here](https://echo.epa.gov/files/echodownloads/). We load a number of specific tables into a [Postgresql database](https://github.com/sunggheel/edgipgdb) hosted at Stony Brook University (SBU). These tables are then linked with one another through various lookups and materialized views. For instance, the table that contains summary information about facilities (ECHO_EXPORTER) is linked to the table with detailed records on Clean Water Act violations through the `NPDES_ID` key. 

`ECHO_modules` provides convenient dataset definitions and pre-defined queries that enable users to retrieve information from the SBU database and to visualize it as tables, maps, and charts. It also supports user-defined queries. With `ECHO_modules`, users can easily access summaries of EPA's records for specific geographies (e.g. a set of ZIP codes) and examine these records in relation to EPA's measures of environmental inequalities (from EJScreen).

Learn more about the SBU copy of ECHO and how it is used by ECHO_modules [here](https://github.com/edgi-govdata-archiving/ECHO_modules/blob/main/SBU-db.md). EDGI's Environmental Enforcement Watch (EEW) works with `ECHO_modules` extensively. For more on the EEW project, visit [here](https://environmentalenforcementwatch.org/) or check out project-specific repositories in the EDGI organization on GitHub.

Interpreting ECHO Data
--------------------------
The ECHO database is notoriously incomplete and biased. EDGI EEW's own research, based on `ECHO_modules` and published [here](https://envirodatagov.org/wp-content/uploads/2022/09/Gaps_and_Disparities_Report.pdf), has found the following:

> * Over 19,000 facilities regulated under foundational environmental protection laws are missing basic information such as their latitude and longitude. Nearly all — 19,657 out of 19,675 (99.9%) — of these are SDWA-regulated facilities.
> * Data needed for basic EJ assessments, such as the percent minority population surrounding a facility or the Census block it resides in, is missing for 14% of the facilities in EPA’s most public-facing database. This increases to 83% of facilities regulated under SDWA. 
> * Nationally, the typical facility regulated under each of these environmental protection laws is missing:
>   * 86% of CWA-specific information
>   * 86% of RCRA-specific information
>   * 71% of CAA-specific information
>   * 40% of SDWA-specific information
> * Facilities in majority-minority communities have somewhat worse data quality scores than facilities in majority-white communities, for all acts except SDWA.
> * Data missingness is substantially worse for facilities in areas already screened by EPA to be of particular concern for environmental injustices and majority-minority areas when looking at Clean Water Act inspections in particular.
> * 78% of all facilities regulated under the CWA are missing inspection counts, but only 75% of facilities in majority white areas, rising to 83% of facilities in majority-minority areas.
> * Western states including Texas, New Mexico, Colorado, Utah, and Nevada are much worse when it comes to inspection data completeness for facilities in majority-minority communities. 

Simply put, ECHO records are flawed because they rely on industry and state self-reporting. For instance, the emissions levels industry provides to EPA are typically estimates rather than direct measurements. ProPublica [has found](https://www.propublica.org/article/whats-polluting-the-air-not-even-the-epa-can-say) that these estimates actually tend to be *overestimates* - industry knows EPA lacks the will and capacity to look into large emitters, while submitting lower numbers might raise suspicion. 

ECHO records also reflect a flawed governance system. Determining that a facility is in violation of its permit to pollute typically requires either accurate and honest self-reporting of emissions, or regulatory inspections of the facility. However, facility inspections have been in decline since at least the Obama administration. Thus, "true" violations are unlikely to be noticed and recorded. In other words, the ECHO database is rife with type II statistical errors ("false negatives"). 

Even when violations are flagged, it is important to keep in mind that these represent emissions above and beyond permitted thresholds (if they are not paperwork violations), but whether or not these permitted thresholds are adequate is entirely different question. Just because a facility is *not* in violation of its permit does not mean that it is inconsequential to human and environmental health, since most permits to pollute do not account for the cumulative effects of multiple polluters in a region or the synergistic effects of multiple pollutants.

[According to](https://global.oup.com/academic/product/next-generation-compliance-9780197656747) former EPA director of enforcement and compliance assurance Cynthia Giles (2020), records related to the Clean Water Act's National Pollutant Discharge Elimination System (NPDES) tend to be the most reliable, in part because of federal requirements that all regulated facilities submit digitized records straight to US EPA.

Any interpretations you make of ECHO data accessed through `ECHO_modules` should keep all the above in mind. For instance, EEW prefers to use language such as "reported violations" and "estimated emissions" when discussing findings. 

Installation & Basic Usage
--------------------------
For a more complete set of examples, see the Jupyter Notebook [here](https://colab.research.google.com/drive/1EqbWz1KqBqlMc1IYMcOPbI_8Equ2Jwmr?usp=sharing) or notebooks in project-specific repositories in the EDGI organization on GitHub.

Command line installation:
```
pip install ECHO_modules
```

Retrieve records of reported violations of the Clean Water Act for Snohomish County in Washington state:

```
from ECHO_modules.make_data_sets import make_data_sets # Import relevant module
ds = make_data_sets(["CWA Violations"]) # Create a DataSet for handling the data
snohomish_cwa_violations = ds["CWA Violations"].store_results(region_type="County", region_value=["SNOHOMISH"] state="WA") # Store results for this DataSet as a DataSetResults object
snohomish_cwa_violations.dataframe # Show the results as a dataframe
```

|   YEARQTR | HLRNC | NUME90Q | NUMCVDT | NUMSVCD | NUMPSCH | FAC_NAME |                 FAC_STREET |                      FAC_CITY | FAC_STATE | ... | FAC_LAT |  FAC_LONG | FAC_DERIVED_WBD | FAC_DERIVED_CD113 | FAC_PERCENT_MINORITY | FAC_POP_DEN | FAC_DERIVED_HUC | FAC_SIC_CODES | FAC_NAICS_CODES | DFR_URL |                                                   |
|----------:|------:|--------:|--------:|--------:|--------:|---------:|---------------------------:|------------------------------:|----------:|----:|--------:|----------:|----------------:|------------------:|---------------------:|------------:|----------------:|--------------:|----------------:|--------:|---------------------------------------------------|
|  NPDES_ID |       |         |         |         |         |          |                            |                               |           |     |         |           |                 |                   |                      |             |                 |               |                 |         |                                                   |
| WAR126958 | 20144 |       U |       0 |       0 |       0 |        0 |           SOUTHGATE RETAIL |                SOUTH REGAL ST |   SPOKANE |  WA |     ... | 47.609302 |     -117.368209 |      1.701031e+11 |                  5.0 |      12.803 |         2038.02 |    17010306.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20112 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20113 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |            1794 |     NaN | http://echo.epa.gov/detailed-facility-report?f... |
| WAR012442 | 20114 |       U |       0 |       0 |       0 |        0 | LIFT STATION 16 FORCE MAIN | 196TH ST SW AND SCRIBER LK RD |  LYNNWOOD |  WA |     ... | 47.820513 |     -122.307499 |      1.711001e+11 |                  2.0 |      32.770 |         4359.82 |    17110012.0 |                 |         |                                                   |

Show the results in chart form:

```
snohomish_cwa_violations.show_chart()
```

Map the results:

```
from ECHO_modules.utilities import aggregate_by_facility, point_mapper # Import relevant modules
aggregated_results = aggregate_by_facility(snohomish_cwa_violations, snohomish_cwa_violations.dataset.name, other_records=True) # Aggregate each entry using this function. In the case of CWA violations, it will summarize each type of violation (permit, schedule, effluent, etc.) and then aggregate them for each facility over time. By setting other_records to True, we also get CWA-regulated facilities in the county without records of violations.
point_mapper(aggregated_results["data"], aggregated_results["aggregator"], quartiles=True, other_fac=aggregated_results["diff"]) # Map each facility as a point, the size of which corresponds to the number of reported violations since 2001.
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
- `Steve Hansen <https://github.com/shansen5>` (Organizer, Project Management, Code, Tests, Documentation, Reviews)
- `Eric Nost <https://github.com/ericnost>` (Organizer, Project Management, Code, Tests, Documentation, Reviews)
- `Kelsey Breseman <https://github.com/frijol>` (Organizer, Project Management, Code, Tests, Documentation, Reviews)
- `Lourdes Vera <https://github.com/lourdesvera>` (Organizer, Project Management, Events, Documentation)
- `Sara Wylie <https://github.com/@saraannwylie>` (Organizer, Project Management, Events, Documentation)
- `Sung-Gheel Jang <https://github.com/@sunggheel>` (Code, Database)
- `Paul St. Denis <https://github.com/@pstdenis>` (Code, Database)
- `Megan Raisle <https://github.com/@mraisle>` (Code)
- `Olivia Chang <https://github.com/@oliviachang29>` (Code)

A more complete list of contributors to EEW is [here](https://github.com/edgi-govdata-archiving/Environmental_Enforcement_Watch?tab=readme-ov-file#people-of-eew)	

License & Copyright
--------------------------
Copyright (C) 2019-2024 Environmental Data and Governance Initiative (EDGI)

This program is free software: you can redistribute it and/or modify it under the terms of the 3-Clause BSD License. See the `LICENSE <https://github.com/edgi-govdata-archiving/wayback/blob/master/LICENSE>` file for details.
