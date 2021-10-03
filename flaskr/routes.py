from flask import render_template, redirect, flash
from flask.helpers import url_for
from flaskr import app
from flaskr.forms import RegistrationForm

@app.route('/')
def index():
    return render_template("layout.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account Created Successfully', 'success')
        return redirect(url_for('index'))
    return render_template("register.html", form=form)

@app.route('/login')
def login():
    return '<h1>Log In</h1>'
