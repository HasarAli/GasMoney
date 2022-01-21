from datetime import datetime, date, time
from functools import wraps
from flask import render_template, redirect, flash, request
from flask.helpers import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from gasmoney import app, db, twilio_verify_client, sendgrid_client
from gasmoney.forms import (RegistrationForm, LoginForm, ReservationForm, 
                            RideForm, SettingsForm, ResetPasswordForm, 
                            RequestResetForm, VerifyPhoneForm)
from gasmoney.models import User, Ride, Reservation
from flask_login import login_user, current_user, logout_user, login_required, fresh_login_required
from sqlalchemy import desc, or_
from sendgrid.helpers.mail import Mail


def verification_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        elif not current_user.is_email_verified:
            flash('Must Verify Email First', 'warning')
            return redirect(url_for('settings'))
        return func(*args, **kwargs)
    return decorated_view


@app.route('/', methods=["GET", "POST"])
def home():
    form = ReservationForm(meta={'csrf': False})
    return render_template("home.html", form=form)


def send_verification_text(user=current_user):
    verification = twilio_verify_client \
                     .verifications \
                     .create(rate_limits={
                         'user_id': user.id
                     },to=user.phone, channel='sms')
    app.logger.info('Verification SMS attempted: ', verification)
    return verification.status


def auth_phone_code(code, user=current_user):
    verification_check = twilio_verify_client \
                           .verification_checks \
                           .create(to=user.phone, code=code)
    app.logger.info('Auth of SMS code attempted: ', verification_check)
    return verification_check.status


@app.route("/verify-phone", methods=['GET', 'POST'])
@login_required
def verify_phone():
    form = VerifyPhoneForm()
    if form.validate_on_submit():
        try:
            status = auth_phone_code(form.code.data)
        except:
            app.loger.exception('Phone authentication failed')
            flash('Something went wrong.', 'danger')
            return(url_for('settings'))
        if status == 'approved':
            pass
        elif status == 'pending':
            flash('Wrong Code. Try Again.', 'warning')
            return redirect(request.referrer)
        elif status == 'canceled':
            flash('Expired Code. Try Again.', 'warning')
            return (url_for('settings'))
            
        
        user = User.query.filter_by(id = current_user.id)
        user.is_phone_verified = True
        try:
            db.session.commit()
        except:
            db.session.rollback()
            app.logger.exception('Failed to update phone verification status.')
            flash('Something went wrong', 'danger')
            return redirect(url_for('settings'))
        
        flash('Phone Number Verified', 'success')
        return redirect(url_for('home'))
    return render_template('verify_phone.html', form=form, is_phone_verified=current_user.is_phone_verified)


@app.route("/request-verify-phone", methods=['POST'])
@login_required
def request_verify_phone():
    status = send_verification_text()
    if status != 'pending':
        flash('Could Not Send Code', 'danger')
        return redirect(request.referrer)
    
    flash('Code Sent', 'success')
    return redirect(url_for('verify_phone')) 


def send_verification_email(user):
    token = user.get_token({'email verification': True})

    mail = Mail(
        from_email='GasMoney.Clients@simplelogin.co',
        to_emails=user.email)
    
    mail.dynamic_template_data = {
        'url': url_for("verify_email", token=token, _external=True)}
    mail.template_id = 'd-c7db68935eab464492456b3b6f965177'

    try:
        response = sendgrid_client.send(mail)
    except:
        app.logger.exception('Confirmation email failed to send')
        raise
    
    return response.status_code

@app.route("/verify-email", methods=['POST'])
@login_required
def request_verify_email():
    response_code = send_verification_email(current_user)

    if int(response_code) > 299 :
        flash('Failed to Send Confirmation Email', 'danger')
        return redirect(url_for('settings'))
        
    flash('Confirmation Email sent', 'success')
    return redirect(url_for('home'))
    

@app.route("/verify-email/<token>", methods=['GET'])
@login_required
def verify_email(token):
    try:
        user = User.verify_token(token, {'email verification' : True})
    except:
        flash('Token Is Invalid or Expired', 'warning')
        return redirect(url_for('request_reset'))
    
    try:
        user.is_email_verified = True
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.exception('Failed to update email verification status')
        flash('Something Went Wrong. Try Again.', 'danger')
        return redirect(url_for('settings'))
        
    flash('Email Confirmation Was Successfull', 'success')
    return redirect(url_for('home'))


def send_reset_email(user):
    token = user.get_token({'email': True})

    mail = Mail(
        from_email='GasMoney.Clients@simplelogin.co',
        to_emails=user.email)
    
    mail.dynamic_template_data = {
        'url': url_for("reset_token", token=token, _external=True)}
    mail.template_id = 'd-cac7631c436c455d93360ab1af5826cf'

    # Send an HTTP POST request to /mail/send
    try:
        response = sendgrid_client.send(mail)
    except:
        app.logger.exception('Reset email failed to send')
        raise
    
    return response.status_code


@app.route("/reset-password", methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
        except:
            flash('Failed to send email', 'danger')
            return redirect(url_for('settings'))
        
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.html', title='Reset Password', form=form)


@app.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    try:
        user = User.verify_token(token, {'email' : True})
    except:
        flash('Token Is Invalid or Expired', 'warning')
        return redirect(url_for('request_reset'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
                form.password.data, method='pbkdf2:sha256', salt_length=16)
        user.password = hashed_password
        try:
            db.session.commit()
        except:
            db.session.rollback()
            app.logger.exception('Reset Password Failed')
            flash('Something Went Wrong. Try Again.', 'danger')
            return redirect(request.referrer)
        
        flash('Password Reset Was Successfull', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset.html', form=form)


@app.route('/settings', methods=["GET", "POST"])
@fresh_login_required
def settings():
    user = User.query.filter_by(id=current_user.id).first()
    form = SettingsForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        print(user)
        if form.change_password.data:
            hashed_password = generate_password_hash(
                form.change_password.data, method='pbkdf2:sha256', salt_length=16)
            user.password = hashed_password
        if form.change_email.data:
            user.is_email_verified = False
            user.email = form.change_email.data
        if form.change_phone.data:
            user.is_phone_verified = False
            user.phone = form.change_phone.data
            
        try:
            db.session.commit()
        except:
            db.session.rollback()
            app.logger.exception('Failed to update user info')
            flash('Failed To Update Your Information', 'danger')
            return redirect(request.referrer)
        
        flash('Updated Your Information Successfully', 'success')
        return redirect(url_for('home'))
    return render_template("settings.html", form=form, current_user=current_user)


@app.route("/users/<username>")
@login_required
def profile(username):
    user = User.query.filter(User.username.ilike(username)).first()
    if not user:
        flash('User Not Found', 'danger')
        return redirect(url_for('home'))
    pagination = Ride.query.filter(or_(
        Ride.reservations.any(passenger_id=user.id),
        Ride.driver_id == user.id
    )).order_by(desc(Ride.departure_dt)).paginate()
    return render_template("profile.html", user=user, pagination=pagination, current_user=current_user)


@app.route("/users/")
@login_required
def current_user_profile():
    return redirect(url_for('profile', username=current_user.username))


@app.route('/reserve', methods=["POST"])
@verification_required
def reserve():
    seats_required = int(request.form.get("seats_required"))
    if not seats_required > 0:
        return flash('Could Not Reserve Seats', 'danger')
    ride_id = request.form.get("ride_id")
    ride = Ride.query.filter_by(id=ride_id).one()
    if not ride:
        flash('Ride Does Not Exist', 'danger')
        return redirect(request.referrer)
    elif seats_required > ride.seats_available:
        flash('Seats Are Not Available', 'danger')
        return redirect(request.referrer)
    
    reservation = Reservation(
        ride_id=ride_id, 
        passenger_id=current_user.id,
        seats_reserved=seats_required
        )
    try:
        db.session.add(reservation)
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.exception('Failed to add reservation')
        flash('Reservation Failed', 'danger')
        return redirect(request.referrer)
    
    flash('Reservation Created Successfully', 'success')
    return redirect(url_for('current_user_profile'))


@app.route('/cancel-reservation', methods=["POST"])
@login_required
def cancel_reservation():
    ride_id = request.form.get("ride_id")
    reservation = Reservation.query.filter(
        Reservation.ride_id==ride_id, 
        Reservation.passenger_id==current_user.id
        ).first()
    if not reservation:
        flash('Reservation Does Not Exist', 'danger')
        return redirect(request.referrer)
    
    try:
        db.session.delete(reservation)
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.exception('failed to delete a reservation')
        flash('Reservation Failed', 'danger')
        return redirect(request.referrer)

    flash('Reservation Deleted Successfully', 'success')
    return redirect(url_for('current_user_profile'))


@app.route('/cancel-ride', methods=["POST"])
@login_required
def cancel_ride():
    ride_id = request.form.get("ride_id")
    ride = Ride.query.filter(Ride.id==ride_id, Ride.driver_id==current_user.id, Ride.status==0).first()
    if not ride:
        flash('Ride Does Not Exist', 'danger')
        return redirect(request.referrer)
    try:
        ride.status = -1
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.exception('failed to update ')
        flash('Ride Was Not Canceled', 'danger')
        return redirect(request.referrer)

    flash('Ride Cancelled Successfully', 'success')
    return redirect(url_for('current_user_profile'))    


@app.route('/start-ride', methods=["POST"])
@login_required
def start_ride():
    ride_id = request.form.get("ride_id")
    ride = Ride.query.filter(Ride.id==ride_id, Ride.driver_id==current_user.id, Ride.status==0).first()
    if not ride:
        flash('Ride Does Not Exist', 'danger')
        return
    try:
        ride.status = 1
        db.session.commit()
    except:
        db.session.rollback()
        app.logger.exception('Failed to update ride status')
        flash('Ride Was Not Started', 'danger')
        return redirect(request.referrer)

    flash('Ride Started Successfully', 'success')
    return redirect(url_for('current_user_profile')) 


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
@verification_required
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
        except:
            db.session.rollback()
            app.logger.exception('failed to offer ride')
            flash('Something Went Wrong', 'danger')
            return redirect(url_for('offer'))
        
        flash('Ride Added Successfully', 'success')
        return redirect(url_for('current_user_profile'))
    
    return render_template("offer.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        user = User(
            first_name=form.first_name.data, 
            last_name=form.last_name.data, 
            gender=form.gender.data, 
            username=form.username.data,
            email=form.email.data, 
            phone=form.phone.data, 
            password=hashed_password
            )
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
