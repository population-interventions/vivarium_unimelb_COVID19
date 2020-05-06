import datetime
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
from vivarium.framework.artifact import hdf
from vivarium.framework.artifact import Artifact

from vivarium_unimelb_COVID19.external_data.population import Population
from vivarium_unimelb_COVID19.external_data.epidemic import Epidemic
from vivarium_unimelb_COVID19.external_data.mortality_effects import MortEffects
from vivarium_unimelb_COVID19.external_data.disease import AcuteDisease
from vivarium_unimelb_COVID19.external_data.disease_modifier import Disease_modifier
from vivarium_unimelb_COVID19.external_data.uncertainty import Normal, LogNormal

#YEAR_START = 2011
BASE_LIFETABLE_YEAR_START = 2017
SIMULATION_YEAR_START = 2020
RANDOM_SEED = 49430

#POPULATIONS = ['new_zealand_test']
POPULATIONS = ['australia','new_zealand','sweden']
ACUTE_DISEASES = ['RTC', 'SelfHarm']
SCENARIOS = ['elimination', 'flatten', 'suppress']
#SCENARIOS = ['elimination_asymp', 'flatten_asymp', 'suppress_asymp']
#SCENARIOS = ['elimination_verity', 'flatten_verity', 'suppress_verity']
#SCENARIOS = ['suppress_2point5inf', 'suppress_5inf', 'flatten_60inf']


def check_for_bin_edges(df):
    """
    Check that lower (inclusive) and upper (exclusive) bounds for year and age
    are defined as table columns.
    """

    if 'age_start' in df.columns and 'year_start' in df.columns:
        return df
    else:
        raise ValueError('Table does not have bins')

def get_data_dir(population):
    here = Path(__file__).resolve()
    return here.parent / 'input_data' / population


def assemble_artifacts(num_draws, output_path: Path, seed: int = RANDOM_SEED):
    """
    Assemble the data artifacts required to simulate the various interventions.

    Parameters
    ----------
    num_draws
        The number of random draws to sample for each rate and quantity,
        for the uncertainty analysis.
    output_path
        The path to the artifact being assembled.
    seed
        The seed for the pseudo-random number generator used to generate the
        random samples.

    """
    prng = np.random.RandomState(seed=seed)
    logger = logging.getLogger(__name__)

    for population in POPULATIONS:
        data_dir = get_data_dir(population)

        # Instantiate components for the population.
        pop = Population(data_dir, BASE_LIFETABLE_YEAR_START)
        mort = MortEffects(data_dir, SIMULATION_YEAR_START, 'ExcessMort')
        epi = Epidemic(data_dir, SIMULATION_YEAR_START)

        # Now write all of the required tables:
        pop_artifact_fmt = '{}.hdf'.format(population)

        logger.info('{} Generating artifacts'.format(
            datetime.datetime.now().strftime("%H:%M:%S")))

        pop_artifact_file = output_path / pop_artifact_fmt


        # Initialise each artifact file.
        if pop_artifact_file.exists():
            pop_artifact_file.unlink()

        # Write the data tables to each artifact file.
        art = Artifact(str(pop_artifact_file))

        # Write the main population tables.
        logger.info('{} Writing population tables'.format(
            datetime.datetime.now().strftime("%H:%M:%S")))

        write_table(art, 'population.structure',
                        pop.get_population())
        write_table(art, 'cause.all_causes.mortality',
                        pop.get_mortality_rate())
        write_table(art, 'cause.all_causes.disability_rate',
                        pop.get_disability_rate())
        write_table(art, 'population.expenditure',
                        pop.get_expenditure())

        # Write the mortality effect tables.
        logger.info('{} Writing mortality effects tables'.format(
            datetime.datetime.now().strftime("%H:%M:%S")))

        write_table(art, 'mortality_effects.ExcessMort',
                        mort.get_mort_effects())

        # Write epidemic tables.
        logger.info('{} Writing epidemic tables'.format(
            datetime.datetime.now().strftime("%H:%M:%S")))

        for scenario in SCENARIOS:
            write_table(art, 'COVID19.infection_prop.{}'.format(scenario),
                        epi.get_infection_proportion(scenario))
        
            write_table(art, 'COVID19.fatality_risk.{}'.format(scenario),
                        epi.get_fatality_risk(scenario))

            write_table(art, 'COVID19.disability_risk.{}'.format(scenario),
                        epi.get_disability_risk(scenario))

            write_table(art, 'COVID19.health_cost.{}'.format(scenario),
                        epi.get_health_cost(scenario))       

        # Write the acute disease tables.
        for disease in ACUTE_DISEASES:
            logger.info('{} Writing tables for {}'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), disease))

            acdis = AcuteDisease(data_dir, disease, SIMULATION_YEAR_START)

            write_table(art, 'acute_disease.{}.mortality'.format(disease),
                        acdis.get_death_risk())
            
            write_table(art, 'acute_disease.{}.morbidity'.format(disease),
                        acdis.get_disability_risk())

        # Write disease modifier tables.
        logger.info('{} Writing disease modifier tables'.format(
                datetime.datetime.now().strftime("%H:%M:%S")))
        for disease in ACUTE_DISEASES:
            unempl = Disease_modifier(data_dir, SIMULATION_YEAR_START, 'unemployment', disease)
            for scenario in SCENARIOS:
                write_table(art, 'acute_disease.{}.mortality_modifier_unemployment_{}'.format(disease, scenario),
                                unempl.get_disease_rate_scalar(scenario, 'mortality'))

                write_table(art, 'acute_disease.{}.disability_modifier_unemployment_{}'.format(disease, scenario),
                                unempl.get_disease_rate_scalar(scenario, 'disability'))


        print(pop_artifact_file)


def write_table(artifact, path, data):
    """
    Write a data table to an artifact, after ensuring that it doesn't contain
    any NA values.

    :param artifact: The artifact object.
    :param path: The table path.
    :param data: The table data.
    """
    if np.any(data.isna()):
        msg = 'NA values in table {} for {}'.format(path, artifact.path)
        raise ValueError(msg)

    logger = logging.getLogger(__name__)
    logger.info('{} Writing table {} to {}'.format(
        datetime.datetime.now().strftime("%H:%M:%S"), path, artifact.path))

    #Add age,sex,year etc columns to multi index
    col_index_filters = ['year','age','sex', 'date', 'year_start','year_end','age_start','age_end', 'date_start', 'date_end']
    data.set_index([col_name for col_name in data.columns if col_name in col_index_filters], inplace =True)
    
    #Convert wide to long
    if ('value' not in data.columns) and ('draw_0' not in data.columns):
        data = (pd.melt(data.reset_index(), id_vars=data.index.names,var_name = 'measure')
                .set_index(data.index.names+['measure']))

    artifact.write(path, data)
