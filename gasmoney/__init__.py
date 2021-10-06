from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '0106a27624e960346ad0a1415b56cac9'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from gasmoney import routes 