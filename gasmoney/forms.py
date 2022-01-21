from datetime import date, datetime
from flask_wtf import FlaskForm
from wtforms.fields.core import BooleanField, DateField, IntegerField, RadioField, StringField, TimeField
from flask_login import current_user
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError, Regexp, Optional
from wtforms.fields.html5 import EmailField, TelField
import phonenumbers
from gasmoney import db
from gasmoney.models import User

class FieldsRequiredForm(FlaskForm):
    """ https://github.com/wtforms/wtforms/issues/477#issuecomment-716417410
    Require all fields to have content. This works around the bug that WTForms radio
    fields don't honor the `DataRequired` or `InputRequired` validators.
    """

    class Meta:
        def render_field(self, field, render_kw):
            if field.type == "_Option":
                render_kw.setdefault("required", True)
            return super().render_field(field, render_kw)

class RegistrationForm(FieldsRequiredForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    gender = RadioField('Gender', validators=[DataRequired()], choices=[('f', 'Female'), ('m', 'Male'), ('o', 'Other/Prefer Not Say')])
    email = EmailField('Email', validators=[DataRequired(), Length(max=254), Email()])
    # regex: https://stackoverflow.com/a/12019115/15004958
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20), 
        Regexp('^(?=.{4,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', 
            message='Username must consist of 4-20 alphanumeric characters seperated by single dot or underscore')])
    phone = TelField('Phone Number', validators=[DataRequired(), Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128), 
        Regexp('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$', 
        message="Your password must have minimum eight characters, \
        at least one upper and one lower case English letter, \
        one number, and one special character")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
            
            user = db.session.query(User.id).filter_by(phone=phone.data).first()
            if user:
                raise Exception()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
        except:
            raise ValidationError('That phonenumber is already taken. Please use a different one')

    def validate_email(self, email):
        user = db.session.query(User.id).filter(User.email.ilike(email.data)).first()
        if user:
            raise ValidationError('That email is already taken. Please use a different one')

    def validate_username(self, username):
        user = db.session.query(User.id).filter(User.username.ilike(username.data)).first()
        if user:
            raise ValidationError("That username is already taken. Please use a different one")        

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(max=254), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ReservationForm(FlaskForm):
    origin = StringField('From', validators=[Length(max=254)])
    destination = StringField('To', validators=[Length(max=254)])
    departure_date = DateField('Date')
    departure_time = TimeField('Time')
    seats_required = IntegerField('Seats', validators=[NumberRange(min=1)])
    submit = SubmitField('Search')

class RideForm(FlaskForm):
    origin = StringField('From', validators=[DataRequired(), Length(max=254)])
    destination = StringField('To', validators=[DataRequired(), Length(max=254)])
    rendezvous = StringField('Rendezvous', validators=[DataRequired(), Length(max=254)])
    departure_date = DateField('Date', validators=[DataRequired()])
    departure_time = TimeField('Time', validators=[DataRequired()])
    seats = IntegerField('Seats', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add')


class SettingsForm(FieldsRequiredForm):
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    gender = RadioField('Gender', validators=[], choices=[('f', 'Female'), ('m', 'Male'), ('o', 'Other/Prefer Not Say')])
    change_email = EmailField('Email', validators=[Length(max=254), Email()])
    username = StringField('Username', validators=[Length(min=4, max=20), 
        Regexp('^(?=.{4,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$', 
        message='Username must consist of 4-20 alphanumeric characters seperated by single dot or underscore')])
    change_phone = TelField('Phone Number', validators=[Length(max=15)])
    change_password = PasswordField('Change Password', validators=[Optional(), 
        Regexp('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,128}$', 
        message="Your password must have minimum eight characters, \
        at least one upper and one lower case English letter, \
        one number, and one special character")])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('change_password')])
    submit = SubmitField('Update')

    def validate_phone(self, phone):
        if current_user.phone != phone.data:
            try:
                p = phonenumbers.parse(phone.data)
                if not phonenumbers.is_valid_number(p):
                    raise ValueError()
                
                user = db.session.query(User.id).filter_by(phone=phone.data).first()
                if user:
                    raise Exception()
            except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
                raise ValidationError('Invalid phone number')
            except:
                raise ValidationError('That phonenumber is already taken. Please use a different one')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = db.session.query(User.id).filter(User.email.ilike(email.data)).first()
            if user:
                raise ValidationError('That email is already taken. Please use a different one')
    
    def validate_username(self, username):
        if current_user.username != username.data:
            user = db.session.query(User.id).filter(User.username.ilike(username.data)).first()
            if user:
                raise ValidationError("That username is already taken. Please use a different one")

class RequestResetForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(max=254), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = db.session.query(User.id).filter(User.email.ilike(email.data)).first()
        if not user:
            raise ValidationError('There is no account associated with that email.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128), 
        Regexp('^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$', 
        message="Your password must have minimum eight characters, \
        at least one upper and one lower case English letter, \
        one number, and one special character")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset Password')

class VerifyPhoneForm(FlaskForm):
    code = StringField('Code', validators=[ DataRequired(),
                                            Regexp('^\d{6}$', message="Please enter 6 digits")])
    submit = SubmitField('Verify')