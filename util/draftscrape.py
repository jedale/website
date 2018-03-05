# scrapes NFL draft data from PFR
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from scipy.interpolate import UnivariateSpline

# grabs draft data from PFR for years start to end
def scrapeDraftData(start, end):
    urlprefix = 'https://www.pro-football-reference.com/years/'
    urlend = '/draft.htm'
    
    # will be filling in and returning this guy
    master = pd.DataFrame()
    
    for year in range(start, end + 1):
        print('Processing year ', year)
        url = urlprefix + str(year) + urlend
        html = urlopen(url).read()
        soup = BeautifulSoup(html, 'lxml')
        
        column_headers = [th.getText() for th in 
                         soup.findAll('tr', limit=2)[1].findAll('th')]
        
        data_rows = soup.findAll('tr')[2:]
        
        # why do we look for both 'th' and 'td'? Because PFR uses the 'th' tag
        # for the round in its tables
        draft_data = [[td.getText() for td in data_rows[i].findAll(['th', 'td'])]
                     for i in range(len(data_rows))]
        
        df = pd.DataFrame(draft_data, columns = column_headers)
        
        # having gotten a year of draft data, begin janitoring.
        # first task? For comprehensibility on the site PFR repeats
        # table headers after each round. But they are easily detected
        df = df[df.Rnd != 'Rnd']
        
        # tackles are not tracked for every year. If the column doesn't exist
        # we have to insert it. 
        if not 'Tkl' in df.columns:
            df.insert(loc=25, column='Tkl', value=0)

        # add a column for year; make it the first column
        df.insert(loc=0, column='Year', value = year)
        
        # last column just has a link to college stats; don't care
        df = df.drop(labels='', axis=1)
                
        # need to rename a bunch of columns
        # could do this in place but there's sufficiently many that it's 
        # worth doing in bulk
        df.columns = ['Year', 
                      'Round',
                      'Pick',
                      'Team',
                      'Player',
                      'Position',
                      'Age',
                      'To', # table records last year player played
                      'AP1', # first team all pro selections
                      'PB', #pro bowl appearances
                      'St', # years as a starter
                      'CarAV',
                      'DrAV',
                      'Games',
                      'Pass_Cmp', #passing stats here
                      'Pass_Att',
                      'Pass_Yds',
                      'Pass_TD',
                      'Pass_Int',
                      'Rush_Att', #rushing stats here
                      'Rush_Yds',
                      'Rush_TD',
                      'Rec', #receiving stats
                      'Rec_Yds',
                      'Rec_TD',
                      'Def_Tkl', #defensive stats
                      'Def_Int',
                      'Def_Sk',
                      'College/Univ']
        
        # convert stuff 
        # TODO: deprecated; should fix this later
        df = df.convert_objects(convert_numeric = True)
        
        # Missing values should just be zero
        df = df[:].fillna(0)
        
        # more bits of cleaning I've encountered along the way
        df = df[df.Team != 0]
        df = df[df.Team != '']

        
        master = master.append(df, ignore_index = True)
    
    return master

df_draft = scrapeDraftData(1990, 2017)

# some teams have moved over the years; fix things up
# SDG = Chargers = LAC
# RAI = Raiders = Oakland
# RAM = Rams = LAR
# PHO = Phoenix = ARI
# STL = Rams = LAR
# iterate over a dictionary for this
fixedteams = {'SDG': 'LAC',
              'RAI': 'OAK',
              'RAM': 'LAR',
              'PHO': 'ARI',
              'STL': 'LAR'}

for old in fixedteams:
    df_draft.loc[df_draft['Team'] == old,'Team'] = fixedteams[old]

# one more thing; Houston before 1996 is really Tennessee. Cleveland before '96 is really Baltimore.
# The current Houston team is a new franchise, so is the current Cleveland team. At least for these purposes.
df_draft.loc[(df_draft['Team'] == 'HOU') & (df_draft['Year'] < 1997), 'Team'] = 'TEN'
df_draft.loc[(df_draft['Team'] == 'CLE') & (df_draft['Year'] < 1996), 'Team'] = 'BAL'

# compute residual value for every player in every draft
for year in df_draft.Year.unique():
    y = df_draft[df_draft['Year'] == year].CarAV.values.reshape(-1, 1)
    x = np.linspace(1, len(y), len(y))
    s = UnivariateSpline(x, y, s=25000)
    yhat = s(x)
    df_draft.loc[df_draft['Year'] == year,'RV'] = df_draft[df_draft['Year'] == year].CarAV - yhat

# build data frames of mean and total RV# build a df of summed RV for every team for each year
column_headers = df_draft.Year.unique().tolist()
index_ordered = ['BUF', 'MIA', 'NYJ', 'NWE',
               'BAL', 'CIN', 'CLE', 'PIT',
               'IND', 'JAX', 'HOU', 'TEN',
               'DEN', 'KAN', 'LAC', 'OAK',
               'DAL', 'NYG', 'PHI', 'WAS',
               'CHI', 'DET', 'GNB', 'MIN',
               'ATL', 'CAR', 'NOR', 'TAM',
               'ARI', 'LAR', 'SFO', 'SEA']

df_RVSum = pd.concat([df_draft[df_draft['Year'] == year].groupby('Team').RV.sum() for year in df_draft.Year.unique()], axis=1)
df_RVSum.columns = column_headers
df_RVSum = df_RVSum.reindex(index = index_ordered)

df_RVmean = pd.concat([df_draft[df_draft['Year'] == year].groupby('Team').RV.mean()for year in df_draft.Year.unique()], axis=1)
df_RVmean.columns = column_headers
df_RVmean = df_RVmean.reindex(index = index_ordered)

df_RVSum.to_csv('draftRVSum.data')
df_RVmean.to_csv('draftRVMean.data')