import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from scipy.stats import pearsonr
plt.style.use('seaborn-white')
plt.rcParams['font.size'] = 14

comps_df = pd.read_csv('transfermarkt-data/competitions.csv')
mv_df = pd.read_csv('created-data/match_values.csv')
mv_df = mv_df.drop(mv_df[(mv_df['home_start_av_value'] == 0) | (mv_df['away_start_av_value'] == 0) |
                   (mv_df['home_av_value'] == 0) | (mv_df['away_av_value'] == 0) |
                   (mv_df['home_def_av_value'] == 0) | (mv_df['away_def_av_value'] == 0) |
                   (mv_df['home_mid_av_value'] == 0) | (mv_df['away_mid_av_value'] == 0) |
                   (mv_df['home_att_av_value'] == 0) | (mv_df['away_att_av_value'] == 0)].index)

comp_dict = {'FR1': 'Ligue 1', 'ES1': 'La Liga', 'GB1': 'Premier League', 'IT1': 'Serie A', 'L1': 'Bundesliga'}

# check the average values of match-day squads for each of 5 leagues over years - see upward trend
# for defence, midfield and attack
squadValues_df = pd.DataFrame(columns=['team_id', 'season', 'competition_id', 'av_player_value', 'av_def_value',
                                       'av_mid_value', 'av_att_value', 'points'])
teams = list(set(mv_df['home_id'].to_list() + mv_df['away_id'].to_list()))
seasons = list(set(mv_df['season'].to_list()))
seasons.sort()
for team in teams:
    for season in seasons:
        points, games, value, def_value, mid_value, att_value = 0, 0, 0, 0, 0, 0
        homeGames_df = mv_df[(mv_df['home_id'] == team) & (mv_df['season'] == season)]
        for index, game in homeGames_df.iterrows():
            games += 1
            value += game['home_av_value']
            def_value += game['home_def_av_value']
            mid_value += game['home_mid_av_value']
            att_value += game['home_att_av_value']
            if game['home_gf'] > game['away_gf']:
                points += 3
            elif game['home_gf'] == game['away_gf']:
                points += 1
            else: pass
        awayGames_df = mv_df[(mv_df['away_id'] == team) & (mv_df['season'] == season)]
        for index, game in awayGames_df.iterrows():
            games += 1
            value += game['away_av_value']
            def_value += game['away_def_av_value']
            mid_value += game['away_mid_av_value']
            att_value += game['away_att_av_value']
            if game['away_gf'] > game['home_gf']:
                points += 3
            elif game['away_gf'] == game['home_gf']:
                points += 1
            else: pass
        try: av_value = value / games
        except ZeroDivisionError:
            av_value = None
        try: av_def_value = def_value / games
        except ZeroDivisionError:
            av_def_value = None
        try: av_mid_value = mid_value / games
        except ZeroDivisionError:
            av_mid_value = None
        try: av_att_value = att_value / games
        except ZeroDivisionError:
            av_att_value = None
        comp_id = mv_df.loc[mv_df['home_id'] == team, 'competition_id'].values[0]
        if games == 0:
            pass
        else:
            squadValues_df.loc[len(squadValues_df)] = [team, season, comp_id, av_value, av_def_value, av_mid_value,
                                                   av_att_value, points]

comps = list(set(mv_df['competition_id'].to_list()))
comps.sort()

for comp in comps:
    x_season = []
    y_value = []
    y_def_value, y_mid_value, y_att_value = [], [], []
    for season in seasons:
        x_season.append(season)
        total_teams = squadValues_df.loc[(squadValues_df['competition_id'] == comp) &
                                         (squadValues_df['season'] == season), 'team_id'].nunique()
        total_value = squadValues_df.loc[(squadValues_df['competition_id'] == comp) &
                                         (squadValues_df['season'] == season), 'av_player_value'].sum()
        total_def_value = squadValues_df.loc[(squadValues_df['competition_id'] == comp) &
                                         (squadValues_df['season'] == season), 'av_def_value'].sum()
        total_mid_value = squadValues_df.loc[(squadValues_df['competition_id'] == comp) &
                                             (squadValues_df['season'] == season), 'av_mid_value'].sum()
        total_att_value = squadValues_df.loc[(squadValues_df['competition_id'] == comp) &
                                             (squadValues_df['season'] == season), 'av_att_value'].sum()
        av_value = total_value / total_teams
        av_def_value = total_def_value / total_teams
        av_mid_value = total_mid_value / total_teams
        av_att_value = total_att_value / total_teams
        y_value.append(av_value)
        y_def_value.append(av_def_value)
        y_mid_value.append(av_mid_value)
        y_att_value.append(av_att_value)

    # first plot - ave player value
    default_x_ticks = range(len(x_season))
    plt.bar(default_x_ticks, y_value, width=0.6)
    plt.xticks(default_x_ticks, x_season)
    plt.xlabel("Season (beginning year)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.ylabel("Average player value (in millions)")
    plt.ylim(0, 25_000_000)
    plt.grid(axis='y')
    title = comp_dict[comp]
    plt.title(title)
    plt.savefig('plots/ave_pv_league_season/{}.png'.format(comp))
    plt.close()

    # second plot - def/mid/att split
    xs = np.arange(len(seasons))
    width = 0.2  # Width of each bar
    offset = width  # Offset for positioning bars side by side
    plt.bar(xs - offset, y_def_value, width=width, label='Defenders', color='lightsteelblue')
    plt.bar(xs, y_mid_value, width=width, label='Midfielders', color='cornflowerblue')
    plt.bar(xs + offset, y_att_value, width=width, label='Attackers', color='mediumblue')
    plt.xticks(xs, seasons)
    plt.xlabel("Season (beginning year)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.ylabel("Average player value (in millions)")
    plt.ylim(0, 31_000_000)
    title = comp_dict[comp]
    plt.title(title)
    plt.legend(fontsize=14)
    plt.grid(axis='y')
    plt.savefig('plots/ave_pv_league_season_position/{}.png'.format(comp))
    plt.close()

# points total vs average value
for comp in comps:
    pointsValue_comp_df = squadValues_df[squadValues_df['competition_id'] == comp].dropna()
    plt.scatter(pointsValue_comp_df['points'], pointsValue_comp_df['av_player_value'])
    plt.xlabel("Points total")
    plt.ylabel("Average player value (millions)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    title = comp_dict[comp]
    plt.title(title)
    cov = np.cov(pointsValue_comp_df['points'], pointsValue_comp_df['av_player_value'])[0, 1]
    corr, _ = pearsonr(pointsValue_comp_df['points'], pointsValue_comp_df['av_player_value'])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/points_value/{}.png'.format(comp))
    plt.close()

# (home goals - away goals) vs (home value - away value)
# per league
goalsValue_df = pd.DataFrame(columns=['season', 'competition_id', 'goal_dif', 'value_dif'])
for index, row in mv_df.iterrows():
    season = row['season']
    comp_id = row['competition_id']
    goal_dif = row['home_gf'] - row['away_gf']
    value_dif = row['home_start_av_value'] - row['away_start_av_value']
    goalsValue_df.loc[len(goalsValue_df)] = [season, comp_id, goal_dif, value_dif]

for comp in comps:
    goalsValue_comp_df = goalsValue_df[goalsValue_df['competition_id'] == comp]
    plt.scatter(goalsValue_comp_df['goal_dif'], goalsValue_comp_df['value_dif'])
    plt.xlabel("Difference (home - away) in goals")
    plt.ylabel("Difference (home - away) in value (millions)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    title = comp_dict[comp]
    plt.title(title)
    cov = np.cov(goalsValue_comp_df['goal_dif'], goalsValue_comp_df['value_dif'])[0, 1]
    corr, _ = pearsonr(goalsValue_comp_df['goal_dif'], goalsValue_comp_df['value_dif'])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/goals_value_dif/{}.png'.format(comp))
    plt.close()

# focus on premier league over the seasons
for season in seasons:
    goalsValue_prem_season_df = goalsValue_df[(goalsValue_df['competition_id'] == 'GB1') &
                                              (goalsValue_df['season'] == season)]
    plt.scatter(goalsValue_prem_season_df['goal_dif'], goalsValue_prem_season_df['value_dif'])
    plt.xlabel("Difference (home - away) in goals")
    plt.ylabel("Difference (home - away) in value (millions)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    title = "Premier League {}".format(season)
    plt.title(title)
    cov = np.cov(goalsValue_prem_season_df['goal_dif'], goalsValue_prem_season_df['value_dif'])[0, 1]
    corr, _ = pearsonr(goalsValue_prem_season_df['goal_dif'], goalsValue_prem_season_df['value_dif'])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/goals_value_dif/premier_league_years/{}.png'.format(season))
    plt.close()

# (change in points total) vs (change in value)
# per league and per season
delta_df = pd.DataFrame(columns=['team_id', 'season', 'competition_id', 'delta_points', 'delta_value',
                                 'delta_def_value', 'delta_mid_value', 'delta_att_value'])
for index, row in squadValues_df.iterrows():
    team_id = row['team_id']
    season = row['season']
    comp_id = row['competition_id']
    curr_points = row['points']
    curr_value = row['av_player_value']
    curr_def_value = row['av_def_value']
    curr_mid_value = row['av_mid_value']
    curr_att_value = row['av_att_value']
    prev_season = season - 1
    team_played = ((squadValues_df['season'] == prev_season) & (squadValues_df['team_id'] == team_id)).any()
    if team_played:
        prev_points = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                         (squadValues_df['team_id'] == team_id), 'points'].values[0]
        delta_points = curr_points - prev_points
        prev_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                        (squadValues_df['team_id'] == team_id), 'av_player_value'].values[0]
        delta_value = curr_value - prev_value
        prev_def_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_def_value'].values[0]
        delta_def = curr_def_value - prev_def_value
        prev_mid_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_mid_value'].values[0]
        delta_mid = curr_mid_value - prev_mid_value
        prev_att_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_att_value'].values[0]
        delta_att = curr_att_value - prev_att_value
        delta_df.loc[len(delta_df)] = [team_id, season, comp_id, delta_points, delta_value, delta_def, delta_mid,
                                       delta_att]

for comp in comps:
    delta_comp_df = delta_df[delta_df['competition_id'] == comp]
    plt.scatter(delta_comp_df['delta_points'], delta_comp_df['delta_value'])
    plt.xlabel("Change in points total")
    plt.ylabel("Change in average player value (millions)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    title = comp_dict[comp]
    plt.title(title)
    cov = np.cov(delta_comp_df['delta_points'], delta_comp_df['delta_value'])[0, 1]
    corr, _ = pearsonr(delta_comp_df['delta_points'], delta_comp_df['delta_value'])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/points_value_delta/{}.png'.format(comp))
    plt.close()

title_dict = {'delta_def_value': 'Defence', 'delta_mid_value': 'Midfield', 'delta_att_value': 'Attack'}
for position in ['delta_def_value', 'delta_mid_value', 'delta_att_value']:
    delta_comp_df = delta_df[delta_df['competition_id'] == 'GB1']
    plt.scatter(delta_comp_df['delta_points'], delta_comp_df[position])
    plt.xlabel("Change in points total")
    plt.ylabel("Change in average player value (millions)")
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    title = title_dict[position]
    plt.title(title)
    cov = np.cov(delta_comp_df['delta_points'], delta_comp_df[position])[0, 1]
    corr, _ = pearsonr(delta_comp_df['delta_points'], delta_comp_df[position])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/points_value_delta/premier_league_pos/{}.png'.format(title))
    plt.close()

# %(change in points total) vs %(change in value)
# per league and per season
pc_delta_df = pd.DataFrame(columns=['team_id', 'season', 'competition_id', 'delta_points', 'delta_value',
                                    'delta_def_value', 'delta_mid_value', 'delta_att_value'])
for index, row in squadValues_df.iterrows():
    team_id = row['team_id']
    season = row['season']
    comp_id = row['competition_id']
    curr_points = row['points']
    curr_value = row['av_player_value']
    curr_def_value = row['av_def_value']
    curr_mid_value = row['av_mid_value']
    curr_att_value = row['av_att_value']
    prev_season = season - 1
    team_played = ((squadValues_df['season'] == prev_season) & (squadValues_df['team_id'] == team_id)).any()
    if team_played:
        prev_points = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                         (squadValues_df['team_id'] == team_id), 'points'].values[0]
        delta_points = ((curr_points - prev_points) / prev_points) * 100
        prev_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                        (squadValues_df['team_id'] == team_id), 'av_player_value'].values[0]
        delta_value = ((curr_value - prev_value) / prev_value) * 100
        prev_def_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_def_value'].values[0]
        delta_def = ((curr_def_value - prev_def_value) / prev_def_value) * 100
        prev_mid_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_mid_value'].values[0]
        delta_mid = ((curr_mid_value - prev_mid_value) / prev_mid_value) * 100
        prev_att_value = squadValues_df.loc[(squadValues_df['season'] == prev_season) &
                                            (squadValues_df['team_id'] == team_id), 'av_att_value'].values[0]
        delta_att = ((curr_att_value - prev_att_value) / prev_att_value) * 100
        pc_delta_df.loc[len(pc_delta_df)] = [team_id, season, comp_id, delta_points, delta_value, delta_def, delta_mid,
                                             delta_att]



for comp in comps:
    pc_delta_comp_df = pc_delta_df[pc_delta_df['competition_id'] == comp]
    plt.scatter(pc_delta_comp_df['delta_points'], pc_delta_comp_df['delta_value'])
    plt.xlabel("Change in points total")
    plt.ylabel("Change in average player value (millions)")
    title = comp_dict[comp]
    plt.title(title)
    cov = np.cov(pc_delta_comp_df['delta_points'], pc_delta_comp_df['delta_value'])[0, 1]
    corr, _ = pearsonr(delta_comp_df['delta_points'], delta_comp_df['delta_value'])
    plt.text(0.05, 0.95, f'Covariance: {cov:.2f},\nPearsons: {corr:.2f}', fontsize=14, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.savefig('plots/points_value_delta/percentage_change/{}.png'.format(comp))
    plt.close()