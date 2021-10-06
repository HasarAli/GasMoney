from flask_wtf import FlaskForm
from wtforms.fields.core import BooleanField, RadioField, StringField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets.html5 import TelInput
from wtforms.fields.html5 import EmailField, TelField
import phonenumbers

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
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=24)])
    gender = RadioField('Gender', validators=[DataRequired()], choices=[('m', 'Male'), ('f', 'Female'), ('o', 'Other/Prefer Not Say')])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
