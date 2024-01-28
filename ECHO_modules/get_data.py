import pdb
import geopandas
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
    url= 'https://portal.gss.stonybrook.edu/echoepa/?query=' #'http://apps.tlt.stonybrook.edu/echoepa/?query=' 
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
            lm_ds = pd.read_csv(lm_data_location,encoding='iso-8859-1')
            last_modified = lm_ds.modified[0]
            print("Data last updated: " + last_modified) # Print the last modified date for each file we get 
        except:
            print("Data last updated: Unknown")
    
    return ds

def spatial_selector(units):
    '''
    helper function for `get_spatial_data`
    helps parse out multiple inputs into a SQL format
    e.g. takes a list ["AL", "AK", "AR"] and returns the string ("AL", "AK", "AR")
    '''
    selection = '('
    if (type(units) == list):
      for place in units:
          selection += '\''+str(place)+'\', '
      selection = selection[:-2] # remove trailing comma
      selection += ')'
    else:
      selection = '(\''+str(units)+'\')'
    return selection

def get_spatial_data(region_type, states, spatial_tables, fips=None, region_filter=None):
    '''
    returns spatial data from the database utilizing an intersection query 
    e.g. return watersheds based on whether they cross the selected state

    region_type = "Congressional District" # from cell 3 region_type_widget
    states = ["AL"]  # from cell 2 state dropdown selection. 
    states variable has ability to be expanded to multiple state selection.
    spatial_tables is from ECHO_modules/geographies.py
    fips is also from geographies.py but is not required - only for Census Tracts
    region_filter can specify whether to return a single unit (e.g. a specific county)
    region_filter should be based on the id_field specified in spatial_tables
    '''

    def retrieve(query):
      '''
      Actually gets the data...
      '''
      #print(query) # Debugging
      result = get_echo_data(query)
      result['geometry'] = geopandas.GeoSeries.from_wkb(result['wkb_geometry'])
      result.drop("wkb_geometry", axis=1, inplace=True)
      result = geopandas.GeoDataFrame(result, crs=4269)   
      return result
    
    selection = spatial_selector(states)

    # Get the regions of interest (watersheds, zips, etc.) based on their intersection with the state(s)
    if (region_type == "Census Tract"):
      # Get all census tracts for this state
      # Which state is it? FIPS look up
      f = fips[states[0]] #assuming just one state for the time being
      #print(f) # Debugging
      # Get tracts
      import requests, zipfile, io
      url = "https://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_"+f+"_tract10.zip"
      r = requests.get(url)
      z = zipfile.ZipFile(io.BytesIO(r.content))
      z.extractall("/content")
      regions = geopandas.read_file("/content/tl_2010_"+f+"_tract10.shp")
      regions.columns = regions.columns.str.lower() #convert columns to lowercase for consistency

    else: 
      #print(selection) # Debugging
      query = """
        SELECT this.* 
        FROM """ + spatial_tables[region_type]['table_name'] + """ AS this
        JOIN """ + spatial_tables["State"]['table_name'] + """ AS other 
        ON other.""" + spatial_tables["State"]['id_field'] + """ IN """ + selection + """ 
        AND ST_Within(this.wkb_geometry,other.wkb_geometry) """
      if region_filter:
        region_filter = spatial_selector(region_filter)
        query += """AND this.""" + spatial_tables[region_type]['match_field'] + """ in """ + region_filter + """ """
      #print(query) # debugging
      regions = retrieve(query)

    # Get the intersecting geo (i.e. states)
    query = """
      SELECT * 
      FROM """ + spatial_tables["State"]['table_name'] + """
      WHERE """ + spatial_tables["State"]['id_field'] + """ IN """ + selection + ""
    states = retrieve(query) #reset intersecting_geo to its spatial data

    return regions, states

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
