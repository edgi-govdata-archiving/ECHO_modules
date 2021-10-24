## Overview

This describes how the Stony Brook University (SBU) PostgreSQL database of EPA ECHO data is organized and used. 
This ECHO_modules repository is the primary location
of code to access the database. How this code accesses the database is described in this document.

### Database Schema - Tables

The ECHO tables in the SBU database maintain the same names and fields of the CSV files available for download 
through [the ECHO system here](https://echo.epa.gov/tools/data-downloads#downloads).

#### ECHO_EXPORTER

The ECHO_EXPORTER table is an important summary that can be used to tie together all the other data tables.  It 
provides key facility information

### EPA Facility and Program Identifiers

There are different identifiers used within different EPA programs (Clean Air Act, Clean Water Act, Safe Drinking Water Act, 
Resource Conservation and Recovery Act, etc.)

### Database Material Views

