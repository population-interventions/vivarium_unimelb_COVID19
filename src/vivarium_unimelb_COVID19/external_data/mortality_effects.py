"""Build mortality_effects data tables."""

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

class GDP:

    def __init__(self, data_dir, year_start):
        GDP_data_file = '{}/GDP_mortality_effects.csv'.format(data_dir)
        GDP_df = get_dataframe(GDP_data_file)

        self._GDP_data = GDP_df


    def get_GDP_effects(self):
        """Return the mortality delta for each age stratum."""
        return self._GDP_data

