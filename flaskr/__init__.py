from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = '0106a27624e960346ad0a1415b56cac9'

from flaskr import routes 