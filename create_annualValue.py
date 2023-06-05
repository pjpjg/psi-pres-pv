import pandas as pd
from datetime import datetime

# import datasets
playerpool_df = pd.read_csv('created-data/playerpool.csv')
values_df = pd.read_csv('transfermarkt-data/player_valuations.csv')

# filter values on 'player_id's in playerpool_df
player_ids = playerpool_df['player_id']

# merge values_df on player_id
values_df = values_df[values_df['player_id'].isin(player_ids)]

# drop unnecessary columns
values_df = values_df.drop(['last_season', 'datetime', 'dateweek', 'n', 'current_club_id',
                            'player_club_domestic_competition_id'], axis=1)

# add a column for year
values_df['date'] = pd.to_datetime(values_df['date'])
values_df['year'] = values_df['date'].dt.year

# convert 'date column to datetime
values_df['date'] = pd.to_datetime(values_df['date'])

# calculate the difference in days from June 30th of the row's year
total = len(values_df)
count = 0
for index, row in values_df.iterrows():
    delta = int(abs((row['date'] - datetime(row['year'], 6, 30, 0, 0, 0)).days))
    values_df.at[index, 'delta'] = delta
    count += 1
    print((count/total)*100)

# sort df on 'player_id', 'year', 'delta'
values_df = values_df.sort_values(by=['player_id', 'year', 'delta'])

# group by 'player_id' and 'year' and select the first row
values_df = values_df.groupby(['player_id', 'year']).first().reset_index()

# Remove the 'date' and 'delta' columns
values_df = values_df.drop(['date', 'delta'], axis=1)

# save df
values_df.to_csv('created-data/annual_values.csv', index=False)
