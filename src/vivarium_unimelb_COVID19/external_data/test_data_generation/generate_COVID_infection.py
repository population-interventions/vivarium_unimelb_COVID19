import numpy as np
import pandas as pd 

from datetime import date, timedelta
from pathlib import Path

output_filename = 'COVID_infection.csv'
here = Path(__file__).resolve()
output_file = here.parent / output_filename

start_year = 2020
start_month = 1
start_day = 1

end_year = 2030
end_month = 12
end_day = 31

timestep = 30

start_date = date(year=start_year,
                  month=start_month,
                  day=start_day)

end_date = date(year=end_year,
                month=end_month,
                day=end_day)

age_bin_size = 5
age_bins = 22

total_infected_proportion = 0.6

#Assumes virus has a constant proportion for the first $constant_infection_months$ months
constant_infection_months = 6

constant_infection_proportion = total_infected_proportion/constant_infection_months

timesteps = ((end_date-start_date)/timestep).days

#output_columns = ['age_start', 'age_end', 'sex', 'date', 'value']
output_columns = ['age_start', 'age_end', 'sex', 'year_start', 'year_end', 'value']
infection_df = pd.DataFrame(columns=output_columns)

age_bin_starts = np.array([age_bin_size*i for i in range(age_bins)])

for age in age_bin_starts:
    cohort_df = pd.DataFrame(columns=output_columns)

    age_start = age*np.ones(timesteps*2)
    age_end = age_start + age_bin_size

    sex = ['female']*timesteps + ['male']*timesteps
    
    #date = np.array([start_date + timedelta(days=timestep*t) for t in range(timesteps)]*2)
    year_start = np.array([start_year + (timestep/365.25)*t for t in range(timesteps)]*2)
    year_end = np.concatenate((year_start[1:],np.array([year_start[-1] + (timestep/365.25)])), axis=None)
    
    value = np.array(([constant_infection_proportion]*constant_infection_months + [0]*(timesteps-constant_infection_months))*2)

    cohort_df['age_start'] = age_start
    cohort_df['age_end'] = age_end
    cohort_df['sex'] = sex
    #cohort_df['date'] = date
    cohort_df['year_start'] = year_start
    cohort_df['year_end'] = year_end
    cohort_df['value'] = value

    infection_df = infection_df.append(cohort_df)

infection_df.to_csv(output_file, index=False)


    