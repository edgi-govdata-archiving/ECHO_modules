from ECHO_modules_delta.make_data_sets import make_data_sets
from ECHO_modules_delta.utilities import mapper
from ECHO_modules_delta.get_data import get_echo_api_access_token

token = get_echo_api_access_token()

data_sets = make_data_sets([
    "RCRA Violations",
    "RCRA Inspections",
    "RCRA Penalties",
    "CAA Violations",
    "CAA Penalties",
    "CAA Inspections",
    "Combined Air Emissions",
    "Greenhouse Gas Emissions",
    "Toxic Releases",
    "CWA Violations",
    "CWA Inspections",
    "CWA Penalties",
])

sdwa_data_sets = make_data_sets([
    "SDWA Site Visits",
    "SDWA Enforcements",
    "SDWA Public Water Systems",
    "SDWA Violations",
    "SDWA Serious Violators"
])

def _run_test(program, region_type, region_value, state=None, years=None):
    program_results = program.store_results(region_type=region_type,
                                region_value=region_value, state=state,
                                years=years, api=True, token=token)
    program_data = None
    if ( program_results is not None ):
        program_data = program_results.dataframe.copy()
    else:
        print( "There is no data for this data set in this region.")
    print(f'Found {len(program_data)} program records.')
    print(f'Last query: {program.last_sql}')
    mapper(program_data)

region_type = 'County'
region_value = ['ADAMS', 'JEFFERSON']
state = 'CO'
years = [2013, 2023]

for name, program in data_sets.items():
    print(f'running test on {name}')
    _run_test(program=program, region_type=region_type, region_value=region_value, 
              state=state, years=years)
    
region_type = 'State'
state = 'NJ'
region_value = None

for name, program in sdwa_data_sets.items():
    print(f'running test on {name}')
    _run_test(program=program, region_type=region_type, region_value=region_value, 
              state=state, years=years)

program = data_sets['CWA Violations']
region_type = 'Zip Code'
years = [2010, 2023]
region_value = ['14201', '14202', '14203']

_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=None, years=years)

program = data_sets['Greenhouse Gas Emissions']
region_type = 'County'
state = 'IA'
years = [2010, 2023]
region_value = ['POLK']

_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=state, years=years)

program = data_sets['Toxic Releases']  
region_type = 'Neighborhood'
years = [2010, 2023]
region_value = ((-105.181732, 39.835959),
     (-105.04715, 39.847558),
     (-104.986725, 39.786379),
     (-105.060883, 39.628961),
     (-105.250397, 39.619441),
     (-105.26413, 39.746266))
_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=None, years=years)

region_type = 'County'
region_value = ['ADAMS', 'JEFFERSON']
state = 'CO'
years = [2013, 2023]

program = data_sets['CWA Violations']
region_type = 'Neighborhood'
years = [2010, 2023]
region_value = ((-95.983772, 41.2768), 
                (-95.898628, 41.295891), 
                (-95.927467, 41.270607), 
                (-95.919914, 41.238602), 
                (-95.956306, 41.230857), 
                (-95.998878, 41.244798))

_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=None, years=years)


program = data_sets['CAA Violations']
region_type = 'Neighborhood'
years = [2010, 2023]
region_value = ((-105.181732, 39.835959),
     (-105.04715, 39.847558),
     (-104.986725, 39.786379),
     (-105.060883, 39.628961),
     (-105.250397, 39.619441),
     (-105.26413, 39.746266))
_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=None, years=years)

program = data_sets['Combined Air Emissions']
years = [2010, 2023]
region_type = 'Neighborhood'
region_value = ((-105.181732, 39.835959),
     (-105.04715, 39.847558),
     (-104.986725, 39.786379),
     (-105.060883, 39.628961),
     (-105.250397, 39.619441),
     (-105.26413, 39.746266))
_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=None, years=years)

region_type = 'County'
state = 'NJ'
region_value = ['MONMOUTH', 'ESSEX']
_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=state, years=years)
