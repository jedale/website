from app import app, db
from app.forms import LoginForm, RegistrationForm, PlotChoiceForm
from app.models import User
from app.plots import DraftHeatmap, CapTreemap

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
	Range1d
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

@app.route('/visualizations/draft', methods=['GET', 'POST'])
def vis_draft():
	form = PlotChoiceForm()

	if form.validate_on_submit():
		choice = form.plotchoice.data
	else:
		choice = 'sum'

	p = DraftHeatmap(choice)

	script, div = components(p)

	return render_template('vis_draft.html', script=script, div=div,
		form = form, title='NFL Draft Performance')

@app.route('/visualizations/cap', methods=['GET', 'POST'])
def vis_cap():

	p = CapTreemap()

	script, div = components(p)

	return render_template('vis_cap.html', script=script, div=div,
		title='NFL Salary Cap Usage')

	