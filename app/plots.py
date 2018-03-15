# code for various visualizations 
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

# tree structure for salary cap visualization
# TODO: probably some abstraction to be done here
class Node:
    
    def __init__(self, label, data):
        self.label = label
        self.data = data
        self.children = None

# tree structure for a single NFL Team
NFLTeam = Node('Team',0)
NFLTeam.children = [Node('Offense', 0),
                    Node('Defense', 0),
                    Node('SpecialTeams', 0)]
NFLTeam.children[0].children = [Node('QB', 0),
                                Node('RB', 0),
                                Node('OL', 0),
                                Node('TE', 0),
                                Node('WR', 0)]
NFLTeam.children[1].children = [Node('DL', 0),
                                Node('LB', 0),
                                Node('DB', 0)]
NFLTeam.children[2].children = [Node('K', 0),
                                Node('P', 0),
                                Node('LS', 0)]
NFLTeam.children[0].children[1].children = [Node('FB', 0),
                                            Node('HB', 0)]
NFLTeam.children[0].children[2].children = [Node('T', 0),
                                            Node('G', 0),
                                            Node('C', 0),
                                            Node('LT', 0)]
NFLTeam.children[1].children[0].children = [Node('NT', 0),
                                            Node('DT', 0),
                                            Node('DE', 0)]
NFLTeam.children[1].children[1].children = [Node('OLB', 0),
                                            Node('ILB', 0),
                                            Node('MLB', 0)]
NFLTeam.children[1].children[2].children = [Node('CB', 0),
                                            Node('S', 0),
                                            Node('FS', 0),
                                            Node('SS', 0)]

colors = {
    'Offense' : '#78BE20',
    'QB' : '#78BE20',
    'TE' : '#78BE20',
    'G' : '#78BE20',
    'LT' : '#78BE20',
    'WR' : '#78BE20',
    'RB' : '#78BE20',
    'C' : '#78BE20',
    'OL': '#78BE20',
    'RT' : '#78BE20',
    'T' : '#78BE20',
    'FB' : '#78BE20',
    'Defense' : '#0C2340',
    'DE' : '#0C2340',
    'FS' : '#0C2340',
    'DT' : '#0C2340',
    'ILB' : '#0C2340',
    'OLB' : '#0C2340',
    'CB' : '#0C2340',
    'SS' : '#0C2340',
    'S' : '#0C2340',
    'LB' : '#0C2340',
    'DB' : '#0C2340',
    'DL' : '#0C2340',
    'SpecialTeams' : '#A2AAAD',
    'P' : '#A2AAAD',
    'K' : '#A2AAAD',
    'LS' : '#A2AAAD'
}


# uses squarify to generate a list of rectangles for the treemap
def treemap(queue, glyphs):
    if len(queue) == 0:
        return
        
    node = queue[0]
    queue.pop(0)
        
    if node.children:
        # squarify the children based on parent coordinates
        values = list()
        [values.append(child.data) for child in node.children]
        values = squarify.normalize_sizes(values, node.dx, node.dy)
        rects = squarify.padded_squarify(values, 
                                  node.x, node.y, 
                                  node.dx, node.dy)
        
        # have to save glyph info so we can squarify children
        for i in range(len(node.children)):
            node.children[i].x = rects[i]['x']
            node.children[i].y = rects[i]['y']
            node.children[i].dx = rects[i]['dx']
            node.children[i].dy = rects[i]['dy']
            rects[i]['label'] = node.children[i].label
              
        [queue.append(child) for child in node.children]
        [glyphs.append(rect) for rect in rects]
        
    treemap(queue, glyphs)

# populate the tree via a reverse order traversal
def filltree(node, data):    
    if node.children:
        total = 0
        for child in node.children:
            filltree(child, data)
            total = total + child.data
        node.data = total + data[data.Position == node.label].Cap_Hit.sum()
    else:
        # node doesn't have children; just populate it based on label
        node.data = data[data.Position == node.label].Cap_Hit.sum()

def preptree(node):
    if node.children:
        for child in node.children:
            preptree(child)
        # remove nodes that have zero value
        node.children = [x for x in node.children if x.data != 0]
        node.children.sort(key=lambda x: x.data, reverse=True)
    

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

def CapTreemap():
	# TODO: this is just a placeholder demo

	# get the data
	df = pd.read_csv('data/Seahawks_Cap_2017.data')
	Seahawks = NFLTeam

	filltree(Seahawks, df)
	preptree(Seahawks)

	queue = list()
	Seahawks.x = 0
	Seahawks.y = 0
	Seahawks.dx = 600
	Seahawks.dy = 600
	queue.append(Seahawks)

	glyphs = list()

	treemap(queue, glyphs)


	# get data
	x_range = Range1d(0, 600, bounds=(0, 600))
	y_range = Range1d(0, 600, bounds=(0, 600))

	TOOLS = "hover,save"

	p = figure(title='Seattle Seahawks Salary Cap Usage (2017)',
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