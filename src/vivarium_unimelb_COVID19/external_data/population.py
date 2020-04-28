"""Build population data tables."""

import pandas as pd
import numpy as np
import pathlib

#Includes draw 0
DRAW_NUM = 2001

class Population:

    def __init__(self, data_dir, year_start):
        self.draw_columns = ['draw_{}'.format(i) for i in range(DRAW_NUM)]

        data_file_mort = '{}/base_population_mor.csv'.format(data_dir)
        data_path_mort = str(pathlib.Path(data_file_mort).resolve())

        data_file_dis = '{}/base_population_dis.csv'.format(data_dir)
        data_path_dis = str(pathlib.Path(data_file_dis).resolve())

        data_file_exp = '{}/base_population_exp.csv'.format(data_dir)
        data_path_exp = str(pathlib.Path(data_file_exp).resolve())

        df_mort = pd.read_csv(data_path_mort)
        df_mort = df_mort.rename(columns={'mortality per 1 rate': 'mortality_rate',
                                          'APC in all-cause mortality': 'mortality_apc',
                                          '5-year': 'population'})

        df_dis = pd.read_csv(data_path_dis)
        df_exp = pd.read_csv(data_path_exp)

        # Use identical populations in the BAU and intervention scenarios.
        df_mort['bau_population'] = df_mort['population'].values

        df_mort['year'] = year_start
        df_dis['year'] = year_start
        df_exp['year'] = year_start

        # Remove strata that have already reached the terminal age.
        df_mort = df_mort[~ (df_mort.age == df_mort['age'].max())]
        df_dis = df_dis[~ (df_dis.age == df_dis['age'].max())]
        df_exp = df_exp[~ (df_exp.age == df_exp['age'].max())]

        # Sort the rows.
        df_mort = df_mort.sort_values(by=['year', 'age', 'sex']).reset_index(drop=True)
        df_dis = df_dis.sort_values(by=['year', 'age', 'sex']).reset_index(drop=True)
        df_exp = df_exp.sort_values(by=['year', 'age', 'sex']).reset_index(drop=True)

        self.year_start = year_start
        self.year_end = year_start + df_mort['age'].max() - df_mort['age'].min()
        self._num_apc_years = 15
        
        #convert age to float for non-year timesteps
        df_mort['age'] = df_mort['age'].astype(float)
        df_dis['age'] = df_dis['age'].astype(float)
        df_exp['age'] = df_exp['age'].astype(float)

        self._mort_data = df_mort
        self._dis_data = df_dis
        self._exp_data = df_exp

    def years(self):
        """Return an iterator over the simulation period."""
        return range(self.year_start, self.year_end + 1)

    def get_population(self):
        """Return the initial population size for each stratum."""
        cols = ['year', 'age', 'sex', 'population']
        # Retain only those strata for whom the population size is defined.
        df = self._mort_data.loc[self._mort_data['population'].notna(), cols].copy()
        df = df.rename(columns = {'population': 'value'})
        return df


    def get_disability_rate(self):
        """Return the disability rate for each stratum."""
        df = self._dis_data[['age', 'sex'] + self.draw_columns]

        # Replace 'age' with age groups.
        df = df.rename(columns={'age': 'age_start'})
        df.insert(df.columns.get_loc('age_start') + 1,
                  'age_end',
                  df['age_start'] + 1)

        # These values apply at each year of the simulation, so we only need
        # to define a single bin.
        df.insert(0, 'year_start', self.year_start)
        df.insert(1, 'year_end', self.year_end + 1)

        df = df.sort_values(['year_start', 'age_start', 'sex'])
        df = df.reset_index(drop=True)

        return df

    def get_acmr_apc(self):
        """Return the annual percent change (APC) in mortality rate."""
        df = self._mort_data[['year', 'age', 'sex', 'mortality_apc']]
        df = df.rename(columns={'mortality_apc': 'value'})

        tables = []
        for year in self.years():
            df['year'] = year
            tables.append(df.copy())

        df = pd.concat(tables).sort_values(['year', 'age', 'sex'])
        df = df.reset_index(drop=True)

        return df

    def get_mortality_rate(self):
        """
        Return the mortality rate for each strata.

        :param df_base: The base population data.
        """
        # NOTE: see column IG in ErsatzInput.
        # - Each cohort has a separate APC (column FE)
        # - ACMR = BASE_ACMR * e^(APC * (year - 2011))
        df_apc = self.get_acmr_apc()
        df_acmr = self._mort_data[['age', 'sex'] + self.draw_columns]
        base_acmr = df_acmr[self.draw_columns].copy()

        # Replace 'age' with age groups.
        df_acmr = df_acmr.rename(columns={'age': 'age_start'})
        df_acmr.insert(df_acmr.columns.get_loc('age_start') + 1,
                       'age_end',
                       df_acmr['age_start'] + 1)

        # These values apply at each year of the simulation, so we only need
        # to define a single bin.
        df_acmr.insert(0, 'year_start', self.year_start -1)
        df_acmr.insert(1, 'year_end', self.year_start)

        tables = []
        tables.append(df_acmr.copy())
        for counter, year in enumerate(self.years()):
            if counter <= self._num_apc_years:
                year_apc = df_apc[df_apc.year == year]
                apc = year_apc['value'].values
                scale = np.exp(apc * (year - self.year_start))
                df_acmr.loc[:, self.draw_columns] = base_acmr * scale[:, None]
            else:
                # NOTE: use the same scale for this cohort as per the previous
                # year; shift by 2 because there are male and female cohorts.
                scale[2:] = scale[:-2]
                df_acmr.loc[:, self.draw_columns] = base_acmr * scale[:, None]
            df_acmr['year_start'] = year
            df_acmr['year_end'] = year + 1
            tables.append(df_acmr.copy())

        df = pd.concat(tables).sort_values(['year_start', 'age_start',
                                            'sex'])
        df = df.reset_index(drop=True)

        return df

    def get_expenditure(self):
        """Return the health expenditure for each stratum."""
        df = self._exp_data[['age', 'sex'] + self.draw_columns]

        # Replace 'age' with age groups.
        df = df.rename(columns={'age': 'age_start'})
        df.insert(df.columns.get_loc('age_start') + 1,
                  'age_end',
                  df['age_start'] + 1)

        # These values apply at each year of the simulation, so we only need
        # to define a single bin.
        df.insert(0, 'year_start', self.year_start)
        df.insert(1, 'year_end', self.year_end + 1)

        df = df.sort_values(['year_start', 'age_start', 'sex'])
        df = df.reset_index(drop=True)

        return df
