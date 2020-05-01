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
    scenarios = ['flatten', 'elimination', 'suppress']

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
