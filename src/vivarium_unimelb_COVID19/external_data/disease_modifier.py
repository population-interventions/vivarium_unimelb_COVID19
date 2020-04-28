"""Build disease modifier data tables."""

import pandas as pd
import numpy as np
import pathlib

from datetime import datetime

#from .uncertainty import sample_fixed_rate_from

def get_dataframe(filename):
    data_file = filename
    data_path = str(pathlib.Path(data_file).resolve())
    df = pd.read_csv(data_path)

    return df

class Disease_modifier:

    def __init__(self, data_dir, year_start, modifier):
        modifier_data_file = '{}/{}_effects.csv'.format(data_dir, modifier)
        df = get_dataframe(modifier_data_file)

        self._data = df


    def get_disease_mortality(self, disease_name):
        """Return the mortality effects for a single disease for each age stratum."""
        index_cols = ['age_start', 'age_end', 'sex', 'year_start', 'year_end']
        mortality_column = 'mortality_scalar'
        cols = index_cols + [mortality_column]

        df =  self._data.loc[self._data['disease'] == disease_name]
        df = df[cols].rename(columns={mortality_column: 'value'})

        return df

    def get_disease_disability(self, disease_name):
        """Return the disability effects for a single disease for each age stratum."""
        index_cols = ['age_start', 'age_end', 'sex', 'year_start', 'year_end']
        disability_column = 'disability_scalar'
        cols = index_cols + [disability_column]

        df =  self._data.loc[self._data['disease'] == disease_name]
        df = df[cols].rename(columns={disability_column: 'value'})

        return df

    def get_disease_rate_scalar(self, disease_name, rate_name):
        """Return the effects of a single rate for a single disease for each age stratum."""
        df = self._data.loc[(self._data['disease'] == disease_name) &
                            (self._data['rate'] == rate_name)]
        
        return df

                


