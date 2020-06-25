import urllib.parse
import pandas as pd

# This is the global function that can run an SQL query against
# the database and return the resulting Pandas DataFrame.
def get_data( sql, index_field=None ):
    url='http://apps.tlt.stonybrook.edu/echoepa/?query='
    data_location=url+urllib.parse.quote(sql)
    # print( sql )
    # print( data_location )
    if (index_field == "REGISTRY_ID"):
        ds = pd.read_csv(data_location,encoding='iso-8859-1', dtype={"REGISTRY_ID": "Int64"})
    else:
        ds = pd.read_csv(data_location,encoding='iso-8859-1')
    if ( index_field is not None ):
        try:
            ds.set_index( index_field, inplace=True)
        except KeyError:
            pass
    # print( "get_data() returning {} records.".format( len(ds) ))
    return ds


# This class represents the data set and the fields and methods it requires 
# to retrieve data from the database.
class DataSet:
    def __init__( self, name, table_name, echo_type=None,
                 idx_field=None, date_field=None, date_format=None, sql=None ):
        # the echo_type can be a single string--AIR, NPDES, RCRA, SDWA,
        # or a list of multiple strings--['GHG','TRI']

        self.name = name                    #Friendly name 
        self.table_name = table_name        #Database table name
        self.echo_type = echo_type          #AIR, NPDES, RCRA, SDWA or list
        self.idx_field = idx_field          #The table's index field
        self.date_field = date_field
        self.date_format = date_format
        self.sql = sql                      #The SQL query to retrieve the data 
        
    def get_data( self, ee_ids, int_flag=False ):
        # The id_string can get very long for a state or even a county.
        # That can result in an error from too big URI.
        # Get the data in batches of 50 ids.

        id_string = ""
        program_data = None
        
        if ( len( ee_ids ) == 0 ):
            return None
         
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
                if ( program_data is None ):
                    program_data = data
                else:
                    program_data = pd.concat([ program_data, data ])
                id_string = ""

        if ( pos % 50 != 0 ):
            id_string=id_string[:-1] # removes trailing comma
            data = self._try_get_data( id_string )
            if ( program_data is None ):
                program_data = data
            else:
                program_data = pd.concat([ program_data, data ])
                
        return program_data
                
    def get_echo_ids( self, echo_data ):
        if ( self.echo_type is None ):
            return None
        if ( isinstance( self.echo_type, str )):
            return self._get_echo_ids( self.echo_type, echo_data )
        if ( isinstance( self.echo_type, list )):
            my_echo_ids = []
            [ my_echo_ids.append( _get_echo_ids( t ), echo_data ) \
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
            # breakpoint()
            if ( self.sql is None ):
                x_sql = "select * from `" + self.table_name + "` where " \
                            + self.idx_field + " in (" \
                            + id_list + ")"
            else:
                x_sql = self.sql + "(" + id_list + ")"
            this_data = get_data( x_sql, self.idx_field )
            # print( "Data found from " + self.table_name )
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
