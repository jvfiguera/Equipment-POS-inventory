from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField,PasswordField
from wtforms.validators import DataRequired,URL,length,input_required

class LoginForm(FlaskForm):
    email_user      = StringField(name='Email Adress :',render_kw={"placeholder": "Email Address", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=30),input_required()])
    password_user   = PasswordField(name='Password :' ,render_kw={"placeholder": "Your password",'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=30),input_required()])
    submit          = SubmitField('Login')

class RegisterForm(FlaskForm):
    email_user      = StringField(name='Email Adress :',render_kw={"placeholder": "Email Address", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=30),input_required()])
    first_name      = StringField(name='First name :',render_kw={"placeholder": "Your first name", 'style': 'width: 30ch'},validators=[DataRequired(),length(min=5,max=100),input_required()])
    last_name       = StringField(name='Last name :', render_kw={"placeholder": "Your last name", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=100), input_required()])
    password_user   = PasswordField(name='Password :' ,render_kw={"placeholder": "Your password",'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=30),input_required()])
    submit          = SubmitField('Sign Up')
    cancel          = SubmitField('Cancel')