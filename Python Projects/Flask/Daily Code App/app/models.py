from app import db, login_manager, app
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
	return Perdorues.query.get(int(user_id))

class Perdorues(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	emri_perdoruesit = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.png')
	password = db.Column(db.String(60), nullable=False)
	postim = db.relationship('Postim', backref='autori', lazy=True)

	
	def get_reset_token(self, expires_sec=420):
		s = Serializer(current_app.config['SECRET_KEY'],expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')


	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return Perdorues.query.get(user_id)

	def __repr__(self):
		return f"Perdorues('{self.emri_perdoruesit}', '{self.email}', '{self.image_file}')"

class Postim(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	titull = db.Column(db.String(100), nullable=False)
	data_postimit = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	permbajtja = db.Column(db.Text, nullable=False)
	imazhi = db.Column(db.String(), nullable=True)
	perdorues_id = db.Column(db.Integer, db.ForeignKey('perdorues.id'), nullable=False)

	def __repr__(self):
		return f"Postim('{self.titulli}', '{self.imazhi}', {self.data_postimit}')"