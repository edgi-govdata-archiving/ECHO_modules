# Create a DataSet object for each of the programs we track.  
# Initialize each one with the information it needs to do its query
# of the database.
# Store the DataSet objects in a dictionary with keys being the
# friendly names of the program, which will be used in selection
# widgets.

# In the following line, 'from DataSet' refers to the file DataSet.py
# while 'import DataSet' refers to the DataSet class within DataSet.py.

from ECHO_modules.DataSet import DataSet

def make_data_sets( data_set_list = None ):
    data_sets = {}
    ds_name = 'RCRA Violations'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, idx_field='ID_NUMBER', 
                        base_table='RCRA_VIOLATIONS',
                        table_name='RCRA_VIOLATIONS_MVIEW', echo_type="RCRA",
                        date_field='DATE_VIOLATION_DETERMINED', 
                        date_format='%m/%d/%Y', agg_type = "count", 
                        agg_col="VIOL_DETERMINED_BY_AGENCY", 
                        unit="violations") 
                        # For possible later use in assessing state v federal )
        data_sets[ ds.name ] = ds
    ds_name = 'RCRA Inspections'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, idx_field='ID_NUMBER', 
                        base_table='RCRA_EVALUATIONS',
                        table_name='RCRA_EVALUATIONS_MVIEW', echo_type="RCRA",
                        date_field='EVALUATION_START_DATE', date_format='%m/%d/%Y', 
                        agg_type = "count", agg_col="EVALUATION_AGENCY", 
                        unit="inspections") 
                        # For possible later use in assessing state v federal )
        data_sets[ ds.name ] = ds
    ds_name = 'RCRA Penalties'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name,  echo_type="RCRA",
                        base_table='RCRA_ENFORCEMENTS',
                        table_name='RCRA_ENFORCEMENTS_MVIEW', idx_field='ID_NUMBER', 
                        date_field='ENFORCEMENT_ACTION_DATE', date_format='%m/%d/%Y', 
                        agg_type = "sum", agg_col="FMP_AMOUNT", unit="dollars") 
        data_sets[ ds.name ] = ds
    ds_name = 'ICIS EPA Inspections'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="AIR",
                        base_table='ICIS_FEC_EPA_INSPECTIONS',
                        table_name='AIR_INSPECTIONS_MVIEW', idx_field='REGISTRY_ID', 
                        date_field='ACTUAL_END_DATE', date_format='%m/%d/%Y', 
                        agg_type = "count", agg_col="ACTIVITY_TYPE_DESC", 
                        unit="inspections" )
        data_sets[ ds.name ] = ds
    ds_name = 'CAA Enforcements'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name,  echo_type="AIR",
                        base_table='CASE_ENFORCEMENTS',
                        table_name='AIR_ENFORCEMENTS_MVIEW', idx_field='REGISTRY_ID',
                        date_field='FISCAL_YEAR', date_format='%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'CAA Violations'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name,  echo_type="AIR",
                        base_table='ICIS-AIR_VIOLATION_HISTORY',
                        table_name='AIR_VIOLATIONS_MVIEW', idx_field='PGM_SYS_ID', 
                        date_field='Date', date_format='%m-%d-%Y', 
                        agg_type = "count", agg_col="AGENCY_TYPE_DESC", 
                        unit="violations") 
                        # For possible later use in assessing state v federal )
        data_sets[ ds.name ] = ds
    ds_name = 'CAA Penalties'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="AIR",
                        base_table='ICIS-AIR_FORMAL_ACTIONS',
                        table_name='AIR_FORMAL_ACTIONS_MVIEW', idx_field='PGM_SYS_ID',
                        date_field='SETTLEMENT_ENTERED_DATE', date_format='%m/%d/%Y', 
                        agg_type = "sum", agg_col="PENALTY_AMOUNT", unit="dollars") 
        data_sets[ ds.name ] = ds
    ds_name = 'CAA Inspections'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="AIR",
                        base_table='ICIS-AIR_FCES_PCES',
                        table_name='AIR_COMPLIANCE_MVIEW', idx_field='PGM_SYS_ID',
                        date_field='ACTUAL_END_DATE', date_format='%m-%d-%Y', 
                        agg_type = "count", agg_col="STATE_EPA_FLAG", 
                        unit="inspections") 
                        # For possible later use in assessing state v federal )
        data_sets[ ds.name ] = ds
    ds_name = 'Combined Air Emissions'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type=["GHG","TRI"],
                        base_table='POLL_RPT_COMBINED_EMISSIONS',
                        table_name='COMBINED_AIR_EMISSIONS_MVIEW', 
                        idx_field='REGISTRY_ID', date_field='REPORTING_YEAR', 
                        date_format='%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'Greenhouse Gas Emissions'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="GHG",
                        base_table='POLL_RPT_COMBINED_EMISSIONS',
                        table_name='GREENHOUSE_GASES_MVIEW', idx_field='REGISTRY_ID',
                        date_field='REPORTING_YEAR', date_format='%Y', 
                        agg_type = "sum", agg_col="ANNUAL_EMISSION", 
                        unit="metric tons of CO2 equivalent")
        data_sets[ ds.name ] = ds
    ds_name = 'Toxic Releases'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="TRI",
                        base_table='POLL_RPT_COMBINED_EMISSIONS',
                        table_name='TOXIC_RELEASES_MVIEW', idx_field='REGISTRY_ID',
                        date_field='REPORTING_YEAR', date_format='%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'CWA Violations'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="NPDES",
                        base_table='NPDES_QNCR_HISTORY',
                        table_name='WATER_QUARTERLY_VIOLATIONS_MVIEW', 
                        idx_field='NPDES_ID', date_field='YEARQTR', date_format='%Y', 
                        agg_type = "sum", agg_col="NUME90Q", 
                        unit="effluent violations")
        data_sets[ ds.name ] = ds
    ds_name = 'CWA Inspections'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="NPDES",
                        base_table='NPDES_INSPECTIONS',
                        table_name='CLEAN_WATER_INSPECTIONS_MVIEW', 
                        idx_field='NPDES_ID', date_field='ACTUAL_END_DATE', 
                        date_format='%m/%d/%Y', agg_type = "count", 
                        agg_col="STATE_EPA_FLAG", unit="inspections") 
                        # For possible later use in assessing state v federal 
        data_sets[ ds.name ] = ds
    ds_name = 'CWA Penalties'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="NPDES",
                        base_table='NPDES_FORMAL_ENFORCEMENT_ACTIONS',
                        table_name='CLEAN_WATER_ENFORCEMENT_ACTIONS_MVIEW', 
                        idx_field='NPDES_ID', date_field='SETTLEMENT_ENTERED_DATE', 
                        date_format='%m/%d/%Y', agg_type = "sum", 
                        agg_col="FED_PENALTY_ASSESSED_AMT", unit="dollars")
        data_sets[ ds.name ] = ds
    ds_name = 'SDWA Site Visits'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="SDWA",
                        base_table='SDWA_SITE_VISITS',
                        table_name='SDWA_SITE_VISITS_MVIEW', idx_field='PWSID',
                        date_field='SITE_VISIT_DATE', date_format='%m/%d/%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'SDWA Enforcements'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="SDWA",
                        base_table='SDWA_ENFORCEMENTS',
                        table_name='SDWA_ENFORCEMENTS_MVIEW', idx_field='PWSID',
                        date_field='ENFORCEMENT_DATE', date_format='%m/%d/%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'SDWA Public Water Systems'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="SDWA",
                        base_table='SDWA_PUB_WATER_SYSTEMS',
                        table_name='SDWA_PUB_WATER_SYSTEMS_MVIEW', idx_field='PWSID',
                        date_field='FISCAL_YEAR', date_format='%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'SDWA Violations'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="SDWA",
                        base_table='SDWA_VIOLATIONS',
                        table_name='SDWA_VIOLATIONS_MVIEW', idx_field='PWSID',
                        date_field='FISCAL_YEAR', date_format='%Y' )
        data_sets[ ds.name ] = ds
    ds_name = 'SDWA Serious Violators'
    if ( data_set_list is None or ds_name in data_set_list ):
        ds = DataSet( name=ds_name, echo_type="SDWA",
                        base_table='SDWA_SERIOUS_VIOLATORS',
                        table_name='SDWA_SERIOUS_VIOLATORS_MVIEW', idx_field='PWSID',
                        date_field='FISCAL_YEAR', date_format='%Y' )
        data_sets[ ds.name ] = ds
    # ds_name = 'RCRA Violations'
    # if ( data_set_list is None or ds_name in data_set_list ):
        # ds = DataSet( name='SDWA Return to Compliance', echo_type="SDWA",
        #                 table_name='SDWA_RETURN_TO_COMPLIANCE', idx_field='PWSID',
        #                 date_field='FISCAL_YEAR', date_format='%Y' )
        # data_sets[ ds.name ] = ds
    return data_sets

