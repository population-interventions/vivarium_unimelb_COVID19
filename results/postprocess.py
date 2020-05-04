import pandas as pd

countries = ['australia', 'new_zealand', 'sweden']
scenarios = ['elimination', 'flatten', 'suppress']
draws = 100 #Not including expected values

output_file = 'COVID19_postprocess.csv'

sum_cols = [
            'sum_population', 'sum_bau_population', 
            'sum_prev_population', 'sum_bau_prev_population',
            'sum_acmr', 'sum_bau_acmr',	
            'sum_pr_death', 'sum_bau_pr_death',
            'sum_deaths', 'sum_bau_deaths',
            'sum_yld_rate', 'sum_bau_yld_rate',
            'sum_person_years', 'sum_bau_person_years',
            'sum_haly', 'sum_haly_disc',
            'sum_bau_haly', 'sum_bau_haly_disc',
            'sum_expenditure', 'sum_expenditure_disc',
            'sum_bau_expenditure', 'sum_bau_expenditure_disc',
            'sum_covid19_deaths'
            ]
cols = ['date'] + sum_cols + ['draw_', 'country','scenario']
output_df = pd.DataFrame(columns = cols)

for country in countries:
    for scenario in scenarios:
        #Expected vals
        input_file = '{}\COVID19_{}_{}_mm.csv'.format(country, country, scenario)
        print('Processing input:'+input_file)
        df = pd.read_csv(input_file)
        df = df.drop(columns='year_of_birth').set_index(['age','sex','date'])
        df = df.sum(level = 2)
        df.columns = sum_cols
        df.reset_index(inplace=True)
        df['draw_'] = ([0]*df.shape[0])
        df['country'] = ([country]*df.shape[0])
        df['scenario'] = ([scenario]*df.shape[0])
        output_df = pd.concat([output_df, df])

        #draws
        for draw in range(1, draws+1):
            input_file = '{}\COVID19_{}_{}_mm_{}.csv'.format(country, country, scenario, draw)
            print('Processing input:'+input_file)
            df = pd.read_csv(input_file)
            df = df.drop(columns='year_of_birth').set_index(['age','sex','date'])
            df = df.sum(level = 2)
            df.columns = sum_cols
            df.reset_index(inplace=True)
            df['draw_'] = ([draw]*df.shape[0])
            df['country'] = ([country]*df.shape[0])
            df['scenario'] = ([scenario]*df.shape[0])
            output_df = pd.concat([output_df, df])

print('Writing output...)
output_df.to_csv(output_file, index=False)
print('Done.')      

