SPATIAL_TABLES = {
    "HUC8 Watersheds": dict(
        table_name="wbdhu8",
        id_field="huc8"
    ),

    "HUC10 Watersheds": dict(
        table_name="wbdhu10",
        id_field="huc10"
    ),

    "HUC12 Watersheds": dict(
        table_name="wbdhu12",
        id_field="huc12"
    ),

    #"Ecoregions": dict(
    #    table_name="eco_level3",
    #    id_field="US_L3NAME" #e.g. Atlantic Coastal Pine Barrens 
    #    
    #),


    #"Counties": dict(
    #    table_name="tl_2019_us_county",
    #    id_field="GEOID" # four or five digit code corresponding to two digit state number (e.g. 55) and 2-3 digit county code! 
    #    
    #),

    "Zip Codes": dict(
        table_name="tl_2020_us_zcta520",
        id_field="zcta5ce20" 
        
    ),

    "EPA Regions": dict(
        table_name="epa_regions",
        id_field="eparegion" # In the form of "Region 1", "Region 2", up to "Region 10"
    ),

    "States": dict(
        table_name = "tl_2019_us_state",
        id_field = "STUSPS" # e.g. MS, IA, AK
    ),

    "Congressional Districts": dict(
        table_name = "tl_2019_us_cd116",
        id_field = "GEOID" # this is the combination of the state id and the CD e.g. AR-2 = 0502
    )
}

# The keys of this dictionary are the preset names and the values are
# dictionaries of the constructor arguments for `DataSet` that should be used
# when creating one based on the preset.
ATTRIBUTE_TABLES = {
    "Facilities": dict(
        idx_field="REGISTRY_ID", 
        base_table="ECHO_EXPORTER",
        table_name="ECHO_EXPORTER",
        echo_type="",
        date_field="",
        date_format="%m/%d/%Y",
        agg_type="count", 
        agg_col="", 
        unit=""
    ),

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
    ),

    "RCRA Inspections": dict(
        idx_field="ID_NUMBER", 
        base_table="RCRA_EVALUATIONS",
        table_name="RCRA_EVALUATIONS_MVIEW",
        echo_type="RCRA",
        date_field="EVALUATION_START_DATE",
        date_format="%m/%d/%Y", 
        agg_type="count",
        agg_col="EVALUATION_AGENCY", 
        unit="inspections"
    ),

    "RCRA Penalties": dict(
        echo_type="RCRA",
        base_table="RCRA_ENFORCEMENTS",
        table_name="RCRA_ENFORCEMENTS_MVIEW",
        idx_field="ID_NUMBER", 
        date_field="ENFORCEMENT_ACTION_DATE",
        date_format="%m/%d/%Y", 
        agg_type="sum",
        agg_col="FMP_AMOUNT",
        unit="dollars"
    ),

    "ICIS EPA Inspections": dict(
        echo_type="AIR",
        base_table="ICIS_FEC_EPA_INSPECTIONS",
        table_name="AIR_INSPECTIONS_MVIEW",
        idx_field="REGISTRY_ID", 
        date_field="ACTUAL_END_DATE",
        date_format="%m/%d/%Y", 
        agg_type="count",
        agg_col="ACTIVITY_TYPE_DESC", 
        unit="inspections"
    ),

    "CAA Violations": dict(
        echo_type="AIR",
        base_table="ICIS-AIR_VIOLATION_HISTORY",
        table_name="AIR_VIOLATIONS_MVIEW",
        idx_field="PGM_SYS_ID", 
        date_field="Date",
        date_format="%m-%d-%Y", 
        agg_type="count",
        agg_col="AGENCY_TYPE_DESC", 
        unit="violations"
    ),

    "CAA Penalties": dict(
        echo_type="AIR",
        base_table="ICIS-AIR_FORMAL_ACTIONS",
        table_name="AIR_FORMAL_ACTIONS_MVIEW",
        idx_field="PGM_SYS_ID",
        date_field="SETTLEMENT_ENTERED_DATE",
        date_format="%m/%d/%Y", 
        agg_type="sum",
        agg_col="PENALTY_AMOUNT",
        unit="dollars"
    ),

    "CAA Inspections": dict(
        echo_type="AIR",
        base_table="ICIS-AIR_FCES_PCES",
        table_name="AIR_COMPLIANCE_MVIEW",
        idx_field="PGM_SYS_ID",
        date_field="ACTUAL_END_DATE",
        date_format="%m-%d-%Y", 
        agg_type="count",
        agg_col="STATE_EPA_FLAG", 
        unit="inspections"
    ),

    "Combined Air Emissions": dict(
        echo_type=["GHG","TRI"],
        base_table="POLL_RPT_COMBINED_EMISSIONS",
        table_name="COMBINED_AIR_EMISSIONS_MVIEW", 
        idx_field="REGISTRY_ID",
        date_field="REPORTING_YEAR", 
        date_format="%Y"
    ),

    "Greenhouse Gas Emissions": dict(
        echo_type="GHG",
        base_table="POLL_RPT_COMBINED_EMISSIONS",
        table_name="GREENHOUSE_GASES_MVIEW",
        idx_field="REGISTRY_ID",
        date_field="REPORTING_YEAR",
        date_format="%Y", 
        agg_type="sum",
        agg_col="ANNUAL_EMISSION", 
        unit="metric tons of CO2 equivalent"
    ),

    "Toxic Releases": dict(
        echo_type="TRI",
        base_table="POLL_RPT_COMBINED_EMISSIONS",
        table_name="TOXIC_RELEASES_MVIEW",
        idx_field="REGISTRY_ID",
        date_field="REPORTING_YEAR",
        date_format="%Y",
        agg_type="sum",
        agg_col="ANNUAL_EMISSION", 
        unit="pounds"
    ),

    "CWA Violations": dict(
        echo_type="NPDES",
        base_table="NPDES_QNCR_HISTORY",
        table_name="WATER_QUARTERLY_VIOLATIONS_MVIEW", 
        idx_field="NPDES_ID",
        date_field="YEARQTR",
        date_format="%Y", 
        agg_type="sum",
        agg_col="NUME90Q", 
        unit="effluent violations"
    ),

    "CWA Inspections": dict(
        echo_type="NPDES",
        base_table="NPDES_INSPECTIONS",
        table_name="CLEAN_WATER_INSPECTIONS_MVIEW", 
        idx_field="NPDES_ID",
        date_field="ACTUAL_END_DATE", 
        date_format="%m/%d/%Y",
        agg_type="count", 
        agg_col="STATE_EPA_FLAG",
        unit="inspections"
    ),

    "CWA Penalties": dict(
        echo_type="NPDES",
        base_table="NPDES_FORMAL_ENFORCEMENT_ACTIONS",
        table_name="CLEAN_WATER_ENFORCEMENT_ACTIONS_MVIEW", 
        idx_field="NPDES_ID",
        date_field="SETTLEMENT_ENTERED_DATE", 
        date_format="%m/%d/%Y",
        agg_type="sum", 
        agg_col="FED_PENALTY_ASSESSED_AMT",
        unit="dollars"
    ),

    "SDWA Site Visits": dict(
        echo_type="SDWA",
        base_table="SDWA_SITE_VISITS",
        table_name="SDWA_SITE_VISITS_MVIEW",
        idx_field="PWSID",
        date_field="SITE_VISIT_DATE",
        date_format="%m/%d/%Y"
    ),

    "SDWA Enforcements": dict(
        echo_type="SDWA",
        base_table="SDWA_ENFORCEMENTS",
        table_name="SDWA_ENFORCEMENTS_MVIEW",
        idx_field="PWSID",
        date_field="ENFORCEMENT_DATE",
        date_format="%m/%d/%Y"
    ),

    "SDWA Public Water Systems": dict(
        echo_type="SDWA",
        base_table="SDWA_PUB_WATER_SYSTEMS",
        table_name="SDWA_PUB_WATER_SYSTEMS_MVIEW",
        idx_field="PWSID",
        date_field="FISCAL_YEAR",
        date_format="%Y"
    ),

    "SDWA Violations": dict(
        echo_type="SDWA",
        base_table="SDWA_VIOLATIONS",
        table_name="SDWA_VIOLATIONS_MVIEW",
        idx_field="PWSID",
        date_field="FISCAL_YEAR",
        date_format="%Y"
    ),

    "SDWA Serious Violators": dict(
        echo_type="SDWA",
        base_table="SDWA_SERIOUS_VIOLATORS",
        table_name="SDWA_SERIOUS_VIOLATORS_MVIEW",
        idx_field="PWSID",
        date_field="FISCAL_YEAR",
        date_format="%Y"
    ),
    
    "2020 Discharge Monitoring": dict(
        echo_type="NPDES",
        base_table="NPDES_DMRS_FY2020",
        table_name="DMR_FY2020_MVIEW",
        idx_field="EXTERNAL_PERMIT_NMBR",
        date_field="LIMIT_BEGIN_DATE",
        date_format="%m/%d/%Y",
        agg_type="count", 
        agg_col = "VIOLATION_CODE",
        unit = "discharge monitoring reports"
    ),

    "2022 Discharge Monitoring": dict(
        echo_type="NPDES",
        base_table="NPDES_DMRS_FY2022",
        table_name="DMR_FY2022_MVIEW",
        idx_field="EXTERNAL_PERMIT_NMBR",
        date_field="LIMIT_BEGIN_DATE",
        date_format="%m/%d/%Y",
        agg_type="count", 
        agg_col = "VIOLATION_CODE",
        unit = "discharge monitoring reports"
    ),

    "Effluent Violations": dict(
        echo_type = "NPDES",
        base_table = "NPDES_EFF_VIOLATIONS",
        table_name="EFF_VIOLATIONS_MVIEW",
        idx_field="NPDES_ID",
        date_field="MONITORING_PERIOD_END_DATE",
        date_format="%Y-%m-%d",
        agg_type="count", 
        agg_col="VIOLATION_CODE", # What should the default be? Can modify in post-processing...
    )

    # "SDWA Return to Compliance": dict(
    #     echo_type="SDWA",
    #     table_name="SDWA_RETURN_TO_COMPLIANCE",
    #     idx_field="PWSID",
    #     date_field="FISCAL_YEAR",
    #     date_format="%Y"
    # )
}

REGIONS = {
    'States': { "field": 'FAC_STATE' },
    'Congressional Districts': { "field": 'FAC_DERIVED_CD113' },
    'Counties': { "field": 'FAC_COUNTY' },
    'Zip Codes': { "field": 'FAC_ZIP' },
    'HUC8 Watersheds': {"field": 'FAC_DERIVED_HUC'},
    'HUC12 Watersheds': {"field": 'FAC_DERIVED_WBD'},
    #'Census Block': {"field": 'FAC_DERIVED_CB2010'} # No spatial data available yet
}

def get_attribute_tables():
    return ATTRIBUTE_TABLES
