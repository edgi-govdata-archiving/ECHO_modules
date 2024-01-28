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
        table_name="tl_2020_us_county",
        id_field="geoid", # four or five digit code corresponding to two digit state number (e.g. 55) and 2-3 digit county code! 
        match_field="name", #match with state_counties.csv
        pretty_field="name" # e.g. CEDAR
    ),

    "Zip Code": dict(
        table_name="tl_2020_us_zcta520",
        id_field="zcta5ce20",
        match_field="zcta5ce20",
        pretty_field="zcta5ce20" 
    ),

    "EPA Region": dict(
        table_name="epa_regions",
        id_field="eparegion" # In the form of "Region 1", "Region 2", up to "Region 10"
    ),

    "State": dict(
        table_name = "tl_2020_us_state",
        id_field = "stusps", # e.g. MS, IA, AK
        match_field="stusps",
        pretty_field="name" # e.g. cedar
    ),

    "Congressional District": dict(
        table_name = "tl_2020_us_cd116", # Unfortunately, ECHO seems based on 113th Congress
        id_field = "GEOID", # this is the combination of the state id and the CD e.g. AR-2 = 0502
        match_field="CD116FP", #match with state_counties.csv
        pretty_field="CD116FP" # two digit state-specific district number
    )
    ,

    "Census Tract": dict(
        table_name = "###", # 
        id_field = "GEOID10", # 
        match_field="GEOID10", # 
        pretty_field="GEOID10" # NAMELSAD10 ?
    )
}

region_field = {
    'State': { "field": 'FAC_STATE' },
    'Congressional District': { "field": 'FAC_DERIVED_CD113' },
    'County': { "field": 'FAC_COUNTY' },
    'Zip Code': { "field": 'FAC_ZIP' },
    'Watershed': {"field": 'FAC_DERIVED_HUC'},
    'Census Tract': {"field": 'FAC_DERIVED_CB2010'},
}
# Commenting out these region types until implemented
#     'Census Block': {"field": 'FAC_DERIVED_CB2010'} # We don't have this in the spatial database because there are too many CBs - too much data!
#     'EPA Region': { "field": 'FAC_EPA_REGION'} # Possibly too large to handle in Colab environment

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

fips = {
  "AK": "02",
  "AL": "01",
  "AR": "05",
  "AS": "60",
  "AZ": "04",
  "CA": "06",
  "CO": "08",
  "CT": "09",
  "DC": "11",
  "DE": "10",
  "FL": "12",
  "GA": "13",
  "GU": "66",
  "HI": "15",
  "IA": "19",
  "ID": "16",
  "IL": "17",
  "IN": "18",
  "KS": "20",
  "KY": "21",
  "LA": "22",
  "MA": "25",
  "MD": "24",
  "ME": "23",
  "MI": "26",
  "MN": "27",
  "MO": "29",
  "MS": "28",
  "MT": "30",
  "NC": "37",
  "ND": "38",
  "NE": "31",
  "NH": "33",
  "NJ": "34",
  "NM": "35",
  "NV": "32",
  "NY": "36",
  "OH": "39",
  "OK": "40",
  "OR": "41",
  "PA": "42",
  "PR": "72",
  "RI": "44",
  "SC": "45",
  "SD": "46",
  "TN": "47",
  "TX": "48",
  "UT": "49",
  "VA": "51",
  "VI": "78",
  "VT": "50",
  "WA": "53",
  "WI": "55",
  "WV": "54",
  "WY": "56"
}

