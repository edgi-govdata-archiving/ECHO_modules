import os
import urllib.parse
import pandas as pd
from geographies import region_field, states
from DataSetResults import DataSetResults

# This is the global function that can run an SQL query against
# the database and return the resulting Pandas DataFrame.
def get_data( sql, index_field=None ):
    url='http://apps.tlt.stonybrook.edu/echoepa/?query='
    data_location=url+urllib.parse.quote_plus(sql) + '&pg'
    # print( sql )
    # print( data_location )
    if ( index_field == "REGISTRY_ID" ):
        ds = pd.read_csv(data_location,encoding='iso-8859-1', 
                 dtype={"REGISTRY_ID": "Int64"})
    else:
        ds = pd.read_csv(data_location,encoding='iso-8859-1')
    if ( index_field is not None ):
        try:
            ds.set_index( index_field, inplace=True)
        except KeyError:
            pass
    # print( "get_data() returning {} records.".format( len(ds) ))
    return ds

# Development only - unless...?
# Read stored data from a file rather than go to the database.
def read_file( base, type, state, region ):
    if ( not os.path.exists( 'CSVs' )):
        return None
    filename = 'CSVs/' + base
    if ( type != 'Zip Code' ):
        filename += '-' + state
    filename += '-' + type
    if ( region is not None ):
        filename += '-' + str(region)
    filename += '.csv'
    program_data = None
    try:
        f = open( filename )
        f.close()
        program_data = pd.read_csv( filename ) 
    except FileNotFoundError:
        pass
    return program_data

# This class represents the data set and the fields and methods it requires 
# to retrieve data from the database.
class DataSet:
    
    def __init__( self, name, table_name, echo_type=None,
                 idx_field=None, date_field=None, date_format=None,
                 sql=None, agg_type=None, agg_col=None, unit=None):
        # the echo_type can be a single string--AIR, NPDES, RCRA, SDWA,
        # or a list of multiple strings--['GHG','TRI']

        self.name = name                    #Friendly name 
        self.table_name = table_name        #Database table name
        self.echo_type = echo_type          #AIR, NPDES, RCRA, SDWA or list
        self.idx_field = idx_field          #The table's index field
        self.date_field = date_field
        self.date_format = date_format
        self.agg_type = agg_type            #The type of aggregation to be performed - summing emissions or counting violations, e.g.
        self.agg_col = agg_col              #The field to aggregate by
        self.unit = unit                    #Unit of measure
        self.sql = sql                      #The SQL query to retrieve the data 
        self.results = {}                   #Dictionary of DataSetResults objects

    def store_results( self, region_type, region_value, state=None ):
        result = DataSetResults( self, region_type, region_value, state )
        df = self.get_data( region_type, region_value, state )
        result.store( df )
        self.results[ (region_type, region_value, state) ] = result

    def show_charts( self ):
        for result in self.results.values():
            result.show_chart()
        
    def get_data( self, region_type, region_value, state=None ):
        program_data = None

        # Development only
        # # See if there is a local .csv with the data to use 
        program_data = read_file( self.name, region_type, state, region_value )
        if ( program_data is not None ):
            return program_data
        
        filter = self._set_facility_filter( region_type, region_value, state )
        try:
            if ( self.sql is None ):
                x_sql = 'select * from "' + self.table_name + '" where ' \
                            + filter
            else:
                x_sql = self.sql + ' where ' + filter
            program_data = get_data( x_sql, self.idx_field )
        except pd.errors.EmptyDataError:
            print( "No program records were found." )

        if ( program_data is not None ):
            print( "{} program records were found".format( str( len( program_data ))))        
        return program_data

    def get_data_by_ee_ids( self, ee_ids, int_flag=False ):
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
                data = self._try_get_data( id_string )   
                if ( data is not None ):
                    if ( program_data is None ):
                        program_data = data
                    else:
                        program_data = pd.concat([ program_data, data ])
                id_string = ""

        if ( pos % 50 != 0 ):
            id_string=id_string[:-1] # removes trailing comma
            data = self._try_get_data( id_string )
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
   
    def _try_get_data( self, id_list ):
        this_data = None
        try:
            if ( self.sql is None ):
                x_sql = 'select * from "' + self.table_name + '" where "' \
                            + self.idx_field + '" in (' \
                            + id_list + ')'
            else:
                x_sql = self.sql + "(" + id_list + ")"
            this_data = get_data( x_sql, self.idx_field )
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
        filter = '"' + region_field[region_type]['field'] + '"'
        if ( region_type == 'County' ):
            filter += ' like \'' + str( region_value ) + '%\''
        else:
            filter += ' = \'' + str( region_value ) + '\''
        if ( region_type == 'Congressional District' or region_type == 'County' ):
            filter += ' and "FAC_STATE" = \'' + state + '\''
        return filter
