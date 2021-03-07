"""
Create a DataSet object for each of the programs we track.
Initialize each one with the information it needs to do its query
of the database.

Store the DataSet objects in a dictionary with keys being the
friendly names of the program, which will be used in selection
widgets.
"""

# In the following line, 'from DataSet' refers to the file DataSet.py
# while 'import DataSet' refers to the DataSet class within DataSet.py.

from ECHO_modules.DataSet import DataSet


# These are all the presets that `make_data_sets()` can construct.
# The keys of this dictionary are the preset names and the values are
# dictionaries of the constructor arguments for `DataSet` that should be used
# when creating one based on the preset.
PRESETS = {
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
        date_format="%Y"
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
    
    "DMRs": dict(
        echo_type="NPDES",
        base_table="NPDES_DMRS_FY2020",
        table_name="DMRS_FY2020_MVIEW",
        idx_field="EXTERNAL_PERMIT_NMBR",
        date_field="MONITORING_PERIOD_END_DATE",
        date_format="%m/%d/%Y", 
        agg_type="sum",
        agg_col="LIMIT_VALUE_NMBR", #we need to take a closer look and think through how to summarize this info, since it addresses a vast array of chemicals and differing units of measure
        unit="units" #differing units of measure, which can be found in the LIMIT_UNIT_DESC field
    )

    "2020 Discharge Monitoring": dict(
        echo_type="NPDES",
        base_table="NPDES_DMRS_FY2020",
        table_name="DMR_FY2020_MVIEW",
        idx_field="EXTERNAL_PERMIT_NMBR",
        date_field="LIMIT_BEGIN_DATE",
        date_format="%m/%d/%Y",
    ),

    # "SDWA Return to Compliance": dict(
    #     echo_type="SDWA",
    #     table_name="SDWA_RETURN_TO_COMPLIANCE",
    #     idx_field="PWSID",
    #     date_field="FISCAL_YEAR",
    #     date_format="%Y"
    # )
}


def make_data_sets( data_set_list = None ):
    """
    Create DataSet objects from a list of preset configurations. This takes a
    list of preset names and returns a dictionary where the keys are the preset
    names and values are the DataSet objects that were created with those
    presets. These presets are an important convenience since DataSet objects
    are complex with lots of options.

    For example, the preset "RCRA Violations" creates a DataSet from the
    ``RCRA_VIOLATIONS`` table, indexed by the ``ID_NUMBER`` column, with the
    date format ``%m/%d/%Y``, and so on.

    Parameters
    ----------
    data_set_list : sequence of str
        A list of preset configuration names for which to construct DataSets.
        e.g. ``["RCRA Violations", "CAA Enforcements"]``. If not set, this will
        construct and return a DataSet for every possible preset.

    Returns
    -------
    dict
        A dictionary where the keys are the preset names and the values are
        the ``DataSet`` objects created from the presets.

    Examples
    --------
    >>> make_data_sets(["RCRA Violations", "CAA Enforcements"])
    {
        "RCRA Violations":  DataSet(name="RCRA Violations",
                                    idx_field="ID_NUMBER",
                                    base_table="RCRA_VIOLATIONS",
                                    # and so on
                                   ),
        "CAA Enforcements": DataSet(name="CAA Enforcements",
                                    idx_field="REGISTRY_ID",
                                    base_table="CASE_ENFORCEMENTS",
                                    # and so on
                                   ),
    }
    """
    return {name: DataSet(name=name, **PRESETS[name])
            for name in data_set_list or PRESETS.keys()}
