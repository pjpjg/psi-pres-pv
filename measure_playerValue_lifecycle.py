import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

ageValues_df = pd.read_csv('created-data/ages_values.csv')
playerpool_df = pd.read_csv('created-data/playerpool.csv')
playerClub_df = playerpool_df[['player_id', 'current_club_domestic_competition_id']]
age_cut_off = [18, 36]
filtered_df = ageValues_df[(ageValues_df['age'] >= age_cut_off[0]) &
                           (ageValues_df['age'] <= age_cut_off[1])]
filtered_df = pd.merge(filtered_df, playerClub_df, on='player_id', how='left')
comp_dict = {'FR1': 'Ligue 1', 'ES1': 'La Liga', 'GB1': 'Premier League', 'IT1': 'Serie A', 'L1': 'Bundesliga'}
comps = set(comp_dict.keys())
filtered_df = filtered_df[filtered_df['current_club_domestic_competition_id'].isin(comps)]

# plot mean value vs age
grouped = filtered_df.groupby('age').agg({'value': ['mean', 'std']})
ages = grouped.index
means = grouped['value']['mean']
stds = grouped['value']['std']
plt.plot(ages, means, color='blue', label='Mean')
plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
plt.gca().yaxis.set_major_formatter(formatter)
plt.ylim(0, 20_000_000)
plt.grid(axis='y')
plt.xlabel("Player age")
plt.ylabel('Player value (in millions)')
plt.title('Mean value with variance by age')
plt.savefig('plots/value_lifecycle/value.png')
plt.close()

# plot mean change in value vs age
# but first remove outliers using Z-score method
z_scores = np.abs((filtered_df['pc_delta_value'] - filtered_df['pc_delta_value'].mean()) /
                  filtered_df['pc_delta_value'].std())
threshold = 3
filtered_outlier_df = filtered_df[z_scores <= threshold]
# now plot
grouped = filtered_outlier_df.groupby('age').agg({'pc_delta_value': ['mean', 'std']})
ages = grouped.index
means = grouped['pc_delta_value']['mean']
stds = grouped['pc_delta_value']['std']
plt.plot(ages, means, color='blue', label='Mean')
plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
plt.grid(axis='y')
plt.xlabel("Player age")
plt.ylabel('Annual change in value (in millions)')
plt.title('Mean % change in value with variance by age')
plt.savefig('plots/value_lifecycle/delta_value.png')
plt.close()

# do the above but over leagues
for league in comps:
    league_df = filtered_df[filtered_df['current_club_domestic_competition_id'] == league]
    grouped = league_df.groupby('age').agg({'value': ['mean', 'std']})
    ages = grouped.index
    means = grouped['value']['mean']
    stds = grouped['value']['std']
    plt.plot(ages, means, color='blue', label='Mean')
    plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.ylim(0, 20_000_000)
    plt.grid(axis='y')
    plt.xlabel("Player age")
    plt.ylabel('Player value (in millions)')
    plt.title(comp_dict[league])
    plt.savefig('plots/value_lifecycle/leagues/{}_value.png'.format(league))
    plt.close()

    league_outlier_df = filtered_outlier_df[filtered_outlier_df['current_club_domestic_competition_id'] == league]
    grouped = league_outlier_df.groupby('age').agg({'pc_delta_value': ['mean', 'std']})
    ages = grouped.index
    means = grouped['pc_delta_value']['mean']
    stds = grouped['pc_delta_value']['std']
    plt.plot(ages, means, color='blue', label='Mean')
    plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
    plt.grid(axis='y')
    plt.xlabel("Player age")
    plt.ylabel('Annual change in value (in millions)')
    plt.title(comp_dict[league])
    plt.savefig('plots/value_lifecycle/leagues/{}_delta_value.png'.format(league))
    plt.close()

# now for positions
for position in ['Goalkeeper', 'Defender', 'Midfield', 'Attack']:
    position_df = filtered_df[filtered_df['position'] == position]
    grouped = position_df.groupby('age').agg({'value': ['mean', 'std']})
    ages = grouped.index
    means = grouped['value']['mean']
    stds = grouped['value']['std']
    plt.plot(ages, means, color='blue', label='Mean')
    plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
    formatter = ticker.FuncFormatter(lambda x, pos: '{:.1f}'.format(x * 1e-6))
    plt.gca().yaxis.set_major_formatter(formatter)
    plt.ylim(0, 20_000_000)
    plt.grid(axis='y')
    plt.xlabel("Player age")
    plt.ylabel('Player value (in millions)')
    plt.title(position)
    plt.savefig('plots/value_lifecycle/positions/{}_value.png'.format(position))
    plt.close()

    position_outlier_df = filtered_outlier_df[filtered_outlier_df['position'] == position]
    grouped = position_outlier_df.groupby('age').agg({'pc_delta_value': ['mean', 'std']})
    ages = grouped.index
    means = grouped['pc_delta_value']['mean']
    stds = grouped['pc_delta_value']['std']
    plt.plot(ages, means, color='blue', label='Mean')
    plt.fill_between(ages, means - stds, means + stds, color='lightblue', alpha=0.5, label='Variance')
    plt.grid(axis='y')
    plt.xlabel("Player age")
    plt.ylabel('Annual change in value (in millions)')
    plt.title(position)
    plt.savefig('plots/value_lifecycle/positions/{}_delta_value.png'.format(position))
    plt.close()