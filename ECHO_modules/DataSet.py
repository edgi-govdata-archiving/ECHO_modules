import pdb

import os
import urllib.parse
import pandas as pd
from datetime import datetime, date
from itertools import islice
from . import geographies
from .DataSetResults import DataSetResults
from .get_data import get_echo_data
from .utilities import get_facs_in_counties, filter_by_geometry
import json
import requests

SCHEMA_DIR = os.environ.get('SCHEMA_HOST_PATH')
API_SERVER = "https://portal.gss.stonybrook.edu/api"

class DataSet:
    '''
    This class represents the data set and the fields and methods it requires 
    to retrieve data from the database.
    The database contains views (table_name) that are based on a data table
    (base_table).  

    Attributes
    ----------
    name : str
        The name of the data set, e.g. 'CAA Violations'
    base_table : str
        The database table that is the basis for the data set
    echo_type : {'AIR','NPDES','RCRA','SDWA','GHG','TRI'}
        Or it can be a list of types, e.g.  ['GHG',TRI']
        The EPA program type
    idx_field : str
        The index field
    date_field : str
        The name of the field in the table that gives the data's date
    date_format : str
        The format to expect the data in the date_field
    agg_type : {'sum','count'}
        How to aggregate the data
    unit : str
        The unit of measure for the data field
    sql : str
        The SQL query to use to retrieve the data
    last_sql : str
        The last query made of the database
    api : boolean
        True if using the DeltaLake api, False if using a local DB
    token : string
        The authentication token for the api
    '''

    def __init__( self, name, base_table, table_name, echo_type=None,
                 idx_field=None, date_field=None, date_format=None,
                 sql=None, agg_type=None, agg_col=None, unit=None,
                 api=True, token=None):
        # the echo_type can be a single string--AIR, NPDES, RCRA, SDWA,
        # or a list of multiple strings--['GHG','TRI']

        self.name = name                    #Friendly name 
        self.base_table = base_table        #Actual database table
        self.table_name = table_name        #Database table (now material view) name
        self.echo_type = echo_type          #AIR, NPDES, RCRA, SDWA or list
        self.idx_field = idx_field          #The table's index field
        self.date_field = date_field
        self.date_format = date_format
        self.agg_type = agg_type            #The type of aggregation to be performed - summing emissions or counting violations, e.g.
        self.agg_col = agg_col              #The field to aggregate by
        self.unit = unit                    #Unit of measure
        self.sql = sql                      #The SQL query to retrieve the data 
        self.results = {}                   #Dictionary of DataSetResults objects
        self.last_modified_is_set = False
        self.last_modified = datetime.strptime( '01/01/1970', '%m/%d/%Y')
        self.last_sql = ''
        self.api = api 
        self.token = token

    def store_results( self, region_type, region_value, state=None, years=None):
        result = DataSetResults( self, region_type, region_value, state )
        df = self.get_data_delta( region_type, region_value, state, years )
        print("got the data")
        result.store( df )
        value = region_value
        if type(value) == list:
            value = ''.join( map( str, value ))
        self.results[ (region_type, value, state) ] = result
        return result

    def store_results_by_ids( self, ids, region_type, use_registry_id=True, years=None ):
        result = DataSetResults( self, region_type=region_type )
        df = self.get_data_by_ids( ids, use_registry_id=use_registry_id, years=years )
        result.store( df )
        value = use_registry_id
        self.results[ (region_type, value) ] = result
        return result

    def show_charts( self ):
        for result in self.results.values():
            result.show_chart()
    
    def get_data_delta( self, region_type, region_value, state=None, years=None ):
        print(self.base_table)
        if self.api:
            if self.token == None:
                try:
                    with open('token.txt', 'r') as f:
                        token = f.read().strip()
                except:
                    # If token file does not exist, prompt user to get token
                    print("Token file not found. Please run get_echo_api_access_token() or the get token cell to obtain a token.")
                    return None
            else:
                token = self.token
                
            headers = {
            "Authorization": f"Bearer {token}",
            }
            
            response = requests.get(f"{API_SERVER}/echo/schema/{self.base_table}", headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch schema: {response.status_code} - {response.text}")
            
            data = response.json()  
        else:
            with open(os.path.join(SCHEMA_DIR, f"{self.base_table}_schema.json")) as f: # MOVE THIS TO AN API SCHEMA, AS ENDPOINT
                data = json.load(f)
                
        if ( not self.last_modified_is_set ):
            last_modified = data['last_modified']  # Now this will work
            self.last_modified = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S ")
            self.last_modified_is_set = True
            print("Data last modified: " + str(self.last_modified)) # Print the last modified date for each file we get
            
        # program_data = None

        if (region_type == 'Neighborhood'):
            return self._get_nbhd_data(region_value, years) # TODO: can't continue, has geometry data
        filter = self._set_facility_filter( region_type, region_value, state )
        try:
            if ( self.sql is None ):
                x_sql = 'select * from ' + self.table_name + ' where ' \
                            + filter
            else:
                x_sql = self.sql + ' where ' + filter
            self.last_sql = x_sql
            print(self.last_sql)
            program_data = get_echo_data( x_sql, self.idx_field, self.table_name, api=self.api, token=self.token) 
            print(self.idx_field)
            program_data = self._apply_date_filter(program_data, years)
        except pd.errors.EmptyDataError:
            print( "No program records were found.")

        if (region_type == 'County'):
            if (type(region_value) == str):
                region_value = [region_value,]
            program_data = get_facs_in_counties(program_data, region_value)

        if ( program_data is not None ):
            print( "There were {} program records found".format( str( len( program_data ))))        
        return program_data

    def get_data_by_ids( self, ids, use_registry_id=False, int_flag=False, years=None ):
        # The id_string can get very long for a state or even a county.
        # That can result in an error from too big URI.
        # Get the data in batches of 50 ids.
        
        program_data = None
        
        if ( ids is None ):
            return None
        else:
            ids_len = len( ids )

        iterator = iter(ids)
        while chunk := list(islice(iterator, 50)):
            id_string = ""

            for id in chunk:
                if ( not int_flag ):
                    id_string += "'"
                id_string += str(id)
                if ( not int_flag ):
                    id_string += "'"
                id_string +=  ","
            id_string=id_string[:-1] # removes trailing comma
            data = self._try_get_data( id_string, use_registry_id )
            if ( data is not None ):
                if ( program_data is None ):
                    program_data = data
                else:
                    program_data = pd.concat([ program_data, data ])
        program_data = self._apply_date_filter(program_data, years)
        print( "{} ids were searched".format( str( ids_len )))
        if ( program_data is None ):
            print( "No program records were found." )
        else:
            print( "{} program records were found".format( str( len( program_data ))))        
        return program_data

    
    def get_pgm_ids( self, ee_ids, int_flag=False ):
        # ee_ids should be a list of ECHO_EXPORTER REGISTRY_IDs
        # Use the EXP_PGM table to turn the list into program ids.
        # If the DataSet's index field is REGISTRY_ID there is nothing to
        # do so we just return back what we were given.

        if ( self.idx_field == 'REGISTRY_ID' ):
            return ee_ids

        pgm_id_df = None
        
        if ( ee_ids is None ):
            return None
        else:
            ee_ids_len = len( ee_ids )

        iterator = iter(ee_ids)
        while chunk := list(islice(iterator, 50)):
            id_string = ""
            for id in chunk:
                if ( not int_flag ):
                    id_string += "'"
                id_string += str(id)
                if ( not int_flag ):
                    id_string += "'"
                id_string +=  ","
            id_string=id_string[:-1] # removes trailing comma
            this_data = None
            try:
                x_sql = 'select PGM_ID from EXP_PGM where REGISTRY_ID in (' \
                                    + id_string + ')'
                self.last_sql = x_sql
                this_data = get_echo_data( x_sql, api=self.api, token=self.token )
            except pd.errors.EmptyDataError:
                print( "..." )
            if ( this_data is not None ):
                if ( pgm_id_df is None ):
                    pgm_id_df = this_data
                else:
                    pgm_id_df = pd.concat([ pgm_id_df, this_data ])

        print( "{} ids were searched".format( str( ee_ids_len )))
        if ( pgm_id_df is None ):
            print( "No program records were found." )
        else:
            print( "{} program ids were found".format( str( len( pgm_id_df ))))        
        return pgm_id_df['PGM_ID']
      

    def get_echo_ids( self, echo_data ):
        if ( self.echo_type is None ):
            return None
        if ( isinstance( self.echo_type, str )):
            return self._get_echo_ids( self.echo_type, echo_data )
        if ( isinstance( self.echo_type, list )):
            my_echo_ids = []
            [ my_echo_ids.append( self._get_echo_ids( t, echo_data )) \
                 for t in self.echo_type ]
            return my_echo_ids
        return None
        
    def has_echo_flag( self, echo_data ):
        if ( self.echo_type is None ):
            return False
        if ( isinstance( self.echo_type, str )):
            return self._has_echo_flag( self.echo_type, echo_data )
        if ( isinstance( self.echo_type, list )):
            for t in self.echo_type:
                if ( self._has_echo_flag( t, echo_data ) > 0 ):
                    return True
            return False
        return False
     
    # Private methods of the class
    # Spatial data function
    def _get_nbhd_data(self, points, years=None):
        #poly_str = ''
        #for point in points:
        #    poly_str += f'{point[0]} {point[1]} ,'
        #poly_str += f'{points[0][0]} {points[0][1]}'

        if self.echo_type == 'SDWA':
            echo_flag = 'SDWIS_FLAG'
        elif type(self.echo_type) != list:
            echo_flag = self.echo_type + '_FLAG'
            
        echo_ids = []
        if type(self.echo_type) == list:
            for flag in self.echo_type:
                
                # Get only id and coords from table
                sql = f"""
                    SELECT REGISTRY_ID, FAC_LAT, FAC_LONG
                    FROM ECHO_EXPORTER 
                    WHERE {flag}_FLAG = 'Y'
                """
                self.last_sql = sql
                df = get_echo_data( sql, 'REGISTRY_ID', api=self.api, token=self.token)
                registry_ids = filter_by_geometry(points, df)
                
                
                # sql = """
                # SELECT "REGISTRY_ID"
                # FROM "ECHO_EXPORTER"
                # WHERE "{}_FLAG" = 'Y' AND ST_WITHIN("wkb_geometry", ST_GeomFromText('POLYGON(({}))', 4269) );
                # """.format(flag, poly_str)
                # self.last_sql = sql
                # registry_ids = get_echo_data(sql)
                if registry_ids.index.name == 'REGISTRY_ID':
                    echo_ids.extend(registry_ids.index.to_list())
                else:
                    echo_ids.extend(registry_ids["REGISTRY_ID"].to_list())
        else:
            # sql = """
            # SELECT "REGISTRY_ID"
            # FROM "ECHO_EXPORTER"
            # WHERE "{}" = 'Y' AND ST_WITHIN("wkb_geometry", ST_GeomFromText('POLYGON(({}))', 4269) );
            # """.format(echo_flag, poly_str)
            # Get only id and coords from table
            sql = f"""
                SELECT REGISTRY_ID, FAC_LAT, FAC_LONG
                FROM ECHO_EXPORTER 
                WHERE {echo_flag} = 'Y'
            """
            self.last_sql = sql
            df = get_echo_data( sql, 'REGISTRY_ID', api=self.api, token=self.token)
            registry_ids = filter_by_geometry(points, df)
            if registry_ids.index.name == 'REGISTRY_ID': # We set registry_id as index so, we can extract it right here
                echo_ids = registry_ids.index.to_list()
            else:
                echo_ids = registry_ids["REGISTRY_ID"].to_list()

        # self.last_sql = sql
        # registry_ids = get_echo_data(sql)
        # echo_ids = registry_ids["REGISTRY_ID"].to_list()
        return self.get_data_by_ids(ids=echo_ids, use_registry_id=True, years=years)
    

    def _try_get_data( self, id_list, use_registry_id=False ):
        # The use_registry_id flag determines whether we use the table or view's
        # defined index field or the REGISTRY_ID which is part of each MVIEW.
        this_data = None
        try:
            if ( self.sql is None ):
                idx = self.idx_field
                if use_registry_id:
                    idx = "REGISTRY_ID"
                x_sql = f'select * from {self.table_name} where {idx} in ({id_list})'
            else:
                x_sql = self.sql + "(" + id_list + ")"
            self.last_sql = x_sql
            print(self.last_sql)
            this_data = get_echo_data( x_sql, index_field=self.idx_field, table_name=self.table_name, 
                                      api=self.api, token=self.token )
        except pd.errors.EmptyDataError:
            print( "..." )
        return this_data
    

    def _apply_date_filter(self, program_data, years=None):
            if program_data is None:
                return None
            df = program_data.copy()
            if self.echo_type in ['TRI', 'GHG', 'SDWA'] or 'TRI' in self.echo_type or 'GHG' in self.echo_type:
                if self.name == 'SDWA Site Visits' or self.name == 'SDWA Enforcements':
                    df[self.date_field] = pd.to_datetime(df[self.date_field], errors='coerce')
                    df['year'] = df[self.date_field].dt.year
                else:
                    df['year'] = df[self.date_field].astype(int)
            elif self.name == 'CWA Violations':
                df[self.date_field] = df[self.date_field].astype(int)
                df['year'] = df[self.date_field]/10
                df['year'] = df['year'].astype(int)
            else:
                df[self.date_field] = pd.to_datetime(df[self.date_field], errors='coerce')
                df['year'] = df[self.date_field].dt.year
            start_year = 2001
            today = date.today()
            end_year = today.year
            if years is not None:
                start_year = years[0]
                end_year = years[1]
            df = df[df['year'] >= start_year]
            df = df[df['year'] <= end_year]
            df.drop('year', axis=1, inplace=True)
            return df

    def _get_echo_ids( self, echo_type, echo_data ):
        # Return the ids for a single echo type.
        echo_id = echo_type + '_IDS'
        if ( self.echo_type == 'SDWA' ):
            echo_flag = 'SDWIS_FLAG'
        else:
            echo_flag = self.echo_type + '_FLAG'
        my_echo_ids = echo_data[ echo_data[ echo_flag ] == 'Y' ][ echo_id ]
        return my_echo_ids

    def _has_echo_flag( self, echo_type, echo_data ):
        # Return True if the single echo type flag is set
        if ( echo_type == 'SDWA' ):
            echo_flag = 'SDWIS_FLAG'
        else:
            echo_flag = echo_type + '_FLAG'
        my_echo_data = echo_data[ echo_data[ echo_flag ] == 'Y' ]
        return len( my_echo_data ) > 0

    def _set_facility_filter( self, region_type, region_value=None, state=None ):
        print(region_type)
        print(region_value)
        print(state)
        if ( region_type == 'State' ):
            region_value = state
        if ( region_type == 'County' or region_type == 'State' ):
            filter = '' + geographies.region_field['State']['field'] + ''
            filter += ' = \'' + state + '\''
        else:
            filter = '' + geographies.region_field[region_type]['field'] + ''
            # region_value will be an list of values
            id_string = ""
            value_type = type(region_value)
            if ( value_type == list or value_type == tuple ): # <- Question for tmr: Would this ever be a list because you are taking state, CD by pairs? Region value is currently an int.
                for region in region_value:
                    if ( region_type == 'Congressional District' ):
                        id_string += str( region ) + ','
                    else:
                        id_string += '\'' + str( region ) + '\','
                # Remove trailing comma from id_string
                filter += ' in (' + id_string[:-1] + ')'
            elif ( type(region_value) == str ):
                region_value = ''.join(region_value.split())
                region_value = ",".join(map(lambda x: "\'" + str(x) + "\'", region_value.split(',')))
                filter += ' in (' + region_value + ')'
            if ( region_type == 'Congressional District' ):
                filter += ' and ' + geographies.region_field['State']['field']
                filter += ' = \'' + state + '\''
        return filter
