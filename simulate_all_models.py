
import os
from time import time

from vivarium.framework.engine import SimulationContext

model_specification_directory ='model_specifications/'

outfile = open('model_timings.csv', 'w')
outfile.write('Model name, Total time (minutes), Setup time, Initialise time, Run time, Finalise time'+'\n')

def run_timed_simulation(model_specification_file):
    simulation = SimulationContext(model_specification_file, None, None, None)

    setup_start_time = time()
    simulation.setup()
    setup_time = time() - setup_start_time

    initialize_start_time = time()
    simulation.initialize_simulants()
    initialize_time = time() - initialize_start_time

    run_start_time = time()
    simulation.run()
    run_time = time() - run_start_time

    finalize_start_time = time()
    simulation.finalize()
    finalize_time = time() - finalize_start_time

    return setup_time, initialize_time, run_time, finalize_time


for file in os.listdir(os.fsencode(model_specification_directory)):
    filename = os.fsdecode(file)
    start_time = time()
    model_specification_file = os.path.abspath(model_specification_directory+filename)
    setup_time, initialize_time, run_time, finalize_time = run_timed_simulation(model_specification_file)
    total_time = time() - start_time
    outfile.write(filename+','+str(total_time/60)+','+str(setup_time/60)+','+str(initialize_time/60)+
                  ','+str(run_time/60)+','+str(finalize_time/60)+'\n')
