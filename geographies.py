spatial_tables = {
    #table_name = name of table in spatial database
    #id_field = field used to identify the data
    #match_field = field used to match data with ECHO
    #pretty_field = field that has a human-readable ID e.g. county name

    # HUC8
    "Watershed": dict(
        table_name="wbdhu8",
        id_field="huc8",
        match_field="huc8",
        pretty_field="NAME"
    ),

    "HUC10 Watersheds": dict(
        table_name="wbdhu10",
        id_field="huc10",
        match_field="huc10",
        pretty_field="NAME"
    ),

    "HUC12 Watersheds": dict(
        table_name="wbdhu12",
        id_field="huc12",
        match_field="huc12",
        pretty_field="NAME"
    ),

    "Ecoregions": dict(
        table_name="eco_level3",
        id_field="US_L3NAME" #e.g. Atlantic Coastal Pine Barrens     
    ),

    "County": dict(
        table_name="tl_2019_us_county",
        id_field="GEOID", # four or five digit code corresponding to two digit state number (e.g. 55) and 2-3 digit county code! 
        match_field="NAME", #match with state_counties.csv
        pretty_field="NAME" # e.g. CEDAR
    ),

    "Zip Code": dict(
        table_name="tl_2019_us_zcta510",
        id_field="zcta5ce10",
        match_field="zcta5ce10",
        pretty_field="zcta5ce10" 
    ),

    "EPA Region": dict(
        table_name="epa_regions",
        id_field="eparegion" # In the form of "Region 1", "Region 2", up to "Region 10"
    ),

    "State": dict(
        table_name = "tl_2019_us_state",
        id_field = "STUSPS", # e.g. MS, IA, AK
        match_field="STUSPS",
        pretty_field="NAME" # e.g. cedar
    ),

    "Congressional District": dict(
        table_name = "tl_2019_us_cd116", # Unfortunately, ECHO seems based on 113th Congress
        id_field = "GEOID", # this is the combination of the state id and the CD e.g. AR-2 = 0502
        match_field="CD116FP", #match with state_counties.csv
        pretty_field="CD116FP" # two digit state-specific district number
    )
}

region_field = {
    'State': { "field": 'FAC_STATE' },
    'Congressional District': { "field": 'FAC_DERIVED_CD113' },
    'County': { "field": 'FAC_COUNTY' },
    'Zip Code': { "field": 'FAC_ZIP' },
    'Watershed': {"field": 'FAC_DERIVED_HUC'}
}
# Commenting out these region types until implemented
#     'Census Block': {"field": 'FAC_DERIVED_CB2010'} # We don't have this in the spatial database because there are too many CBs - too much data!
#     'EPA Region': { "field": 'FAC_EPA_REGION'} # Possibly too large to handle in Colab environment

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

