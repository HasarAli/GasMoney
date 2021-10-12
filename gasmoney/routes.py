from flask import render_template, redirect, flash
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from gasmoney import app, db
from gasmoney.forms import RegistrationForm, LoginForm
from gasmoney.models import User, Ride, Reservation
from flask_login import login_user

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

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successfull', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessfull. Please check email and password.', 'danger')
    return render_template("login.html", form=form)
