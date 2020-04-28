"""
=========
Observers
=========

This module contains tools for recording various outputs of interest in
multi-state lifetable simulations.

"""
import numpy as np
import pandas as pd

from datetime import datetime

def output_file(config, suffix, sep='_', ext='csv'):
    """
    Determine the output file name for an observer, based on the prefix
    defined in ``config.observer.output_prefix`` and the (optional)
    ``config.input_data.input_draw_number``.

    Parameters
    ----------
    config
        The builder configuration object.
    suffix
        The observer-specific suffix.
    sep
        The separator between prefix, suffix, and draw number.
    ext
        The output file extension.

    """
    if 'observer' not in config:
        raise ValueError('observer.output_prefix not defined')
    if 'output_prefix' not in config.observer:
        raise ValueError('observer.output_prefix not defined')
    prefix = config.observer.output_prefix
    if 'input_draw_number' in config.input_data:
        draw = config.input_data.input_draw_number
    else:
        draw = 0
    out_file = prefix + sep + suffix
    if draw > 0:
        out_file += '{}{}'.format(sep, draw)
    out_file += '.{}'.format(ext)
    return out_file


class MorbidityMortality:
    """
    This class records the all-cause morbidity and mortality rates for each
    cohort for each timestep of the simulation.

    Parameters
    ----------
    output_suffix
        The suffix for the CSV file in which to record the
        morbidity and mortality data.

    """

    def __init__(self, output_suffix='mm'):
        self.output_suffix = output_suffix

    @property
    def name(self):
        return 'morbidity_mortality_observer'

    def setup(self, builder):
        # Record the key columns from the core multi-state life table.
        columns = ['age', 'sex',
                   'population', 'bau_population',
                   'acmr', 'bau_acmr',
                   'pr_death', 'bau_pr_death',
                   'deaths', 'bau_deaths',
                   'yld_rate', 'bau_yld_rate',
                   'person_years', 'bau_person_years',
                   'HALY', 'bau_HALY',
                   'expenditure', 'bau_expenditure']
        self.population_view = builder.population.get_view(columns)
        self.clock = builder.time.clock()
        builder.event.register_listener('collect_metrics', self.on_collect_metrics)
        builder.event.register_listener('simulation_end', self.write_output)
        self.tables = []
        
        self.output_table_cols = ['sex', 'age', 'date',
                                  'population', 'bau_population',
                                  'prev_population', 'bau_prev_population',
                                  'acmr', 'bau_acmr',
                                  'pr_death', 'bau_pr_death',
                                  'deaths', 'bau_deaths',
                                  'yld_rate', 'bau_yld_rate',
                                  'person_years', 'bau_person_years',
                                  'HALY', 'bau_HALY',
                                  'expenditure', 'bau_expenditure']

        self.table_cols = self.output_table_cols + ['year']

        self.output_file = output_file(builder.configuration,
                                       self.output_suffix)

    def on_collect_metrics(self, event):
        pop = self.population_view.get(event.index)
        if len(pop.index) == 0:
            # No tracked population remains.
            return
 
        pop['year'] = self.clock().year
        #pop['month'] = self.clock().month
        #pop['day'] = self.clock().day
        pop['date'] = self.clock().date()
        # Record the population size prior to the deaths.
        pop['prev_population'] = pop['population'] + pop['deaths']
        pop['bau_prev_population'] = pop['bau_population'] + pop['bau_deaths']
        self.tables.append(pop[self.table_cols])

    def calculate_LE(self, table, py_col, denom_col):
        """Calculate the life expectancy for each cohort at each time-step.

        Parameters
        ----------
        table
            The population life table.
        py_col
            The name of the person-years column.
        denom_col
            The name of the population denominator column.

        Returns
        -------
            The life expectancy for each table row, represented as a
            pandas.Series object.

        """
        # Group the person-years by cohort.
        group_cols = ['year_of_birth', 'sex']
        subset_cols = group_cols + [py_col]
        grouped = table.loc[:, subset_cols].groupby(by=group_cols)[py_col]
        # Calculate the reverse-cumulative sums of the adjusted person-years
        # (i.e., the present and future person-years) by:
        #   (a) reversing the adjusted person-years values in each cohort;
        #   (b) calculating the cumulative sums in each cohort; and
        #   (c) restoring the original order.
        cumsum = grouped.apply(lambda x: pd.Series(x[::-1].cumsum()).iloc[::-1])
        return cumsum / table[denom_col]

    def write_output(self, event):
        data = pd.concat(self.tables, ignore_index=True)
        data['age'] = data['age'].apply(np.floor)
        data['year_of_birth'] = data['year'] - data['age']
        #data['year_of_birth'] = data['year_of_birth'].apply(np.ceil)
        # Sort the table by cohort (i.e., generation and sex), and then by
        # calendar year, so that results are output in the same order as in
        # the spreadsheet models.
        data = data.sort_values(by=['year_of_birth', 'sex', 'date'], axis=0)
        data = data.reset_index(drop=True)
        # Re-order the table columns.
        cols = ['year_of_birth'] + self.output_table_cols
        data = data[cols]
        # Calculate life expectancy and HALE for the BAU and intervention,
        # with respect to the initial population, not the survivors.
        data['LE'] = self.calculate_LE(data, 'person_years', 'prev_population')
        data['bau_LE'] = self.calculate_LE(data, 'bau_person_years',
                                           'bau_prev_population')
        data['HALE'] = self.calculate_LE(data, 'HALY', 'prev_population')
        data['bau_HALE'] = self.calculate_LE(data, 'bau_HALY',
                                           'bau_prev_population')
        data.to_csv(self.output_file, index=False)

class EpidemicMortality:
    """
    This class records both the deaths due to epidemic and the all-cause 
    mortality rates for eachn cohort for each timestep of the simulation.

    Parameters
    ----------
    output_suffix
        The suffix for the CSV file in which to record the
        morbidity and mortality data.

    """

    def __init__(self, name, output_suffix='em'):
        self._name = name
        self.output_suffix = output_suffix

    @property
    def name(self):
        return f'{self._name}_epidemic_mort_observer'

    def setup(self, builder):
        # Record the key columns from the core multi-state life table.
        columns = ['age', 'sex',
                   'population', 'bau_population',
                   'acmr', 'bau_acmr',
                   'pr_death', 'bau_pr_death',
                   'deaths', 'bau_deaths',
                   f'{self._name}_infection_risk',
                   f'{self._name}_fatality_risk',
                   f'{self._name}_deaths',
                   f'{self._name}_mort_risk']

        self.population_view = builder.population.get_view(columns)
        self.clock = builder.time.clock()
        builder.event.register_listener('collect_metrics', self.on_collect_metrics)
        builder.event.register_listener('simulation_end', self.write_output)
        self.tables = []
        
        self.output_table_cols = ['sex', 'age', 'date',
                                  'prev_population', 'bau_prev_population',
                                  'population', 'bau_population',
                                  'acmr', 'bau_acmr',
                                  'pr_death', 'bau_pr_death',
                                  'deaths', 'bau_deaths',
                                  f'{self._name}_infection_risk',
                                  f'{self._name}_fatality_risk',
                                  f'{self._name}_deaths',
                                  f'{self._name}_mort_risk']

        self.table_cols = self.output_table_cols + ['year']

        self.output_file = output_file(builder.configuration,
                                       self.output_suffix)

    def on_collect_metrics(self, event):
        pop = self.population_view.get(event.index)
        if len(pop.index) == 0:
            # No tracked population remains.
            return
 
        pop['year'] = self.clock().year
        pop['date'] = self.clock().date()
        # Record the population size prior to the deaths.
        pop['prev_population'] = pop['population'] + pop['deaths']
        pop['bau_prev_population'] = pop['bau_population'] + pop['bau_deaths']
        self.tables.append(pop[self.table_cols])

    def write_output(self, event):
        data = pd.concat(self.tables, ignore_index=True)
        data['age'] = data['age'].apply(np.floor)
        data['year_of_birth'] = data['year'] - data['age']
        #data['year_of_birth'] = data['year_of_birth'].apply(np.ceil)
        # Sort the table by cohort (i.e., generation and sex), and then by
        # calendar year, so that results are output in the same order as in
        # the spreadsheet models.
        data = data.sort_values(by=['year_of_birth', 'sex', 'date'], axis=0)
        data = data.reset_index(drop=True)
        # Re-order the table columns.
        cols = ['year_of_birth'] + self.output_table_cols
        data = data[cols]

        data.to_csv(self.output_file, index=False)