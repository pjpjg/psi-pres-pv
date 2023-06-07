import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer, r2_score
from sklearn.preprocessing import LabelEncoder

playerpool_df = pd.read_csv('created-data/playerpool-final.csv')
furtherInfo_df = pd.read_csv('created-data/playerpool.csv')
annualStats_df = pd.read_csv('created-data/annual_stats.csv')
annualValues_df = pd.read_csv('created-data/annual_values.csv')

# limit age of those analysed
age_cut_off = [20, 32]
playerAges_df = furtherInfo_df[['player_id', 'age']]
playerpool_df = pd.merge(playerpool_df, playerAges_df, on='player_id', how='left')
playerpool_df = playerpool_df[(playerpool_df['age'] >= age_cut_off[0]) &
                              (playerpool_df['age'] <= age_cut_off[1])]
# limit to players currently in big five leagues
playerClub_df = furtherInfo_df[['player_id', 'current_club_domestic_competition_id']]
playerpool_df = pd.merge(playerpool_df, playerClub_df, on='player_id', how='left')
comp_dict = {'FR1': 'Ligue 1', 'ES1': 'La Liga', 'GB1': 'Premier League', 'IT1': 'Serie A', 'L1': 'Bundesliga'}
comps = set(comp_dict.keys())
playerpool_df = playerpool_df[playerpool_df['current_club_domestic_competition_id'].isin(comps)]
player_ids = list(set(playerpool_df['player_id'].to_list()))

# use values (for past 6 years) to predict 2022 and 2023 values
years = [2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016]
df1 = pd.DataFrame(columns=['player_id'] + years)
for player_id in player_ids:
    present = ((annualValues_df['player_id'] == player_id) & (annualValues_df['year'] == 2023)).any()
    if present:
        values = [player_id]
        for year in years:
            try: value = annualValues_df.loc[(annualValues_df['player_id'] == player_id)
                                             & (annualValues_df['year'] == year), 'market_value_in_eur'].values[0]
            except IndexError: value = 0
            values.append(value)

        df1.loc[len(df1)] = values

# divide all values by 1m
df1.iloc[:, 1:] = df1.iloc[:, 1:] / 1_000_000

# target is 2022, variables are 2021 to 2016
y = df1.iloc[:, 1]
print('Target mean: {}'.format(y.mean()))
print('Target standard deviation: {}'.format(y.std()))
X = df1.iloc[:, 3:]
r2_scorer = make_scorer(r2_score)

# first build simple regression model and evaluate
print('\nSimple linear regression')
for scorer in ['neg_mean_squared_error', r2_scorer]:
    first_model = LinearRegression()
    cv_scores = cross_val_score(first_model, X, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
        reg = LinearRegression().fit(X, y)
        print(reg.coef_)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

# relationship may not be linear
# create polynomial features
poly = PolynomialFeatures(2)
polyX = poly.fit_transform(X)
print('\nPolynomial linear regression')
for scorer in ['neg_mean_squared_error', r2_scorer]:
    second_model = LinearRegression()
    cv_scores = cross_val_score(second_model, polyX, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

# ridge regression
print('\nRidge regression')
for scorer in ['neg_mean_squared_error', r2_scorer]:
    third_model = Ridge(alpha=100.0)
    cv_scores = cross_val_score(third_model, polyX, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

print('\nSimple linear regression with positional variable (encoded)')
playerPos_df = furtherInfo_df[['player_id', 'position']]
df2 = df1.merge(playerPos_df, on='player_id')
label_encoder = LabelEncoder()
df2['position_encoded'] = label_encoder.fit_transform(df2['position'])
df2 = df2.drop(['position'], axis=1)
y = df2.iloc[:, 1]
X = df2.iloc[:, 3:]
for scorer in ['neg_mean_squared_error', r2_scorer]:
    first_model = LinearRegression()
    cv_scores = cross_val_score(first_model, X, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

# try first with one year's previous stats
# not we will use linear regression here
print('Simple linear regression with many exogenous variable')
# issue here is data loss
prev_year = 2021
exoVar1_df = annualStats_df[annualStats_df['season'] == prev_year]
exoVar1_df = exoVar1_df[['player_id', 'player_wins', 'player_losses', 'player_draws', 'team_gf', 'team_ga', 'goals',
                         'assists']]
df3 = pd.merge(df1, exoVar1_df, on='player_id')
y = df3.iloc[:, 1]
X = df3.iloc[:, 3:]
for scorer in ['neg_mean_squared_error', r2_scorer]:
    first_model = LinearRegression()
    cv_scores = cross_val_score(first_model, X, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

print('Ridge regression with many exogenous variable')
for scorer in ['neg_mean_squared_error', r2_scorer]:
    model = Ridge(alpha=100.0)
    cv_scores = cross_val_score(model, X, y, cv=10, scoring=scorer)
    if scorer == 'neg_mean_squared_error':
        mse_scores = -cv_scores
        rmse_scores = np.sqrt(mse_scores)
        rmse_mean = rmse_scores.mean()
        rmse_std = rmse_scores.std()
        print('Root Mean Squared Error:', rmse_mean)
        print('Standard Deviation:', rmse_std)
    else:
        r2_mean = cv_scores.mean()
        r2_std = cv_scores.std()
        print('Cross-Validation R-squared Mean:', r2_mean)
        print('Cross-Validation R-squared Standard Deviation:', r2_std)

y = df1.iloc[:, 1]
X = df1.iloc[:, 3:]
final_model = LinearRegression()
final_model.fit(X, y)
new_X = df1.iloc[:, 1:-2]
y_pred = pd.Series(final_model.predict(new_X))

# final model and prediction
output_df = pd.concat([df1[['player_id', 2023]], y_pred.rename('pred_values')], axis=1)
sorted_output = output_df.sort_values(by='pred_values', ascending=False)
print(sorted_output.head(10))



