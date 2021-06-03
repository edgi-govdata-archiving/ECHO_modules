"""
Create a DataSet object for each of the programs we track.
Initialize each one with the information it needs to do its query
of the database.

Store the DataSet objects in a dictionary with keys being the
friendly names of the program, which will be used in selection
widgets.
"""

# In the following line, 'from DataSet' refers to the file DataSet.py
# while 'import DataSet' refers to the DataSet class within DataSet.py.

from ECHO_modules.DataSet import DataSet
from ECHO_modules.data_set_presets import get_attribute_tables


def make_data_sets( data_set_list = None, exclude_list = None ):
    """
    Create DataSet objects from a list of preset configurations. This takes a
    list of preset names and returns a dictionary where the keys are the preset
    names and values are the DataSet objects that were created with those
    presets. These presets are an important convenience since DataSet objects
    are complex with lots of options.

    For example, the preset "RCRA Violations" creates a DataSet from the
    ``RCRA_VIOLATIONS`` table, indexed by the ``ID_NUMBER`` column, with the
    date format ``%m/%d/%Y``, and so on.

    Parameters
    ----------
    data_set_list : list of str
        A list of preset configuration names for which to construct DataSets.
        e.g. ``["RCRA Violations", "CAA Enforcements"]``. If not set, this will
        construct and return a DataSet for every possible preset.

    exclude_list : list of str
        Configuration names to be excluded

    Returns
    -------
    dict
        A dictionary where the keys are the preset names and the values are
        the ``DataSet`` objects created from the presets.

    Examples
    --------
    >>> make_data_sets(["RCRA Violations", "CAA Enforcements"])
    {
        "RCRA Violations":  DataSet(name="RCRA Violations",
                                    idx_field="ID_NUMBER",
                                    base_table="RCRA_VIOLATIONS",
                                    # and so on
                                   ),
        "CAA Enforcements": DataSet(name="CAA Enforcements",
                                    idx_field="REGISTRY_ID",
                                    base_table="CASE_ENFORCEMENTS",
                                    # and so on
                                   ),
    }
    >>> make_data_sets(data_set_list=['RCRA Violations',
                                      'DMRs','2020 Discharge Monitoring'],
                       exclude_list=['DMRs'])

    """
    presets = get_attribute_tables()
    return {name: DataSet(name=name, **presets[name])
            for name in data_set_list or presets.keys()}
