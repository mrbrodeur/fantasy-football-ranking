import pandas as pd

pd.options.display.float_format = '{:.2f}'.format

# get the data
points_df = pd.read_csv('data/points.csv')
rankings_df = pd.read_csv('data/rankings.csv')
# make 'overall_rank' a float so we can use NaN
rankings_df['overall_rank'] = rankings_df['overall_rank'].astype('float64')

# remove recent/current weeks with incomplete data
LAST_WEEK_WITH_COMPLETE_DATA = 13
points_df = points_df[points_df['week'] <= LAST_WEEK_WITH_COMPLETE_DATA]
rankings_df = rankings_df[rankings_df['week'] <= LAST_WEEK_WITH_COMPLETE_DATA]

POSITIONS_LOOKING_AT = ['K']
points_df = points_df[points_df['position'].isin(POSITIONS_LOOKING_AT)]
rankings_df = rankings_df[rankings_df['position'].isin(POSITIONS_LOOKING_AT)]

weeks = points_df['week'].unique()
analysts = rankings_df.columns[3:]

# We don't want to keep all the analyst rankings. In a typical fantasy football league with
# 12 teams, we may only want to see the analyst performace on their top 12 rankings. If
# they have bad rankings on #25, for example, it is not important if their top 12 are accurate.
RANKINGS_TO_KEEP = 12
m = rankings_df.loc[:,analysts] <= RANKINGS_TO_KEEP
rankings_df.loc[:,analysts] = rankings_df.loc[:,analysts].where(m, pd.NA)

# We need to create a relative points ranking for each player for each week, so we know who had
# the most points, second most, etc. 
for position in POSITIONS_LOOKING_AT:
    for week in weeks:
        # create df of data from that week, sorted by points, descending
        points_week = points_df[(points_df['week']==week) & (points_df['position']==position)].sort_values('points', ascending=False)
        # create a ranking of the points column. Use 'min' method so ties get the same ranking
        # and then you skip the next rank
        points_rank = points_week['points'].rank(method='min', ascending=False)
        # add the weekly ranking to the main data df
        points_df.loc[(points_df['week']==week) & (points_df['position']==position), 'ranking'] = points_rank

pd.set_option('display.max_rows', None)

# merge 
data = rankings_df.merge(points_df, how='inner', on=['week', 'name', 'position'])

analyst_names_error_list = []
for analyst in analysts:
    data[analyst + '_error'] = (data[analyst] - data['ranking']).abs()
    analyst_names_error_list.append(analyst + '_error')

data.to_csv('Errors_analysis_export_widedata.csv')
print(data.head(10))

# create a 'long' version of the data with each prediction getting its own row
data_long = pd.melt(
    data, 
    id_vars=['week', 'position', 'name'], 
    value_vars=analyst_names_error_list, 
    var_name='analyst', 
    value_name='error'
    )
data_long.to_csv('Errors_analysis_export_long.csv')

print(data_long.head(10))

