import pandas as pd

# import datasets
playerpool_df = pd.read_csv('created-data/playerpool.csv')
apps_df = pd.read_csv('transfermarkt-data/appearances.csv')
games_df = pd.read_csv('transfermarkt-data/games.csv')
comps_df = pd.read_csv('transfermarkt-data/competitions.csv')

LEAGUES = ['premier-league', 'laliga', 'ligue-1', 'serie-a', 'bundesliga']

# get player_ids
player_ids = playerpool_df['player_id'].to_list()

# filter apps_df and games_df to given 'player_id's and 'competition-id's
apps_df = apps_df[apps_df['player_id'].isin(player_ids)]
league_ids = []
for league in LEAGUES:
    league_id = comps_df.loc[comps_df['competition_code'] == league, 'competition_id'].values[0]
    league_ids.append(league_id)
apps_df = apps_df[apps_df['competition_id'].isin(league_ids)]
games_df = games_df[games_df['competition_id'].isin(league_ids)]

# prepare games_df
games_df = games_df.drop(['round', 'date', 'home_club_position', 'away_club_position', 'home_club_manager_name',
                          'away_club_manager_name', 'stadium', 'attendance', 'referee', 'url', 'home_club_name',
                          'away_club_name', 'aggregate', 'competition_type', 'competition_id'], axis=1)

# get club ids and seasons
club_ids = list(set(games_df['home_club_id'].to_list() + games_df['away_club_id'].to_list()))
seasons = list(set(games_df['season'].to_list()))

# create a new df for each club_id for each season
clubSeason_df = pd.DataFrame(columns=['club_id', 'season', 'club_wins', 'club_draws', 'club_losses',
                                      'club_gf', 'club_ga'])  # gf and ga are goals for and goals against

# build initial df
for season in seasons:
    for club_id in club_ids:
        row_exists = games_df.loc[(games_df['season'] == season) & ((games_df['home_club_id'] == club_id) |
                                                                (games_df['away_club_id'] == club_id)), "game_id"].any()
        if row_exists:
            new_row = [club_id, season, 0, 0, 0, 0, 0]
            clubSeason_df.loc[len(clubSeason_df)] = new_row
        else: pass

# now move through the dataframe and update each row
for index, row in clubSeason_df.iterrows():
    # add new row
    # get info for each club and season in games_df
    home_df = games_df[(games_df['home_club_id'] == row['club_id']) & (games_df['season'] == row['season'])]
    for index2, row2 in home_df.iterrows():
        row['club_gf'] += row2['home_club_goals']
        row['club_ga'] += row2['away_club_goals']
        if row2['home_club_goals'] > row2['away_club_goals']:
            row['club_wins'] += 1
        elif row2['home_club_goals'] < row2['away_club_goals']:
            row['club_losses'] += 1
        else:
            row['club_draws'] += 1
    away_df = games_df[(games_df['away_club_id'] == row['club_id']) & (games_df['season'] == row['season'])]
    for index2, row2 in away_df.iterrows():
        row['club_gf'] += row2['away_club_goals']
        row['club_ga'] += row2['home_club_goals']
        if row2['home_club_goals'] < row2['away_club_goals']:
            row['club_wins'] += 1
        elif row2['home_club_goals'] > row2['away_club_goals']:
            row['club_losses'] += 1
        else:
            row['club_draws'] += 1

# merge apps_df and club_df on game_id and drop unnecessary cols
apps_games_df = pd.merge(apps_df, games_df, on='game_id')
apps_games_df = apps_games_df.drop(['appearance_id', 'player_current_club_id', 'date', 'player_name'], axis=1)

# then do the above - note the difference between team and club
playerSeason_df = pd.DataFrame(columns=['player_id', 'club_id', 'season', 'mins', 'player_wins', 'player_losses',
                                        'player_draws', 'team_gf', 'team_ga', 'goals', 'assists', 'yellows', 'reds'])

total = len(seasons) * len(player_ids)
count = 0
for season in seasons:
    for player_id in player_ids:
        row_exists = apps_games_df.loc[(apps_games_df['season'] == season) & (apps_games_df['player_id'] == player_id),
                                       'game_id'].any()
        if row_exists:
            new_row = [player_id, 0, season, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            playerSeason_df.loc[len(playerSeason_df)] = new_row
            count += 1
        else:
            count += 1
            pass
        print((count/total)*100)

# think about issues if people transfer in January
total = len(playerSeason_df)
count = 0
for index, row in playerSeason_df.iterrows():
    player_df = apps_games_df[(apps_games_df['player_id'] == row['player_id']) &
                              (apps_games_df['season'] == row['season'])]
    row['club_id'] = player_df['player_club_id'].iloc[0]
    row['mins'] = player_df['minutes_played'].sum()
    row['goals'] = player_df['goals'].sum()
    row['assists'] = player_df['assists'].sum()
    row['yellows'] = player_df['yellow_cards'].sum()
    row['reds'] = player_df['red_cards'].sum()
    for index2, row2 in player_df.iterrows():
        # home team
        if row2['player_club_id'] == row2['home_club_id']:
            row['team_gf'] += row2['home_club_goals']
            row['team_ga'] += row2['away_club_goals']
            if row2['home_club_goals'] > row2['away_club_goals']:
                row['player_wins'] += 1
            elif row2['home_club_goals'] < row2['away_club_goals']:
                row['player_losses'] += 1
            else:
                row['player_draws'] += 1
        # away team
        else:
            row['team_gf'] += row2['away_club_goals']
            row['team_ga'] += row2['home_club_goals']
            if row2['home_club_goals'] < row2['away_club_goals']:
                row['player_wins'] += 1
            elif row2['home_club_goals'] > row2['away_club_goals']:
                row['player_losses'] += 1
            else:
                row['player_draws'] += 1
    count += 1
    print((count/total)*100)

# merge dataframes on 'club_id' and 'season'
annualStats_df = pd.merge(playerSeason_df, clubSeason_df, on=['club_id', 'season'])
annualStats_df.to_csv('created-data/annual_stats.csv', index=False)
