import pdb

import os
import urllib.parse
import pandas as pd

def get_echo_data( sql, index_field=None, table_name=None ):
    '''
    This is the global function that can run an SQL query against
    the database and return the resulting Pandas DataFrame.

    Parameters
    ----------
    sql : str
        The SQL query to run
    index_field : str
        The field in the result set to set as the Dataframe's index

    Results
    -------
    Dataframe
        The results of the database query
    '''    
    url= 'http://portal.gss.stonybrook.edu/echoepa/?query=' #'http://apps.tlt.stonybrook.edu/echoepa/?query=' 
    data_location=url+urllib.parse.quote_plus(sql) + '&pg'
    # print( sql )
    # print( data_location )
    # pdb.set_trace()
    if ( index_field == "REGISTRY_ID" ):
        ds = pd.read_csv(data_location,encoding='iso-8859-1', 
                 dtype={"REGISTRY_ID": "Int64"})
    else:
        ds = pd.read_csv(data_location,encoding='iso-8859-1')
    if ( index_field is not None ):
        try:
            ds.set_index( index_field, inplace=True)
        except (KeyError, pd.errors.EmptyDataError):
            pass
    # print( "get_data() returning {} records.".format( len(ds) ))
    if (table_name is not None):
        try:
            lm_sql = 'select modified from "Last-Modified" where "name" = \'{}\''.format(table_name)
            lm_data_location=url+urllib.parse.quote_plus(lm_sql) + '&pg'
            ds = pd.read_csv(lm_data_location,encoding='iso-8859-1')
            last_modified = ds.modified[0]
            print("Data last updated: " + last_modified) # Print the last modified date for each file we get 
      except:
          print("Data last updated: Unknown")
    
    return ds

def selector(units):
    #build query
    selection = '('
    if (type(units) == list):
        for place in self.units:
            selection += '\''+str(place)+'\', '
            selection = selection[:-2] # remove trailing comma
            selection += ')'
    else:
        selection = '(\''+str(units)+'\')'
    return selection

def get_spatial_data(intersection, other, units):
    '''
    # return query(unit, unit_type)
    #places = more specifically, the zip code(s). Can provide a list of them. 
    #at least one place is required (can't query the whole db!)

    #return spatial data set based on the intersection between one SDS and another 
    #e.g. return watersheds based on what states they cross
    #When intersection is set to true places should equal a location(s) from another
    #spatial data set (other)
    '''

    selection = selector()
    
    if intersection:
      query = """
        SELECT this.* 
        FROM """ + table_name + """ AS this 
        JOIN """ + other.table_name + """ AS o 
        ON o.""" + other.id_field + """ IN """ + selection + """ 
        AND ST_Intersects(this.geom,o.geom) """
    else:
      query = """
      SELECT * 
      FROM """ + table_name + """
      WHERE """ + id_field + """ IN """ + selection + ""

    #develop sql
    sql = """
      SELECT jsonb_build_object(
          'type', 'FeatureCollection', 'features', jsonb_agg(features.feature)
      )
      FROM (
          SELECT jsonb_build_object(
              'type', 'Feature','id', gid, 'geometry',
              ST_AsGeoJSON(geom)::jsonb,'properties',
              to_jsonb(inputs) - 'gid' - 'geom'
          ) feature
          FROM ( 
            """+query+"""
          ) inputs
      ) features;
    """

    url= 'http://portal.gss.stonybrook.edu/echoepa/index2.php?query=' 
    data_location=url+urllib.parse.quote_plus(sql) + '&pg'
    print(sql) # Debugging
    print(data_location) # Debugging

    result = geopandas.read_file(data_location)
    return result

# Read stored data from a file rather than go to the database.
def read_file( base, type, state, region ):
    '''
    Read stored data from a  file in the CSVs directory, rather
    than the database.  (TBD: This should check the last_modified,
    perhaps against a timestamp on the file name, to verify that
    the file holds the latest data.)

    Parameters
    ----------
    base : str
        The base filename
    type : {'State','County','Congressional District','Zipcode'}
        The region type
    state : str
        The state two-letter abbreviation
    region : str or int
        The region

    Returns
    -------
    Dataframe or None
        The resulting data, if found
    '''

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
