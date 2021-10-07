from flask import render_template, redirect, flash
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from gasmoney import app, db
from gasmoney.forms import RegistrationForm
from gasmoney.models import User, Ride, Reservation

@app.route('/')
def index():
    return render_template("layout.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_passowrd = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        user = User(email=form.email.data, phone=form.phone.data, first_name=form.first_name.data, last_name=form.last_name.data, gender=form.gender.data, password=hashed_passowrd)
        db.session.add(user)
        db.session.commit()
        flash('Account Created Successfully', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/login')
def login():
    return '<h1>Log In</h1>'
