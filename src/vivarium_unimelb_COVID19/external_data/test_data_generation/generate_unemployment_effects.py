import pandas as pd

inputfile = 'unemployment_effects.csv'
outputfile = 'unemployment_effects_new.csv'

df = pd.read_csv(inputfile)

for i in range(1,2001):
    df['draw_{}'.format(i)] = df['draw_0']

df.to_csv(outputfile, index=False)