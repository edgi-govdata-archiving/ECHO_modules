'''
Provide a number of utility Python functions that can de-clutter
the Jupyter notebooks that use them.
'''

# Import libraries
import os 
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas
import folium
import urllib
import seaborn as sns
from folium.plugins import FastMarkerCluster
import ipywidgets as widgets
from ipyleaflet import Map, basemaps, basemap_to_tiles, DrawControl, MarkerCluster, Marker
from ipyleaflet import Map, basemaps, basemap_to_tiles, DrawControl, MarkerCluster
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
from IPython.display import display
from ECHO_modules.get_data import get_echo_data
from ECHO_modules.geographies import region_field, states
from shapely.geometry import Polygon, Point
import geopandas as gpd

# Set up some default parameters for graphing
from matplotlib import cycler
colour = "#00C2AB" # The default colour for the barcharts
colors = cycler('color',
                ['#4FBBA9', '#E56D13', '#D43A69',
                 '#25539f', '#88BB44', '#FFBBBB'])
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none',
       axisbelow=True, grid=True, prop_cycle=colors)
plt.rc('grid', color='w', linestyle='solid')
plt.rc('xtick', direction='out', color='gray')
plt.rc('ytick', direction='out', color='gray')
plt.rc('patch', edgecolor='#E6E6E6')
plt.rc('lines', linewidth=2)
font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 16}
plt.rc('font', **font)
plt.rc('legend', fancybox = True, framealpha=1, shadow=True, borderpad=1)

# Styles for States ("other") and selected regions (e.g. Zip Codes) - "this"
map_style = {'this': {'fillColor': '#0099ff', 'color': '#182799', "weight": 1},
'other': {'fillColor': '#FFA500', 'color': '#182799', "weight": 1}}

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
        if (county.endswith( ' COUNTY' )):
            county = county[:-7]
        counties.append( county.strip() )
    counties = np.unique( counties )
    return counties


def show_region_type_widget( region_types=None, default_value='County' ):
    '''
    Create and return a dropdown list of types of regions

    Parameters
    ----------
    region_types : list of region types to show (str)
    
    Returns
    -------
    widget
        The dropdown widget with the list of regions
    '''

    if ( region_types == None ):
        region_types = region_field.keys()

    style = {'description_width': 'initial'}
    select_region_widget = widgets.Dropdown(
        options=region_types,
        style=style,
        value=default_value,
        description='Region of interest:',
        disabled=False
    )
    display( select_region_widget )
    return select_region_widget


def show_state_widget( multi=False ):
    '''
    Create and return a dropdown list of states

    Parameters
    ----------
    multi
        Allow multiple selection if True

    Returns
    -------
    widget
        The dropdown widget with the state list
    '''

    if ( multi ):
        dropdown_state=widgets.SelectMultiple(
            options=states,
            description='States:',
            disabled=False
        )
    else:
        dropdown_state=widgets.Dropdown(
            options=states,
            description='State:',
            disabled=False
        )
    
    display( dropdown_state )
    return dropdown_state


def get_frsid_list(filename):
    '''
    The file must be a CSV file with one column named FRSID.

    Parameters
    ----------
    filename : str

    Returns
    -------
    Series of FRSID values
    '''
    id_series = None
    try:
        df = pd.read_csv(filename)
        try:
            df = df[pd.to_numeric(df['FRSID'], errors='coerce').notnull()]
            id_series = df['FRSID'].dropna()
        except:
            print(f'Could not read a column in {filename} named FRSID')
            return None
    except:
        print(f'Could not open file: {filename}')
        return None
    return id_series


def make_widget(widget_parms):
    '''
    Make a widget to select items based on input parameters

    Parameters
    ----------
    widget_parms : Dictionary
    Should have keys: 'type', 'default', 'description'
        'type': The type of widget to create
        'default': The default or options 
        'description: The prompt label
    '''
    widget = None
    if widget_parms['type'] == 'text':
        widget = widgets.Text(
            value=widget_parms['default'],
            description=widget_parms['description'],
            disabled=False
        )
    elif widget_parms['type'] == 'multi':
        widget=widgets.SelectMultiple(
            options=widget_parms['default'],
            description=widget_parms['description'],
            disabled=False
        )
    elif widget['type'] == 'dropdown':
        region_widget=widgets.Dropdown(
            options=widget_parms['default'],
            description=widget_parms['description'],
            disabled=False
        )
    return widget


def show_pick_region_widget( type, state_widget=None, multi=True ):
    '''
    Create and return a dropdown list of regions appropriate
    to the input parameters.
    The state_widget might be a single value (string) or 
    multiple (list), or None. If it is a list, just use the first
    value.

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
    widget_parms = {}
    
    if not type in ('Zip Code', 'Watershed', 'FRSID List'):
        if state_widget is None:
            print( "You must first choose a state." )
            return
        my_state = state_widget.value
        if isinstance( my_state, tuple ):
            my_state = my_state[0]
    if type == 'Zip Code':
        widget_parms = {'type' : 'text', 'default' : '98225', 'description' : 'Zip Code:'}
    elif type == 'Watershed':
        widget_parms = {'type' : 'text', 'default' : '7110005', 'description' : 'Watershed:'}
    elif type == 'City':
        widget_parms = {'type' : 'text', 'default' : '', 'description' : 'Cities:'}
    elif type == 'FRSID List':
        widget_parms = {'type' : 'text', 'default' : '', 'description' : 'FRSID filename:'}
    elif type == 'County':
        url = "https://raw.githubusercontent.com/edgi-govdata-archiving/"
        url += "ECHO_modules/main/data/state_counties_corrected.csv"
        df = pd.read_csv( url )
        counties = df[df['FAC_STATE'] == my_state]['County']
        counties = counties.unique()
        if ( multi ):
            widget_parms = {'type' : 'multi', 'default' :counties, 'description' : 'Select counties:'}
        else:
            widget_parms = {'dropdown' : 'multi', 'default' : counties, 'description' : 'Select county:'}
    elif type == 'Congressional District':
        url = "https://raw.githubusercontent.com/edgi-govdata-archiving/"
        url += "ECHO_modules/main/data/state_cd.csv"
        df = pd.read_csv( url )
        cds = df[df['FAC_STATE'] == my_state]['FAC_DERIVED_CD113']
        if ( multi ):
            widget_parms = {'type' : 'multi', 'default' : cds, 'description' : 'Select districts:'}
        else:
            widget_parms = {'dropdown' : 'multi', 'default' : cds, 'description' : 'Select district:'}
    region_widget = make_widget(widget_parms)
    if ( region_widget is not None ):
        display( region_widget )
    return region_widget


def show_year_range_widget():
    start_year = 1970
    end_year = datetime.now().year
    options = [year for year in range(start_year,end_year)]
    index = (0, len(options)-1)
    selection_range_slider = widgets.SelectionRangeSlider(
        options=options,
        index=index,
        description='Dates',
        orientation='horizontal',
        layout={'width': '500px'}
    )
    display(selection_range_slider)
    return selection_range_slider


def get_regions_selected( region_type, region_widget ):
    '''
    The region_widget may have multiple selections.  
    Depending on its region_type, extract the selections
    and return them.

    Parameters
    ----------
    region_type : string
        'Zip Code', 'Congressional District', 'County'
   
    region_widget : widget
        The widget that will contain the selections.

    Returns
    -------
    list
        The selections
    '''

    selections = list()
    if ( region_type == 'Zip Code' ):
        selections = region_widget.value.split(',')
    else:
        selections = list( region_widget.value )

    return selections


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
    display(data_set_widget)
    return data_set_widget


def show_fac_widget( fac_series, top_violators=None ):
    '''
    Create and return a dropdown list of facilities from the 
    input Series. Pre-select the facilities identified in
    top_violators.

    Parameters
    ----------
    fac_series : Series
        The facilities to be shown.  It may have duplicates.

    top_violators : Dataframe
        The top violators in the region.

    Returns
    -------
    widget
        The widget with facility names
    '''
    selected = ()
    if top_violators is not None:
        selected = list(set(fac_series) & set(top_violators))
    fac_list = fac_series.dropna().unique()
    fac_list.sort()
    style = {'description_width': 'initial'}
    widget=widgets.SelectMultiple(
        options=fac_list,
        value=selected,
        style=style,
        layout=Layout(width='70%'),
        description='Facility Name:',
        disabled=False,
    )
    display(widget)
    return widget

def get_facs_in_counties( df, selected ):
    '''
    The dataframe df that is passed in will have all facilities for the state.
    The list selected passed in will have the corrected names of the counties
    we are interested in.
    We must accumulate facilities in all the alternative county names that the
    ECHO data has for facilities.  E.g., "Jefferson" and "Jefferson County"
    may both be in the ECHO data, but we want to consolidate them into
    "Jefferson".

    Parameters
    ----------
    df - DataFrame with facilities for the entire state.
    selected - List of selected counties.

    Returns
    -------
    Dataframe with all facilities in the selected counties.

    '''

    url = "https://raw.githubusercontent.com/edgi-govdata-archiving/"
    url += "ECHO_modules/main/data/state_counties_corrected.csv"
    state_counties = pd.read_csv(url)
    # Get all of the different ECHO names for the selected counties.
    selected_counties = state_counties[state_counties['County'].isin(selected)]['FAC_COUNTY']
    return df[df['FAC_COUNTY'].isin(selected_counties)]

def get_active_facilities( state, region_type, regions_selected, api=False, token=None):
    '''
    Get a Dataframe with the ECHO_EXPORTER facilities with FAC_ACTIVE_FLAG
    set to 'Y' for the region selected.

    Parameters
    ----------
    state : str
        The state, which could be None
    region_type : str
        The type of region:  'State', 'Congressional District', etc.
    regions_selected : list
        The selected regions of the specified region_type
    api : bool
        If True, use the API to get the data.  If False, use the local delta lake connection

    Returns
    -------
    Dataframe
        The active facilities returned from the database query
    '''

    try:
        if region_type == 'State' or region_type == 'County':
            sql = 'select * from ECHO_EXPORTER where FAC_STATE = \'{}\''
            sql += ' and FAC_ACTIVE_FLAG = \'Y\''
            sql = sql.format( state )
            df_active = get_echo_data( sql, 'REGISTRY_ID', api=api, token=token)
        elif ( region_type == 'Congressional District'):
            cd_str = ",".join( map( lambda x: str(x), regions_selected ))
            sql = 'select * from ECHO_EXPORTER where FAC_STATE = \'{}\''
            sql += ' and FAC_DERIVED_CD113 in ({})'
            sql += ' and FAC_ACTIVE_FLAG = \'Y\''
            sql = sql.format( state, cd_str )
            df_active = get_echo_data(sql, 'REGISTRY_ID', api=api, token=token)
        elif ( region_type == 'Zip Code' ):
            regions_selected = ''.join(regions_selected.split())
            zc_str = ",".join( map( lambda x: "\'"+str(x)+"\'", regions_selected.split(',') ))
            sql = 'select * from ECHO_EXPORTER where FAC_ZIP in ({})'
            sql += ' and FAC_ACTIVE_FLAG = \'Y\''
            sql = sql.format( zc_str )
            df_active = get_echo_data(sql, 'REGISTRY_ID', api=api, token=token)
        elif region_type == 'Watershed':
            regions_selected = ''.join(regions_selected.split())
            ws_str = ",".join( map( lambda x: "\'"+str(x)+"\'", regions_selected.split(',') ))
            sql = 'select * from ECHO_EXPORTER where FAC_DERIVED_HUC in ({})'
            sql += ' and FAC_ACTIVE_FLAG = \'Y\''
            sql = sql.format( ws_str )
            df_active = get_echo_data(sql, 'REGISTRY_ID', api=api, token=token)
        elif region_type == 'Neighborhood':
            poly_str = ''
            points = regions_selected
            
            # Get only id and coords from table
            sql = """
                SELECT REGISTRY_ID, FAC_LAT, FAC_LONG
                FROM ECHO_EXPORTER 
                WHERE FAC_ACTIVE_FLAG = 'Y'
            """
            df = get_echo_data( sql, 'REGISTRY_ID', api=api, token=token)
            df = filter_by_geometry(points, df)
            
            id_list_str = ", ".join(map(str, df["REGISTRY_ID"].tolist()))       
        
            # Run a second query to find rows with same IDs as filtered_points
            sql = f"SELECT * FROM ECHO_EXPORTER WHERE REGISTRY_ID IN ({id_list_str})"
            df_active = get_echo_data(sql, api=api, token=token)
        else:
            df_active = None
        if region_type == 'County':
            # df_active is currently all active facilities in the state.
            # Get only those in the selected counties.
            df_active = get_facs_in_counties(df_active, regions_selected)
    except pd.errors.EmptyDataError:
        df_active = None

    return df_active

def filter_by_geometry(points, df):  
    # Bounding Box
    min_lon = min(p[0] for p in points)
    max_lon = max(p[0] for p in points)
    min_lat = min(p[1] for p in points)
    max_lat = max(p[1] for p in points)
    
    # Make a geopandas dataframe of all points
    points_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['FAC_LONG'], df['FAC_LAT']), crs="EPSG:4269")
    
    filtered_points = points_gdf[
        (points_gdf.geometry.x >= min_lon) & 
        (points_gdf.geometry.x <= max_lon) & 
        (points_gdf.geometry.y >= min_lat) & 
        (points_gdf.geometry.y <= max_lat)
    ]
    
    # Filter more by creating a polygon using the points to get the points inside the polygon
    polygon = Polygon(points)
    filtered_points = filtered_points[filtered_points.geometry.intersects(polygon)]
    
    
    return filtered_points

def aggregate_by_facility(records, program, other_records = False, api=False, token=None):
  '''
  Aggregate a set of records by facility IDs, using sum or count operations. 
  Enables point symbol mapping. 
  Other facilities in the selection (e.g. facilities in Snohomish County *without* 
  reported CWA violations) can be identified and retrieved when the diff flag is True

  Parameters
  ----------
  records : DataSetResults object
      The records to aggregate. records should be a DataSetResults object created from
      a database query. In the :
      ds = make_data_sets(["CWA Violations"]) # Create a DataSet for handling the data
      snohomish_cwa_violations = ds["CWA Violations"].store_results(region_type="County", region_value=("SNOHOMISH",) state="WA") # Store results for this DataSet as a DataSetResults object
  program : String
      The name of the program, usually available from records.dataset.name
  other_records : Boolean
      When True, will retrieve other facilities in the selection 
      (e.g. facilities in Snohomish County *without* reported CWA violations)
    api : Boolean
        When True, will use the API to get the data.  If False, will use the local delta lake connection
  
  Returns
  -------
  A dictionary containing:
    the aggregated results
    active facilities regulated under this program, but without recorded violations, inspections, or whatever the metric is (e.g. violations)
    the name of the new field that counts or sums up the relevant metric (e.g. violations) 
  '''

  data = records.dataframe
  diff = None

  def differ(input, program, api=False, token=None):
    '''
    Helper function to sort facilities in this program (input) from the full list of faciliities regulated under the program (active)
    '''
    active = get_active_facilities(records.state, records.region_type, records.region_value, api=api, token=token)

    diff = list(
        set(active[records.dataset.echo_type + "_IDS"]) - set(input[records.dataset.idx_field])
        ) 
    
    # get rid of NaNs - probably no program IDs
    diff = [x for x in diff if str(x) != 'nan']
    
    # ^ Not perfect given that some facilities have multiple NPDES_IDs
    # Below return the full ECHO_EXPORTER details for facilities without violations, penalties, or inspections
    diff = active.loc[active[records.dataset.echo_type + "_IDS"].isin(diff)] 
    return diff

  # CWA Violations
  if (program == "CWA Violations"): 
    year = data["YEARQTR"].astype("str").str[0:4:1]
    data["YEARQTR"] = year
    data["sum"] = data["NUME90Q"] + data["NUMCVDT"] + data['NUMSVCD'] + data["NUMPSCH"]
    data = data.groupby([records.dataset.idx_field, "FAC_NAME", "FAC_LAT", "FAC_LONG"]).sum()
    data = data.reset_index()
    data = data.loc[data["sum"] > 0] # only symbolize facilities with violations
    aggregator = "sum" # keep track of which field we use to aggregate data, which may differ from the preset

  # Penalties
  elif (program == "CAA Penalties" or program == "RCRA Penalties" or program == "CWA Penalties" ):
    data.rename( columns={ records.dataset.date_field: 'Date', records.dataset.agg_col: 'Amount'}, inplace=True )
    if ( program == "CWA Penalties" ):
      data['Amount'] = data['Amount'].fillna(0) + data['STATE_LOCAL_PENALTY_AMT'].fillna(0)
    data = data.groupby([records.dataset.idx_field, "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({'Amount':'sum'})
    data = data.reset_index()
    data = data.loc[data["Amount"] > 0] # only symbolize facilities with penalties
    aggregator = "Amount" # keep track of which field we use to aggregate data, which may differ from the preset

  # Air emissions
  elif (program == "Greenhouse Gas Emissions" or program == "Toxic Releases"):
    data = data.groupby([records.dataset.idx_field, "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({records.dataset.agg_col:'sum'})
    data['sum'] = data[records.dataset.agg_col]
    data = data.reset_index()
    aggregator = "sum" # keep track of which field we use to aggregate data, which may differ from the preset
	  
  # SDWA population served
  elif (program == "SDWA Public Water Systems" or program == "SDWA Serious Violators"):
    # filter to latest fiscal year
    data = data.loc[data[records.dataset.date_field] == 2021]
    data = data.groupby([records.dataset.idx_field, "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({records.dataset.agg_col:'sum'})
    data['sum'] = data[records.dataset.agg_col]
    data = data.reset_index()
    aggregator = "sum" # keep track of which field we use to aggregate data, which may differ from the preset

  # Count of inspections, violations
  else: 
    data = data.groupby([records.dataset.idx_field, "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({records.dataset.date_field: 'count'})
    data['count'] = data[records.dataset.date_field]
    data = data.reset_index()
    data = data.loc[data["count"] > 0] # only symbolize facilities with X
    aggregator = "count" # keep track of which field we use to aggregate data, which may differ from the preset

  if other_records:
    diff = differ(data, program, api=api, token=token)
  
  if ( len(data) > 0 ):
    #print({"data": data, "aggregator": aggregator}) # Debugging
    return {"data": data, "diff": diff, "aggregator": aggregator}
  else:
    print( "There is no data for this program and region after 2000." )

# IGNORE 
def aggregate_by_geography(dsr, agg_type, spatial_tables, region_filter=None):
    '''
    Aggregate attribute data by a spatial unit, such as zip codes

    Parameters
    ----------
    dsr : DataSetResults object
        The data to be aggregated
    agg_type : str
        How to aggregate the data (sum, mean, median)
    spatial_tables : dict
        Import from ECHO_modules/geographies.py
    region_filter : list
        Optional list of regions (zips, counties, etc.) to focus on. Same as region_value from ds.store_results

    Returns
    -------
    result
        GeoDataFrame - data aggregated to the indicated spatial unit. This can then be mapped with choropleth()
        choropleth(result, dsr.dataset.agg_col, key_id=region_field[dsr.region_type]["field"], legend_name=dsr.dataset.agg_col)

    '''
    from ECHO_modules.get_data import get_spatial_data

    # Aggregate attribute data
    aggregated = dsr.dataframe.groupby(by=region_field[dsr.region_type]["field"])[[dsr.dataset.agg_col]].agg({dsr.dataset.agg_col:agg_type}) 
    # Join aggregated data with spatial dataset
    ## Get spatial data
    if region_filter and dsr.region_type == "County":
        region_filter = [c.title() for c in region_filter]
    regions, states = get_spatial_data(dsr.region_type, dsr.state, spatial_tables, region_filter=region_filter)
    ## Join
    if dsr.region_type == "County":
        idx = regions[spatial_tables[dsr.region_type]['match_field']].str.upper()
    else:
        idx = regions[spatial_tables[dsr.region_type]['match_field']]
    
    results = geopandas.GeoDataFrame(aggregated.join(regions[["geometry"]].set_index(idx)), geometry="geometry", crs=4269)
    return results 

def marker_text( row, no_text, name_field="FAC_NAME", url_field="DFR_URL"):
    '''
    Create a string with information about the facility or program instance.

    Parameters
    ----------
    row : Series
        Expected to contain FAC_NAME and DFR_URL fields from ECHO_EXPORTER
    no_text : Boolean
        If True, don't put any text with the markers, which reduces chance of errors 
    name_field : string
        The field to use for the name in the marker
    url_field : string
        The field to use for the marker's URL

    Returns
    -------
    str
        The text to attach to the marker
    '''

    text = ""
    if ( no_text ):
        return text
    if ( type( row[name_field] == str )) :
        try:
            text = row[name_field] + ' - '
        except TypeError:
            print( "A facility was found without a name. ")
        if url_field in row:
            text += " - <p><a href='"+row[url_field]
            text += "' target='_blank'>Link to ECHO detailed report</a></p>" 
    return text


def check_bounds( row, bounds ):
    '''
    See if the FAC_LAT and FAC_LONG of the row are interior to
    the minx, miny, maxx, maxy of the bounds.

    Parameters
    ----------
    row : Series
	Must contain FAC_LAT and FAC_LONG
    bounds : Dataframe
	Bounding rectangle--minx,miny,maxx,maxy

    Returns
    -------
    True if the row's point is in the bounds
    '''

    if ( row['FAC_LONG'] < bounds.minx[0] or row['FAC_LAT'] < bounds.miny[0] \
         or row['FAC_LONG'] > bounds.maxx[0] or row['FAC_LAT'] > bounds.maxy[0]):
        return False
    return True


def mapper(df, bounds=None, no_text=False):
    '''
    Display a map of the Dataframe passed in.
    Based on https://medium.com/@bobhaffner/folium-markerclusters-and-fastmarkerclusters-1e03b01cb7b1

    Parameters
    ----------
    df : Dataframe
        The facilities to map.  They must have a FAC_LAT and FAC_LONG field.
    bounds : Dataframe
        A bounding rectangle--minx, miny, maxx, maxy.  Discard points outside.

    Returns
    -------
    folium.Map
    '''

    if df.empty:
        print("The DataFrame is empty. There is nothing to map.")
        return None

    # Initialize the map
    m = folium.Map(
        location = [df.mean(numeric_only=True)["FAC_LAT"], df.mean(numeric_only=True)["FAC_LONG"]]
    )

    df = df.drop_duplicates(subset=[name_field, lat_field, long_field])

    # Create the Marker Cluster array
    #kwargs={"disableClusteringAtZoom": 10, "showCoverageOnHover": False}
    mc = FastMarkerCluster("")

    # Add a clickable marker for each facility
    for index, row in df.iterrows():
        if ( bounds is not None ):
            if ( not check_bounds( row, bounds )):
                continue
        mc.add_child(folium.CircleMarker(
            location = [row["FAC_LAT"], row["FAC_LONG"]],
            popup = marker_text( row, no_text ),
            radius = 8,
            color = "black",
            weight = 1,
            fill_color = "orange",
            fill_opacity= .4
        ))
    m.add_child(mc)

    bounds = m.get_bounds()
    m.fit_bounds(bounds)

    # Show the map
    return m


def ipymapper(df, bounds=None, no_text=False, lat_field='FAC_LAT', long_field='FAC_LONG', 
           name_field='FAC_NAME', info_field='DFR_URL', zoom=8):
    '''
    Display a map of the Dataframe passed in.
    Based on https://medium.com/@bobhaffner/folium-markerclusters-and-fastmarkerclusters-1e03b01cb7b1

    Parameters
    ----------
    df : Dataframe
        The facilities to map.  They must have latitude and longitude fields.
    bounds : Dataframe
        A bounding rectangle--minx, miny, maxx, maxy.  Discard points outside.

    Returns
    -------
    ipyleaflet map
    '''

    if df.empty:
        print("The DataFrame is empty. There is nothing to map.")
        return None

    # icon = AwesomeIcon(name='building')

    base = basemap_to_tiles(basemaps.CartoDB.Positron)
  
    df = df.dropna(subset=[name_field, lat_field, long_field])
    df = df.drop_duplicates(subset=[name_field, lat_field, long_field])
    center = [df.mean(numeric_only=True)[lat_field], 
              df.mean(numeric_only=True)[long_field]]
    print( f'Center is {center}')

    m = Map(layers=(base, ), 
            center=center, 
            zoom=zoom,
            scroll_wheel_zoom=True,
            min_zoom=2, 
            max_bounds=True,
            layout=Layout(height='500px')
        )

    global shapes
    shapes = set()
    
    markers = []
    marker_radius = 10
    # Add a clickable marker for each facility
    for index, row in df.iterrows():
        if ( bounds is not None ):
            if (not check_bounds( row, bounds, lat_field, long_field)):
                continue
        mark = Marker()
        mark.location = (row[lat_field], row[long_field])
        mark.radius = marker_radius
        mark.color = "black"
        mark.fill_color = "orange"
        mark.opacity = 0.7
        mark.title = row[name_field]
        markers.append(mark)
    marker_cluster = MarkerCluster(markers=markers)
    m.add(marker_cluster)

    draw_control = DrawControl()
    
    draw_control.rectangle = {
        "shapeOptions": {
        "fillColor": "#fca45d",
        "color": "#fca45d",
        "fillOpacity": .25
    }}
    draw_control.on_draw(handle_draw)
    m.add_control(draw_control)

    # bounds = m.get_bounds()
    # m.fit_bounds(bounds)

    # Show the map
    return (m, shapes)


def point_mapper(df, aggcol, quartiles=False, other_fac=None):
  '''
  Display a point symbol map of the Dataframe passed in. A point symbol map represents 
  each facility as a point, with the size of the point scaled to the data value 
  (e.g. inspections, violations) proportionally or through quartiles.
  Parameters
  ----------
  df : Dataframe
      The facilities to map. They must have a FAC_LAT and FAC_LONG field.
      This Dataframe should
      already be aggregated by facility e.g.:
      NPDES_ID  violations  FAC_LAT FAC_LONG
      NY12345   13          43.03   -73.92
      NY54321   2           42.15   -80.12
      ...
  aggcol : String
      The name of the field in the Dataframe that has been aggregated. This is
      used for the legend (pop-up window on the map)
  quartiles : Boolean
      False (default) returns a proportionally-scaled point symbol map, meaning
      that the radius of each point is directly scaled to the value (e.g. 13 violations)
      True returns a graduated point symbol map, meaning that the radius of each 
      point is a function of the splitting the Dataframe into quartiles. 
  other_fac : Dataframe
      Other regulated facilities without violations, inspections,
      penalties, etc. - whatever the value being mapped is. This is an optional 
      variable enabling further context to the map. They must have a FAC_LAT and FAC_LONG field.
  Returns
  -------
  folium.Map
  '''
  if ( df is not None ):

    map_of_facilities = folium.Map()
   
    if quartiles == True:
      df['quantile'] = pd.qcut(df[aggcol], 4, labels=False, duplicates="drop")
      scale = {0: 8,1:12, 2: 16, 3: 24} # First quartile = size 8 circles, etc.

    # Add a clickable marker for each facility
    for index, row in df.iterrows():
      if quartiles == True:
        r = scale[row["quantile"]]
      else:
        r = row[aggcol]
      map_of_facilities.add_child(folium.CircleMarker(
          location = [row["FAC_LAT"], row["FAC_LONG"]],
          popup = aggcol+": "+str(row[aggcol]),
          radius = r * 1.5, # arbitrary scalar
          color = "black",
          weight = 1,
          fill_color = "orange",
          fill_opacity= .4
      ))
    
    if ( other_fac is not None ):
      for index, row in other_fac.iterrows():
        map_of_facilities.add_child(folium.CircleMarker(
            location = [row["FAC_LAT"], row["FAC_LONG"]],
            popup = "other facility",
            radius = 4,
            color = "black",
            weight = 1,
            fill_color = "black",
            fill_opacity= 1
        ))

    bounds = map_of_facilities.get_bounds()
    map_of_facilities.fit_bounds(bounds)

    return map_of_facilities

  else:
    print( "There are no facilities to map." )
    

def choropleth(polygons, attribute, key_id, attribute_table=None, legend_name=None, color_scheme="PuRd"):
    '''
    creates choropleth map - shades polygons by attribute

    Parameters
    ----------
    polygons: geodataframe of polygons to be mapped
    attribute: str, name of field to symbolize
    key_id: str, name of the index field
    attribute_table: dataframe, optional.
    legend_name: str, a nice title for the legend
    color_scheme: str

    Returns
    ----------
    Displays a map

    '''

    import json

    m = folium.Map()

    polygons.reset_index(inplace=True) # Reset index
    polygons = polygons[~polygons.geometry.isna()] # Remove empty geographies we can't map   
    if attribute_table is not None: # if we have a separate attribute table that needs to be joined with the spatial data (polygons)...
        data = attribute_table
    else:
        data = polygons    
    layer = folium.Choropleth(
        geo_data = polygons,
        data = data,
        columns = [key_id, attribute],
        key_on = "feature.properties."+key_id,
        fill_color = color_scheme,
        fill_opacity = 0.7,
        line_opacity = 0.2,
        legend_name = legend_name, 
    ).add_to(m)
    folium.GeoJsonTooltip(fields=[key_id, attribute]).add_to(layer.geojson) # Hover over for information

    bounds = m.get_bounds()
    m.fit_bounds(bounds)

    return m


def bivariate_map(regions, points, bounds=None, no_text=False, region_fields=None, 
                  region_aliases = None, points_fields=None, points_aliases=None,
                  show_marker=False):
    '''
    show the map of region(s) (e.g. zip codes) and points (e.g. facilities within the regions)
    create the map using a library called Folium (https://github.com/python-visualization/folium)
    bounds can be preset if necessary
    no_text errors can be managed
    '''
    m = folium.Map()  

    region_popup = None
    if region_fields:
       region_popup = folium.GeoJsonPopup(
           fields = region_fields,
           aliases = region_aliases,
           localize=True,
           labels=True,
           style="background-color: yellow;",
        )

    # Show the region(s
    s = folium.GeoJson(
      regions,
      style_function = lambda x: map_style['other'],
      popup=region_popup,
    ).add_to(m)

    # Show the points
    ## Create the Marker Cluster array
    #kwargs={"disableClusteringAtZoom": 10, "showCoverageOnHover": False}
 
    points_popup = None
    if points_fields:
        points_popup = folium.GeoJsonPopup(
           fields = points_fields,
           aliases = points_aliases,
           localize=True,
           labels=True,
           style="background-color: yellow;",
        )

    # Show the points
    if show_marker:
        marker=folium.Marker()
    else:
        marker=folium.CircleMarker(radius = 8, color = "black", weight = 1, fill_color = "orange", fill_opacity= .4)
    folium.GeoJson(
        points,
        marker=marker,
        popup=points_popup,
        highlight_function=lambda x: {"fillOpacity": 0.8},
        zoom_on_click=True,
    ).add_to(m)

    # compute boundaries so that the map automatically zooms in
    bounds = m.get_bounds()
    m.fit_bounds(bounds, padding=0)

    # display the map!
    display(m)


def show_regions(regions, states, region_type, spatial_tables):
    '''
    show the map of just the regions (e.g. zip codes) and the selected state(s)
    create the map using a library called Folium (https://github.com/python-visualization/folium)
    '''
    m = folium.Map()  

    # Show the state(s)
    s = folium.GeoJson(
      states,
      name = "State",
      style_function = lambda x: map_style['other']
    ).add_to(m)

    # Show the intersection regions (e.g. Zip Codes)
    i = folium.GeoJson(
      regions,
      name = region_type,
      style_function = lambda x: map_style['this']
    ).add_to(m)
    folium.GeoJsonTooltip(fields=[spatial_tables[region_type]["pretty_field"].lower()]).add_to(i) # Add tooltip for identifying features

    # compute boundaries so that the map automatically zooms in
    bounds = m.get_bounds()
    m.fit_bounds(bounds, padding=0)

    # return the map!
    return m


def dataset_filename(base, type, state, regions):
    '''
    Create a suggested filename.

    Parameters
    ----------
    base: str
        A base string of the file to write
    type: str
        The region type of the data
    state: str
        The state, or None
    regions: tuple
        The region identifiers, e.g. CD number, County, State, Zip code
    '''
    filename = base[:50]
    filename = filename.replace(' ', '-')
    if ( state != None ):
        filename += '-' + state
    filename += '-' + type

    if ( type not in ('Neighborhood', 'FRSID List') and regions is not None ):
        for region in regions:
            filename += '-' + str(region)
    filename = filename.replace('\'', '').replace(',', '-')
    filename = urllib.parse.quote_plus(filename, safe='/')
    filename += '.csv'
    filename_widget = widgets.Text(
        value=filename,
        description='File name:',
        disabled=False
    )
    display(filename_widget)
    return filename_widget


def write_dataset( df, filename ):
    '''
    Write out a file of the Dataframe passed in.

    Parameters
    ----------
    df : Dataframe
        The data to write.
    filename:
        The user's choice of a filename
    '''
    if ( df is not None and len( df ) > 0 ):
        if ( not os.path.exists( 'CSVs' )):
            os.makedirs( 'CSVs' )
        filename = 'CSVs/' + filename.replace(' ', '-')
        filename = filename.replace('\'', '').replace(',', '-')
        filename = urllib.parse.quote_plus(filename, safe='/')
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
    x = datetime.now()
    filename += '-' + x.strftime( "%m%d%y") +'.' + filetype
    dir += '/'
    if ( not os.path.exists( dir )):
        os.makedirs( dir )
    return dir + filename


def get_top_violators( df_active, flag, noncomp_field, action_field, num_fac=None ):
    '''
    Sort the dataframe and return the rows that have the most number of
    non-compliant quarters.

    Parameters
    ----------
    df_active : Dataframe
        Must have ECHO_EXPORTER fields
    flag : str
        Identifies the EPA programs of the facility (AIR_FLAG, NPDES_FLAG, etc.)
    noncomp_field : str
        The field with the non-compliance values, 'S' or 'V'.
    action_field
        The field with the count of quarters with formal actions
    num_fac
        The number of facilities to include in the returned Dataframe

    Returns
    -------
    tuple
        The top num_fac violators for the EPA program in the region
        All violators for the EPA program in the region

    Examples
    --------
    >>> (df_top_violators, df_violators) = get_top_violators( df_active, 'AIR_FLAG',
        'CAA_3YR_COMPL_QTRS_HISTORY', 'CAA_FORMAL_ACTION_COUNT', 20 )
    '''
    df = df_active.loc[ df_active[flag] == 'Y' ]
    if ( len( df ) == 0 ):
        return None
    df_active = df.copy()
    noncomp = df_active[ noncomp_field ]
    noncomp_count = noncomp.str.count('S') + noncomp.str.count('V')
    df_active['noncomp_count'] = noncomp_count
    df_active = df_active[['FAC_NAME', 'noncomp_count', action_field,
            'DFR_URL', 'FAC_LAT', 'FAC_LONG']]
    df_active_all = df_active[df_active['noncomp_count'] > 0]
    df_active = df_active_all.sort_values(by=['noncomp_count', action_field], 
            ascending=False)
    if num_fac is not None:
        df_active = df_active.head(num_fac)
    return (df_active, df_active_all)


def get_tri_ghg_violators(df_active, field, num_fac):
    '''
    Sort the dataframe and return the rows that have the most number of
    non-zero records.

    Parameters
    ----------
    df_active : Dataframe
        Must have ECHO_EXPORTER fields
    flag : str
        Identifies the EPA programs of the facility (AIR_FLAG, NPDES_FLAG, etc.)
    field : str
        The field with the non-compliance values
    num_fac
        The number of facilities to include in the returned Dataframe

    Returns
    -------
    tuple
        The top num_fac violators for the EPA program in the region
        All violators for the EPA program in the region

    Examples
    --------
    >>> (df_top_violators, df_violators) = get_top_violators( df_active, 'AIR_FLAG',
        'CAA_3YR_COMPL_QTRS_HISTORY', 'CAA_FORMAL_ACTION_COUNT', 20 )
    '''
    df = df_active.loc[df_active[field]  > 0]
    df_a = df.copy()
    df_a = df_a[['FAC_NAME', field, 'DFR_URL', 'FAC_LAT', 'FAC_LONG']]
    df_a = df_a.sort_values(by=[field], ascending=False)
    df_a_all = df_a
    if num_fac is not None:
        df_a = df_a.head(num_fac)
    return (df_a, df_a_all)   

# def get_sdwa_violators(df_active, num_violators):
# use SDWA_FORMAL_ACTION_COUNT ?
    

def chart_tri_ghg_violators(df, field, title, xlabel):
    unit = df.index
    values = df[field]
    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(10,10))
    try:
      g = sns.barplot(x=values, y=unit, order=list(unit), orient='h', color=colour)
      g.set_title(title)
      ax.set_xlabel(xlabel)
      ax.set_ylabel('Facility')
      # ax.set_yticks(ax.get_yticks())
      ax.set_yticks(range(len(df)))
      ax.set_yticklabels(df['FAC_NAME'])
    except TypeError as te:
      print("TypeError: {}".format(str(te)))


def chart_top_violators( ranked, state, selections, epa_pgm ):
    '''
    Draw a horizontal bar chart of the top non-compliant facilities.

    Parameters
    ----------
    ranked : Dataframe
        The facilities to be charted
    state : str
        The state
    selections : list
        The selections
    epa_pgm : str
        The EPA program associated with this list of non-compliant facilities

    Returns
    -------
    seaborn.barplot
        The graph that is generated
    '''
    if ranked is None:
        print( 'There is no {} data to graph.'.format( epa_pgm ))
        return None
    unit = ranked.index 
    values = ranked['noncomp_count'] 
    if ( len(values) == 0 ):
        if state == None:
            return "No {} facilities with non-compliant quarters in {}".format(
                epa_pgm, str(selections))
        else:
            return "No {} facilities with non-compliant quarters in {} - {}".format(
                epa_pgm, state, str( selections ))
    sns.set_theme(style='whitegrid')
    fig, ax = plt.subplots(figsize=(10,10))
    try:
        g = sns.barplot(x=values, y=unit, order=list(unit), orient="h", color = colour) 
        title = f'{epa_pgm} facilities with the most non-compliant quarters'
        if len(selections) <= 3:
            title += f' in {state} - {str(selections)}'
        g.set_title(title)
        ax.set_xlabel("Non-compliant quarters")
        ax.set_ylabel("Facility")
        # ax.set_yticks(ax.get_yticks())
        ax.set_yticks(range(len(ranked)))
        ax.set_yticklabels(ranked["FAC_NAME"])
        return ( g )
    except TypeError as te:
        print( "TypeError: {}".format( str(te) ))
        return None


def chart (full_data, date_column, counting_column, measure, function, title, mnth_name=""):
  """
  Full documentation coming soon!
  full data = the data to be charted
  date_column = the column in the data to use for summarizing by date
  counting_column = the column to sum up
  measure = the name of the summing method e.g. count or total 
  function = the way to sum up e.g. count or sum or nunique
  title = chart title
  mnth_name = optional description of the months in focus (e.g. for COVID notebook)
  """

  # Organize the data
  this_data = full_data.groupby([date_column])[counting_column].agg(function) # For each day, count the number of inspections/enforcements/violations # Summarize inspections/enforcements/violations on a monthly basis  
  this_data = this_data.resample('Y').sum() # Add together the two months (3 - 4) we're looking at
  this_data = pd.DataFrame(this_data) # Put our data into a dataframe
  this_data = this_data.rename(columns={counting_column: measure}) # Format the data columns
  this_data.index = this_data.index.strftime('%Y') # Make the x axis (date) prettier

  # Create the chart
  ax = this_data.plot(kind='bar', title = ""+title+" in %s of each year 2001-2022" %(mnth_name), figsize=(20, 10), fontsize=16, color=colour)
  ax

  # Label trendline
  trend=this_data[measure].mean()
  ax.axhline(y=trend, color='#e56d13', linestyle='--', label = "Average "+title+" in %s 2001-2022" %(mnth_name))

  # Label the previous three years' trend (2020, 2021, 2022)
  trend_month=pd.concat([this_data.loc["2020"],this_data.loc["2021"],this_data.loc["2022"]])
  trend_month=trend_month[measure].mean()
  ax.axhline(y=trend_month, xmin = .88, xmax=1, color='#d43a69', linestyle='--', label = "Average for %s 2020-2022" %(mnth_name))

  # Label plot
  ax.legend()
  ax.set_xlabel(mnth_name+" of Each Year")
  ax.set_ylabel(title)


def handle_draw(self, action, geo_json):
  global shapes
  polygon=[]
  for coords in geo_json['geometry']['coordinates'][0][:-1][:]:
    polygon.append(tuple(coords))
  polygon = tuple(polygon)
  if action == 'created':
    shapes.add(polygon)
  elif action == 'deleted':
    shapes.discard(polygon)


def polygon_map(center=(39.8282,-98.5796), zoom=5):
  # Create map
  ## Heavily inspired by #https://notebook.community/rjleveque/binder_experiments/misc/ipyleaflet_polygon_selector
  watercolor = basemap_to_tiles(basemaps.CartoDB.Positron)
  
  m = Map(layers=(watercolor, ), center=center, zoom=zoom)
  
  global shapes
  shapes = set()
  
  draw_control = DrawControl()
  
  draw_control.rectangle = {
      "shapeOptions": {
          "fillColor": "#fca45d",
          "color": "#fca45d",
          "fillOpacity": .25
      }
  }
  draw_control.on_draw(handle_draw)
  m.add_control(draw_control)
  return (m, shapes)
