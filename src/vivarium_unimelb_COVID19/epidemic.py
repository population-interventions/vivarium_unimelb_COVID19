"""
========
Epidemic
========

This module contains tools for modelling the all-cause mortality and yld effects 
due to an epidemic.

"""

import numpy as np
import pandas as pd 

class Epidemic:
    """
    This component models the mortality and disability effects of an epidemic
    based on input fatality, disability and infection proportions for each cohort
    per timestep.
    
    """

    def __init__(self, name):
        self._name = name
        
    @property
    def name(self):
        return self._name

    def setup(self, builder):
        self.years_per_timestep = builder.configuration.time.step_size/365

        self.load_infection_data(builder)
        self.load_fatality_data(builder)
        self.load_population_view(builder)
        self.register_mortality_modifier(builder)

        builder.event.register_listener('time_step__prepare',
                                        self.on_time_step_prepare)


    def load_infection_data(self, builder):
        infection_data = builder.data.load(f'{self.name}.infection_prop')
        infection_table = builder.lookup.build_table(infection_data, 
                                                     key_columns=['sex'],
                                                     parameter_columns=['age','year'])

        self.infection_prop = builder.value.register_value_producer(f'{self.name}.infection_prop',
                                                                    source=infection_table)


    def load_fatality_data(self, builder):
        estimate_name = builder.configuration.epidemic.fatality.estimate
        fatality_data = builder.data.load('{}.fatality_risk.{}'.format(self.name, estimate_name))
        fatality_table = builder.lookup.build_table(fatality_data, 
                                                    key_columns=['sex'],
                                                    parameter_columns=['age'])

        self.fatality_risk = builder.value.register_value_producer(f'{self.name}.fatality_risk',
                                                                   source=fatality_table)


    def load_population_view(self, builder):
        required_pop_columns = ['age', 'sex', 'population']
        self.new_pop_columns = [f'{self.name}_mort_risk',
                                f'{self.name}_deaths',
                                f'{self.name}_infection_risk',
                                f'{self.name}_fatality_risk',                        
                               ]
        view_columns = required_pop_columns + self.new_pop_columns

        self.population_view = builder.population.get_view(view_columns)

        builder.population.initializes_simulants(self.on_initialize_simulants,
                                                 creates_columns=self.new_pop_columns,
                                                 requires_columns=required_pop_columns)


    def on_initialize_simulants(self, pop_data):
        pop = pd.DataFrame({}, index=pop_data.index)
        for column in self.new_pop_columns:
            pop[column] = 0.0

        self.population_view.update(pop)


    def on_time_step_prepare(self, event):
        """Calculate deaths from epidemic during current timestep and calculate
        the mortality risk.
        """
        pop = self.population_view.get(event.index)
        if pop.empty:
            return

        idx = pop.index
        infection_risk = self.infection_prop(idx)
        fatality_risk = self.fatality_risk(idx)

        pop_num = pop['population']
        infected_num = pop_num * infection_risk
        deaths = infected_num * fatality_risk
 
        pop[f'{self.name}_mort_risk'] = deaths/pop_num
        pop[f'{self.name}_deaths'] = deaths
        pop[f'{self.name}_infection_risk'] = infection_risk
        pop[f'{self.name}_fatality_risk'] = fatality_risk

        self.population_view.update(pop)
        

    def register_mortality_modifier(self, builder):
        rate_name = 'mortality_rate'
        modifier = lambda ix, mort_rate: self.mortality_rate_adjustment(ix, mort_rate)
        builder.value.register_value_modifier(rate_name, modifier)


    def mortality_rate_adjustment(self, index, mort_rate):
        pop = self.population_view.get(index)

        #Scale mort_rate from annual to timestep
        old_rate = mort_rate * self.years_per_timestep
        #Convert rate to risk
        old_mort_risk = 1 - np.exp(-old_rate)
        #Calculate excess mortality risk due to epidemic
        delta_mort_risk = pop[f'{self.name}_mort_risk'] * (1-old_mort_risk)
        #Add epidemic mortality risk
        new_mort_risk = old_mort_risk + delta_mort_risk
        #Convert risk to rate
        new_rate = np.log(1 / (1 - new_mort_risk))
        #Scale new_rate from timestep to annual
        new_rate = new_rate / self.years_per_timestep

        return new_rate