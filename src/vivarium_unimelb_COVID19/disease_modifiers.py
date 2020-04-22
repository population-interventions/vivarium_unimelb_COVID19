"""
=================
Disease Modifiers
=================

This module contains tools for altering disease rates in the simulation.

"""
import numpy as np
import pandas as pd


class AcuteDiseaseModifier:
    """

    Parameters
    ----------
    modifer_name
        The name of the modifier.
    disease_name
        The name of the disease the modifier affects.
    """

    def __init__(self, disease_name, modifier_name):
        self.disease_name = disease_name
        self.modifier_name = modifier_name
        self._name = '{}_modifier_{}'.format(disease_name, modifier_name)
        
    @property
    def name(self):
        return self._name

    def setup(self, builder):
        """Load the morbidity and mortality modifier data."""
        mortality_mod_data = builder.data.load('acute_disease.{}.mortality_modifier_{}'.format(
                                                                    self.disease_name,
                                                                    self.modifier_name))
        self.mortality_modifier =  builder.lookup.build_table(mortality_mod_data, 
                                              key_columns=['sex'], 
                                              parameter_columns=['age','year'])
        
        disability_mod_data = builder.data.load('acute_disease.{}.disability_modifier_{}'.format(
                                                                    self.disease_name,
                                                                    self.modifier_name))
        self.disability_modifier =  builder.lookup.build_table(disability_mod_data, 
                                              key_columns=['sex'], 
                                              parameter_columns=['age','year'])

        self.register_excess_mortality_modifier(builder)
        self.register_disability_rate_modifier(builder)


    def register_excess_mortality_modifier(self, builder):
        rate_name = f'{self.disease_name}_intervention.excess_mortality'
        modifier = lambda ix, excess_mort: self.excess_mortality_adjustment(ix, excess_mort)
        builder.value.register_value_modifier(rate_name, modifier)


    def register_disability_rate_modifier(self, builder):
        rate_name = f'{self.disease_name}_intervention.yld_rate'
        modifier = lambda ix, yld_rate: self.yld_rate_adjustment(ix, yld_rate)
        builder.value.register_value_modifier(rate_name, modifier)


    def excess_mortality_adjustment(self, index, excess_mort):
        mortality_scalar = self.mortality_modifier(index)

        return excess_mort * mortality_scalar

    def yld_rate_adjustment(self, index, yld_rate):
        yld_scalar = self.disability_modifier(index)

        return yld_rate * yld_scalar


