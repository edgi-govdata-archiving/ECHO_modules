#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 17:05:40 2023

@author: stevehansen

The ECHO_Exporter data for facilities has inconsistent names for counties.
This script strips the most common extra substrings so we can consolidate
the facilities into counties.
"""
from csv import reader
import pandas as pd

input_filename = "../data/state_counties.csv"

with open(input_filename, "r") as read_obj:
    csv_reader = reader(read_obj)
    raw_state_counties = list(map(tuple, csv_reader))

counties = pd.DataFrame(raw_state_counties, columns=['State', 'ECHO County'])
counties['County'] = ''
to_strip = [' COUNTY', ' BOROUGH', ' (CA)', '(CA)', ' CENSUS AREA', 
            ' CITY AND BOROUGH', ' CITY AND', ' CITY', ' PARISH', ' COUNT', 
            ' COUN']
for index, row in counties.iterrows():
    cx = row['ECHO County'].rstrip()
    for x in to_strip:
        strip_len = -(len(x))
        cx = cx[:strip_len] if cx.endswith(x) else cx
    row['County'] = cx
counties.to_csv('../data/state_counties_corrected.csv')
