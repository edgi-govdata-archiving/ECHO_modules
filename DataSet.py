# This class represents the data set and the fields and methods it requires 
# to retrieve data from the database.
class DataSet:
    def __init__( self, name, table_name, echo_type,
                 idx_field, date_field, date_format, sql = None ):
        self.name = name                    #Friendly name 
        self.table_name = table_name        #Database table name
        self.echo_type = echo_type          #AIR, NPDES, RCRA, SDWA
        self.idx_field = idx_field          #The table's index field
        self.date_field = date_field
        self.date_format = date_format
        self.sql = sql                      #The SQL query to retrieve the data 
        
    def get_data( self, ee_ids ):
        # The id_string can get very long for a state or even a county.
        # That can result in an error from too big URI.  Get the data in batches of 50 ids.

        id_string = ""
        program_data = None
        
        if ( len( ee_ids ) == 0 ):
            return None
              
        for pos,row in enumerate( ee_ids ):
            id_string = id_string + "'"+str(row)+"',"
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
    
    def get_echo_ids( self, echo_data ):
        echo_id = self.echo_type + '_IDS'
        if ( self.echo_type == 'SDWA' ):
            echo_flag = 'SDWIS_FLAG'
        else:
            echo_flag = self.echo_type + '_FLAG'
        my_echo_ids = echo_data[ echo_data[ echo_flag ] == 'Y' ][ echo_id ]
        return my_echo_ids
        
    def has_echo_flag( self, echo_data ):
        if ( self.echo_type == 'SDWA' ):
            echo_flag = 'SDWIS_FLAG'
        else:
            echo_flag = self.echo_type + '_FLAG'
        my_echo_data = echo_data[ echo_data[ echo_flag ] == 'Y' ]
        return len( my_echo_data ) > 0
        
