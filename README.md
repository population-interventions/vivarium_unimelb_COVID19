Vivarium COVID19
=============================================

Research repository for the Vivarium COVID19 Australia NZ
project.

Installation
------------

To set up a new research environment, open up a terminal and run::

    $> conda create --name=vivarium_COVID19 python=3.6
    $> conda activate vivarium_COVID19
    (vivarium_COVID19) $> git clone https://github.com/population-interventions/vivarium_unimelb_COVID19
    (vivarium_COVID19) $> cd vivarium_unimelb_COVID19
    (vivarium_COVID19) $> pip install -e .


Make the data artifacts
------------
From the vivarium_unimelb_COVID19 folder, run::

    (vivarium_COVID19) $> make_artifacts minimal
    
Each scenario type has its own artifact. To change the scenario type, the files artifact.py, disease_modifier.py, epidemic.py must be changed. 
To specify the number of draws in the artifact (for multiple draw runs), the files disease_modifier.py, disease.py, epidemic.py, population.py must be changed.
(These processes have been improved in subsequent vivarium projects).


Make the model specification files
------------
From the vivarium_unimelb_COVID19 folder, run::

    (vivarium_COVID19) $> make_model_specifications
    
The model specification files (with suffix .yaml) will be containted in vivarium_unimelb_COVID19/model_specifications.


Run a single simulation
------------
From the vivarium_unimelb_COVID19 folder, run::

    (vivarium_COVID19) $> simulate run -v model_specifications/model_spec
    
where *model_spec* is a valid .yaml model specification file.
Results are stored in vivarium_unimelb_COVID19/results


Run multiple simulations and multiple draws
------------
From the vivarium_unimelb_COVID19 folder, run::

    (vivarium_COVID19) $> run_uncertainty_analysis -d draw_num -s process_num model_specifications/model_spec1 model_specifications/model_spec2
    
where *draw_num* is the number of draws (not including draw 0) and *thread_num* is the number of processors to use (does not work on Windows if process_num > 1). An arbirtrary number of model_spec files can be used here.


Package versions (via pip freeze)
------------
aiocontextvars==0.2.2
certifi==2020.12.5
click==7.1.2
colorama==0.4.4
contextvars==2.4
decorator==4.4.2
immutables==0.14
Jinja2==2.11.2
loguru==0.5.3
MarkupSafe==1.1.1
networkx==2.5
numexpr==2.7.1
numpy==1.15.4
pandas==0.24.2
python-dateutil==2.8.1
pytz==2020.5
PyYAML==5.3.1
risk-distributions==2.0.3
scipy==1.5.4
six==1.15.0
tables==3.3.0
vivarium==0.9.3
vivarium-public-health==0.10.4
-e git+https://github.com/population-interventions/vivarium_unimelb_COVID19.git@d10b4efc751907267d0298eb068b6d430c6f4fec#egg=vivarium_unimelb_COVID19
win32-setctime==1.0.3
wincertstore==0.2
