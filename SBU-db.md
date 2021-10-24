## Overview of Stony Brook University database

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

        "SDWIS_FLAG": "SDWA_IDS",
        "RCRA_FLAG": "RCRA_IDS",    
        "NPDES_FLAG": "NPDES_IDS",
        "AIR_FLAG": "AIR_IDS",
        "RCRA_FLAG": "RCRA_IDS",

### Database Material Views

If we were to use the tables directly from the EPA CSV files to look into program-specific data tables, 
we would have to get facility information from ECHO_EXPORTER, see if it had its program-specific flag set (e.g. SDWIS_FLAG = 'Y').
Then we would get the program-specific identifiers associated with the facility (e.g. SDWIS_IDS), and search the
program-specific table for matching records.

By creating a pivot table called EXP_PGM in the database and then creating "material views", the SBU database is able to provide
high performing retrieval of the program-specific records that also contain key fields from ECHO_EXPORTER that provide
location and other key information on the facility.
get its 

