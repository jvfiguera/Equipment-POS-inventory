import flask
from flask import Flask, render_template,redirect,url_for, flash, request
from flask_login import UserMixin,login_user,LoginManager,current_user,logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from forms import LoginForm, RegisterForm
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash

app =Flask(__name__)
login_manager =LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY']='8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

## Conexión de base de datos
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db =SQLAlchemy(app)
ctl_flg_glb =0

class Users(db.Model,UserMixin):
    __tablename__ ="users"
    email_user  =db.Column(db.String(50) , primary_key = True)
    first_name     =db.Column(db.String(100), nullable = False)
    last_name      =db.Column(db.String(100), nullable = False)
    password       =db.Column(db.String(100), nullable = False)

    def get_id(self):
        return (self.email_user)

# Funciones generales del aplcativo
def fn_check_user_exist(p_userid):
    '''Function to check if the user exist'''
    return Users.query.get(p_userid)

def fn_register_new_user(p_new_user_dat):
    ''' Function to add new users'''
    db.session.add(p_new_user_dat)
    db.session.commit()
    login_user(p_new_user_dat)

## Funciones de paginas web
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/',methods=['POST','GET'])
def fn_home():
    global ctl_flg_glb
    form_login      = LoginForm()
    form_register   = RegisterForm()
    if request.method   ==  'GET':
        ctl_flg_glb =0
        return render_template(template_name_or_list='login.html'
                               ,form        =form_login
                               )
    else :
        if ctl_flg_glb == 0 :
            if form_login.validate_on_submit():
                chk_user_exist = fn_check_user_exist(p_userid=form_login.email_user.data)

                if chk_user_exist:
                    if check_password_hash(pwhash=chk_user_exist.password, password=form_login.password_user.data):
                        login_user(chk_user_exist, remember=True)
                        flask.flash("Usuario autenticado de forma correcta en la plataforma")
                    else:
                        flask.flash("Invalida contraseña , por favor intente de nuevo")
                    return redirect(location=url_for("fn_home"))
                else:
                    ctl_flg_glb = 1
                    flask.flash("Disculpe usuario NO registrado en la plataforma, resgistrese")
                    return render_template(template_name_or_list='login.html'
                                           , form=form_register
                                           )
            else:
                ctl_flg_glb = 0
                return redirect(location=url_for("fn_home"))
        if ctl_flg_glb == 1:
            if form_register.validate_on_submit():
                chk_user_exist = fn_check_user_exist(p_userid=form_login.email_user.data)
                if not chk_user_exist:
                    new_user_dat =Users(email_user =form_register.email_user.data
                                       ,first_name =form_register.first_name.data
                                       ,last_name  =form_register.last_name.data
                                       ,password   =generate_password_hash(password=form_register.password_user.data, method = 'pbkdf2:sha256',salt_length=8)
                                      )
                    fn_register_new_user(p_new_user_dat=new_user_dat)
                    ctl_flg_glb = 0
                    return render_template(template_name_or_list='login.html'
                                           , form=form_login
                                           )
                else :
                    ctl_flg_glb = 1
                    flask.flash("Usuario ya existe, por favor intente con otro correo o identificador")
                    return render_template(template_name_or_list='login.html'
                                           , form=form_register
                                           )
            else:
                ctl_flg_glb = 1
                return render_template(template_name_or_list='login.html'
                                       , form=form_register
                                       )


@login_manager.user_loader
def fn_load_user(user_id):
    return Users.query.get(user_id)

# @app.route('/fn_login',methods=['POST'])
# def fn_login():
#     if request.method == 'POST':
#         email_user      = request.form.get(email)
#         password_user   = request.form.get(password)
#         print(email_user)
#         print(password_user)
#     return render_template(template_name_or_list='login.html')

if __name__ =='__main__':
    app.run(debug=True,port=5001)