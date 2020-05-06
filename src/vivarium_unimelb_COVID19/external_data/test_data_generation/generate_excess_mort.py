import numpy as np
import pandas as pd 

from datetime import date, timedelta
from pathlib import Path

output_filename = 'ExcessMort_mortality_effects.csv'
here = Path(__file__).resolve()
output_file = here.parent / output_filename

start_year = 2020
start_month = 1
start_day = 1

end_year = 2050
end_month = 1
end_day = 1

timestep = 30

start_date = date(year=start_year,
                  month=start_month,
                  day=start_day)

end_date = date(year=end_year,
                month=end_month,
                day=end_day)

age_bin_size = 5
age_bins = 22

mort_effect_val = 1.1

effect_start_timestep = 3
effect_end_timestep = 8

timesteps = ((end_date-start_date)/timestep).days

output_columns = ['age_start', 'age_end', 'sex', 'year_start', 'year_end', 'value']
df = pd.DataFrame(columns=output_columns)

age_bin_starts = np.array([age_bin_size*i for i in range(age_bins)])

for age in age_bin_starts:
    cohort_df = pd.DataFrame(columns=output_columns)

    age_start = age*np.ones(6)
    age_end = age_start + age_bin_size

    sex = ['female']*3 + ['male']*3
    
    year_start_col = [start_year, 
                      start_year + (timestep/365.25)*(effect_start_timestep - 1),
                      start_year + (timestep/365.25)*(effect_end_timestep)] *2

    year_end_col = [start_year + (timestep/365.25)*(effect_start_timestep - 1), 
                    start_year + (timestep/365.25)*(effect_end_timestep),
                    end_year] *2 

    year_start = np.array(year_start_col)
    year_end = np.array(year_end_col)
    
    value = np.array([1, mort_effect_val, 1] * 2)

    cohort_df['age_start'] = age_start
    cohort_df['age_end'] = age_end
    cohort_df['sex'] = sex
    cohort_df['year_start'] = year_start
    cohort_df['year_end'] = year_end
    cohort_df['value'] = value
    df = df.append(cohort_df)

df.to_csv(output_file, index=False)


    