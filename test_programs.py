from ECHO_modules.make_data_sets import make_data_sets
from ECHO_modules.utilities import mapper
from ECHO_modules.get_data import get_echo_api_access_token
import time

#token = get_echo_api_access_token()

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
    "CWA Violations", # Currently won't work for Neighborhoods or ID lists
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
    time.sleep(5) # Slow down requests
    try:
        program_results = program.store_results(region_type=region_type,
                                region_value=region_value, state=state,
                                years=years)
        program_data = None
        if ( program_results is not None ):
            program_data = program_results.dataframe.copy()
        else:
            print( "There is no data for this data set in this region.")
        print(f'Found {len(program_data)} program records.')
        print(f'Last query: {program.last_sql}')
        mapper(program_data)
    except:
        print(f'There was an error running the test for {program.name} in {region_value}')

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

region_type = 'County'
state = 'NJ'
region_value = ['MONMOUTH', 'ESSEX']
_run_test(program=program, region_type=region_type, region_value=region_value, 
          state=state, years=years)

bbox = (
    (-105.00602649894498, 39.83706322053561),
    (-105.00602649894498, 39.76807173117473),
    (-104.88480258486722, 39.76807173117473),
    (-104.88480258486722, 39.83706322053561),
    (-105.00602649894498, 39.83706322053561)
    )
for p in [#data_sets['CWA Violations'],
        data_sets['Toxic Releases'], 
        data_sets['CAA Violations'], 
        data_sets['Combined Air Emissions']
        ]:
    region_type = 'Neighborhood'
    years = [2010, 2023]
    region_value = bbox
    _run_test(program=p, region_type=region_type, region_value=region_value, 
            state=None, years=years)

# API false shouldn't work without local copy of schema and data
data_sets = make_data_sets([
    "CAA Violations",
    "CAA Penalties",
    "CAA Inspections",
], api=False) 

region_type = 'County'
region_value = ['ADAMS', 'JEFFERSON']
state = 'CO'
years = [2013, 2023]

for name, program in data_sets.items():
    print(f'running test on {name}')
    _run_test(program=program, region_type=region_type, region_value=region_value, 
            state=None, years=years)
    
