from flask import render_template, url_for
from flaskr import app
from flaskr.forms import RegistrationForm

@app.route('/')
def index():
    return '<h1>Hey There!</h1>'

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template("register.html", form=form)