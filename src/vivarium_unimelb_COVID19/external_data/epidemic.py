"""Build epidemic data tables."""

import pandas as pd
import numpy as np
import pathlib

from datetime import datetime

#Includes draw 0
DRAW_NUM = 101

#from .uncertainty import sample_fixed_rate_from

def get_dataframe(filename):
    data_file = filename
    data_path = str(pathlib.Path(data_file).resolve())
    df = pd.read_csv(data_path)

    return df

class Epidemic:

    def __init__(self, data_dir, year_start):
        self.year_start = year_start
        #infection_data_file = '{}/COVID_infection.csv'.format(data_dir)
        infection_data_file = '{}/percent_infected.csv'.format(data_dir)
        infection_df = get_dataframe(infection_data_file)
        #fatality_data_file = '{}/COVID_fatality.csv'.format(data_dir)
        #fatality_data_file = '{}/infection_fatality.csv'.format(data_dir)

        fatality_data_file = '{}/dead_table.csv'.format(data_dir)
        fatality_df = get_dataframe(fatality_data_file)

        disability_data_file = '{}/dr_table.csv'.format(data_dir)
        disability_df = get_dataframe(fatality_data_file)

        cost_data_file = '{}/popcost_table.csv'.format(data_dir)
        cost_df = get_dataframe(cost_data_file)

        self._infection_data = infection_df
        self._fatality_data = fatality_df
        self._disability_data = disability_df
        self._cost_data = cost_df


    def get_infection_proportion(self, scenario):
        """Return the proportion of infected for each age stratum."""

        df = self._infection_data.loc[self._infection_data['scenario'] == scenario]

        #Convert relative year columns to absolute years
        df = df.rename(columns={'time_start': 'year_start', 'time_end': 'year_end'})
        df['year_start'] += self.year_start
        df['year_end'] += self.year_start

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        cols = cols = index_cols + draw_cols

        return df[cols]


    def get_fatality_risk(self, scenario):
        """Return the fatality risk for each age stratum."""

        df = self._fatality_data.loc[self._fatality_data['scenario'] == scenario]

        #Convert relative year columns to absolute years
        df = df.rename(columns={'time_start': 'year_start', 'time_end': 'year_end'})
        df['year_start'] += self.year_start
        df['year_end'] += self.year_start

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        cols = cols = index_cols + draw_cols

        return df[cols]


    def get_disability_risk(self, scenario):
        """Return the disability risk for each age stratum."""

        df = self._disability_data.loc[self._disability_data['scenario'] == scenario]

        #Convert relative year columns to absolute years
        df = df.rename(columns={'time_start': 'year_start', 'time_end': 'year_end'})
        df['year_start'] += self.year_start
        df['year_end'] += self.year_start

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        cols = cols = index_cols + draw_cols

        return df[cols]


    def get_health_cost(self, scenario):
        """Return the health cost due to epidemic for each age stratum."""

        df = self._cost_data.loc[self._cost_data['scenario'] == scenario]

        #Convert relative year columns to absolute years
        df = df.rename(columns={'time_start': 'year_start', 'time_end': 'year_end'})
        df['year_start'] += self.year_start
        df['year_end'] += self.year_start

        index_cols = ['age_start', 'age_end', 'year_start', 'year_end', 'sex']
        draw_cols = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        cols = cols = index_cols + draw_cols

        return df[cols]
