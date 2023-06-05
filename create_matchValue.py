import pandas as pd

apps_df = pd.read_csv('transfermarkt-data/appearances.csv')
games_df = pd.read_csv('transfermarkt-data/games.csv')
playerValues_df = pd.read_csv('created-data/annual_values.csv')
playerpool_df = pd.read_csv('created-data/playerpool.csv')
comps_df = pd.read_csv('transfermarkt-data/competitions.csv')

'''
apps_df = 'appearance_id', 'game_id', 'player_id', 'player_club_id', 'player_current_club_id', 'date', 'player_name', 
    'competition_id', 'yellow_cards', 'red_cards', 'goals', 'assists', 'minutes_played'
       
games_df = 'game_id', 'competition_id', 'season', 'round', 'date', 'home_club_id', 'away_club_id', 'home_club_goals', 
    'away_club_goals',

playerValues_df = 'player_id', 'year', 'market_value_in_eur'
'''

# get leagues and player_ids
LEAGUES = ['premier-league', 'laliga', 'ligue-1', 'serie-a', 'bundesliga']
player_ids = playerpool_df['player_id'].to_list()

# filter apps_df and games_df to given 'player_id's and 'competition-id's
apps_df = apps_df[apps_df['player_id'].isin(player_ids)]
league_ids = []
for league in LEAGUES:
    league_id = comps_df.loc[comps_df['competition_code'] == league, 'competition_id'].values[0]
    league_ids.append(league_id)
apps_df = apps_df[apps_df['competition_id'].isin(league_ids)]
games_df = games_df[games_df['competition_id'].isin(league_ids)]

# drop unnecessary columns
apps_df = apps_df.drop(['appearance_id', 'player_current_club_id', 'date', 'player_name', 'competition_id',
                        'yellow_cards', 'red_cards', 'goals', 'assists'], axis=1)
games_df = games_df.drop(['round', 'date', 'home_club_position', 'away_club_position', 'home_club_manager_name',
                          'away_club_manager_name', 'stadium', 'attendance', 'referee', 'url', 'home_club_name',
                          'away_club_name', 'aggregate', 'competition_type'], axis=1)

# create df
# note that defence includes goalkeeper
matchValues_df = pd.DataFrame(columns=['game_id', 'competition_id', 'season', 'home_id', 'away_id', 'home_gf',
                                       'away_gf', 'home_start_av_value', 'away_start_av_value', 'home_av_value',
                                       'away_av_value', 'home_def_av_value', 'home_mid_av_value',
                                       'home_att_av_value', 'away_def_av_value', 'away_mid_av_value',
                                       'away_att_av_value'])

# build the df
total = len(games_df)
count = 0
for index, row in games_df.iterrows():
    game_id, comp_id, season, home_team, away_team, home_gf, away_gf = row['game_id'], row['competition_id'], \
                                                                       row['season'], row['home_club_id'], \
                                                                       row['away_club_id'],row['home_club_goals'], \
                                                                       row['away_club_goals']
    players_df = apps_df[apps_df['game_id'] == game_id]
    exists = players_df['game_id'].any()
    if exists:
        # averages used to overcome missing values
        home_start_value, away_start_value = 0, 0
        home_start_count, away_start_count = 0, 0
        home_def_value, home_mid_value, home_att_value = 0, 0, 0
        away_def_value, away_mid_value, away_att_value = 0, 0, 0
        home_def_count, home_mid_count, home_att_count = 0, 0, 0
        away_def_count, away_mid_count, away_att_count = 0, 0, 0
        for index2, row2 in players_df.iterrows():
            # here we make the assumption that above 45 mins played means the player started
            mins_played = row2['minutes_played']
            player_pos = playerpool_df.loc[playerpool_df['player_id'] == row2['player_id'], 'position'].values[0]
            player_value = playerValues_df.loc[(playerValues_df['player_id'] == row2['player_id']) &
                                               (playerValues_df['year'] == season), 'market_value_in_eur']
            try:
                value = player_value.values[0]
                if row2['player_club_id'] == home_team:
                    if player_pos == "Goalkeeper" or player_pos == "Defender":
                        home_def_value += value
                        home_def_count += 1
                    elif player_pos == "Midfield":
                        home_mid_value += value
                        home_mid_count += 1
                    else:
                        home_att_value += value
                        home_att_count += 1
                    if mins_played > 45:
                        home_start_value += value
                        home_start_count += 1
                else:   # away team
                    if player_pos == "Goalkeeper" or player_pos == "Defender":
                        away_def_value += value
                        away_def_count += 1
                    elif player_pos == "Midfield":
                        away_mid_value += value
                        away_mid_count += 1
                    else:
                        away_att_value += value
                        away_att_count += 1
                    if mins_played > 45:
                        away_start_value += value
                        away_start_count += 1
            except IndexError:
                pass

        # messy code but necessary
        try: home_start_av_value = home_start_value / home_start_count
        except ZeroDivisionError:
            home_start_av_value = 0
        try: home_av_value = (home_def_value + home_mid_value + home_att_value) / (home_def_count + home_mid_count +
                                                                              home_att_count)
        except ZeroDivisionError:
            home_av_value = 0
        try: home_def_av_value = home_def_value / home_def_count
        except ZeroDivisionError:
            home_def_av_value = 0
        try: home_mid_av_value = home_mid_value / home_mid_count
        except ZeroDivisionError:
            home_mid_av_value = 0
        try: home_att_av_value = home_att_value / home_att_count
        except ZeroDivisionError:
            home_att_av_value = 0
        try: away_start_av_value = away_start_value / away_start_count
        except ZeroDivisionError:
            away_start_av_value = 0
        try: away_av_value = (away_def_value + away_mid_value + away_att_value) / (away_def_count + away_mid_count +
                                                                              away_att_count)
        except ZeroDivisionError:
            away_av_value = 0
        try: away_def_av_value = away_def_value / away_def_count
        except ZeroDivisionError:
            away_def_av_value = 0
        try: away_mid_av_value = away_mid_value / away_mid_count
        except ZeroDivisionError:
            away_mid_av_value = 0
        try: away_att_av_value = away_att_value / away_att_count
        except ZeroDivisionError:
            away_att_av_value = 0

        # insert into new dataframe
        matchValues_df.loc[len(matchValues_df)] = [game_id, comp_id, season, home_team, away_team, home_gf, away_gf,
                                                   home_start_av_value, away_start_av_value, home_av_value,
                                                   away_av_value, home_def_av_value, home_mid_av_value,
                                                   home_att_av_value, away_def_av_value, away_mid_av_value,
                                                   away_att_av_value]
    else:
        pass
    count += 1
    print((count/total) * 100)

# and save
matchValues_df.to_csv('created-data/match_values.csv', index=False)