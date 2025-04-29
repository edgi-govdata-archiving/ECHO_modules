import pandas as pd
import numpy as np
import folium
from folium.plugins import FastMarkerCluster
from itertools import islice
from ipywidgets import widgets, Layout
from ECHO_modules.get_data import get_echo_data
from ECHO_modules.utilities import check_bounds, marker_text
from IPython.display import display

def _get_min_max_coord(coord_set):
    '''
    Get the minimum and maximum values of the set of 
    (longitude, latitude) coordinates.

    Parameters
    ----------
    coord_set : set
        The set of (longitude, latitude) values.

    Return
    ------
    A tuple with the results
    '''

    min_lat = 90
    max_lat = 0
    min_long = 180
    max_long = -180
    for x in list(coord_set):
        for coord in x:
            lat = coord[1]
            long = coord[0]
            min_lat = lat if lat < min_lat else min_lat
            max_lat = lat if lat > max_lat else max_lat
            min_long = long if long < min_long else min_long
            max_long = long if long > max_long else max_long
    return (min_lat, max_lat, min_long, max_long)

def get_facs_in_rect(df, lat_field, long_field, rect_set):
    '''
    Select the facilities whose latitude and longitude values
    are inside the rectangle

    Parameters
    ----------
    df : DataFrame
        Containing the lat_field and long_field

    lat_field : str
        The name of the latitude field in the dataframe

    long_field : str
        The name of the longitude field

    rect_set : set
        The set of (longitude, latitude) values
    '''
    (min_lat, max_lat, min_long, max_long) = _get_min_max_coord(rect_set)
    result_df = df.loc[((df[lat_field] >= min_lat) & (df[lat_field] <= max_lat) & \
                        (df[long_field] >= min_long) & (df[long_field] <= max_long))]
    return result_df

def show_rsei_pick_region_widget(type, state_widget=None, multi=False, description=None):
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
    
    description_text = f'{type}'
    if description is not None:
        description_text = description
    if type in ('City', 'County'):
        if ( state_widget is None ):
            print( "You must first choose a state." )
            return
        my_state = state_widget.value
        if ( isinstance( my_state, tuple )):
            my_state = my_state[0]
    if type in ('Zip Code', 'City', 'County', 'FRSID List'):
        region_widget = widgets.Text(
            value='',
            description=description_text,
            disabled=False
        )
    if region_widget is not None:
        display( region_widget )
    return region_widget

def show_select_multiple_widget(items, label, preselected=None):
    '''
    Create and return a dropdown list of the items from the 
    input Series.

    Parameters
    ----------
    items : Series
        The items to be shown.  It may have duplicates.

    preselected : list
        The items to be pre-selected.

    Returns
    -------
    widget
        The widget with items
    '''
    selected = ()
    if preselected is not None:
        selected = list(set(items) & set(top_violators))
    item_list = items.dropna().unique()
    item_list.sort()
    style = {'description_width': 'initial'}
    widget=widgets.SelectMultiple(
        options=item_list,
        value=selected,
        style=style,
        layout=Layout(width='70%'),
        description=label,
        disabled=False,
    )
    return widget

def _filter_years(df, year_column, years):
    start_year = 0
    end_year = 2500
    if years is not None:
        start_year = years[0]
        end_year = years[1]
        df = df[df[year_column].between(start_year, end_year)]
    return df

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

def get_rsei_facilities(state, region_type, regions_selected, rsei_type, columns='*',
                        years=None):
    '''
    Get a Dataframe with the RSEI facilities
    The table identified by the rsei_type must have 
    - A State field for region_type 'State'
    - A City and State field for region_type 'City'
    - A County and State field for region_type 'County'
    - A ZIPCode field for region_type 'Zip Code'
    - A Latitude and Longitude field for region_type 'Neighborhood'

    Parameters
    ----------
    state : str
        The state, which could be None
    region_type : str
        The type of region:  'State', 'Congressional District', etc.
    regions_selected : list
        The selected regions of the specified region_type
    rsei_type : str
        The start of the RSEI table--e.g. 'facility' or 'offsite'
    regions_selected : list
        The selected regions of the specified region_type
    years : list
        A two-element list of the year range

    Returns
    -------
    Dataframe
        The active facilities returned from the database query
    '''
    
    table = f"{rsei_type}_data_rsei_v2312"
    state = state.upper()
    if region_type == 'Zip Code':
        regions_selected = regions_selected.upper()
        regions_selected = ''.join(regions_selected.split())
        split_str = ",".join( map( lambda x: "\'"+str(x)+"\'", regions_selected.split(',') ))
    elif region_type in ('City', 'County'):
        regions_selected = regions_selected.upper().split(',')
        split_str = ""
        started = False
        for s in regions_selected:
            if started:
                split_str += ','
            started = True
            split_str += "\'" + s.strip() + "\'"

    try:
        if region_type == 'State':
            sql = f'select {columns} from "{table}" where upper("State") = \'{state}\''
        elif region_type == 'City':
            sql = f'select {columns} from "{table}" where upper("State") = \'{state}\''
            sql += f' and upper("City") in ({split_str})'
        elif region_type == 'County':
            sql = f'select {columns} from "{table}" where "State" = \'{state}\''
            sql += f' and upper("County") in ({split_str})'
        elif region_type == 'Zip Code':
            sql = f'select {columns} from "{table}" where "ZIPCode" in ({split_str})'
        elif region_type == 'Neighborhood':
            poly_str = ''
            points = regions_selected
            long_min = min(points[0][0], points[1][0], points[2][0], points[3][0])
            lat_min = min(points[0][1], points[1][1], points[2][1], points[3][1])
            long_max = max(points[0][0], points[1][0], points[2][0], points[3][0])
            lat_max = max(points[0][1], points[1][1], points[2][1], points[3][1])

            sql = f"""
                SELECT {columns}
                FROM "{table}"
                WHERE "Latitude" BETWEEN {lat_min} AND {lat_max} AND "Longitude" BETWEEN {long_min} and {long_max}
                """
        print(sql)
        df_active = get_echo_data(sql)
        if years is not None:
            df_active = _filter_years(df_active, 'LLYear', years)
    except pd.errors.EmptyDataError:
        df_active = None

    return df_active

def get_this_by_that(this_name, that_series, this_key, int_flag=True, this_columns='*', 
                     years=None, year_field=None, limit=None):
    '''
    Get the records from 'this' table associated with the ids (in that_series) 
    from 'that' table.
    If that_series is larger than 50 ids, the ids are used in chunks of 50.

    Parameters
    ----------
    this : str
        The table to get records from
    that : str
        The table with associated ids
    that_series : Series
        The list of associated ids from 'that'
    int_flag : boolean
        True if the values in that_series are ints
    this_columns : str
        The columns of 'this' table to include
    years : list
        A two-element list of the year range
    year_field : str
        The field in 'this' table to filter years
    limit : int
        A maximum number of records to return

    Returns
    -------
    Dataframe
        The 'this' records returned from the database query
    '''

    table = f"{this_name}_data_rsei_v2312"
    sql_base = f'select {this_columns} from "{table}"'
    df_result = None
    if that_series is not None:
        that_tuple = tuple(that_series)

        iterator = iter(that_tuple)
        count = 0
        while chunk := list(islice(iterator, 50)):
            id_string = ""

            for id in chunk:
                count += 1
                if ( not int_flag ):
                    id_string += "'"
                id_string += str(id)
                if ( not int_flag ):
                    id_string += "'"
                id_string +=  ","
            id_string=id_string[:-1] # removes trailing comma
            sql = sql_base + f' where "{this_key}" in ({id_string})'
            if limit is not None:
                if limit > 0:
                    sql += f' limit {limit}'
                else:
                    break
            if count % 100 == 0:
                print(f'{count}) reading {table}')
            try:
                df = get_echo_data(sql)
                if limit is not None:
                    limit -= len(df)
                if years is not None:
                    df = _filter_years(df, year_field, years)
            except pd.errors.EmptyDataError:
                df = None
            if df is not None:
                if df_result is None:
                    df_result = df
                else:
                    df_result = pd.concat([df_result, df])
    return df_result

def add_chemical_to_submissions(submissions, chemical_columns='*'):
    '''
    Get the chemical associated with the submissions and add them to
    submissions dataframe
    
    Parameters
    ----------
    submissions : DataFrame
        The submissions
    chemical_columns : str
        The columns of the chemical table to include
    
    Returns
    -------
    Dataframe
        The submission dataframe with the chemical columns joined 
    '''
    chemical_numbers = submissions['ChemicalNumber'].unique() 
    chem_ints = np.asarray(chemical_numbers,dtype="int")
    chem_int_string = ''
    started = False
    for i in chem_ints:
        if started:
            chem_int_string += ', '
        else:
            started = True
        chem_int_string += str(i)
    table = "chemical_data_rsei_v2312"
    table = "chemical_data_rsei_v2312"
    sql = f'select {chemical_columns} from "{table}"'
    sql += f' where "ChemicalNumber" in ({chem_int_string})'
    print(sql)
    
    try:
        chem_df = get_echo_data(sql)
    except pd.errors.EmptyDataError:
        chem_df = None

    sub_df = pd.merge(submissions, chem_df, on='ChemicalNumber')

    return sub_df

def _locate_map(df_dicts):
    '''
    Calculate the mean lat/long location among the dataframes
    contained in the df_dicts (tuple of Dictionaries)
    '''
    lat_sum = 0
    long_sum = 0
    for dict in df_dicts:
        df = dict['DataFrame']
        lat_sum += df.mean(numeric_only=True)[dict['lat_field']] 
        long_sum += df.mean(numeric_only=True)[dict['long_field']]
    return [lat_sum/len(dict), long_sum/len(dict)]

def mapper2(df_dicts, link_df=None, bounds=None, no_text=False):
    '''
    Display a map of the Dataframes passed in.
    Based on https://medium.com/@bobhaffner/folium-markerclusters-and-fastmarkerclusters-1e03b01cb7b1

    Parameters
    ----------
    df_dicts : tuple
        Tuple of dictionaries containing the facilities to map.  They must have a latitude and 
        longitude field. The dictionaries should have these fields:
            - the DataFrame - 'DataFrame'
            - circle border color - 'marker_color'
            - circle interior color - 'marker_fill_color'
            - facility name - 'name_field' in the dataframe 
            - latitude field - 'lat_field'
            - longitude field - 'long_field'
            - info field - 'info_field'

    link_df : DataFrame
        An optional dataframe with two pair of latitude/longitude coordinates
        to draw lines between markers.
            - 'Latitude_left' 
            - 'Longitude_left'
            - 'Latitude_right'
            - 'Longitude_right'

    bounds : Dataframe
        A bounding rectangle--minx, miny, maxx, maxy.  Discard points outside.

    Returns
    -------
    folium.Map
    '''


    # Initialize the map
    m = folium.Map(
        location = _locate_map(df_dicts),
        min_zoom=2,
        max_bounds=True
    )

    # Create the Marker Cluster array
    #kwargs={"disableClusteringAtZoom": 10, "showCoverageOnHover": False}
    mc = FastMarkerCluster("")

    # Add a clickable marker for each facility
    for dict in df_dicts:
        df = dict['DataFrame'].drop_duplicates(subset=[dict['name_field'],
                                                       dict['lat_field'],
                                                       dict['long_field']])
        if df.empty:
            print("The DataFrame is empty. There is nothing to map.")
            break
        for index, row in df.iterrows():
            if ( bounds is not None ):
                if ( not check_bounds( row, bounds, df['lat_field'], df['long_field'] )):
                    continue
            mc.add_child(folium.CircleMarker(
                location = [row[dict['lat_field']], row[dict['long_field']]],
                popup = marker_text(row, no_text, dict['name_field'], dict['info_field']),
    
                radius = 8,
                color = dict['marker_color'],
                weight = 1,
                fill_color = dict['marker_fill_color'],
                fill_opacity= .4
            ))

    m.add_child(mc)
    
    bounds = m.get_bounds()
    m.fit_bounds(bounds)

    if link_df is not None:
        for index, row in link_df.iterrows():
            lat1 = row['Latitude_left']
            long1 = row['Longitude_left']
            lat2 = row['Latitude_right']
            long2 = row['Longitude_right']
            folium.PolyLine([[lat1, long1],
                            [lat2, long2]]).add_to(m)

    # Show the map
    return m
