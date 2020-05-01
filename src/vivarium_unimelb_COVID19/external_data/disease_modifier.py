"""Build disease modifier data tables."""

import pandas as pd
import numpy as np
import pathlib

from datetime import datetime

#Includes draw 0
DRAW_NUM = 101

def get_dataframe(filename):
    data_file = filename
    data_path = str(pathlib.Path(data_file).resolve())
    df = pd.read_csv(data_path)

    return df

class Disease_modifier:

    def __init__(self, data_dir, year_start, modifier, disease_name):
        self.year_start = year_start
        modifier_data_file = '{}/diseases/{}_{}_pif.csv'.format(data_dir, disease_name, modifier)
        df = get_dataframe(modifier_data_file)

        self._data = df

    def get_disease_rate_scalar(self, scenario, rate_name):
        """Return the effects of a single rate for a single disease for each age stratum."""
        #df = self._data.loc[(self._data['scenario'] == scenario) &
        #                    (self._data['rate'] == rate_name)]
        df = self._data.loc[self._data['scenario'] == scenario]

        #Convert relative year columns to absolute years
        df = df.rename(columns={'time_start': 'year_start', 'time_end': 'year_end'})
        df['year_start'] += self.year_start
        df['year_end'] += self.year_start

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        cols = cols = index_cols + draw_cols

        return df[cols]

                


