import make_data_sets
import utilities
from make_data_sets import make_data_sets
data_sets = make_data_sets()
program = data_sets['CWA Violations']
regions_selected = [4,5]
program_results = program.store_results('Congressional District',regions_selected,'WA')

