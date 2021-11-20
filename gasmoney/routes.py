from datetime import datetime
from flask import render_template, redirect, flash, request
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from gasmoney import app, db
from gasmoney.forms import RegistrationForm, LoginForm, ReservationForm
from gasmoney.models import User, Ride, Reservation
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/', methods=["GET", "POST"])
def home():
    form = ReservationForm(meta={'csrf': False})
    return render_template("home.html", form=form)

@app.route('/rides')
def rides():
    form = ReservationForm(request.args, meta={'csrf': False})
    if not form.validate():
        # TODO: POST invalid form to home page
        flash('Invalid Request', 'danger')
        return redirect(url_for('home'))

    origin = form.origin.data
    destination = form.destination.data
    seats_required = form.seats_required.data
    departure_dt = datetime.combine(
        form.departure_before_date.data, 
        form.departure_before_time.data)
    
    # TODO: order_by closest requested date
    per_page = request.args['per_page'] or 20
    page = request.args['page'] or 1

    pagination = Ride.query.filter(
        Ride.origin.contains(origin),
        Ride.destination.contains(destination),
        Ride.seats_available >= seats_required,
        Ride.departure_dt >= departure_dt,
    ).paginate(per_page=per_page, page=page, error_out=True)
    return render_template("rides.html", pagination=pagination)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login Successfull', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessfull. Please check email and password.', 'danger')
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
