from flask import Flask
from .config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_socketio import SocketIO

db= SQLAlchemy()
migrate= Migrate()
mail= Mail()
socketio= SocketIO()

def create_app(config_class= Config):
	app= Flask(__name__, instance_relative_config= True)
	print(app.instance_path)
	app.config.from_object(config_class)

	db.init_app(app)
	migrate.init_app(app, db)
	mail.init_app(app)
	socketio.init_app(app)
	
	with app.app_context():
		db.create_all()

	from .Auth import auth_bp
	app.register_blueprint(auth_bp, url_prefix= '/auth')

	from .Messenger import bp
	app.register_blueprint(bp)

	return app