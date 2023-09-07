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
counties = pd.read_csv(input_filename)
counties['County'] = ''

to_strip = [' COUNTY', ' BOROUGH', ' (CA)', '(CA)', ' (CITY)', ' CENSUS AREA', 
            ' CITY AND BOROUGH', ' CITY AND', ' CITY', ' PARISH', ' COUNT', 
            ' COUN', ' (B)', ' MUNICIPIO']
for index, row in counties.iterrows():
    cx = row['FAC_COUNTY'].rstrip()
    for x in to_strip:
        strip_len = -(len(x))
        cx = cx[:strip_len] if cx.endswith(x) else cx
    row['County'] = cx
counties.to_csv('../data/state_counties_corrected.csv')
