import logging
from pathlib import Path

import click

from vivarium_unimelb_COVID19.external_data import assemble_artifacts, create_model_specifications
from vivarium_unimelb_COVID19.external_data import run_many
@click.command()
@click.argument('scenario', type=click.Choice(['minimal', 'uncertainty']))
def make_artifacts(scenario):
    """Generate artifacts for the intervention simulations."""
    logging.basicConfig(level=logging.INFO)

    output_path = Path('.').resolve() / 'artifacts'
    output_path.mkdir(exist_ok=True)
    draws = 0 if scenario == 'minimal' else 2000

    logging.info(f'Generating artifact for scenario {scenario} with {draws} '
                 f'draws at {str(output_path)}')

    assemble_artifacts(draws, output_path)


@click.command()
def make_model_specifications():
    """Generate model specifications for the intervention simulations."""
    logging.basicConfig(level=logging.INFO)

    output_path = Path('.').resolve() / 'model_specifications'
    output_path.mkdir(exist_ok=True)

    logging.info(f'Generating model_specifications at {str(output_path)}')

    create_model_specifications(output_path)

@click.command()
@click.option('-d', '--draws', default=5, metavar='NUM',
              help='The number of draws for which to run simulations')
@click.option('-s', '--spawn', default=1, metavar='NUM',
              help='The number of simulations to run in parallel')
@click.argument('spec_files', type=click.Path(exists=True), nargs=-1)
def run_uncertainty_analysis(draws, spawn, spec_files):
    """
    Run MSLT tobacco intervention simulations for multiple value draws.

    You can provide any number of model specification files.
    """
    logging.basicConfig(level=logging.INFO)
    num_draws = draws
    num_procs = spawn

    run_many(spec_files, num_draws, num_procs)