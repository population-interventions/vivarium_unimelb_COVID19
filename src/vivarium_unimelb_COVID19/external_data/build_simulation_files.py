#!/usr/bin/env python

"""
This script generates the simulation definition files for each experiment.
"""

import jinja2

from pathlib import Path


def get_model_specification_template_file():
    here = Path(__file__).resolve()
    return here.parent / 'yaml_template.in'


def get_model_specification_BAU_template_file():
    here = Path(__file__).resolve()
    return here.parent / 'yaml_template_BAU.in'


def create_model_specifications(output_dir):
    """
    Construct the model specifications for the intervention simulations.
    """

    # The simulation populations.
    #populations = ['new_zealand_test']
    populations = ['australia','new_zealand','sweden']
    scenarios = ['flatten', 'elimination', 'suppress',
                 'elimination_asymp', 'flatten_asymp', 'suppress_asymp',
                 'elimination_verity', 'flatten_verity', 'suppress_verity',
                 'suppress_0point5inf', 'suppress_5inf', 'flatten_60inf',
                 'elimination_24m', 'flatten_24m', 'suppress_24m',
                 'elimination_36m', 'flatten_36m', 'suppress_36m',
                 'elimination_doubledr', 'flatten_doubledr', 'suppress_doubledr',
                 'elimination_halfifr', 'flatten_halfifr', 'suppress_halfifr']

    template_file = get_model_specification_template_file()
    BAU_template_file = get_model_specification_BAU_template_file()

    with template_file.open('r') as f:
        template_contents = f.read()

    template = jinja2.Template(template_contents,
                               trim_blocks=True,
                               lstrip_blocks=True)

    out_format = 'COVID19_{}_{}.yaml'


    for population in populations:
        for scenario in scenarios:
            out_file = output_dir / out_format.format(population, scenario)

            template_args = {
                'output_root': str(out_file.parent.parent),
                'basename': out_file.stem,
                'population': population,
                'scenario': scenario
            }
            out_content = template.render(template_args)
            with out_file.open('w') as f:
                f.write(out_content)

    #BAU
    with BAU_template_file.open('r') as f:
        template_contents = f.read()

    template = jinja2.Template(template_contents,
                               trim_blocks=True,
                               lstrip_blocks=True)

    out_format = 'COVID19_{}_BAU.yaml'


    for population in populations:
        out_file = output_dir / out_format.format(population)

        template_args = {
            'output_root': str(out_file.parent.parent),
            'basename': out_file.stem,
            'population': population
        }
        out_content = template.render(template_args)
        with out_file.open('w') as f:
            f.write(out_content)
