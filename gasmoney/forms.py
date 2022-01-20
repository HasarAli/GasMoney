from datetime import date, datetime
from flask_wtf import FlaskForm
from wtforms.fields.core import BooleanField, DateField, IntegerField, RadioField, StringField, TimeField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from wtforms.fields.html5 import EmailField, TelField
import phonenumbers
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
    gender = RadioField('Gender', validators=[DataRequired()], choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other/Prefer Not Say')])
    email = EmailField('Email', validators=[DataRequired(), Length(max=254), Email()])
    phone = TelField('Phone Number', validators=[DataRequired(), Length(max=15)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
            
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise Exception()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
        except:
            raise ValidationError('That phonenumber is already taken. Please use a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please use a different one')
            

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
    seats_required = IntegerField('Seats', validators=[NumberRange(min=0)])
    submit = SubmitField('Search')

class RideForm(FlaskForm):
    origin = StringField('From', validators=[DataRequired(), Length(max=254)])
    destination = StringField('To', validators=[DataRequired(), Length(max=254)])
    rendezvous = StringField('Rendezvous', validators=[DataRequired(), Length(max=254)])
    departure_date = DateField('Date', validators=[DataRequired()])
    departure_time = TimeField('Time', validators=[DataRequired()])
    seats = IntegerField('Seats', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add')

    def validate_departure_before_date(self, departure_before_date):       
        if departure_before_date.data < date.today():
            raise ValidationError('Selected date must be in the future')
    
    def validate_departure_before_time(self, departure_before_time):
        dt_data = datetime.combine(self.departure_before_date.data, departure_before_time.data)
        if dt_data < datetime.now():
            raise ValidationError('Selected time must be in the future')