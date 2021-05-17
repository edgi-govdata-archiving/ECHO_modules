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
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual, Layout
from IPython.display import display

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
    url= 'http://portal.gss.stonybrook.edu/echoepa/?query=' #'http://apps.tlt.stonybrook.edu/echoepa/?query=' 
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


def show_region_type_widget():
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
        value='County',
        description='Region of interest:',
        disabled=False
    )
    display( select_region_widget )
    return select_region_widget


def show_state_widget():
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
    
    display( dropdown_state )
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
    
    if ( type != 'Zip Code' ):
        if ( state_widget is None ):
            print( "You must first choose a state." )
            return
        my_state = state_widget.value
    
    if ( type == 'Zip Code' ):
        region_widget = widgets.Text(
            value='98225',
            description='Zip Code:',
            disabled=False
        )
    elif ( type == 'County' ):
        df = pd.read_csv( 'ECHO_modules/state_counties.csv' )
        counties = df[df['FAC_STATE'] == my_state]['FAC_COUNTY']
        region_widget=widgets.Dropdown(
            options=fix_county_names( counties ),
            description='County:',
            disabled=False
        )
    elif ( type == 'Congressional District' ):
        df = pd.read_csv( 'ECHO_modules/state_cd.csv' )
        cds = df[df['FAC_STATE'] == my_state]['FAC_DERIVED_CD113']
        region_widget=widgets.Dropdown(
            options=cds.to_list(),
            description='District:',
            disabled=False
        )
    if ( region_widget is not None ):
        display( region_widget )
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
    display(data_set_widget)
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
    widget=widgets.Dropdown(
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
