## Overview of Stony Brook University database - Organization and Use

This describes how the Stony Brook University (SBU) PostgreSQL database of EPA ECHO data is organized and used. 
This ECHO_modules repository is the primary location
of code to access the database. How this code accesses the database is described in this document.

### Database Schema - Tables

The ECHO tables in the SBU database maintain the same names and fields of the CSV files available for download 
through [the ECHO system here](https://echo.epa.gov/tools/data-downloads#downloads).

#### ECHO_EXPORTER

The ECHO_EXPORTER table is an important summary that can be used to tie together all the other data tables.  It 
provides key facility location information like state, zip code, congressional district and watershed.  It has flags 
that identify which EPA programs the facility is regulated under, and then lists identifiers to sub-sites within 
those programs that let us match the facility in the records of tables with more detailed information within those
programs.

For example, the ECHO_EXPORTER field SDWIS_FLAG will indicate whether the facility is regulated under the Safe Drinking
Water Act (SDWA).  If the flay is 'Y' then the SDWA_IDS field can list one or more identifiers which will match the
PWSID field in the tables SDWA_PUB_WATER_SYSTEMS, SDWA_SITE_VISITS, SDWA_VIOLATIONS, etc.

### EPA Facility and Program Identifiers

There are different identifiers used within different EPA programs (Clean Air Act, Clean Water Act, Safe Drinking Water Act, 
Resource Conservation and Recovery Act, etc.)  The ECHO_EXPORTER fields for the different EPA programs that allow this
mapping from ECHO_EXPORTER's REGISTRY_ID field to program-specific identifiers are as follows:

EPA Program | ECHO_EXPORTER flag | Program-specific ID field
------------| ------------------ | -------------------------
SDWA |       SDWIS_FLAG | SDWA_IDS
RCRA |        RCRA_FLAG | RCRA_IDS    
CWA |       NPDES_FLAG | NPDES_IDS
CAA |        AIR_FLAG | AIR_IDS
RCRA |        RCRA_FLAG | RCRA_IDS
GHG | GHG_FLAG | GHG_IDS
TRI | TRI_FLAG | TRI_IDS

### Database Material Views

If we were to use the tables directly from the EPA CSV files to look into program-specific data tables, 
we would have to get facility information from ECHO_EXPORTER, see if it had its program-specific flag set (e.g. SDWIS_FLAG = 'Y').
Then we would get the program-specific identifiers associated with the facility (e.g. SDWIS_IDS), and search the
program-specific table for matching records.

By creating a pivot table called EXP_PGM in the database and then creating "material views", the SBU database is able to provide
high performing retrieval of the program-specific records that also contain key fields from ECHO_EXPORTER that provide
location and other key information on the facility.

Every facility in ECHO_EXPORTER will have one or more rows in the EXP_PGM table. The EXP_PGM table has this simple structure:
* PGM - This is the EPA program identifier--SDWIS, RCRA, CWA, CAA, GHG, etc.
* REGISTRY_ID - This is the value of the key field in ECHO_EXPORTER.  The value is also used in some program data sets.
* PGM_ID - This is the value of the key field in the program-specific table.  
Again, there may be multiple rows with different PGM_ID
values for the same REGISTRY_ID value.

The schema of the material views in the SBU database can be found in [the schema.psql](https://github.com/edgi-govdata-archiving/ECHOEPA-to-SQL/blob/main/schema.psql) file in the ECHOEPA-to-SQL Github repository.

### Defining DataSets - make_data_sets.py and data_set_presets.py

There are a number of parameters that can be used in creating DataSet objects. For data we have been working with there
are definitions in the *data_set_presets.py* file, in the ATTRIBUTE_TABLES list.  Here is an example of a DataSet definition for 
the RCRA Violations which will serve to discuss the options:
```Python
    "RCRA Violations": dict(
        idx_field="ID_NUMBER",
        base_table="RCRA_VIOLATIONS",
        table_name="RCRA_VIOLATIONS_MVIEW",
        echo_type="RCRA",
        date_field="DATE_VIOLATION_DETERMINED",
        date_format="%m/%d/%Y",
        agg_type="count",
        agg_col="VIOL_DETERMINED_BY_AGENCY",
        unit="violations"
 ```
     
 **idx_field** - This is the index field of the table.  The RCRA program uses a field called ID_NUMBER as its key.  CWA
 program files use NPDES_ID, SDWA uses PWSID, Greenhouse Gas uses REGISTRY_ID, CAA uses PGM_SYS_ID.
 **base_table** - This is the name of the ECHO CSV file, and the PostgreSQL table that imports it.
 **table_name** - This is the name of the material view for the table, which has concatenated several key ECHO_EXPORTER
 fields identifying the facility to the base_table.
 **echo_type** - This identifies the program-type--RCRA, AIR, GHG, NPDES, SDWA, TRI.
 **date_field** - This is the best option identifying a date with the record.  It might be the date of violation, inspection, or
 enforcement decision.  There may be multiple dates associated with the record and choosing the appropriate one for the analysis
 at hand will be necessary.
 **date_format** - The program-specific files do not all format the dates alike. This field lets us specify the format to use
 for this DataSet.
 **agg_type** - When records for this type of data are aggregated, how it that done?  In some cases we simply "count" the records
 that are found.  Alternatively we might "sum" the values in the *agg_col* field of the record.
 **agg_col** - This is the field on which we may want to aggregate values of the DataSet.  If the *agg_type* is "count" and 
 we are simply counting records, it could be any field in the data set.  If *agg_type* is "sum" then the values of this column
 are summed.
 
 Generally it will be better to use the **table_name** value to query the database, since the results will have the facility information
 along with the program-specific data.

By default, all of the data set definitions in the ATTRIBUTE_TABLE of *data_set_presets.py* are used to construct all
of the corresponding DataSet objects by the make_data_set() function in *make_data_set.py*. A list can also be given to 
the function to construct only some of the DataSets.  For example, 
```Python
make_data_sets(["RCRA Violations", "CAA Enforcements"])
```
will only cause the creation of these two DataSet objects.
