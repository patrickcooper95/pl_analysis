import pandas as pd
import os

# Read in results data
results_path = os.path.join('PL Analysis', 'premier-league', 'results.csv')
pl_results = pd.read_csv(results_path)

# Filter the DF by boolean mask to fill a newly created 'winner' column with the home team name, away team name, or draw
pl_home_wins = pl_results['result'] == 'H'
pl_away_wins = pl_results['result'] == 'A'
pl_results['winner'] = pl_results.loc[pl_home_wins, 'home_team']
pl_results.loc[pl_away_wins, 'winner'] = pl_results['away_team']
pl_results['winner'] = pl_results['winner'].fillna('Draw')

# A dict container to hold as many tables as needed (final tables, weekly tables, etc.)
pl_tables = {}

# DataFrame used later to store our results - what was the table (and date) when the top team each season accumulated
# enough points to mathematically avoid finishing last?
final_gap_df = pd.DataFrame(columns=['Date', 'Top', 'Bottom', 'Top_Points', 'Bottom_Points', 'Matches_Played'])


# Because naming conventions are not standard across multiple sources of data, standardize team names through mapping.
# Also convert all seasons to "xx-xx" format instead of "20xx-20xx", also by way of mapping, so we can join DFs later.
team_names = {'Blackburn': 'Blackburn Rovers',
              'Bolton': 'Bolton Wanderers',
              'Stoke': 'Stoke City',
              'Wolves': 'Wolverhampton Wanderers',
              'Tottenham': 'Tottenham Hotspur',
              'Man United': 'Manchester United',
              'Man City': 'Manchester City',
              'Birmingham': 'Birmingham City',
              'Hull': 'Hull City',
              'West Brom': 'West Bromwich Albion',
              'Newcastle': 'Newcastle United',
              'Wigan': 'Wigan Athletic',
              'QPR': 'Queens Park Rangers',
              'Swansea': 'Swansea City',
              'Norwich': 'Norwich City',
              'West Ham': 'West Ham United',
              'Cardiff': 'Cardiff City',
              'Leicester': 'Leicester City',
              'Bournemouth': 'AFC Bournemouth',
              'Brighton': 'Brighton and Hove Albion',
              'Huddersfield': 'Huddersfield Town'}
seasons_map = {'2009-2010': '0910', '2010-2011': '1011', '2011-2012': '1112', '2012-2013': '1213', '2013-2014': '1314',
               '2014-2015': '1415', '2015-2016': '1516', '2016-2017': '1617', '2017-2018': '1718'}
pl_results['season'] = pl_results['season'].map(seasons_map, na_action='ignore')
pl_results['match_id'] = pl_results['season'] + pl_results['home_team'] + pl_results['away_team']

# Rows where Season is NaN are seasons we do not have schedule data for, so we will drop them.
pl_results = pl_results.dropna(subset=['season'])

# The seasons for which we have schedule data. sch_seasons dict will be a container for each season's schedule.
# We'll go ahead and fill this dict with these keys so we can read in the files by indexing keys.
schedule_keys = ['0910', '1011', '1112', '1213', '1314', '1415', '1516', '1617', '1718']
sch_seasons = {}
for key in schedule_keys:
    sch_seasons[key] = None

# Read in each csv with schedule data, dropping unnecessary columns, and mapping team names.
# We'll also create a unique match_id by concatenating the strings in the Season, HomeTeam, and AwayTeam columns.
for sc in schedule_keys:
    temp_path = os.path.join('PL Analysis', 'english-premier-league', 'data',
                             'season-' + sc + '_csv.csv')
    t_df = pd.read_csv(temp_path)
    t_df = t_df.drop(t_df.columns[4:], axis=1)
    t_df = t_df.drop('Div', axis=1)
    t_df['Season'] = sc
    t_df['HomeTeam'] = t_df['HomeTeam'].map(team_names).fillna(t_df['HomeTeam'])
    t_df['AwayTeam'] = t_df['AwayTeam'].map(team_names).fillna(t_df['AwayTeam'])
    t_df['match_id'] = t_df['Season'] + t_df['HomeTeam'] + t_df['AwayTeam']
    sch_seasons[sc] = t_df

# After creating a DataFrame for each season, combine them into one master schedule, to be joined with pl_results.
schedule_master = pd.DataFrame()
for season in sch_seasons.keys():
    schedule_master = pd.concat([schedule_master, sch_seasons[season]])

# It all comes together. All the PL results are merged with the dates/seasons they occurred.
pl_results = pl_results.merge(schedule_master, how='inner', on='match_id')
pl_results['Date'] = pd.to_datetime(pl_results['Date'])

# Make sure our names were correct and we joined every record. Prints a count of 3420, or 9 seasons, which is what we
# expect.
print(pl_results['match_id'].count())


"""
    The pl_results DataFrame now contains all the data necessary to create tables based on a specific date, within a 
    specific season. The function below can do this by receiving the a teams parameter and a specified list of 
    matches played.
    """


# Create tables for each date of each season.
def team_points(teams, temp_df, ppr, matchday):

    table = {}
    goals_for = {}
    goals_against = {}
    points_left = ppr
    matches = matchday

    for t in teams:
        match_df = temp_df[(temp_df['home_team'] == 'Manchester City') | (temp_df['away_team'] == 'Manchester City')]
        if match_df['home_team'].count() > matches:
            points_left -= 3
            matches += 1

        team = temp_df[(temp_df['home_team'] == t) | (temp_df['away_team'] == t)]
        no_of_wins = team.loc[team['winner'] == t, 'winner']
        wins = no_of_wins.count()
        no_of_draws = team.loc[team['winner'] == 'Draw', 'winner']
        draws = no_of_draws.count()
        points = (wins * 3) + draws
        home_gf = team.loc[team['home_team'] == t, 'home_goals']
        away_gf = team.loc[team['away_team'] == t, 'away_goals']
        home_ga = team.loc[team['home_team'] == t, 'away_goals']
        away_ga = team.loc[team['away_team'] == t, 'home_goals']
        tm_goals_for = home_gf.sum() + away_gf.sum()
        tm_goals_against = home_ga.sum() + away_ga.sum()
        goals_for.update({t: tm_goals_for})
        goals_against.update({t: tm_goals_against})
        table.update({t: points})
    table_df = pd.DataFrame.from_dict(table, orient='index', columns=['Points'])
    table_df['Goals For'] = pd.Series(goals_for).astype(int)
    table_df['Goals Against'] = pd.Series(goals_against).astype(int)
    table_df['Goal Diff'] = table_df['Goals For'] - table_df['Goals Against']
    table_df = table_df.sort_values(by=['Points', 'Goal Diff'], ascending=False)
    return table_df, matches, points_left


def get_table_on_date(df, t):
    ppr = 114
    matchday = 0
    top_to_bottom = 0

    for d in df['Date'].unique():
        date_df = df[df['Date'] <= d]
        table, matchday, ppr = team_points(t, date_df, ppr, matchday)
        top_to_bottom = table['Points'].max() - table['Points'].min()
        if top_to_bottom > ppr:
            return d, table, matchday


# Create list of teams that were in the PL each season
for s in schedule_keys:
    temp_df = pl_results[pl_results['season'] == s]
    teams = temp_df['home_team'].unique()
    final_date, final_table, mp = get_table_on_date(temp_df, teams)
    final_table['MP'] = mp
    pl_tables.update({s: final_table})
    answers_dict = {'Date': [final_date], 'Top': [final_table.index[0]], 'Bottom': [final_table.index[19]],
                    'Top_Points': [final_table['Points'].max()], 'Bottom_Points': [final_table['Points'].min()],
                    'Matches_Played': [final_table['MP'].max()]}
    data_df = pd.DataFrame(answers_dict)
    final_gap_df = pd.concat([final_gap_df, data_df], ignore_index=True)


# This can be used for UI to run from the command line.
def ui_table():
    print('Please select from the following options: ' + '\n')
    for k in pl_tables.keys():
        print(str(k) + '\n')
    selection = input("")
    print(pl_tables[selection])


def save_plot():
    print('\nCreating and saving scatter plot...')
    final_gap_df['Matches_Played'] = final_gap_df['Matches_Played'].astype(int)
    final_gap_df['Top_Points'] = final_gap_df['Top_Points'].astype(int)
    final_gap_df.drop(labels=['Date'], axis=1)
    ax1 = final_gap_df.plot.scatter(x='Matches_Played', y='Top_Points').get_figure()
    ax1.savefig('pl_scatter.pdf')


def write_files():
    print('\nWriting output files...')
    with pd.ExcelWriter('tables.xlsx') as writer:
        for k in pl_tables.keys():
            pl_tables[k].to_excel(writer, sheet_name=k)

    final_gap_df.to_excel('pl_analysis.xlsx')


write_files()
