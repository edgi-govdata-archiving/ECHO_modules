import pandas as pd


# This class represents the results of a query of a DataSet and 
# configuration to allow the display of the results.
class DataSetResults:
    def __init__( self, dataset, region_type, region_value, state=None ):

        self.dataset = dataset
        self.region_type = region_type      # State, CD, Zip, Region
        self.region_value = region_value    # instance of Zip, CD, etc.
        self.state = state

        self.dataframe = None

    def store( self, df ): 
        if ( df is None ):
            return
        if ( self.dataset.name == 'CAA Violations' ):
            df['Date'] = df['EARLIEST_FRV_DETERM_DATE'].fillna(
                df['HPV_DAYZERO_DATE'] )   
        self.dataframe = df

    def show_chart( self ):
        program = self.dataset
        if ( self.dataframe is None ):
            print( "There is no data for {} to chart.".format( program.name ))
            return
        chart_title = program.name 
        chart_title += ' - ' + self.region_type 
        if ( self.state is not None ):
            chart_title += ' - ' + self.state
        if ( self.region_value is not None ):
            value = self.region_value
            if ( type( value ) == list ):
                value = ''.join( map( str, value ))
            chart_title += ' - ' + str( value )
    
        # SDWA programs - use a different date field
        SDWA_progs = ["SDWA Public Water Systems","SDWA Violations",
             "SDWA Serious Violators","SDWA Return to Compliance",
             "SDWA Enforcements"]
        # Handle NPDES_QNCR_HISTORY because there are multiple counts we need to sum
        data = self.dataframe
        if (program.name == "CWA Violations"): 
            year = data["YEARQTR"].astype("str").str[0:4:1]
            data["YEARQTR"] = year
            # Remove fields not relevant to this graph.
            data = data.drop(columns=['FAC_LAT', 'FAC_LONG', 'FAC_ZIP', 
                'FAC_EPA_REGION', 'FAC_DERIVED_WBD', 'FAC_DERIVED_CD113',
                'FAC_PERCENT_MINORITY', 'FAC_POP_DEN', 'FAC_DERIVED_HUC',
                'FAC_SIC_CODES', 'FAC_NAICS_CODES'])
            d = data.groupby(pd.to_datetime(data['YEARQTR'], 
                    format="%Y", errors='coerce').dt.to_period("Y")).sum()
            d.index = d.index.strftime('%Y')
            d = d[ d.index > '2000' ]
    
            ax = d.plot(kind='bar', title = chart_title, figsize=(20, 10), fontsize=16)
            ax
        # These data sets use a FISCAL_YEAR field
        elif (program.name in SDWA_progs):
            year = data["FISCAL_YEAR"].astype("str")
            data["FISCAL_YEAR"] = year
            d = data.groupby(pd.to_datetime(data['FISCAL_YEAR'], format="%Y",
                    errors='coerce').dt.to_period("Y"))[['PWS_NAME']].count()
            d.index = d.index.strftime('%Y')
            d = d[ d.index > '2000' ]
    
            ax = d.plot(kind='bar', title = chart_title, figsize=(20, 10), fontsize=16)
            ax        
        elif (program.name == "Combined Air Emissions" or program.name == "Greenhouse Gas Emissions" \
                  or program.name == "Toxic Releases"):
            d = data.groupby( 'REPORTING_YEAR' )[['ANNUAL_EMISSION']].sum()
            ax = d.plot(kind='bar', title = chart_title, figsize=(20, 10), fontsize=16)
            ax.set_xlabel( 'Reporting Year' )
            ax.set_ylabel( program.unit )
            ax        
        elif (program.name == "CAA Penalties" or program.name == "RCRA Penalties"  or program.name == "CWA Penalties" ):
            data.rename( columns={ program.date_field: 'Date',
                                   program.agg_col: 'Amount'}, inplace=True )
            if ( program.name == "CWA Penalties" ):
                data['Amount'] = data['Amount'].fillna(0) + \
                      data['STATE_LOCAL_PENALTY_AMT'].fillna(0)
            d = data.groupby( pd.to_datetime( data['Date'],
                    format="%m/%d/%Y", errors='coerce')).agg({'Amount':'sum'})
            d = d.resample('Y').sum()
            d.index = d.index.strftime('%Y')
            d = d[ d.index >= '2001' ]
            if ( len(d) > 0 ):
                ax = d.plot(kind='bar', title = chart_title, figsize=(20, 10), fontsize=16)
                ax.set_xlabel( 'Reporting Year' )
                ax.set_ylabel( 'Total penalties ($)' )
                ax        

        # All other programs
        else:
            try:
                d = data.groupby(pd.to_datetime(data[program.date_field], 
                        format=program.date_format, errors='coerce'))[[program.date_field]].count()
                d = d.resample("Y").sum()
                d.index = d.index.strftime('%Y')
                d = d[ d.index > '2000' ]
    
                if ( len(d) > 0 ):
                    ax = d.plot(kind='bar', title = chart_title, figsize=(20, 10), legend=False, fontsize=16)
                    ax.set_xlabel( 'Reporting Year' )
                    ax.set_ylabel( 'Count' )
                    ax
                else:
                    print( "There is no data for this program and region after 2000." )
    
            except AttributeError:
                print("There's no data to chart for " + program.name + " !")
    
