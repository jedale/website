from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse

import pandas as pd

from bokeh.models import (
	ColumnDataSource,
	HoverTool,
	LinearColorMapper,
	BasicTicker,
	PrintfTickFormatter,
	ColorBar,
	)
from bokeh.plotting import figure
from bokeh.embed import components


# testing visualization here
iris_df = pd.read_csv('data/iris.data',
	names=["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Species"])
feature_names = iris_df.columns[0:-1].values.tolist()

# create a plot
def create_figure(current_feature_name, bins):
	p = Histogram(iris_df, current_feature_name, title=current_feature_name, color='Species', 
	 	bins=bins, legend='top_right', width=600, height=400)

	p.xaxis.axis_label = current_feature_name
	p.yaxis.axis_label = 'Count'
	return p

@app.route('/')
@app.route('/index')
def index():
	# TODO: temp logic, fill with actual posts
	user = {'username': 'Jeff'}
	posts = [
		{
			'title': 'Placeholder Post',
			'author': {'username': 'Jeff'},
			'body': 'Someday there will be real content here. But for now visualizations at least work! '
		}
	]
	return render_template('index.html', title='Home', posts=posts)

@app.route('/about')
def about():
	return render_template('about.html', title='About Me')

@app.route('/jeff')
def jeff():
	return render_template('jeff.html', title='Jeff\'s CV')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))

		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			return redirect(url_for('index'))

		return redirect(next_page)

	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/regiter', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))

	return render_template('register.html', title='Register', form=form)



@app.route('/posts')
def analysis():
	return render_template('posts.html', title='Posts')


@app.route('/visualizations')
def visualizations():
	return render_template('visualizations.html', title='Visualizations')

@app.route('/visualizations/draft')
def vis_draft():
	# draft_vis.data is preformatted to display properly.
	# TODO: code to build it if it doesn't already exist
	df = pd.read_csv('data/draft_vis.data')

	# unfortunately have to change a type to make bokeh happy
	df.Year = df.Year.astype(str)

	# setup the plot
	years = list(df.Year.unique())
	teams = list(df.Team.unique())

	colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
	mapper = LinearColorMapper(palette=colors, low=df.SumRV.min(), high=df.SumRV.max())

	source = ColumnDataSource(df)

	TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

	p = figure(title="NFL Draft Performance ({0} - {1})".format(years[0], years[-1]),
          x_range = years, y_range = list(reversed(teams)),
          x_axis_location="above", plot_width=600, plot_height=600,
          tools=TOOLS, toolbar_location="below")
	p.grid.grid_line_color = None
	p.axis.axis_line_color = None
	p.axis.major_tick_line_color = None
	p.axis.major_label_text_font_size = "10pt"
	p.axis.major_label_standoff = 0

	p.rect(x="Year", y="Team", width=1, height=1,
		source=source,
		fill_color={'field': 'SumRV', 'transform': mapper},
		line_color=None)

	color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
		ticker=BasicTicker(desired_num_ticks=len(colors)),
		formatter=PrintfTickFormatter(format="%d"),
		label_standoff=6, border_line_color=None, location=(0,0))
	p.add_layout(color_bar, 'right')

	p.select_one(HoverTool).tooltips = [
		('Team', '@Team'),
		('Year', '@Year'),
		('Total Value', '@SumRV'),
	]

	script, div = components(p)

	return render_template('vis_draft.html', script=script, div=div,
	 title='NFL Draft Performance')
