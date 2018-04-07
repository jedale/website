# code for various visualizations 
# TODO: probably makes sense to wrap this all up as one class. Someday. 
import pandas as pd

from bokeh.models import (
	ColumnDataSource,
	HoverTool,
	LinearColorMapper,
	BasicTicker,
	PrintfTickFormatter,
	ColorBar,
	Range1d,
	Label
	)
from bokeh.models.glyphs import Quad, Text
from bokeh.plotting import figure
from bokeh.embed import components
import squarify
from app.treemap import Node, NFLTeam, colors, treemap, filltree, preptree, TeamName

# tree structure for salary cap visualization
# TODO: probably some abstraction to be done here

# draws a heatmap of draft success
# can be total team value (type='sum'), team pick efficiency (type='mean'),
# or position (type = 'pos')
def DraftHeatmap(type):
	# TODO: better labels for position groups
	# todo: dynamic dates
	start = 2010
	end = 2017
	x_range = Range1d(start-0.5, end+0.5, bounds=(1990-0.5, 2017+0.5))
	
	# TODO: maybe don't assume data files exist lol
	# TODO: set date range properly 
	if type == 'mean':
		df = pd.read_csv('data/draftRVMean.data')
		title = "NFL Draft Team Pick Efficiency ({0} - {1})".format(1990, 2017)
		y_range = list(reversed(df.Team.unique()))
		ydata = 'Team'
		tooltip = [
			('Team', '@Team'),
			('Year', '@Year'),
			('Mean Value', '@RV'),
		]
	elif type == 'possum':
		df = pd.read_csv('data/draftPosRVSum.data')
		title = "NFL Draft Position Success ({0} - {1})".format(1990, 2017)
		y_range = list(df.Position.unique())
		ydata = 'Position'
		tooltip = [
			('Position', '@Position'),
			('Year', '@Year'),
			('Total Value', '@RV'),
		]
	elif type == 'posmean':
		df = pd.read_csv('data/draftPosRVMean.data')
		title = "NFL Draft Position Pick Efficiency ({0} - {1})".format(1990, 2017)
		y_range = list(df.Position.unique())
		ydata = 'Position'
		tooltip = [
			('Position', '@Position'),
			('Year', '@Year'),
			('Mean Value', '@RV'),
		]
	else:
		df = pd.read_csv('data/draftRVSum.data')
		title = "NFL Draft Team Success ({0} - {1})".format(1990, 2017)
		y_range = list(reversed(df.Team.unique()))
		ydata = 'Team'
		tooltip = [
			('Team', '@Team'),
			('Year', '@Year'),
			('Total Value', '@RV'),
		]

	# make bokeh happy
	df.Year = df.Year.astype(str)

	# setup the plot
	years = list(df.Year.unique())
	# teams = list(df.Team.unique())

	colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
	mapper = LinearColorMapper(palette=colors, low=df.RV.min(), high=df.RV.max())

	source = ColumnDataSource(df)

	TOOLS = "hover,save,xpan,box_zoom,reset,wheel_zoom"
	
	p = figure(title=title,
          x_range = x_range, y_range = y_range,
          x_axis_location="above", plot_width=600, plot_height=600,
          tools=TOOLS, toolbar_location="below")
	p.grid.grid_line_color = None
	p.axis.axis_line_color = None
	p.axis.major_tick_line_color = None
	p.axis.minor_tick_line_color = None
	p.axis.major_label_text_font_size = "10pt"
	p.axis.major_label_standoff = 0


	p.rect(x="Year", y=ydata, width=1, height=1,
		source=source,
		fill_color={'field': 'RV', 'transform': mapper},
		line_color=None)

	color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
		ticker=BasicTicker(desired_num_ticks=len(colors)),
		formatter=PrintfTickFormatter(format="%d"),
		label_standoff=6, border_line_color=None, location=(0,0))
	p.add_layout(color_bar, 'right')

	p.select_one(HoverTool).tooltips = tooltip

	return p

def CapTreemap(team, year):
	# TODO: this is just a placeholder demo

	# get the data
	df = pd.read_csv('data/NFLSalaryCap.data')
	Team = NFLTeam

	filltree(Team, df[(df['Team'] == team) & (df['Year'] == year)])
	preptree(Team)

	queue = list()
	Team.x = 0
	Team.y = 0
	Team.dx = 600
	Team.dy = 600
	queue.append(Team)

	glyphs = list()

	treemap(queue, glyphs)


	# get data
	x_range = Range1d(0, 600, bounds=(0, 600))
	y_range = Range1d(0, 600, bounds=(0, 600))

	TOOLS = "hover,save"

	p = figure(title=TeamName[team] +' Cap Usage (' + str(year) +')',
		x_range = x_range, y_range=y_range,
		plot_width=600, plot_height=600)
	p.grid.grid_line_color = None
	p.axis.visible = False
	# p.axis.axis_line_color = None
	# p.axis.major_tick_line_color = None
	# p.axis.minor_tick_line_color = None
	# p.axis.major_label_standoff = 0
	# p.axis.major_label_text_font_size = '10pt'

	for glyph in glyphs:
		rect = Quad(left=glyph['x'],
					right = glyph['x'] + glyph['dx'],
					bottom = glyph['y'],
					top = glyph['y'] + glyph['dy'],
					fill_color = colors[glyph['label']])

		if glyph['label'] in ['Offense', 'Defense', 'SpecialTeams']:
			label = Label(x = glyph['x'] + glyph['dx']/2,
	                      y = glyph['y'] + glyph['dy']/2,
	                      text = glyph['label'],
	                      text_font_size='14pt', text_font_style='bold',
	                      text_color='white')
		elif glyph['label'] in ['LB', 'OL', 'DL', 'DB', 'RB']:
			label = Label(x = glyph['x'], 
	                      y = glyph['y'] + glyph['dy'] - 20,
	                      text = glyph['label'],
	                      text_font_style='bold', text_color='white')
		else:
			label = Label(x = glyph['x'],
	                      y = glyph['y'],
	                      text=glyph['label'],
	                      text_font_style='bold', text_color='white') 
		p.add_glyph(rect)
		p.add_layout(label)

	return p