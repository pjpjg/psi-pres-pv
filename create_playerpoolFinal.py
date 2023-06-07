import pandas as pd

annualValues_df = pd.read_csv('created-data/annual_values.csv')
# remove retired players
player_ids = list(set(annualValues_df['player_id'].to_list()))
total = len(player_ids)
count = 0
retired_players = []
for player_id in player_ids:
    seasons = set(annualValues_df['year'].to_list())
    if 2022 not in seasons:
        retired_players.append(player_id)
    count += 1
    print((count/total)*100)
annualValues_df = annualValues_df[~annualValues_df['player_id'].isin(retired_players)]
# save_df
annualValues_df.to_csv('created-data/playerpool-final.csv', index=False)
