import pandas as pd
import numpy as np
from ipywidgets import widgets
from ECHO_modules.get_data import get_echo_data
from IPython.display import display


def show_rsei_pick_region_widget( type, state_widget=None, multi=False ):
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
    
    if type in ('City', 'County'):
        if ( state_widget is None ):
            print( "You must first choose a state." )
            return
        my_state = state_widget.value
        if ( isinstance( my_state, tuple )):
            my_state = my_state[0]
    if type in ('Zip Code', 'City', 'County'):
        region_widget = widgets.Text(
            value='',
            description=f'{type}:',
            disabled=False
        )
    if region_widget is not None:
        display( region_widget )
    return region_widget

def _filter_years(df, year_column, years):
    start_year = 0
    end_year = 2500
    if years is not None:
        start_year = years[0]
        end_year = years[1]
        df = df[df[year_column].between(start_year, end_year)]
    return df

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
            sql = f'select {columns} from "{table}") = \'{state}\''
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

def get_submissions_by_facilities(facilities=None, columns='*', years=None, limit=None):
    '''
    Get the submissions associated with the given facilities

    Parameters
    ----------
    facilities : list
        The facilities to use to look for submissions
    columns : str
        The columns of the submissions table to include
    years : list
        A two-element list of the year range

    Returns
    -------
    Dataframe
        The submissions records returned from the database query
    '''

    table = "submissions_data_rsei_v2312"
    sql = f'select {columns} from "{table}"'
    if facilities is not None:
        facilities = tuple(facilities)
        sql += f' where "FacilityNumber" in {facilities}'
    if limit is not None:
        sql += f' limit {limit}'
    print(sql)
    
    try:
        df_active = get_echo_data(sql)
        if years is not None:
            df_active = _filter_years(df_active, 'SubmissionYear', years)
    except pd.errors.EmptyDataError:
        df_active = None
    return df_active

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