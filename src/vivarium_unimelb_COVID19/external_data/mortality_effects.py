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

class MortEffects:

    def __init__(self, data_dir, year_start, effect_name):
        data_file = '{}/{}_mortality_effects.csv'.format(data_dir,effect_name)
        df = get_dataframe(data_file)

        self._data = df


    def get_mort_effects(self):
        """Return the mortality scale for each age stratum."""
        return self._data

