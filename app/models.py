from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(128), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


# Posts represent posts made to the main page
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(128), index=True)
	body = db.Column(db.String(256)) # TODO: increase post size limit eventually
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	def __repr__(self):
		return '<Post {}>'.format(self.title)

# Comments represent comments users leave on posts
class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(256)) # TODO: increase comment size limit eventually
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	def __repr__(self):
		return '<Comment {}>'.format(self.body)

@login.user_loader
def load_user(id):
	return User.query.get(int(id))