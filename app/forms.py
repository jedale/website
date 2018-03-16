from app.models import User

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
		'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise Validationerror('Username taken. Please choose another.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email address already in use. Please choose another.')

class PlotChoiceForm(FlaskForm):
	plotchoice = SelectField(label='Plot Type?', choices=[
		('sum', 'Total Value (by team)'), 
		('mean', 'Pick Efficiency (by team)'),
		('possum', 'Total Value (by position)'),
		('posmean', 'Pick Efficiency (by position)')])
	submit = SubmitField('Choose')

class TreemapForm(FlaskForm):
	team = SelectField(label='Team', choices=[
		('arizona-cardinals', 'Arizona Cardinals'),
		('atlanta-falcons', 'Atlanta Falcons'),
		('baltimore-ravens', 'Baltimore Ravens'),
		('buffalo-bills', 'Buffalo Bills'),
		('carolina-panthers', 'Carolina Panthers'),
		('chicago-bears', 'Chicago Bears'),
		('cincinnati-bengals', 'Cincinnati Bengals'),
		('cleveland-browns', 'Cleveland Browns'),
		('dallas-cowboys', 'Dallas Cowboys'),
		('denver-broncos', 'Denver Broncos'),
		('detroit-lions', 'Detroit Lions'),
		('green-bay-packers', 'Green Bay Packers'),
		('houston-texans', 'Houston Texans'),
		('indianapolis-colts', 'Indianapolis Colts'),
		('jacksonville-jaguars', 'Jacksonville Jaguars'),
		('kansas-city-chiefs', 'Kansas City Chiefs'),
		('los-angeles-chargers', 'Los Angeles Chargers'),
		('los-angeles-rams', 'Los Angeles Rams'),
		('miami-dolphins', 'Miami Dolphins'),
		('minnesota-vikings', 'Minnesota Vikings'),
		('new-england-patriots', 'New England Patriots'),
		('new-orleans-saints', 'New Orleans Saints'),
		('new-york-giants', 'New York Giants'),
		('new-york-jets', 'New York Jets'),
		('oakland-raiders', 'Oakland Raiders'),
		('philadelphia-eagles', 'Philadelphia Eagles'),
		('pittsburgh-steelers', 'Pittsburgh Steelers'),
		('san-fransisco-49ers', 'San Fransisco 49ers'),
		('seattle-seahawks', 'Seattle Seahawks'),
		('tampa-bay-buccaneers', 'Tampa Bay Buccaneers'),
		('tennessee-titans', 'Tennessee Titans'),
		('washington-redskins', 'Washington Redskins')
		])

	year = SelectField(label='Year', choices=[
		('2011', '2011'),
		('2012', '2012'),
		('2013', '2013'),
		('2014', '2014'),
		('2015', '2015'),
		('2016', '2016'),
		('2017', '2017')
		])

	submit = SubmitField('Show')

