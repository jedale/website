# scrape salary cap data 
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

urlprefix = 'http://www.spotrac.com/nfl/'

years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017']

# Rams and Chargers have to be special cased because they moved
teams = ['arizona-cardinals',
		 'atlanta-falcons',
		 'baltimore-ravens',
		 'buffalo-bills',
		 'carolina-panthers',
		 'chicago-bears',
		 'cincinnati-bengals',
		 'cleveland-browns',
		 'dallas-cowboys',
		 'denver-broncos',
		 'detroit-lions',
		 'green-bay-packers',
		 'houston-texans',
		 'indianapolis-colts',
		 'jacksonville-jaguars',
		 'kansas-city-chiefs',
		 'miami-dolphins',
		 'minnesota-vikings',
		 'new-england-patriots',
		 'new-orleans-saints',
		 'new-york-giants',
		 'new-york-jets',
		 'oakland-raiders',
		 'philadelphia-eagles',
		 'pittsburgh-steelers',
		 'san-francisco-49ers',
		 'seattle-seahawks',
		 'tampa-bay-buccaneers',
		 'tennessee-titans',
		 'washington-redskins']

column_headers = ['Player', 
                  'Position',
                  'Base_Salary',
                  'Signing_Bonus',
                  'Roster_Bonus',
                  'Option_Bonus',
                  'Workout_Bonus',
                  'Restruct_Bonus',
                  'Misc',
                  'Dead_Cap',
                  'Cap_Hit',
                  'Cap_Pct']

# function that grabs a year/team combo of salary cap data
def GetCapData(year, team):
	print('Processing', team, 'for ' + year)
	url = urlprefix + team + '/cap/' + year
	html = urlopen(url).read()
	soup = BeautifulSoup(html, 'lxml')

	data_rows = soup.findAll('tr')[1:]
	cap_data = [[td.getText() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]
	df = pd.DataFrame(cap_data, columns=column_headers)

		# some cleanup
	df = df[:].fillna('')
	df = df[df.Player != ''].reset_index()
	drop = df.index[df.Player == year + ' NFL Salary Cap'][0]
	df = df.drop(df.index[drop:])

	# some cap hits are -, change to 0
	df.loc[df.Cap_Hit == '- ', 'Cap_Hit'] = '0'

	# cap hit needs to be a number
	df.Cap_Hit = df.Cap_Hit.replace('[\$,]', '', regex=True).astype(float)

	# add a column for year and team
	df.insert(loc=0, column='Year', value = year)
	df.insert(loc=1, column='Team', value = team)

	return df


# will be working with this guy
df = pd.DataFrame()

for team in teams:
	for year in years:
		df = df.append(GetCapData(year, team), ignore_index = True)

# Chargers and Rams have to be processed separately
team = 'san-diego-chargers'
years = ['2011', '2012', '2013', '2014', '2015', '2016']
for year in years:
	df = df.append(GetCapData(year, team), ignore_index = True)

df = df.append(GetCapData('2017', 'los-angeles-chargers'))	

team = 'st.-louis-rams'
years = ['2011', '2012', '2013', '2014', '2015']
for year in years:
	df = df.append(GetCapData(year, team), ignore_index = True)

for year in ['2016', '2017']:
	df = df.append(GetCapData(year, 'los-angeles-rams'), ignore_index = True)	
		
# adjust chargers and rams team names
df.loc[df.Team == 'st.-louis-rams', 'Team'] = 'los-angeles-rams'
df.loc[df.Team == 'san-diego-chargers', 'Team'] = 'los-angeles-chargers'
df.to_csv('NFLSalaryCap.data')

