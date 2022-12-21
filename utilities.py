'''
Provide a number of utility Python functions that can de-clutter
the Jupyter notebooks that use them.
'''

# Import libraries
import os 
import csv
import datetime
import pandas as pd
import numpy as np
import urllib
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
from IPython.core.display import display, HTML

def get_data( sql, index_field=None ):
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
    data_location = url + urllib.parse.quote_plus(sql) + '&pg'
    # print( sql ) # Debugging
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

def place_picker():
  '''
  Allow users to pick a point on an ipyleaflet map and store those coordinates in `marker`

  Parameters
  ----------
  None

  Returns
  ----------
  Displays an ipyleaflet map with a moveable marker
  Returns the marker, whose current coordinates can be accessed with marker.location
  '''
  from ipyleaflet import Map, Marker, basemaps, basemap_to_tiles

  m = Map(
      basemap=basemap_to_tiles(basemaps.CartoDB.Positron),
      center=(40, -74), 
      zoom=7
    ) # Default to NJ

  marker = Marker(location=(40, -74), draggable=True) # defaults to New Jersey for SDWA project
  m.add_layer(marker);

  display(m)

  return marker

def add_spatial_data(url, name, projection=4326):
  """
  Gets external geospatial data
  
  Parameters
  ----------
  url: a zip of shapefile (in the future, extend to geojson)
  name: a string handle for the data files
  projection (optional): an EPSG projection for the spatial dataa

  Returns
  -------
  sd: spatial data reads ]as a geodataframe and projected to a specified projected coordinate system, or defaults to GCS
  
  """
  import requests, zipfile, io, geopandas

  r = requests.get(url) 
  z = zipfile.ZipFile(io.BytesIO(r.content))
  z.extractall("/content/"+name)
  sd = geopandas.read_file("/content/"+name+"/")
  sd.to_crs(crs=projection, inplace=True) # transform to input projection, defaults to WGS GCS
  return sd

def place_by_point(places, point):
  """
  get the place that contains a point
  
  Parameters
  ----------
  place: a geopandas geodataframe of polygons
  point: a geopandas geoseries (in the future, extend to gdf)

  Returns
  -------
  Filtered geodataframe
  """

  # Try to find overlap. If none, report it
  place = places.loc[places.geometry.contains(point[0])]
  if place.empty:
    print("Looks like your point doesn't fall within any of the places")
  else:
    return place # Theoretically, for some data, multiple places could contain a point (extend)

def show_map(layers, style):
  """
  maps layers according to styles

  Parameters
  ----------
  layers: a dict like {"places": places} where places is geojson, ordered in the z order you want
  styles: a dict like {"places": {"fill": none}} with other leaflet style properties

  Returns
  ----------
  Displays an ipyleaflet map

  """
  from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoData, LayersControl

  m = Map(
    basemap=basemap_to_tiles(basemaps.CartoDB.Positron),
    )
  
  for name, layer in layers.items():
    layer = layer.to_crs(4326) # transformation to geographic coordinate system required for mapping
    l = GeoData(
      geo_dataframe = layer,
      name = name,
      style = style[name]
    )
    m.add_layer(l)

    # hacky - iteratively fits the map frame to the bounds/extent of the layers
    bounds = layer.total_bounds
    bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
    m.fit_bounds(bounds) 

  m.zoom = 13

  m.add_control(LayersControl()) # adds a toggle for the layers

  display(m)

def get_data_from_ids(table, key, input):
  """
  Gets ECHO data from table based on matching ids

  Parameters
  ----------
  input: dataframe to get ids out of
  table: str, ECHO table of interest
  key: str, the field to match ids on
  currently only works where column names are same between input and table (extend)

  Returns
  ----------
  dataframe from SBU ECHO database copy

  """
  from ECHO_modules.utilities import get_data
  
  # process ids
  ids  = ""
  for id in list(input[key].unique()):
    ids += "'"+id +"',"
  ids = ids[:-1]
  ids
  
  # get data
  sql = 'select * from "'+table+'" where "'+key+'" in ({})'.format(ids)
  data = get_data(sql)
  
  return data

def chart_top_violators(ranked, values, size, labels):
  '''
  rank and chart entities based on a provided dataframe

  Parameters
  ----------
  ranked: dataframe sorted by the variable of interest (# of violations)
  values: str, name of variable (column) of interest
  size: int, how many of the top rows/entities to rank
  labels: dict, labels for the chart e.g. {'title': 'title', 'x': 'x-axis', 'y':'y-axis'}

  Returns
  ----------
  Matplotlib chart
  
  '''
  import seaborn as sns
  import matplotlib.pyplot as plt

  if ranked is None:
    print( 'There is no data to graph.')
    return None
  
  # Process data
  ranked = ranked.head(size)
  unit = ranked.index
  values = ranked[values] 
  
  # Create chart
  sns.set(style='whitegrid')
  fig, ax = plt.subplots(figsize=(10,10))
  try:
    g = sns.barplot(x=values, y=unit, order=list(unit), orient="h", color = "red") 
    g.set_title(labels["title"])
    ax.set_xlabel(labels["x"])
    ax.set_ylabel(labels["y"])
    ax.set_yticklabels(unit)
    return ( g )
  except TypeError as te:
    print( "TypeError: {}".format( str(te) ))
    return None

def bivariate_map(points, point_attribute, polygons, polygon_attribute):
  """
  Creates a bivariate map consisting of a point and a polygon layer symbolized according to specified attributes
  Parameters
  ----------
  points: geodataframe of point features
  point_attribute: str, indicating the field in the `points` to symbolize
  polygons: geodataframe of polygon features
  polygon_attribute: str, indicating the field in the `polygons` to symbolize
  """
  import branca
  from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoJSON, LayersControl, LayerGroup, Circle
  import json
  
  # set colorscale
  colorscale = branca.colormap.linear.YlOrRd_09.scale(polygons[polygon_attribute].min(), polygons[polygon_attribute].max()) 
  
  # set layers and style
  def style_function(feature):
    """
    Assumes a geojson as input feature
    """
    return {
      "fillOpacity": .5,
      "weight": .1,
      "fillColor": "#d3d3d3" if feature["properties"][polygon_attribute] is None else colorscale(feature["properties"][polygon_attribute]),
    }

  # Create map
  m = Map(
    basemap=basemap_to_tiles(basemaps.CartoDB.Positron),
    center=(40,-74),
    zoom = 7
    )

  # Create polygon layer
  polygons = polygons.to_crs(4326) # transformation to geographic coordinate system required
  geo_json = GeoJSON(
    data = json.loads(polygons.to_json()), # load as geojson
    style_callback = style_function
  )
  m.add_layer(geo_json)
  

  # Create points layer
  circles = []
  points = points.loc[points[point_attribute] > 0] # remove NaNs :(
  points = json.loads(points.to_json()) # convert to geojson
  for row in points["features"]:
    try:
      circle = Circle(
        location = (row["properties"]["FAC_LAT"], row["properties"]["FAC_LONG"]), #Need to un-hard code this. Should be able to use geometry.
        title = str(row["properties"][point_attribute]),
        radius = int(row["properties"][point_attribute]) * 2,
        color = "black",
        weight = 1,
        fill_color = "black",
        fill_opacity= 1
      )
      circles.append(circle)
    except:
      pass
  layer_group = LayerGroup(layers=(circles))
  m.add_layer(layer_group)

  # fits the map to the polygon layer
  bounds = polygons.total_bounds
  bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
  m.fit_bounds(bounds) 

  m.add_control(LayersControl()) # add control to toggle layers on/off

  display(m)

def choropleth(polygons, polygon_attribute):
  '''
  creates choropleth map - shades polygons by attribute

  Parameters
  ----------
  polygons: geodataframe of polygons to be mapped
  polygon_attribute: str, name of field in `polygons` geodataframe to symbolize

  Returns
  ----------
  Displays a map

  '''
  import branca
  import json
  from ipyleaflet import Map, basemaps, basemap_to_tiles, Choropleth, LayersControl

  m = Map(
      basemap=basemap_to_tiles(basemaps.CartoDB.Positron),
      center=(40,-74),
      zoom = 7
      )

  # split data into geo and choro data for mapping
  polygons = polygons.to_crs(4326) # requires transformation to geographic coordinate system
  geo_data = json.loads(polygons[["geometry"]].to_json()) # convert to geojson
  choro_data = polygons[[polygon_attribute]] # the attribute data
  choro_data = json.loads(choro_data.to_json()) # convert to geojson

  # Create layer
  layer = Choropleth(
    geo_data=geo_data,
    choro_data=choro_data[polygon_attribute],
    colormap=branca.colormap.linear.YlOrRd_09,
    border_color='black',
    style={'fillOpacity': 0.5, 'weight': .1},
    key_on = "id" #leaflet default
    )
  m.add_layer(layer)

  # fits the map to the layer
  bounds = polygons.total_bounds
  bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
  m.fit_bounds(bounds) 

  display(m)

def fix_county_names( in_counties ):
    '''
    ECHO_EXPORTER has counties listed both as ALAMEDA and ALAMEDA COUNTY, seemingly
    for every county.  We drop the 'COUNTY' so they only get listed once.

    Parameters
    ----------
    in_counties : list of county names (str)

    Returns
    -------
    list
        The list of counties without duplicates
    '''

    counties = []
    for county in in_counties:
        if (county.endswith( ' COUNTY' )): # TBD: or parish...
            county = county[:-7]
        counties.append( county.strip() )
    counties = np.unique( counties )
    return counties


def show_region_type_widget(region_field):
    '''
    Create and return a dropdown list of types of regions

    Returns
    -------
    widget
        The dropdown widget with the list of regions
    '''

    style = {'description_width': 'initial'}
    select_region_widget = widgets.Dropdown(
        options=region_field.keys(),
        style=style,
        #value='Zip Codes', # No Default
        description='Region of interest:',
        disabled=False
    )
    #display( select_region_widget )
    return select_region_widget


def show_state_widget(states):
    '''
    Create and return a dropdown list of states

    Returns
    -------
    widget
        The dropdown widget with the state list
    '''

    dropdown_state=widgets.Dropdown(
        options=states,
        description='State:',
        disabled=False,
    )
    
    #display( dropdown_state )
    return dropdown_state


def show_pick_region_widget( type, state_widget=None ):
    '''
    Create and return a dropdown list of regions appropriate
    to the input parameters

    Parameters
    ----------
    type : str
        The type of region
    state_widget : widget
        The widget in which a state may have been selected

    Returns
    -------
    widget
        The dropdown widget with region choices
    '''

    region_widget = None
    
    #if ( type != 'Zip Code' ):
    #    if ( state_widget is None ):
    #        print( "You must first choose a state." )
    #        return
    #    my_state = state_widget.value
    
    if ( type == 'Zip Code' ):
        region_widget = widgets.Text(
            value='98225',
            description='Zip Code:',
            disabled=False
        )
    elif ( type.startswith("HUC") ):
        region_widget = widgets.Text(
            value='14303',
            description='Zip Code:',
            disabled=False
        )
    elif ( type == 'County' ): 
        df = pd.read_csv( 'ECHO_modules/state_counties.csv' )
        counties = df[df['FAC_STATE'] == my_state]['FAC_COUNTY']
        region_widget=widgets.SelectMultiple(
            options=fix_county_names( counties ),
            description='County:',
            disabled=False
        )
    elif ( type == 'Congressional District' ):
        df = pd.read_csv( 'ECHO_modules/state_cd.csv' )
        cds = df[df['FAC_STATE'] == my_state]['FAC_DERIVED_CD113']
        region_widget=widgets.SelectMultiple(
            options=cds.to_list(),
            description='District:',
            disabled=False
        )
    #if ( region_widget is not None ):
        #display( region_widget )
    return region_widget


def show_data_set_widget( data_sets ):
    '''
    Create and return a dropdown list of data sets with appropriate
    flags set in the echo_data.

    Parameters
    ----------
    data_sets : dict
        The data sets, key = name, value = DataSet object

    Returns
    -------
    widget
        The widget with data set choices
    '''
    
    data_set_choices = list( data_sets.keys() )
    
    data_set_widget=widgets.Dropdown(
        options=list(data_set_choices),
        description='Data sets:',
        disabled=False,
    ) 
    #display(data_set_widget)
    return data_set_widget


def show_fac_widget( fac_series ):
    '''
    Create and return a dropdown list of facilities from the 
    input Series

    Parameters
    ----------
    fac_series : Series
        The facilities to be shown.  It may have duplicates.

    Returns
    -------
    widget
        The widget with facility names
    '''

    fac_list = fac_series.dropna().unique()
    fac_list.sort()
    style = {'description_width': 'initial'}
    widget=widgets.SelectMultiple(
        options=fac_list,
        style=style,
        layout=Layout(width='70%'),
        description='Facility Name:',
        disabled=False,
    )
    display(widget)
    return widget


def write_dataset( df, base, type, state, region ):
    '''
    Write out a file of the Dataframe passed in.

    Parameters
    ----------
    df : Dataframe
        The data to write.
    base: str
        A base string of the file to write
    type: str
        The region type of the data
    state: str
        The state, or None
    region: str
        The region identifier, e.g. CD number, County, State, Zip code
    '''
    if ( df is not None and len( df ) > 0 ):
        if ( not os.path.exists( 'CSVs' )):
            os.makedirs( 'CSVs' )
        filename = 'CSVs/' + base
        if ( type != 'Zip Code' ):
            filename += '-' + state
        filename += '-' + type
        if ( region is not None ):
            filename += '-' + str(region)
        filename += '.csv'
        df.to_csv( filename ) 
        print( "Wrote " + filename )
    else:
        print( "There is no data to write." )


def make_filename( base, type, state, region, filetype='csv' ):
    '''
    Make a filename from the parameters and return it.
    The filename will be in the Output directory relative to
    the current working directory, and in a sub-directory
    built out of the state and CD.

    Parameters
    ----------
    base : str
        A base string of the file
    type : str
        The region type
    state : str
        The state or None
    region : str
        The region
    filetype : str
        Optional file suffix.

    Returns
    -------
    str
        The filename created.

    Examples
    --------
    >>> filename = make_filename( 'noncomp_CWA_pg6', *df_type )
    '''
    # If type is 'State', the state name is the region.
    dir = 'Output/'
    if ( type == 'State' ):
        dir += region
        filename = base + '_' + region
    else:
        dir += state
        filename = base + '_' + state
        if ( region is not None ):
            dir += str(region)
            filename += '-' + str(region)
    x = datetime.datetime.now()
    filename += '-' + x.strftime( "%m%d%y") +'.' + filetype
    dir += '/'
    if ( not os.path.exists( dir )):
        os.makedirs( dir )
    return dir + filename
