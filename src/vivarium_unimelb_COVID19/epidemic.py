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
        self.scenario = builder.configuration.scenario

        self.load_infection_data(builder)
        self.load_fatality_data(builder)
        self.load_disability_data(builder)
        self.load_cost_data(builder)
        self.load_population_view(builder)
        self.register_mortality_modifier(builder)
        self.register_morbidity_modifier(builder)
        self.register_expenditure_modifier(builder)

        builder.event.register_listener('time_step__prepare',
                                        self.on_time_step_prepare)


    def load_infection_data(self, builder):
        infection_data = builder.data.load('{}.infection_prop.{}'.format(self.name, self.scenario))
        infection_table = builder.lookup.build_table(infection_data, 
                                                     key_columns=['sex'],
                                                     parameter_columns=['age', 'year'])

        self.infection_prop = builder.value.register_value_producer(f'{self.name}.infection_prop',
                                                                    source=infection_table)


    def load_fatality_data(self, builder):
        fatality_data = builder.data.load('{}.fatality_risk.{}'.format(self.name, self.scenario))
        fatality_table = builder.lookup.build_table(fatality_data, 
                                                    key_columns=['sex'],
                                                    parameter_columns=['age', 'year'])

        self.fatality_risk = builder.value.register_value_producer(f'{self.name}.fatality_risk',
                                                                   source=fatality_table)


    def load_disability_data(self, builder):
        disability_data = builder.data.load('{}.disability_risk.{}'.format(self.name, self.scenario))
        disability_table = builder.lookup.build_table(disability_data, 
                                                      key_columns=['sex'],
                                                      parameter_columns=['age', 'year'])

        self.disability_risk = builder.value.register_value_producer(f'{self.name}.disability_risk',
                                                                     source=disability_table)


    def load_cost_data(self, builder):
        cost_data = builder.data.load('{}.health_cost.{}'.format(self.name, self.scenario))
        cost_table = builder.lookup.build_table(cost_data, 
                                                key_columns=['sex'],
                                                parameter_columns=['age', 'year'])

        self.health_cost = builder.value.register_value_producer(f'{self.name}.health_cost',
                                                                     source=cost_table)                                                               


    def load_population_view(self, builder):
        required_pop_columns = ['age', 'sex', 'population', 'expenditure']
        self.new_pop_columns = [f'{self.name}_cost',
                                f'{self.name}_infected_num',
                                f'{self.name}_mort_risk',
                                f'{self.name}_disability_loss',
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
        disability_risk = self.disability_risk(idx)
        health_cost = self.health_cost(idx)

        pop_num = pop['population']
        infected_num = pop_num * infection_risk
        deaths = infected_num * fatality_risk
        disability_loss = disability_risk
        mort_risk = deaths/pop_num
        total_cost = health_cost

        pop[f'{self.name}_cost'] = total_cost
        pop[f'{self.name}_infected_num'] = infected_num
        pop[f'{self.name}_mort_risk'] = mort_risk
        pop[f'{self.name}_disability_loss'] = disability_loss
        pop[f'{self.name}_deaths'] = deaths
        pop[f'{self.name}_infection_risk'] = infection_risk
        pop[f'{self.name}_fatality_risk'] = fatality_risk

        self.population_view.update(pop)
        

    def register_mortality_modifier(self, builder):
        rate_name = 'mortality_rate'
        modifier = lambda ix, mort_rate: self.mortality_rate_adjustment(ix, mort_rate)
        builder.value.register_value_modifier(rate_name, modifier)


    def register_morbidity_modifier(self, builder):
        rate_name = 'yld_rate'
        modifier = lambda ix, yld_rate: self.yld_rate_adjustment(ix, yld_rate)
        builder.value.register_value_modifier(rate_name, modifier)

    
    def register_expenditure_modifier(self, builder):
        rate_name = 'health_costs'
        modifier = lambda ix, expenditure: self.expenditure_adjustment(ix, expenditure)
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

    
    def yld_rate_adjustment(self, index, yld_rate):
        pop = self.population_view.get(index)

        disability_loss = pop[f'{self.name}_disability_loss']
        #Scale disability loss for timestep to year
        disability_loss_scaled = disability_loss * self.years_per_timestep
        #Calculate excess yld
        yld_delta = disability_loss_scaled * (1 - yld_rate)
        new_rate = yld_rate + yld_delta

        return new_rate


    def expenditure_adjustment(self, index, expenditure):
        pop = self.population_view.get(index)

        #Scale?
        total_health_cost = pop[f'{self.name}_cost']

        return expenditure + total_health_cost