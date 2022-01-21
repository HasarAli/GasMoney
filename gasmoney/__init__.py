from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sendgrid import SendGridAPIClient

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

sendgrid_client = SendGridAPIClient(api_key=app.config['SEND_GRID_API_KEY'])

from gasmoney import routes