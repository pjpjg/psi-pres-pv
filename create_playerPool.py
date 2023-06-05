import pandas as pd
from datetime import date, datetime

comps_df = pd.read_csv('transfermarkt-data/competitions.csv')
players_df = pd.read_csv('transfermarkt-data/players.csv')



# helper function to give an age given two dates
def get_age(birth, today):
    birth = datetime.strptime(birth, '%Y-%m-%d') # note that the input birth is string format rather than datetime
    age = today.year - birth.year
    if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
        age -= 1
    return age


# drop columns and rows and nan values
playerpool_df = players_df.drop(["first_name", "last_name", "player_code", "city_of_birth","country_of_citizenship",
                                 "market_value_in_eur", "highest_market_value_in_eur","agent_name", "image_url",
                                 "url", "contract_expiration_date"],
                                axis=1)  # contract_expiration_date dropped as it is not measured over time
# drop entries with na values
playerpool_df = playerpool_df.dropna()

# convert date-of-birth to age
today = date.today()
playerpool_df['date_of_birth'] = playerpool_df['date_of_birth'].apply(lambda x: get_age(x, today))
playerpool_df = playerpool_df.rename(columns={'date_of_birth' : 'age'})

# save df
playerpool_df.to_csv('created-data/playerpool.csv', index=False)
