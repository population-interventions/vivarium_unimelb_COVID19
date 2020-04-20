"""Build epidemic data tables."""

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

class Epidemic:

    def __init__(self, data_dir, year_start):
        infection_data_file = '{}/COVID_infection.csv'.format(data_dir)
        infection_df = get_dataframe(infection_data_file)
        fatality_data_file = '{}/COVID_fatality.csv'.format(data_dir)
        fatality_df = get_dataframe(fatality_data_file)

        self._infection_data = infection_df
        self._fatality_data = fatality_df


    def get_infection_proportion(self):
        """Return the proportion of infected for each age stratum."""
        return self._infection_data

    def get_fatality_risk(self):
        """Return the fatality risk for each age stratum."""
        return self._fatality_data
