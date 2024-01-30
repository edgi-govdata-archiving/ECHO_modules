import pdb

import os
import urllib.parse
import pandas as pd
from datetime import datetime
from . import geographies
from .DataSetResults import DataSetResults
from .get_data import get_echo_data

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
        if ( type( value ) == list ):
            value = ''.join( map( str, value ))
        self.results[ (region_type, value, state) ] = result
        return result

    def show_charts( self ):
        for result in self.results.values():
            result.show_chart()
        
    def get_data( self, region_type, region_value, state=None, 
                  debug=False ):
        
        if ( not self.last_modified_is_set ):
            sql = 'select modified from "Last-Modified" where "name" = \'{}\''.format(
                self.base_table )
            ds = get_echo_data( sql )
            self.last_modified = datetime.strptime( ds.modified[0], '%Y-%m-%d' )
            self.last_modified_is_set = True
            print("Data last modified: " + str(self.last_modified)) # Print the last modified date for each file we get
            
        program_data = None

        filter = self._set_facility_filter( region_type, region_value, state )
        try:
            if ( self.sql is None ):
                x_sql = 'select * from "' + self.table_name + '" where ' \
                            + filter
            else:
                x_sql = self.sql + ' where ' + filter
            program_data = get_echo_data( x_sql, self.idx_field )
        except pd.errors.EmptyDataError:
            print( "No program records were found." )

        if ( program_data is not None ):
            print( "There were {} program records found".format( str( len( program_data ))))        
        return program_data

    def get_data_by_ee_ids( self, ee_ids, int_flag=False, debug=False ):
        # The id_string can get very long for a state or even a county.
        # That can result in an error from too big URI.
        # Get the data in batches of 50 ids.

        id_string = ""
        program_data = None
        
        if ( ee_ids is None ):
            return None
        else:
            ee_ids_len = len( ee_ids )

        pos = 0
        for pos,row in enumerate( ee_ids ):
            if ( not int_flag ):
                id_string += "'"
            id_string += str(row)
            if ( not int_flag ):
                id_string += "'"
            id_string +=  ","
            if ( pos % 50 == 0 ):
                id_string=id_string[:-1] # removes trailing comma
                data = self._try_get_data( id_string, debug )   
                if ( data is not None ):
                    if ( program_data is None ):
                        program_data = data
                    else:
                        program_data = pd.concat([ program_data, data ])
                id_string = ""

        if ( pos % 50 != 0 ):
            id_string=id_string[:-1] # removes trailing comma
            data = self._try_get_data( id_string, debug )
            if ( data is not None ):
                if ( program_data is None ):
                    program_data = data
                else:
                    program_data = pd.concat([ program_data, data ])
        
        print( "{} ids were searched for".format( str( ee_ids_len )))
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

        id_string = ''
        pgm_id_df = None
        
        if ( ee_ids is None ):
            return None
        else:
            ee_ids_len = len( ee_ids )

        pos = 0
        for pos,row in enumerate( ee_ids ):
            if ( not int_flag ):
                id_string += "'"
            id_string += str(row)
            if ( not int_flag ):
                id_string += "'"
            id_string +=  ","
            if ( pos % 50 == 0 ):
                id_string=id_string[:-1] # removes trailing comma
                this_data = None
                try:
                    x_sql = 'select "PGM_ID" from "EXP_PGM" where "REGISTRY_ID" in (' \
                                    + id_string + ')'
                    this_data = get_data( x_sql )
                except pd.errors.EmptyDataError:
                    print( "..." )
                if ( this_data is not None ):
                    if ( pgm_id_df is None ):
                        pgm_id_df = this_data
                    else:
                        pgm_id_df = pd.concat([ pgm_id_df, this_data ])
                id_string = ""

        if ( pos % 50 != 0 ):
            id_string=id_string[:-1] # removes trailing comma
            this_data = None
            try:
                x_sql = 'select "PGM_ID" from "EXP_PGM" where "REGISTRY_ID" in (' \
                                + id_string + ')'
                this_data = get_data( x_sql )
            except pd.errors.EmptyDataError:
                print( "..." )
            if ( this_data is not None ):
                if ( pgm_id_df is None ):
                    pgm_id_df = this_data
                else:
                    pgm_id_df = pd.concat([ pgm_id_df, this_data ])

        print( "{} ids were searched for".format( str( ee_ids_len )))
        if ( pgm_id_df is None ):
            print( "No program records were found." )
        else:
            print( "{} program ids were found".format( str( len( pgm_id_df ))))        
        return pgm_id_df['PGM_ID']
        

    def get_data_by_pgm_ids( self, pgm_ids, int_flag=False, debug=False ):
        # pgm_ids should be a list of the data set's idx_field values
        # The id_string can get very long for a state or even a county.
        # That can result in an error from too big URI.
        # Get the data in batches of 50 ids.

        id_string = ""
        program_data = None
        
        if ( pgm_ids is None ):
            return None
        else:
            pgm_ids_len = len( pgm_ids )

        pos = 0
        for pos,row in enumerate( pgm_ids ):
            if ( not int_flag ):
                id_string += "'"
            id_string += str(row)
            if ( not int_flag ):
                id_string += "'"
            id_string +=  ","
            if ( pos % 50 == 0 ):
                id_string=id_string[:-1] # removes trailing comma
                data = self._try_get_data( id_string, debug )   
                if ( data is not None ):
                    if ( program_data is None ):
                        program_data = data
                    else:
                        program_data = pd.concat([ program_data, data ])
                id_string = ""

        if ( pos % 50 != 0 ):
            id_string=id_string[:-1] # removes trailing comma
            data = self._try_get_data( id_string, debug )
            if ( data is not None ):
                if ( program_data is None ):
                    program_data = data
                else:
                    program_data = pd.concat([ program_data, data ])
        
        print( "{} ids were searched for".format( str( pgm_ids_len )))
        if ( program_data is None ):
            print( "No program records were found." )
        else:
            print( "{} program records were found".format( str( len( program_data ))))        
        return program_data
                
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
   
    def _try_get_data( self, id_list, debug=False ):
        this_data = None
        try:
            if ( self.sql is None ):
                x_sql = 'select * from "' + self.table_name + '" where "' \
                            + self.idx_field + '" in (' \
                            + id_list + ')'
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
        filter = '"' + geographies.region_field[region_type]['field'] + '"'
        if ( region_type == 'County' ):
            filter = '('
            for county in region_value:
                filter += '"' + geographies.region_field[region_type]['field'] + '"'
                filter += ' like \'' + county + '%\' or '
            filter = filter[:-3]
            filter += ')'
        elif ( region_type == 'State' ) :
            filter += ' = \'' + state + '\''
        else:
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
                filter += ' = \'' + region_value + '\'' 
        if ( region_type == 'Congressional District' or region_type == 'County' ):
            filter += ' and "FAC_STATE" = \'' + state + '\''
        return filter
