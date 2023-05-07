import flask
from flask import Flask, render_template,redirect,url_for, flash, request
from flask_login import UserMixin,login_user,LoginManager,current_user,logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from forms import LoginForm, RegisterForm, RegisterNewEqp,marca_eqp_list,model_eqp_list,status_eqp_list,FilterTblEqp
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
    email_user      =db.Column(db.String(50) , primary_key = True)
    first_name      =db.Column(db.String(100), nullable = False)
    last_name       =db.Column(db.String(100), nullable = False)
    password        =db.Column(db.String(100), nullable = False)

    def get_id(self):
        return (self.email_user)

class MarcaEqp(db.Model,UserMixin):
    __tablename__ ="marca_eqp"
    id_marca     =db.Column(db.Integer , primary_key = True)
    desc_marca   =db.Column(db.String(30), nullable = False)

class ModelEqp(db.Model,UserMixin):
    __tablename__ ="model_eqp"
    id_model     =db.Column(db.Integer , primary_key = True)
    desc_model   =db.Column(db.String(30), nullable = False)

class StatusEqp(db.Model,UserMixin):
    __tablename__ ="status_eqp"
    id_status     =db.Column(db.Integer , primary_key = True)
    desc_status   =db.Column(db.String(30), nullable = False)

class InventoryEqp(db.Model,UserMixin):
    __tablename__ ="inventory_eqp"
    serial_number =db.Column(db.String(30), primary_key = True,nullable = False)
    store_id      =db.Column(db.String(10) , nullable = False)
    id_marca      =db.Column(db.Integer, nullable=False)
    id_model      =db.Column(db.Integer, nullable=False)
    id_status     =db.Column(db.Integer, nullable=False)

class InventoryEqp_vw(db.Model,UserMixin):
    __tablename__ ="inventory_eqp_vw"
    serial_number =db.Column(db.String(30), primary_key = True,nullable = False)
    store_id      =db.Column(db.String(10) , nullable = False)
    desc_store    =db.Column(db.String(30), nullable=False)
    id_marca      =db.Column(db.Integer, nullable=False)
    desc_marca    =db.Column(db.String(30), nullable=False)
    id_model      =db.Column(db.Integer, nullable=False)
    desc_model    =db.Column(db.String(30), nullable=False)
    id_status     =db.Column(db.Integer, nullable=False)
    desc_status   =db.Column(db.String(30), nullable=False)

# Funciones generales del aplicativo

def fn_get_all_inveqp(p_filter,p_filter_data):
    '''Función que retorna el listado del inventario de equipos'''
    if p_filter == 0 :
        return InventoryEqp_vw.query.all()
    else :
        if p_filter_data[0] !=0 and p_filter_data[1] !=0 and p_filter_data[2] !=0: # Marca, Model, Status
            print('Marca,Modelo,Status')
            return  InventoryEqp_vw.query.filter(InventoryEqp_vw.id_marca==p_filter_data[0],InventoryEqp_vw.id_model==p_filter_data[1],InventoryEqp_vw.id_status==p_filter_data[2]).all()
        elif p_filter_data[0] !=0 and p_filter_data[1] !=0 and p_filter_data[2] ==0: # Marca , Modelo
            print('Marca,Modelo')
            return  InventoryEqp_vw.query.filter(InventoryEqp_vw.id_marca==p_filter_data[0],InventoryEqp_vw.id_model==p_filter_data[1]).all()
        elif p_filter_data[0] !=0 and p_filter_data[1] ==0 and p_filter_data[2] !=0: # Marca , Status
            print('Marca,Status')
            return  InventoryEqp_vw.query.filter(InventoryEqp_vw.id_marca==p_filter_data[0],InventoryEqp_vw.id_status==p_filter_data[2]).all()
        elif p_filter_data[0] ==0 and p_filter_data[1] !=0 and p_filter_data[2] !=0: # Model, Status
            print('Modelo,Status')
            return InventoryEqp_vw.query.filter(InventoryEqp_vw.id_model==p_filter_data[1],InventoryEqp_vw.id_status==p_filter_data[2]).all()
        elif p_filter_data[0] !=0 and p_filter_data[1] ==0 and p_filter_data[2] ==0: # Marca
            print('Marca')
            print(p_filter_data)
            return  InventoryEqp_vw.query.filter(InventoryEqp_vw.id_marca==p_filter_data[0]).all()
        elif  p_filter_data[0] ==0 and p_filter_data[1] !=0 and p_filter_data[2] ==0: # Modelo
            print('Modelo')
            return InventoryEqp_vw.query.filter(InventoryEqp_vw.id_model==p_filter_data[1]).all()
        else : # Status
            print('Status')
            return InventoryEqp_vw.query.filter(InventoryEqp_vw.id_status==p_filter_data[2]).all()

def fn_chk_eqp_exist(p_serial_number):
    '''Function to check if the equipment exist'''
    if InventoryEqp.query.get(p_serial_number):
        return True
    else:
        return False

def fn_add_inv_neweqp(p_new_inveqp):
    '''Function to add new inentory equipment'''
    if not fn_chk_eqp_exist(p_serial_number=p_new_inveqp.serial_number):
        db.session.add(p_new_inveqp)
        db.session.commit()
        return True
    else :
        return False

def fn_get_all_marcaeqp(p_filter):
    '''Function to get list mark'''
    marca_eqp_list.clear()
    all_marca_eqp = MarcaEqp.query.all()
    if p_filter ==1 :
        marca_eqp_list.append((0,'Todas las marcas'))
    for i in range(len(all_marca_eqp)):
        marca_eqp_list.append((all_marca_eqp[i].id_marca,all_marca_eqp[i].desc_marca))

def fn_get_all_modeleqp(p_filter):
    '''Function to get List model'''
    model_eqp_list.clear()
    all_model_eqp = ModelEqp.query.all()
    if p_filter ==1 :
        model_eqp_list.append((0,'Todos los modelos'))
    for i in range(len(all_model_eqp)):
        model_eqp_list.append((all_model_eqp[i].id_model,all_model_eqp[i].desc_model))

def fn_get_all_statuseqp(p_filter):
    '''Function to get List Status'''
    status_eqp_list.clear()
    all_status_eqp = StatusEqp.query.all()
    if p_filter ==1 :
        status_eqp_list.append((0,'Todos los status'))
    for i in range(len(all_status_eqp)):
        status_eqp_list.append((all_status_eqp[i].id_status,all_status_eqp[i].desc_status))

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
        if not form_register.cancel.data :
            if ctl_flg_glb == 0 :
                if form_login.validate_on_submit():
                    chk_user_exist = fn_check_user_exist(p_userid=form_login.email_user.data)

                    if chk_user_exist:
                        if check_password_hash(pwhash=chk_user_exist.password, password=form_login.password_user.data):
                            login_user(chk_user_exist, remember=True)
                            #flask.flash("Usuario autenticado de forma correcta en la plataforma")
                            return render_template(template_name_or_list='index.html'
                                                   ,flg             =1
                                                   )
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
        else :
            return redirect(location=url_for("fn_home"))

@app.route('/fn_logout',methods=['GET','POST'])
def fn_logout():
    logout_user()
    return redirect(location=url_for("fn_home"))

@login_manager.user_loader
def fn_load_user(user_id):
    return Users.query.get(user_id )

# Funciones para el procesamiento del inventario
# de Equipos
@app.route('/fn_register_neweqp',methods=['GET','POST'])
def fn_register_neweqp():
    fn_get_all_marcaeqp(p_filter=0)
    fn_get_all_modeleqp(p_filter=0)
    fn_get_all_statuseqp(p_filter=0)
    form_reg_eqp = RegisterNewEqp()
    print(request.method)
    if request.method == 'GET':
        return render_template(template_name_or_list='index.html'
                               ,flg             =2
                               ,title_form      ='Registro de Nuevos Equipos'
                               ,form=form_reg_eqp
                               )
    else:
            if form_reg_eqp.validate_on_submit():
                new_inveqp_data  =InventoryEqp(serial_number    =form_reg_eqp.serial_number.data
                                               ,store_id        =form_reg_eqp.store_id.data
                                               ,id_marca        =form_reg_eqp.marca_eqp.data
                                               ,id_model        =form_reg_eqp.model_eqp.data
                                               ,id_status       =form_reg_eqp.status_eqp.data
                                            )
                if fn_add_inv_neweqp(p_new_inveqp=new_inveqp_data):
                    flask.flash("El equipo ha sido registrado de manera correcta")
                else:
                    flask.flash("El equipo ya esta registrado en el inventario")

            return render_template(template_name_or_list='index.html'
                                   , flg=2
                                   , title_form='Registro de Nuevos Equipos'
                                   , form=form_reg_eqp
                                   )

                #return redirect(location=url_for("fn_register_neweqp"))
@app.route('/fn_get_show_inveqp',methods=['GET','POST'])
def fn_get_show_inveqp():
    fn_get_all_marcaeqp(p_filter=1)
    fn_get_all_modeleqp(p_filter=1)
    fn_get_all_statuseqp(p_filter=1)
    form_filter =FilterTblEqp()
    tbl_header_list =('Nro. Serial','Stored Id','Store name','Marca','Modelo','Status')
    print(request.method)
    if request.method == 'GET':
        tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0,p_filter_data=(0,0,0))
    else:
        filter_data =(int(form_filter.marca_eqp.data),int(form_filter.model_eqp.data),int(form_filter.status_eqp.data))
        if filter_data ==(0,0,0) :
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0, p_filter_data=filter_data)
        else:
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=1,p_filter_data=filter_data)

    return render_template(template_name_or_list   ='index.html'
                           ,flg                    =3
                           ,title_form             ='Tabla inventario de Equipos'
                           ,tbl_header_list_web    =tbl_header_list
                           ,tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                           ,form                   =form_filter
                           )

if __name__ =='__main__':
    app.run(debug=True,port=5001)