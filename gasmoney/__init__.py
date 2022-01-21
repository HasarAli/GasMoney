from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from os import getenv

app = Flask(__name__, instance_relative_config=True)
if getenv('ENV') == 'PROD':
  app.config['SECRET_KEY'] = getenv('SECRET_KEY')
  app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URI')
  app.config['SEND_GRID_API_KEY'] = getenv('SEND_GRID_API_KEY')
  app.config['TWILIO_API_KEY'] = getenv('TWILIO_API_KEY')
  app.config['TWILIO_API_SECRET'] = getenv('TWILIO_API_SECRET')
  app.config['TWILIO_ACCOUNT_SID'] = getenv('TWILIO_ACCOUNT_SID')
  app.config['TWILIO_VERIFY_SERVICE'] = getenv('TWILIO_VERIFY_SERVICE')
else:
  app.config.from_object('config')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

sendgrid_client = SendGridAPIClient(api_key=app.config['SEND_GRID_API_KEY'])

twilio_verify_client = TwilioClient(app.config['TWILIO_API_KEY'], 
                            app.config['TWILIO_API_SECRET'], 
                            app.config['TWILIO_ACCOUNT_SID']) \
                            .verify.services(
                              app.config['TWILIO_VERIFY_SERVICE_SID']
                            )

from gasmoney import routes