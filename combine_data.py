import pandas as pd
pd.options.display.float_format = '{:.0f}'.format

# get the data
points_df = pd.read_csv('fantasy_football_rank/points.csv')
rankings_df = pd.read_csv('fantasy_football_rank/rankings.csv')
# make 'overall_rank' a float so we can use NaN
rankings_df['overall_rank'] = rankings_df['overall_rank'].astype('float64')

# remove recent/current weeks with incomplete data
LAST_WEEK_WITH_COMPLETE_DATA = 13
points_df = points_df[points_df['week'] <= LAST_WEEK_WITH_COMPLETE_DATA]
rankings_df = rankings_df[rankings_df['week'] <= LAST_WEEK_WITH_COMPLETE_DATA]

POSITIONS_LOOKING_AT = ['K']
rankings_df = rankings_df[rankings_df['position'].isin(POSITIONS_LOOKING_AT)]

weeks = points_df['week'].unique()
analysts = rankings_df.columns[4:]

# We don't want to keep all the analyst rankings. In a typical fantasy football league with
# 12 teams, we may only want to see the analyst performace on their top 12 rankings. If
# they have bad rankings on #25, for example, it is not important if their top 12 are accurate.
RANKINGS_TO_KEEP = 12
m = rankings_df.loc[:,analysts] <= RANKINGS_TO_KEEP
rankings_df.loc[:,analysts] = rankings_df.loc[:,analysts].where(m, pd.NA)
m = rankings_df.loc[:, 'overall_rank'] <= RANKINGS_TO_KEEP
rankings_df.loc[:, 'overall_rank'] = rankings_df.loc[:, 'overall_rank'].where(m, pd.NA)

# We need to create a relative points ranking for each player for each week, so we know who had
# the most points, second most, etc. 
for week in weeks:
    # create df of data from that week, sorted by points, descending
    points_week = points_df[points_df['week']==week].sort_values('points', ascending=False)
    # create a ranking of the points column. Use 'min' method so ties get the same ranking
    # and then you skip the next rank
    points_rank = points_week['points'].rank(method='min', ascending=False)
    # add the weekly ranking to the main data df
    points_df.loc[points_df['week']==week, 'ranking'] = points_rank

pd.set_option('display.max_rows', None)

# merge 
data = rankings_df.merge(points_df, how='inner', on=['week', 'name', 'position']) #.fillna(33)

data['overall_error'] = (data['overall_rank'] - data['ranking']).abs()

for analyst in analysts:
    data[analyst + '_error'] = (data[analyst] - data['ranking']).abs()

analyst_total_error = data.filter(regex='_error').sum()
print(analyst_total_error)

analyst_monthly_error = data.filter(regex='_error|week').groupby(by=['week']).sum()
print(analyst_monthly_error)

data.to_csv(f'Errors_analysis.csv')
