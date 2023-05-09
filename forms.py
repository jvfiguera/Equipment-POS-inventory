from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SubmitField,PasswordField,SelectField
from wtforms.validators import DataRequired,URL,length,input_required,equal_to

# Definición de Listas
marca_eqp_list =[]
model_eqp_list =[]
status_eqp_list =[]

class LoginForm(FlaskForm):
    email_user      = StringField(name='Email Adress :',render_kw={"placeholder": "Email Address", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=30),input_required()])
    password_user   = PasswordField(name='Password :' ,render_kw={"placeholder": "Your password",'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=30),input_required()])
    submit          = SubmitField('Login')

class RegisterForm(FlaskForm):
    email_user      = StringField(name='Email Adress :',render_kw={"placeholder": "Email Address", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=30),input_required()])
    first_name      = StringField(name='First name :',render_kw={"placeholder": "Your first name", 'style': 'width: 30ch'},validators=[DataRequired(),length(min=5,max=100),input_required()])
    last_name       = StringField(name='Last name :', render_kw={"placeholder": "Your last name", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=100), input_required()])
    password_user   = PasswordField(name='Password :' ,render_kw={"placeholder": "Your password",'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=30),input_required(), equal_to('confirm_password',message='Passwords must match')])
    confirm_password= PasswordField(name='Confirm Password :', render_kw={"placeholder": "Confirm your password", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=5, max=30), input_required()])
    submit          = SubmitField('Sign Up')
    cancel          = SubmitField('Cancel')

class RegisterNewEqp(FlaskForm):
    serial_number   = StringField(name='Serial number :',render_kw={"placeholder": "Número de serial", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=20),input_required()])
    store_id        = StringField(name='Store Id :',render_kw={"placeholder": "Store id", 'style': 'width: 30ch'},validators=[DataRequired(),length(min=10,max=10),input_required()])
    marca_eqp       = SelectField('Marca del equipo:',[DataRequired(),input_required()],coerce=str, choices=marca_eqp_list)
    model_eqp       = SelectField('Modelo del equipo:',[DataRequired(),input_required()],coerce=str, choices=model_eqp_list)
    status_eqp      = SelectField('Estatus del equipo:',[DataRequired(),input_required()],coerce=str, choices=status_eqp_list)
    submit          = SubmitField('Registrar')
    cancel          = SubmitField('Cancel')

class FilterTblEqp(FlaskForm):
    marca_eqp       = SelectField('Marca del equipo:',[DataRequired(),input_required(),length(min=5, max=5)],coerce=str, choices=marca_eqp_list)
    model_eqp       = SelectField('Modelo del equipo:',[DataRequired(),input_required()],coerce=str, choices=model_eqp_list)
    status_eqp      = SelectField('Estatus del equipo:',[DataRequired(),input_required()],coerce=str, choices=status_eqp_list)
    submit          = SubmitField('Consultar')

class GetSerialEqp(FlaskForm):
    serial_number   = StringField(name='Serial number :',render_kw={"placeholder": "Número de serial", 'style': 'width: 30ch'},validators=[DataRequired(), length(min=20, max=20),input_required()])
    select          = SubmitField('Consultar')
    delete          = SubmitField('Eliminar')
    cancel          = SubmitField('Cancelar')