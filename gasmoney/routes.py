from datetime import datetime, date, time
from flask import render_template, redirect, flash, request
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from gasmoney import app, db
from gasmoney.forms import RegistrationForm, LoginForm, ReservationForm, RideForm
from gasmoney.models import User, Ride, Reservation
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/', methods=["GET", "POST"])
def home():
    form = ReservationForm(meta={'csrf': False})
    return render_template("home.html", form=form)

@app.route('/rides')
def rides():
    form = ReservationForm(request.args, meta={'csrf': False})

    origin = form.origin.data or ''
    destination = form.destination.data or ''
    seats_required = form.seats_required.data or 1
    d = form.departure_date.data or date.today()
    t = form.departure_time.data or time()
    departure_dt = datetime.combine(d, t)
    
    per_page = request.args.get('per_page', 20, type=int)
    page = request.args.get('page', 1, type=int)

    pagination = Ride.query.filter(
        Ride.origin.contains(origin),
        Ride.destination.contains(destination),
        Ride.seats_available >= seats_required,
        Ride.departure_dt >= departure_dt,
        Ride.status == 0
        ).order_by(Ride.departure_dt). \
        paginate(per_page=per_page, page=page, error_out=True)
    return render_template("rides.html", pagination=pagination, current_user=current_user)

@app.route('/offer', methods=["GET", "POST"])
@login_required
def offer():
    form = RideForm()
    if form.validate_on_submit():
        ride = Ride(
            driver_id=current_user.id, 
            origin=form.origin.data, 
            destination=form.destination.data, 
            rendezvous=form.rendezvous.data,
            departure_dt=datetime.combine(
                form.departure_date.data, 
                form.departure_time.data), 
            seats_offered=form.seats.data)
        try:
            db.session.add(ride)
            db.session.commit()
            flash('Ride Added Successfully', 'success')
        except:
            flash('Something Went Wrong. Try Again.', 'danger')
            return redirect(url_for('offer'))
        return redirect(url_for('home'))
    return render_template("offer.html", form=form)

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
