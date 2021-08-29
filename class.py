import ECHO_modules.utilities as utilities
import ECHO_modules.presets as presets
import geopandas as geopandas
import topojson as tp
import rtree
import json
import folium
from folium.plugins import FastMarkerCluster
import urllib
import pandas as pd

class Echo: 
  def __init__( self, units, unit_type, programs=[], intersection=False, intersecting_geo=None): 
    # Data parameters
    self.units = units # e.g. 52358
    self.unit_type = unit_type
    self.programs = programs # e.g. ["CWA Violations", "CAA Inspections"]. Optional.
    self.intersection = intersection
    self.intersecting_geo = intersecting_geo
    self.table_name = presets.spatial_tables[unit_type]["table_name"] # Spatial table name e.g. wbdhu8
    self.id_field = presets.spatial_tables[unit_type]["id_field"] # ID field in spatial database e.g. huc8
    self.geo_field = presets.region_field[unit_type]["field"] # Spatial ID Field in ECHO EXPORTER. Can this be None?

    # Style parameters
    self.style = {'this': {'fillColor': '#0099ff', 'color': '#182799', "weight": 1}, 'other': {'fillColor': 'orange', 'color': '#182799', "weight": 1}} # Can adjust map styling

    # Get Data
    self.spatial_data = self.get_spatial_data()
    self.selection = self.selector() # Selection for spatial units (do after intersection, before results)
    self.results = Echo.attributes(self.programs, self.unit_type, self.geo_field, self.selection, self.spatial_data, existing_facilities=None).results
    self.facilities = self.results["facilities"]

    # To Do
    # - fully comment

  # General data manipulation methods 
  def add(self, program):
    '''
    ## To add program data after initialization
    # program = "CWA Violations" e.g.
    # Currently getting facilities a second time....
    '''

    # Need to do a check first - don't run if already added....
    if program in self.results.keys():
      print("This data has already been added!")
    else:
      self.results[program] = Echo.attributes([program], self.unit_type, self.geo_field, self.selection, self.spatial_data, existing_facilities = self.facilities).results[program]
    
    return self.results[program]

  def program_check(self, program):
    '''
    Checks to see whether a program has actually been added yet if the user is trying to show a chart or map of that program.
    If the program data hasn't been added, this function points to `add`
    '''
    if program not in self.results.keys():
      self.add(program)
    else:
      return
      
  def aggregate_by_facility(self, program):
    '''
    Definition
    '''
    data = self.results[program]
    diff = None

    def differ(input, program):
      '''
      helper function to sort facilities in this program (input) from the full list of faciliities regulated under the program
      '''
      diff = list(
          set(self.facilities[presets.attribute_tables[program]["echo_type"]+"_IDS"]) - set(input[presets.attribute_tables[program]['idx_field']])
          ) 
      
      # get rid of NaNs - probably no program IDs
      diff = [x for x in diff if str(x) != 'nan']
      
      # ^ Not perfect given that some facilities have multiple NPDES_IDs
      # Below return the full ECHO_EXPORTER details for facilities without violations, penalties, or inspections
      diff = self.facilities.loc[self.facilities[presets.attribute_tables[program]["echo_type"]+"_IDS"].isin(diff)] 
      return diff

    if (program == "CWA Violations"): 
      year = data["YEARQTR"].astype("str").str[0:4:1]
      data["YEARQTR"] = year
      data["sum"] = data["NUME90Q"] + data["NUMCVDT"] + data['NUMSVCD'] + data["NUMPSCH"]
      data = data.groupby([presets.attribute_tables[program]['idx_field'], "FAC_NAME", "FAC_LAT", "FAC_LONG"]).sum()
      data = data.reset_index()
      data = data.loc[data["sum"] > 0] # only symbolize facilities with violations
      diff = differ(data, program)
      aggregator = "sum" # keep track of which field we use to aggregate data, which may differ from the preset

    # Penalties
    elif (program == "CAA Penalties" or program == "RCRA Penalties" or program == "CWA Penalties" ):
      data.rename( columns={ presets.attribute_tables[program]['date_field']: 'Date', presets.attribute_tables[program]['agg_col']: 'Amount'}, inplace=True )
      if ( program == "CWA Penalties" ):
        data['Amount'] = data['Amount'].fillna(0) + data['STATE_LOCAL_PENALTY_AMT'].fillna(0)
      data = data.groupby([presets.attribute_tables[program]['idx_field'], "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({'Amount':'sum'})
      data = data.reset_index()
      data = data.loc[data["Amount"] > 0] # only symbolize facilities with penalties
      diff = differ(data, program)
      aggregator = "Amount" # keep track of which field we use to aggregate data, which may differ from the preset

    # Air emissions

    # Inspections, violations
    else: 
      data = data.groupby([presets.attribute_tables[program]['idx_field'], "FAC_NAME", "FAC_LAT", "FAC_LONG"]).agg({presets.attribute_tables[program]['date_field']: 'count'})
      data['count'] = data[presets.attribute_tables[program]['date_field']]
      data = data.reset_index()
      data = data.loc[data["count"] > 0] # only symbolize facilities with X
      diff = differ(data, program)
      aggregator = "count" # ??? keep track of which field we use to aggregate data, which may differ from the preset
      
    if ( len(data) > 0 ):
      return {"data": data, "diff": diff, "aggregator": aggregator}
    else:
      print( "There is no data for this program and region after 2000." )

  def aggregate_by_year(self, program):
    '''
    # program should = an already added program e.g "CWA Violations"
    '''
    if ( self.results[program] is None ):
      print( "There is no data for {} to chart.".format( program ))
      return

    chart_title = program
    chart_title += ' - ' + self.geo_field
    #if ( self.state is not None ):
    #    chart_title += ' - ' + self.state
    #if ( self.region_value is not None ):
    #    chart_title += ' - ' + str( self.region_value )

    data = self.results[program]

    # Handle NPDES_QNCR_HISTORY because there are multiple counts we need to sum
    if (program == "CWA Violations"): 
      year = data["YEARQTR"].astype("str").str[0:4:1]
      data["YEARQTR"] = year
      # Remove fields not relevant to this graph.
      data = data.drop(columns=['FAC_LAT', 'FAC_LONG', 'FAC_ZIP', 
          'FAC_EPA_REGION', 'FAC_DERIVED_WBD', 'FAC_DERIVED_HUC', 'FAC_DERIVED_CD113',
          'FAC_PERCENT_MINORITY', 'FAC_POP_DEN']) #, 'index'
      data = data.groupby(pd.to_datetime(data['YEARQTR'], format="%Y", errors='coerce').dt.to_period("Y")).sum()
      data.index = data.index.strftime('%Y')
      data = data[ data.index > '2000' ]

    # These data sets use a FISCAL_YEAR field
    elif (program == "SDWA Public Water Systems" or program == "SDWA Violations" or
        program == "SDWA Serious Violators" or program == "SDWA Return to Compliance"):
      year = data["FISCAL_YEAR"].astype("str")
      data["FISCAL_YEAR"] = year
      data = data.groupby(pd.to_datetime(data['FISCAL_YEAR'], format="%Y",errors='coerce').dt.to_period("Y"))[['PWS_NAME']].count()
      data.index = data.index.strftime('%Y')
      data = data[ data.index > '2000' ]

    # Air emissions
    elif (program == "Combined Air Emissions" or program == "Greenhouse Gases" or program == "Toxic Releases"):
      data = data.groupby( 'REPORTING_YEAR' )[['ANNUAL_EMISSION']].sum() # This is combining things that shouldn't be combined!!!
        #ax.set_xlabel( 'Reporting Year' )
        #ax.set_ylabel( 'Pounds of Emissions')

    # Penalties
    elif (program == "CAA Penalties" or program == "RCRA Penalties" or program == "CWA Penalties" ):
      data.rename( columns={ presets.attribute_tables[program]['date_field']: 'Date', presets.attribute_tables[program]['agg_col']: 'Amount'}, inplace=True )
      if ( program == "CWA Penalties" ):
        data['Amount'] = data['Amount'].fillna(0) + data['STATE_LOCAL_PENALTY_AMT'].fillna(0)
      data = data.groupby( pd.to_datetime( data['Date'], format="%m/%d/%Y", errors='coerce')).agg({'Amount':'sum'})
      data = data.resample('Y').sum()
      data.index = data.index.strftime('%Y')
      data = data[ data.index >= '2001' ]
            
    elif (program == "2020 Discharge Monitoring" or program == "Effluent Violations"):
      # To distinguish potential violations from reported ones...
      #def labeler (row):
      #  if (row['RNC_DETECTION_CODE'] == "K") | (row['RNC_DETECTION_CODE'] == 'N'):
      #    return "Missing - Potential Violations/Exceedences"
      #  else:
      #    return "Reported"
      #data['alpha'] = data.apply (lambda row: labeler(row), axis=1)

      data['Date'] = pd.to_datetime( data['MONITORING_PERIOD_END_DATE'], format="%m/%d/%Y", errors='coerce')
      data = data.groupby(['Date', 'PARAMETER_DESC'])['Date'].count().unstack(['PARAMETER_DESC']).fillna(0) #, 'alpha'
      data = data.groupby([pd.Grouper(level='Date')]).sum() #, pd.Grouper(level='alpha')
      data = data.resample("Y").sum()
      data.index = data.index.strftime('%Y')
      data = data[ data.index >= '2001' ]
          
    # All other programs (inspections and violations)
    else:
      try:
        data = data.groupby(pd.to_datetime(data[presets.attribute_tables[program]['date_field']], 
          format=presets.attribute_tables[program]['date_format'], errors='coerce'))[[presets.attribute_tables[program]['date_field']]].count()
        data = data.resample("Y").sum()
        data.index = data.index.strftime('%Y')
        data = data[ data.index > '2000' ]

      except AttributeError:
        print( "There is no data for {} to chart.".format( program ))

    if ( len(data) > 0 ):
      return {"chart_data": data, "chart_title": chart_title}
    else:
      print( "There is no data for this program and region after 2000." )
  
  # Data display methods
  def show_data(self, program):
    '''
    Display the program data table
    '''

    self.program_check(program)

    display(self.results[program])

  def show_top_violators(self, program, count):
    #def get_top_violators( df_active, flag, state, cd, noncomp_field, action_field, num_fac=10 ):
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
    count
        The number of facilities to include in the returned Dataframe
    Returns
    -------
    Dataframe
        The top *count* of violators for the EPA program in the region
    Examples
    --------
    >>> zips = echo(['52358'], "Zip Codes")
    >>> zips.show_top_violators("CWA", 20 )
    '''
    df = self.facilities

    # Parameters and Lookups
    flags = {
        "CWA": {'flag': "NPDES_FLAG", 'noncomp_field': 'CWA_13QTRS_COMPL_HISTORY','action_field': 'CWA_FORMAL_ACTION_COUNT'},
        "CAA": {'flag': "AIR_FLAG", 'noncomp_field': 'CAA_3YR_COMPL_QTRS_HISTORY','action_field': 'CAA_FORMAL_ACTION_COUNT'},
        "RCRA": {'flag': "RCRA_FLAG", 'noncomp_field': 'RCRA_3YR_COMPL_QTRS_HISTORY','action_field': 'RCRA_FORMAL_ACTION_COUNT'}
    }
    noncomp_field = flags[program]['noncomp_field']
    action_field = flags[program]['action_field']
    num_fac = count
    
    df = df.loc[ df[flags[program]['flag']] == 'Y' ]
    if ( len( df ) == 0 ):
        return None

    noncomp = df[ noncomp_field ]
    noncomp_count = noncomp.str.count('S') + noncomp.str.count('V')
    df['noncomp_count'] = noncomp_count
    df = df[['FAC_NAME', 'noncomp_count', action_field, 'DFR_URL', 'FAC_LAT', 'FAC_LONG']]
    df = df.sort_values( by=['noncomp_count', action_field], ascending=False )
    df = df.head( num_fac )

    # Draw a horizontal bar chart of the top non-compliant facilities.
    import seaborn as sns
    from matplotlib import pyplot as plt

    sns.set(style='whitegrid')
    fig, ax = plt.subplots(figsize=(10,10))

    unit = df.index 
    values = df['noncomp_count'] 
    try:
        g = sns.barplot(values, unit, order=list(unit), orient="h") 
        g.set_title('{} facilities with the most non-compliant quarters'.format(program))
        ax.set_xlabel("Non-compliant quarters")
        ax.set_ylabel("Facility")
        ax.set_yticklabels(df["FAC_NAME"])
        return ( g )
    except TypeError as te:
        print( "TypeError: {}".format( str(te) ))
        return None

  def show_chart(self, program):
    '''
    # program should = an already added program e.g "CWA Violations"
    # could be a list?
    '''

    self.program_check(program)

    # Set up some default parameters for graphing
    from matplotlib import pyplot as plt
    from matplotlib import cycler
    colour = "#00C2AB" # The default colour for the barcharts
    colors = cycler('color', ['#4FBBA9', '#E56D13', '#D43A69','#25539f', '#88BB44', '#FFBBBB'])
    plt.rc('axes', facecolor='#E6E6E6', edgecolor='none', axisbelow=True, grid=True, prop_cycle=colors)
    plt.rc('grid', color='w', linestyle='solid')
    plt.rc('xtick', direction='out', color='gray')
    plt.rc('ytick', direction='out', color='gray')
    plt.rc('patch', edgecolor='#E6E6E6')
    plt.rc('lines', linewidth=2)
    font = {'family' : 'DejaVu Sans', 'weight' : 'normal', 'size' : 16}
    plt.rc('font', **font)
    plt.rc('legend', fancybox = True, framealpha=1, shadow=True, borderpad=1)

    results = self.aggregate_by_year(program)
    chart_data = results["chart_data"] 
    chart_title = results["chart_title"]
    if (program == "2020 Discharge Monitoring" or program == "Effluent Violations"): # STACKED BAR CHART
      ax = chart_data[list(chart_data.columns)].plot(kind='bar', stacked=True, figsize=(20,10), 
                                  alpha = 1, 
                                  fontsize=12, title = presets.attribute_tables[program]['units']) 
    else:
      ax = chart_data.plot(kind='bar', title = chart_title, figsize=(20, 10), fontsize=16)
    # additional parameters for labeling axes here...
    
    display(ax)

  def show_map(self):
    '''
    # show the map of just the units
    # create the map using a library called Folium (https://github.com/python-visualization/folium)
    '''
    map = folium.Map()  

    m = folium.GeoJson(
      self.spatial_data,
      name = self.table_name,
      style_function = lambda x: self.style['this']
    ).add_to(map)
    folium.GeoJsonTooltip(fields=[self.id_field.lower()]).add_to(m) # Add tooltip for identifying features

    # if there is an intersecting geography we also want to show...
    if self.intersection:
      z = folium.GeoJson(
        self.intersecting_geo,
        #name = "Zip Code",
        style_function = lambda x: self.style['other']
      ).add_to(map)
      #folium.GeoJsonTooltip(fields=["zcta5ce10"]).add_to(z)

    # compute boundaries so that the map automatically zooms in
    bounds = m.get_bounds()
    map.fit_bounds(bounds, padding=0)

    # display the map!
    display(map)

  def show_facility_map(self):
    '''
    # show the map of just the facilities
    '''
    df = self.facilities
    
    #print("show fac map") #Debugging

    # Initialize the map
    map = folium.Map(
      location = [df.mean()["FAC_LAT"], df.mean()["FAC_LONG"]]
    )

    m = folium.GeoJson(
      self.spatial_data,
      name = self.table_name,
      style_function = lambda x: self.style['this']
    ).add_to(map)

    # if there is an intersecting geography we also want to show...
    if self.intersection:
      z = folium.GeoJson(
        self.intersecting_geo,
        #name = "Zip Code",
        style_function = lambda x: self.style['other']
      ).add_to(map)

    # Create the Marker Cluster array
    #kwargs={"disableClusteringAtZoom": 10, "showCoverageOnHover": False}
    mc = FastMarkerCluster("")
 
    # Add a clickable marker for each facility
    for index, row in df.iterrows():
      mc.add_child(folium.CircleMarker(
        location = [row["FAC_LAT"], row["FAC_LONG"]],
        popup = self.marker_text(row), # Still getting errors here...
        radius = 8,
        color = "black",
        weight = 1,
        fill_color = "orange",
        fill_opacity= .4
      ))
    map.add_child(mc)

    bounds = map.get_bounds()
    map.fit_bounds(bounds)

    # Show the map
    display(map)

  def show_program_map(self, program, quartiles=False):
    '''
    Display a point symbol map of the data. A point symbol map represents 
    each facility as a point, with the size of the point scaled to the data value 
    (e.g. inspections, violations) proportionally or through quartiles.
    Parameters
    ----------
    df : Dataframe
      The facilities to map. They must have a FAC_LAT and FAC_LONG field.
    quartiles : Boolean
      False (default) returns a proportionally-scaled point symbol map, meaning
      that the radius of each point is directly scaled to the value (e.g. 13 violations)
      True returns a graduated point symbol map, meaning that the radius of each 
      point is a function of the splitting the Dataframe into quartiles. 
    Returns
    -------
    folium.Map
    '''

    self.program_check(program)

    results = self.aggregate_by_facility(program)
    map_data = results["data"] 
    other_fac = results["diff"] #Other facilities without penalties, violations, etc.
    aggregator = results["aggregator"]

    if ( map_data is not None ):

      map_of_facilities = folium.Map(
        location = [map_data.mean()["FAC_LAT"], map_data.mean()["FAC_LONG"]]
      )

      # Add basemap
      m = folium.GeoJson(
        self.spatial_data,
        name = self.table_name,
        style_function = lambda x: self.style['this']
      ).add_to(map_of_facilities)

      # if there is an intersecting geography we also want to show...
      if self.intersection:
        z = folium.GeoJson(
          self.intersecting_geo,
          #name = "Zip Code",
          style_function = lambda x: self.style['other']
        ).add_to(map_of_facilities)
      
      quartiles = True # To control sizing errors, set quartiles to true
      if quartiles == True:
        map_data['quantile'] = pd.qcut(map_data[aggregator], 4, labels=False, duplicates="drop")
        scale = {0: 6,1:10, 2: 14, 3: 20} # First quartile = 8 pt radius circles, etc.

      # Add a clickable marker for each facility
      for index, row in map_data.iterrows():
        if quartiles == True:
          r = scale[row["quantile"]]
        else:
          r = row[aggregator]
        
        map_of_facilities.add_child(folium.CircleMarker(
            location = [row["FAC_LAT"], row["FAC_LONG"]],
            popup = self.marker_text(row), #row["FAC_NAME"] + " - " + aggregator + ": " + str(row[aggregator]),
            radius = r * 3, # arbitrary scalar
            color = "black",
            weight = 1,
            fill_color = "orange",
            fill_opacity= .4
        ))
      
      if ( other_fac is not None ):
        for index, row in other_fac.iterrows():
          map_of_facilities.add_child(folium.CircleMarker(
            location = [row["FAC_LAT"], row["FAC_LONG"]],
            popup = self.marker_text(row),
            radius = 3,
            color = "black",
            weight = 1,
            fill_color = "black",
            fill_opacity= 1
          ))

      bounds = map_of_facilities.get_bounds()
      map_of_facilities.fit_bounds(bounds, padding=0)

      display(map_of_facilities)

    else:
      print( "There are no facilities to map." ) 

  # Basic utilities
  def marker_text(self, row):
    '''
    Create a string with information about the facility or program instance.
    Parameters
    ----------
    row : Series
        Expected to contain FAC_NAME and DFR_URL fields from ECHO_EXPORTER
    Returns
    -------
    str
        The text to attach to the marker
    '''

    text = ""
    if ( type( row['FAC_NAME'] == str )) :
        try:
            text = row["FAC_NAME"] + ' - '
        except TypeError:
            print( "A facility was found without a name. ")
        if 'DFR_URL' in row:
            text += " - <p><a href='"+row["DFR_URL"]
            text += "' target='_blank'>Link to ECHO detailed report</a></p>" 
    return text

  def selector(self):
    '''
    #build query
    '''
    selection = '('
    if (type(self.units) == list):
      for place in self.units:
          selection += '\''+str(place)+'\', '
      selection = selection[:-2] # remove trailing comma
      selection += ')'
    else:
      selection = '(\''+str(self.units)+'\')'
    return selection

  def get_spatial_data(self):
    '''
    return query(unit, unit_type)
    Can provide multiple places (e.g. multiple zip codes) 
    but at least one is required (can't query the whole database!)

    return spatial data set based on the intersection between one SDS and another 
    e.g. return watersheds based on what states they cross
    When intersection is set to true places should equal to another preset spatial
    preset (e.g. "HUC10 Watersheds")
    '''

    def sqlizer(query):
      '''
      takes a default sql and injects a query into it
      '''
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
      #print(sql) # Debugging
      url = 'http://portal.gss.stonybrook.edu/echoepa/index2.php?query=' 
      data_location = url + urllib.parse.quote_plus(sql) + '&pg'
      #print(data_location) # Debugging
      result = geopandas.read_file(data_location)
      return result

    selection = self.selector()

    units = self.units
    
    if self.intersection:
      # e.g. hucs = echo([14303,14207,14219], "HUC10 Watersheds", ["CWA Violations"], intersection=True, intersecting_geo="Zip Codes")
      # i.e. Get the HUC watersheds and their CWA violations that intersect with this zip code/s

      # Get intersecting geographies (watersheds)
      query = """
        SELECT this.* 
        FROM """ + self.table_name + """ AS this 
        JOIN """ + presets.spatial_tables[self.intersecting_geo]['table_name'] + """ AS other 
        ON other.""" + presets.spatial_tables[self.intersecting_geo]['id_field'] + """ IN """ + selection + """ 
        AND ST_Intersects(this.geom,other.geom) """
      result = sqlizer(query)

      # Get the original geo (zip codes)
      query = """
        SELECT * 
        FROM """ + presets.spatial_tables[self.intersecting_geo]['table_name'] + """
        WHERE """ + presets.spatial_tables[self.intersecting_geo]['id_field'] + """ IN """ + selection + ""
      self.intersecting_geo = sqlizer(query) #reset intersecting_geo to its spatial data
    
      #if we're doing an intersection we need to change the units after getting the
      # intersection results (e.g. we started with zip 14303, now we have the HUC8s)
      units = list(result[self.id_field])

    else:
      query = """
      SELECT * 
      FROM """ + self.table_name + """
      WHERE """ + self.id_field + """ IN """ + selection + ""
      result = sqlizer(query)
    
    if self.unit_type == "HUC10 Watersheds":
      units = [x[:-2] for x in units]
    if self.unit_type == "HUC12 Watersheds":
      units = [x[:-4] for x in units]
    self.units = ["04120104" if (x == "04270101") else x for x in units]

    #print("units:", self.units) #Debugging

    return result

  # Create attributes as a class since we may want multiple attributes (multiple
  # program data) for a single geography
  class attributes:
    def __init__(self, programs, unit_type, geo_field, selection, spatial_data, existing_facilities=None):
      self.programs = programs
      self.unit_type = unit_type
      self.geo_field = geo_field
      self.selection = selection
      self.spatial_data = spatial_data
      self.facilities = self.get_facility_data() if existing_facilities is None else existing_facilities  #value_when_true if condition else value_when_false #only run if not already added i.e. don't run under "add"
      self.program_data = {p:self.get_program_data(p) for p in self.programs}
      self.results = {"facilities": self.facilities, **self.program_data}
      
    def clip(self, input):
      '''
      #helper function to clip results to spatial boundaries
      #clip (in cases where )
      #convert program data to geodataframe
      '''
      #print("clipping", input) #Debugging

      r = geopandas.GeoDataFrame(input, geometry=geopandas.points_from_xy(input["FAC_LONG"], input["FAC_LAT"]), crs="EPSG:4326")  
      
      #de-index in order to clip
      r = r.reset_index() 
      
      # Clip facilities to just those within the selected area(s)
      r = geopandas.clip(r,self.spatial_data)

      return r

    def selector(self, facilities):
      '''
      #build query
      '''
      
      selection = '('
      if (type(facilities) == list):
        for place in facilities:
            selection += '\''+str(place)+'\', '
        selection = selection[:-2] # remove trailing comma
        selection += ')'
      else:
        selection = '(\''+str(facilities)+'\')'
      return selection
    
    # Two options for getting attribute data
    # Either get facilities from ECHO_EXPORTER based on a geography (initial condition)
    def get_facility_data(self):
      '''
      create and exectute a query based on the geographic unit type (e.g. zip code) and units of interest (e.g. 52358)
      '''

      # Should be able to merge the following three using self.geo_field
      if ( self.unit_type == 'States' ):
        sql = 'select * from "ECHO_EXPORTER" where "FAC_STATE" in {}' # Using 'in' for lists. 
        sql += ' and "FAC_ACTIVE_FLAG" = \'Y\''
        sql = sql.format( self.selection )
      elif (self.unit_type == 'Zip Codes'): 
        sql = 'select * from "ECHO_EXPORTER" where "FAC_ZIP" in {}'
        sql += ' and "FAC_ACTIVE_FLAG" = \'Y\''
        sql = sql.format( self.selection )
      elif (self.unit_type in ["HUC8 Watersheds", "HUC10 Watersheds", "HUC12 Watersheds"]):
        sql = 'select * from "ECHO_EXPORTER" where "' + self.geo_field + '" in {}'
        sql += ' and "FAC_ACTIVE_FLAG" = \'Y\''
        sql = sql.format( self.selection )

      # Will not currrently work - need to set up a way to handle inputs like (IA, 02)  
      elif ( self.unit_type == 'Congressional Districts'): 
        sql = 'select * from "ECHO_EXPORTER" where "FAC_STATE" in {}'
        sql += ' and "FAC_DERIVED_CD113" = {}'
        sql += ' and "FAC_ACTIVE_FLAG" = \'Y\''
        sql = sql.format( self.selection )
      elif ( self.unit_type == 'Counties' ):
        sql = 'select * from "ECHO_EXPORTER" where "FAC_STATE" in {}'
        sql += ' and "FAC_COUNTY" = {}'
        sql += ' and "FAC_ACTIVE_FLAG" = \'Y\''
        sql = sql.format( self.selection )
      
      #print(sql) #Debugging
      data = utilities.get_data(sql) # still relying on ECHO_Modules/DataSet.py global function

      #print("fac before clip: ", len(data.index)) #Debugging
      # Clip to geographic boundaries (especially for watersheds...)
      data = self.clip(data)
      #print("fac after clip: ", len(data.index)) #Debugging

      return data

    # Or, get program data facilities whose IDs have already been pulled 
    def get_program_data(self, program):
      '''
      # return query(program, clipping unit [spatial results])
      '''
      p = presets.attribute_tables[program] # Details about this program (e.g. index field)
      facs = [f for f in list(self.facilities[p["echo_type"]+"_IDS"]) if str(f) != 'nan']
      selection = facs
      print(selection, len(selection))
      
      # Deal with long URIs - too many facilities - here
      # Divide into batches of 50. Approach based on @shansen's def get_data_by_ee_ids()
      # https://github.com/edgi-govdata-archiving/ECHO_modules/blob/d14014ba864bf736f9887253012d96ffa2feccd8/DataSet.py#L183
      
      def batch(p, id_string, program_data):
        '''
        helper function for get_program_data to get data in batches
        '''
        sql = 'select * from "' + p["table_name"] + '" where "'+ p["idx_field"] + '" in ' + id_string + ''
        #print(sql) # Debugging
        try:
          r = utilities.get_data(sql)   
          if ( r is not None ):
            if ( program_data is None ):
              program_data = r
              return program_data
            else:
              program_data = pd.concat([ program_data, r ])
              return program_data
        except pd.errors.EmptyDataError:
          #print("There were no records found for some set of facilities.") # Debugging
          return program_data

      id_string = "" # Turn program (NPDES, e.g.) IDs into a string
      program_data = None # For storing program data
      
      pos = 0
      for pos,row in enumerate( selection ):
        id_string += "\'"
        id_string += str(row) # Need to handle integers?
        id_string += "\'"
        id_string +=  ","
        if ( pos % 50 == 0 ):
          id_string=id_string[:-1] # removes trailing comma
          id_string = "(" + id_string + ")"# add () for SQL format
          #print(id_string) # Debugging
          program_data = batch(p, id_string, program_data)
          id_string = ""
      
      # Capture data for remaining facilities:
      if ( pos % 50 != 0 ):
        id_string=id_string[:-1] # removes trailing comma
        id_string = "(" + id_string + ")"# add () for SQL format
        #print(id_string) # Debugging
        program_data = batch(p, id_string, program_data)
      
      # Report to the user
      if ( program_data is None ):
        print( "No program records were found." )
      else:
        print( "{} program records were found".format( str( len( program_data ))))        

      # Various adjustments
      if ( program == 'CAA Violations' ):
        program_data['Date'] = program_data['EARLIEST_FRV_DETERM_DATE'].fillna(program_data['HPV_DAYZERO_DATE'])   
      
      return program_data
