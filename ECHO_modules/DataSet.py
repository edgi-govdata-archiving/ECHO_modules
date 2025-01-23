import pdb

import os
import urllib.parse
import pandas as pd
from datetime import datetime
from itertools import islice
from . import geographies
from .DataSetResults import DataSetResults
from .get_data import get_echo_data
from .utilities import get_facs_in_counties

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
    '''

    def __init__( self, name, base_table, table_name, echo_type=None,
                 idx_field=None, date_field=None, date_format=None,
                 sql=None, agg_type=None, agg_col=None, unit=None):
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

    def store_results( self, region_type, region_value, state=None ):
        result = DataSetResults( self, region_type, region_value, state )
        df = self.get_data( region_type, region_value, state )
        result.store( df )
        value = region_value
        if type(value) == list:
            value = ''.join( map( str, value ))
        self.results[ (region_type, value, state) ] = result
        return result

    def store_results_by_ids( self, ids, region_type, use_registry_id=True ):
        result = DataSetResults( self, region_type=region_type )
        df = self.get_data_by_ids( ids, use_registry_id=use_registry_id )
        result.store( df )
        value = use_registry_id
        self.results[ (region_type, value) ] = result
        return result

    def show_charts( self ):
        for result in self.results.values():
            result.show_chart()
        
    def get_data( self, region_type, region_value, state=None ):
        
        if ( not self.last_modified_is_set ):
            sql = 'select modified from "Last-Modified" where "name" = \'{}\''.format(
                self.base_table )
            ds = get_echo_data( sql )
            self.last_modified = datetime.strptime( ds.modified[0], '%Y-%m-%d' )
            self.last_modified_is_set = True
            print("Data last modified: " + str(self.last_modified)) # Print the last modified date for each file we get
            
        program_data = None

        if (region_type == 'Neighborhood'):
            return self._get_nbhd_data(region_value)

        filter = self._set_facility_filter( region_type, region_value, state )
        try:
            if ( self.sql is None ):
                x_sql = 'select * from "' + self.table_name + '" where ' \
                            + filter
            else:
                x_sql = self.sql + ' where ' + filter
            program_data = get_echo_data( x_sql, self.idx_field )
        except pd.errors.EmptyDataError:
            print( "No program records were found.")

        if (region_type == 'County'):
            if (type(region_value) == str):
                region_value = [region_value,]
            program_data = get_facs_in_counties(program_data, region_value)

        if ( program_data is not None ):
            print( "There were {} program records found".format( str( len( program_data ))))        
        return program_data

    def get_data_by_ids( self, ids, use_registry_id=False, int_flag=False ):
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
                x_sql = 'select "PGM_ID" from "EXP_PGM" where "REGISTRY_ID" in (' \
                                    + id_string + ')'
                this_data = get_echo_data( x_sql )
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
   
    def _get_nbhd_data(self, points):
        poly_str = ''
        for point in points:
            poly_str += f'{point[0]} {point[1]} ,'
        poly_str += f'{points[0][0]} {points[0][1]}'

        if ( self.echo_type == 'SDWA' ):
            echo_flag = 'SDWIS_FLAG'
        else:
            echo_flag = self.echo_type + '_FLAG'

        sql = """
            SELECT "REGISTRY_ID"
            FROM "ECHO_EXPORTER"
            WHERE "{}" = 'Y' AND ST_WITHIN("wkb_geometry", ST_GeomFromText('POLYGON(({}))', 4269) );
            """.format(echo_flag, poly_str)

        registry_ids = get_echo_data(sql)
        echo_ids = registry_ids["REGISTRY_ID"].to_list()
        return self.get_data_by_ids(ids=echo_ids, use_registry_id=True)

    def _try_get_data( self, id_list, use_registry_id=False):
        # The use_registry_id flag determines whether we use the table or view's
        # defined index field or the REGISTRY_ID which is part of each MVIEW.
        this_data = None
        try:
            if ( self.sql is None ):
                idx = self.idx_field
                if use_registry_id:
                    idx = "REGISTRY_ID"
                x_sql = f'select * from "{self.table_name}"  where "{idx}" in ({id_list})'
            else:
                x_sql = self.sql + "(" + id_list + ")"
            this_data = get_echo_data( x_sql, self.idx_field )
        except pd.errors.EmptyDataError:
            print( "..." )
        return this_data
    
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
        if ( region_type == 'State' ):
            region_value = state
        if ( region_type == 'County' or region_type == 'State' ):
            filter = '"' + geographies.region_field['State']['field'] + '"'
            filter += ' = \'' + state + '\''
        else:
            filter = '"' + geographies.region_field[region_type]['field'] + '"'
            # region_value will be an list of values
            id_string = ""
            value_type = type(region_value)
            if ( value_type == list or value_type == tuple ):
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
                filter += ' and "' + geographies.region_field['State']['field']
                filter += '" = \'' + state + '\''
        return filter
