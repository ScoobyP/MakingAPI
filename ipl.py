import numpy as np
import pandas as pd


df = pd.read_csv('/Users/ishanp/Downloads/IPL_Matches_2008_2022.csv')

df.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)
df.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
df.replace('Rising Pune Supergiants', 'Rising Pune Supergiant', inplace=True)


def All_teams_API():
    teams = sorted(list(df['Team1'].unique()))
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

    def most_against(team_nam):
        matches_played = df[(df['Team1'] == team_nam) | (df['Team2'] == team_nam)]
        matches_played_against1 = matches_played[(matches_played['Team1'] != team_nam)]
        matches_played_against2 = matches_played[(matches_played['Team2'] != team_nam)]
        matches_played_against1 = matches_played_against1['Team1'].value_counts()
        matches_played_against2 = matches_played_against2['Team2'].value_counts()
        total_against = pd.DataFrame(pd.concat([matches_played_against1, matches_played_against2]))
        total_against.reset_index(inplace=True)
        total_against.rename(columns={'index': 'TeamName', 'count': 'Matches played against'}, inplace=True)
        most_played_against = total_against.groupby('TeamName')['Matches played against'].sum().sort_values(ascending=False).head(1)
        print(team_nam)
        return str(most_played_against.index.to_numpy()[0]) + " " + '(' + str(most_played_against.iloc[0]) + ')'

    record.insert(7, 'Most Against', record['Teams'].apply(most_against))

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

    return {'Team Record': record.loc[str(team_name)].to_dict()}  # IMPORTANT: ELSE TABLE IS NOT JSON serilizable#


ipld = pd.read_csv('/Users/ishanp/Downloads/ipl_deliveries.csv')

ipld.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)
ipld.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
ipld.replace('Rising Pune Supergiants', 'Rising Pune Supergiant', inplace=True)

ipld['Out by bowler'] = (ipld['batter'] == ipld['player_out']) & (~ipld['kind'].isin(['retired out', 'run out', 'retired hurt', 'obstructing the field']))
iplm = pd.read_csv('/Users/ishanp/Downloads/IPL_Matches_2008_2022.csv')

iplm.replace('Delhi Daredevils', 'Delhi Capitals', inplace=True)
iplm.replace('Kings XI Punjab', 'Punjab Kings', inplace=True)
iplm.replace('Rising Pune Supergiants', 'Rising Pune Supergiant', inplace=True)

ndf = ipld.merge(iplm, on='ID')
rep_batrun_df = ndf.groupby(['Season', 'batter'])['batsman_run'].sum().reset_index()
rep_batout_df = ndf.groupby('Season')['player_out'].value_counts().reset_index(name='OUT').rename(columns={'player_out': 'batter'})
original_rep = rep_batrun_df.merge(rep_batout_df, how='outer', on=['Season', 'batter'])
original_rep['OUT'].fillna('Not OUT', inplace=True)
original_rep['batsman_run'].fillna(0, inplace=True)


def average(row):

    if row['batsman_run'] == 0:
        return 0
    elif row['OUT'] == 'Not OUT':
        return row['batsman_run']
    else:
        return round(int(row['batsman_run'])/int(row['OUT']), 2)


original_rep['Average'] = original_rep.apply(average, axis=1)
original_rep = original_rep.merge(ndf.groupby(['Season', 'batter']).size().reset_index(), on=['Season', 'batter'])

original_rep.rename(columns={0: 'All balls faced'}, inplace=True)
original_rep = original_rep.merge(ndf[ndf['extra_type'] == 'wides'].groupby(['Season', 'batter']).size().reset_index(), on=['Season', 'batter'])

original_rep.rename(columns={0: 'wides faced'}, inplace=True)


def balls_faced(row):
    return int(row['All balls faced'] - row['wides faced'])


original_rep['Actual balls faced'] = original_rep.apply(balls_faced, axis=1)


def strike_rate(row):
    return round((row['batsman_run']/row['Actual balls faced'])*100, 2)


original_rep['Strike Rate'] = original_rep.apply(strike_rate, axis=1)
bats_highest = ndf.groupby(['Season', 'ID', 'batter'])['batsman_run'].sum().reset_index().drop(columns='ID').groupby(['Season', 'batter'])['batsman_run'].max().reset_index().rename(columns={'batsman_run': 'Highest Match Score'})

original_rep = original_rep.merge(bats_highest, on=['Season', 'batter'])

original_rep = original_rep.merge(ndf.groupby(['Season', 'batter'])['ID'].nunique().reset_index().rename(columns={'ID': 'Innings'}), on=['Season','batter'])

final_table= original_rep[['Season', 'batter', 'batsman_run', 'Average', 'Strike Rate', 'Highest Match Score','Innings']]

final_table.set_index('Season', inplace=True)
final_table.index.name = None
final_table['batsman_run'] = final_table['batsman_run'].astype(np.int32)

def All_batsmen_API():
    batter = sorted(list(ipld['batter'].unique()))
    return {'Batsman': batter}


def batsman_record(batter):
    table = final_table[final_table['batter'] == str(batter)].copy()
    table.drop('batter', axis=1, inplace=True)
    return {'Batsman Record': table.to_dict(orient='index')}


def POM_names():
    pom = sorted((ndf['Player_of_Match'].unique()).astype('str'))
    return {'POM Names': pom}


def player_of_match_record(POM_player):
    POM_in_df = ndf[ndf['Player_of_Match'] == str(POM_player)]
    POM_runs = POM_in_df[POM_in_df['batter'] == POM_in_df['Player_of_Match']].groupby(['Season', 'ID', 'batter'])['batsman_run'].sum().reset_index()

    POM_batter = POM_in_df[POM_in_df['batter'] == str(POM_player)]
    POM_batter['Balls Counted'] = ~((POM_batter['extra_type'] == 'noballs') | (POM_batter['extra_type'] == 'wides'))
    mainPOM = POM_runs.merge(POM_batter.groupby(['Season', 'ID', 'batter'])['Balls Counted'].sum(), on=['Season', 'ID', 'batter'])

    def batting_fig(row):
        return str(row['batsman_run']) + '/' + str(row['Balls Counted'])

    mainPOM['Batting Figure'] = mainPOM.apply(batting_fig, axis=1)

    def against_team(id_num):
        all_de = ndf[ndf['ID'] == id_num]
        if POM_player in all_de['Team1Players'].drop_duplicates(keep='first').iloc[0]:
            return all_de['Team2'].drop_duplicates(keep='first').iloc[0]
        elif POM_player in all_de['Team2Players'].drop_duplicates(keep='first').iloc[0]:
            return all_de['Team1'].drop_duplicates(keep='first').iloc[0]

    mainPOM.insert(2, 'Against', mainPOM['ID'].apply(against_team))

    POM_in_df = ndf[ndf['Player_of_Match'] == str(POM_player)]
    POM_wic = POM_in_df[POM_in_df['bowler'] == POM_in_df['Player_of_Match']].groupby(['Season', 'ID', 'bowler'])['Out by bowler'].sum().reset_index()

    POM_bowling = POM_in_df[POM_in_df['bowler'] == POM_in_df['Player_of_Match']]
    POM_bol_fig = POM_wic.merge(POM_bowling.groupby(['Season', 'ID', 'bowler'])['total_run'].sum(), on=['Season', 'ID', 'bowler'])

    def bowl_fig(row):
        return str(row['Out by bowler']) + '/' + str(row['total_run'])

    POM_bol_fig['Bowling Figure'] = POM_bol_fig.apply(bowl_fig, axis=1)
    def against_(id_num):
        all_de = ndf[ndf['ID'] == id_num]
        if POM_player in all_de['Team1Players'].drop_duplicates(keep='first').iloc[0]:
            return all_de['Team2'].drop_duplicates(keep='first').iloc[0]
        elif POM_player in all_de['Team2Players'].drop_duplicates(keep='first').iloc[0]:
            return all_de['Team1'].drop_duplicates(keep='first').iloc[0]

    POM_bol_fig.insert(2, 'Against', POM_bol_fig['ID'].apply(against_))

    final_POM = mainPOM.merge(POM_bol_fig, how='outer', on=['Season', 'ID', 'Against'])

    final_POM = final_POM.drop(columns=['ID', 'batsman_run', 'Balls Counted', 'batter', 'bowler', 'Out by bowler', 'total_run'])
    final_POM.rename(columns={'Against_x': 'Against'}, inplace=True)
    #final_POM.set_index('Season', inplace=True)
    final_POM.rename(columns={'Batting Figure': 'Batting Figure (Runs/Balls)', 'Bowling Figure': 'Bowling Figure(Wkts/Runs)'}, inplace=True)
    final_POM.index +=1
    return {'Player of Match Record': final_POM.to_dict(orient='index')}

## Batsman record with opposing team
def against(row):
  if row['batter'] in row['Team1Players']:
    return row['Team2']
  else:
    return row['Team1']
ndf['Against'] = ndf.apply(against, axis=1)

aga_batrun_df = ndf.groupby(['Against','batter'])['batsman_run'].sum().reset_index()
aga_batout_df = ndf.groupby('Against')['player_out'].value_counts().reset_index(name= 'OUT').rename(columns={'player_out': 'batter'})
original_aga = aga_batrun_df.merge(aga_batout_df, how='outer', on=['Against', 'batter'])
original_aga['OUT'].fillna('Not OUT', inplace=True)
original_aga['batsman_run'].fillna(0, inplace=True)
def average(row):
  if row['batsman_run'] == 0:
    return 0
  elif row['OUT'] == 'Not OUT':
    return row['batsman_run']
  else:
    return round(int(row['batsman_run'])/int(row['OUT']),2)
original_aga['Average'] = original_aga.apply(average, axis=1)
original_aga = original_aga.merge(ndf.groupby(['Against', 'batter']).size().reset_index(), on=['Against', 'batter'])

original_aga.rename(columns={0: 'All balls faced'}, inplace=True)
original_aga = original_aga.merge(ndf[ndf['extra_type']== 'wides'].groupby(['Against','batter']).size().reset_index(), on=['Against', 'batter'])

original_aga.rename(columns={0: 'wides faced'}, inplace= True)

def balls_faced(row):
  return int(row['All balls faced'] - row['wides faced'])
original_aga['Actual balls faced'] = original_aga.apply(balls_faced, axis=1)
def strike_rate(row):
  return round((row['batsman_run']/row['Actual balls faced'])*100, 2)
original_aga['Strike Rate'] = original_aga.apply(strike_rate, axis=1)
bats_high_aga = ndf.groupby(['Against','ID','batter'])['batsman_run'].sum().reset_index().drop(columns='ID').groupby(['Against','batter'])['batsman_run'].max().reset_index().rename(columns={'batsman_run':'Highest Match Score'})

original_aga = original_aga.merge(bats_high_aga, on = ['Against', 'batter'])

original_aga=original_aga.merge(ndf.groupby(['Against','batter'])['ID'].nunique().reset_index().rename(columns={'ID':'Innings'}), on=['Against', 'batter'])

final_aga_table= original_aga[['Against', 'batter', 'batsman_run', 'Average', 'Strike Rate', 'Highest Match Score','Innings']]

final_aga_table.set_index('Against', inplace=True)
final_aga_table.index.name = None
final_aga_table['batsman_run']= final_aga_table['batsman_run'].astype(np.int32)

def batsman_against_record(batter):
    table = final_aga_table[final_aga_table['batter'] == str(batter)].copy()
    table.drop('batter', axis=1, inplace=True)
    return {'Batsman Against Record': table.to_dict(orient='index')}