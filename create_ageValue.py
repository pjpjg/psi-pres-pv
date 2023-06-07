import pandas as pd

annualVal_df = pd.read_csv('created-data/annual_values.csv')
playerpool_df = pd.read_csv('created-data/playerpool.csv')
annualStats_df = pd.read_csv('created-data/annual_stats.csv')

agesValue_df = pd.DataFrame(columns=['player_id', 'year', 'age', 'value', 'pc_delta_value', 'position'])

count = 0
total = len(annualVal_df)
for index, row in annualVal_df.iterrows():
    player_id = row['player_id']
    year = row['year']
    curr_age = playerpool_df.loc[playerpool_df['player_id'] == player_id, 'age'].values[0]
    # assume data is true as of 2023
    age = curr_age - (2023 - year)
    value = row['market_value_in_eur']
    pos = playerpool_df.loc[playerpool_df['player_id'] == player_id, 'position'].values[0]
    prev_year = year - 1
    played = ((annualVal_df['player_id'] == player_id) & (annualVal_df['year'] == prev_year)).any()
    if played:
        prev_value = annualVal_df.loc[(annualVal_df['player_id'] == player_id) & (annualVal_df['year'] == prev_year),
                                      'market_value_in_eur'].values[0]
        pc_delta_value = ((value - prev_value) / prev_value) * 100
        agesValue_df.loc[len(agesValue_df)] = [player_id, year, age, value, pc_delta_value, pos]
    count += 1
    print((count/total)*100)

print(agesValue_df)

agesValue_df.to_csv('created-data/ages_values.csv', index=False)