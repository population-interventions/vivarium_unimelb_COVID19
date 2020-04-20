import logging
from pathlib import Path

import click

from vivarium_unimelb_COVID19.external_data import assemble_artifacts, create_model_specifications

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

