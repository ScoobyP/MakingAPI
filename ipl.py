import numpy as np
import pandas as pd


df = pd.read_csv('/Users/ishanp/Downloads/IPL_Matches_2008_2022.csv')

df.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)
df.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
df.replace('Rising Pune Supergiants', 'Rising Pune Supergiant', inplace=True)


def All_teams_API():
    teams = list(df['Team1'].unique())
    return {'Teams': teams}


def team_record_API(team_name):

    total_matches = df['Team1'].value_counts() + df['Team2'].value_counts()
    record = pd.DataFrame(total_matches)

    record.rename(columns={'count': 'Total Matches Played'}, inplace=True)

    record.sort_values('Total Matches Played', ascending=False, inplace=True)

    record['Wins'] = df['WinningTeam'].value_counts()

    def win_per(row):
        return round((row.iloc[1]/row.iloc[0])*100, 1)
    record['Win%'] = record.apply(win_per, axis=1)
    record['Title Wins'] = df[df['MatchNumber'] == 'Final']['WinningTeam'].value_counts()
    record['Title Wins'].fillna(0, inplace=True)
    wb = df[df['MatchNumber'] == 'Final'][['WinningTeam', 'WonBy']]
    wbw = wb[wb['WonBy'] == 'Wickets'].value_counts()

    record['Title Wins'] = record['Title Wins'].astype(np.int16)
    wbw = pd.DataFrame(wbw)
    record['Titles Won By Fielding first'] = wbw.droplevel(level=1)

    wbr = wb[wb['WonBy'] == 'Runs'].value_counts()
    wbr = pd.DataFrame(wbr)
    record['Titles Won By Batting first'] = wbr.droplevel(level=1)

    record['Titles Won By Fielding first'].fillna(0, inplace=True)
    record['Titles Won By Batting first'].fillna(0, inplace=True)
    record['Titles Won By Fielding first'] = record['Titles Won By Fielding first'].astype(np.int16)
    record['Titles Won By Batting first'] = record['Titles Won By Batting first'].astype(np.int16)

    record.reset_index(inplace=True)
    record.rename(columns={'index': 'Teams'}, inplace=True)

    def most_against(team):
        matches_played = df[(df['Team1'] == team) | (df['Team2'] == team)]
        matches_played_against1 = matches_played[(matches_played['Team1'] != team)]
        matches_played_against2 = matches_played[(matches_played['Team2'] != team)]
        matches_played_against1 = matches_played_against1['Team1'].value_counts()
        matches_played_against2 = matches_played_against2['Team2'].value_counts()
        total_against = pd.DataFrame(pd.concat([matches_played_against1, matches_played_against2]))
        total_against.reset_index(inplace=True)
        total_against.rename(columns={'index': 'TeamName', 'count': 'Matches played against'}, inplace=True)
        most_played_against = total_against.groupby('TeamName')['Matches played against'].sum().sort_values(ascending=False).head(1)

        return most_played_against.index[0]  ##CHANGE HERE##

    record['Teams'].apply(most_against)
    most_aga_df = pd.DataFrame(record['Teams'].apply(most_against))
    most_aga_df.rename(columns={'Teams': 'Most Played Against'}, inplace=True)
    record = pd.concat([record, most_aga_df['Most Played Against']], axis=1)
    record = pd.DataFrame(record)

    def total_wb_battingfirst(teamx):
        entire_wins = df[df['WinningTeam'] == teamx]
        return entire_wins[entire_wins['WonBy'] == 'Runs'].shape[0]

    def total_wb_fieldingfirst(teamx):
        entire_wins = df[df['WinningTeam'] == teamx]
        return entire_wins[entire_wins['WonBy'] == 'Wickets'].shape[0]

    record.insert(4, 'Total WonBy Batting first', record['Teams'].apply(total_wb_battingfirst))

    record.insert(5, 'Total WonBy Fieldingfirst', record['Teams'].apply(total_wb_fieldingfirst))

    def super_over(teamX):
        total_victories = df[df['WinningTeam'] == teamX]
        return (total_victories['WonBy'] == 'SuperOver').sum()

    record.insert(6, 'Total WonBy SuperOver', record['Teams'].apply(super_over))

    record.set_index('Teams', inplace=True)

    return {'Team Record': record.loc[str(team_name)].to_dict()} #IMPORTANT: ELSE TABLE IS NOT JSON serilizable#
