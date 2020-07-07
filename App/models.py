from App import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import time
from flask import current_app
import jwt

class Friendship(db.Model):
	__tablename__= "friendship"

	id= db.Column(db.Integer, nullable= False, primary_key= True)
	from_id= db.Column(db.Integer, db.ForeignKey('user.id'))
	to_id= db.Column(db.Integer, db.ForeignKey('user.id'))
	status= db.Column(db.Boolean, default= False)
	updated= db.Column(db.DateTime, index= True, default= datetime.utcnow)

	__table_args__= (db.UniqueConstraint('from_id', 'to_id', name='relation'),)

	def __repr__(self):
		return "from {}, to {} status {}".format(self.from_id, self.to_id, self.status)

class User(db.Model):
	"""id, name, email-address, password_hash, about_me"""

	__tablename__= 'user'
	
	id= db.Column(db.Integer, primary_key= True, nullable= False)

	username= db.Column(db.String(32), unique= True, nullable= False, index= True)

	email= db.Column(db.String(80), unique= True, nullable= False, index= True)

	password_hash= db.Column(db.String(256))

	gender= db.Column(db.String(8), nullable= False)

	about_me= db.Column(db.String(128))

	verified= db.Column(db.Boolean, default= True)
	# in production make the default to false

	# profile_picture= db.Column(db.String, nullable= True)

	last_seen= db.Column(db.DateTime, default= datetime.utcnow)
	
	sent= db.relationship('Chat', backref= 'author', foreign_keys= 'Chat.sender', lazy= 'dynamic')

	received= db.relationship('Chat', backref= 'recipient', foreign_keys= 'Chat.receiver', lazy= 'dynamic')

	received_requests= db.relationship('User',
		secondary= 'friendship',
		primaryjoin= db.and_(Friendship.to_id == id, Friendship.status == False),
		secondaryjoin= db.and_(Friendship.from_id == id, Friendship.status == False),
		order_by= Friendship.updated.desc()
		)

	sent_requests= db.relationship('User',
		secondary= 'friendship',
		primaryjoin= db.and_(Friendship.from_id == id, Friendship.status == False),
		secondaryjoin= db.and_(Friendship.to_id == id, Friendship.status == False),
		order_by= Friendship.updated.desc()
		)

	sent_friends=db.relationship('User',
		secondary= 'friendship',
		primaryjoin= db.and_(Friendship.from_id == id, Friendship.status == True),
		secondaryjoin= db.and_(Friendship.to_id == id, Friendship.status == True),
		order_by= Friendship.updated.desc()
		)

	received_friends=db.relationship('User',
		secondary= 'friendship',
		primaryjoin= db.and_(Friendship.to_id == id, Friendship.status == True),
		secondaryjoin= db.and_(Friendship.from_id == id, Friendship.status == True),
		order_by= Friendship.updated.desc()
		)

	# ---------------------------------------------
	def check_relation(self, id):
		friend= Friendship.query.filter((Friendship.from_id == self.id) & (Friendship.to_id == id)).first()
		if friend is None:
			friend= Friendship.query.filter((Friendship.from_id == id) & (Friendship.to_id == self.id)).first()
		return friend

	def user_status(self, id):
		friend= self.check_relation(id)
		if friend is None:
			return 0
		elif friend.status == False:
			if friend.from_id == self.id:
				return 1
			else:
				return 2
		else:
			return 3

	def all_friends(self):
		friends= self.sent_friends.copy()
		friends.extend(self.received_friends)
		return friends

	def send_request(self, id):
		check= self.user_status(id)
		if check == 0:
			try:
				db.session.add(Friendship(from_id= self.id, to_id= id))
				db.session.commit()
			except:
				return "Something Unexpected Occured"
			return True

		elif check == 3:
			return "Already Friends."
		else:
			return "Request is pending."			

	def accept_request(self, id):
		friend= self.check_relation(id)
		if friend is None:
			return "Please send a request first!"
		elif friend.status == False:
			friend.status= True
			friend.updated= datetime.utcnow()
			try:
				db.session.commit()
			except:
				return "Something Unexpected Occured"
			return True
		else:
			return "Already Friends."

	def unfriend(self, id):
		# this same method is being userd for delete request
		friend= self.check_relation(id)
		if friend is None:
			return "Please send a request first!"
		else:
			try:
				db.session.delete(friend)
				db.session.commit()
			except:
				return "Something Unexpected Occured"
			
			return True
	# ---------------------------------------------

	# ---------------------------------------------
	def set_password(self, password):
		self.password_hash= generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __init__(self, username, email, password, gender, about_me= None,  *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.username= 	username
		self.email=	email
		self.set_password(password)
		self.gender= bool(gender)
		self.about_me= about_me
	# ---------------------------------------------

	# ---------------------------------------------		
	def get_token(self):
		return jwt.encode(
			{'token': self.id, 'exp': time() + current_app.config['EMAIL_EXPIRY']},
			current_app.config['SECRET_KEY'], 
			algorithm='HS256'
			).decode('utf-8')

	@staticmethod 
	def verify_token(token):
		try:
			id= jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['token']
		except:
			return 	
		return id
	# ---------------------------------------------	

	def __repr__(self):
		return 'User object: id {} username {}'.format(self.id, self.username)

class Chat(db.Model):
	__tablename__=  "chat"

	id= db.Column(db.Integer, primary_key= True, nullable= False)

	message= db.Column(db.String(), nullable= False)

	sender= db.Column(db.Integer, db.ForeignKey('user.id'))

	receiver= db.Column(db.Integer, db.ForeignKey('user.id'))

	timestamp= db.Column(db.DateTime, index= True, default= datetime.utcnow)

	def __init__(self, message, sender_id, receiver_id, timestamp= datetime.utcnow, *args, **kwargs):
		self.message= message
		self.sender_id= sender_id
		self.receiver_id= receiver_id	

	def __repr__(self):
		return 'Chat object: sender_id {} and receiver_id {}'.format(self.sender_id, self.receiver_id)
