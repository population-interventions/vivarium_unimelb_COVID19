"""Build disease-specific data tables."""

import logging
import pandas as pd
import numpy as np
import pathlib


#Includes draw 0
DRAW_NUM = 2001

#from .uncertainty import sample_fixed_rate_from

def get_dataframe(filename):
    data_file = filename
    data_path = str(pathlib.Path(data_file).resolve())
    df = pd.read_csv(data_path)

    return df

class AcuteDisease:

    def __init__(self, data_dir, name, year_start):
        self._name = name

        disease_data_file = '{}/diseases/{}_disease_input.csv'.format(data_dir, name)
        df = get_dataframe(disease_data_file)

        self._year_start = year_start
        self._year_end = year_start + df['age'].max() - df['age'].min()

        # Replace 'age' with age groups.
        df = df.rename(columns={'age': 'age_start'})
        df.insert(df.columns.get_loc('age_start') + 1,
                       'age_end',
                       df['age_start'] + 1)

        df.insert(0, 'year_start', self._year_start)
        df.insert(1, 'year_end', self._year_end + 1)

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)] 
        self.cols = index_cols + draw_cols

        self._data = df

    def get_death_risk(self):
        df = self._data.loc[self._data['measure'] == 'Deaths']

        return df[self.cols]
        

    def get_disability_risk(self):
        df = self._data.loc[self._data['measure'] == 'YLDs']
        
        return df[self.cols]
   
