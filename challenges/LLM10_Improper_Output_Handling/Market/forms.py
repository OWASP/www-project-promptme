from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from Market.models import User

class RegisterForm(FlaskForm):
    def validate_username(self, username_check):
        if User.query.filter_by(username=username_check.data).first():
            raise ValidationError('Username already exists! Please try a different username.')
    
    def validate_email_address(self, email_address_check):
        if User.query.filter_by(email_address=email_address_check.data).first():
            raise ValidationError('Email Address already exists! Please try a different email address.')

    username = StringField(label='User Name', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=3), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='Purchase Item!')
