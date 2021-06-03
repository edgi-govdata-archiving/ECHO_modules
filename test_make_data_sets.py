import make_data_sets
from make_data_sets import make_data_sets
data_sets = make_data_sets(exclude_list=['DMRs','2020 Discharge Monitoring'])
print( data_sets.keys() )
data_sets = make_data_sets(data_set_list=['DMRs','2020 Discharge Monitoring'])
print( data_sets.keys() )
data_sets = make_data_sets(data_set_list=['RCRA Violations','DMRs','2020 Discharge Monitoring'],
    exclude_list=['DMRs'])
print( data_sets.keys() )
