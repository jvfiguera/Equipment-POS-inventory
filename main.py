import flask
from flask import Flask, render_template,redirect,url_for, flash, request,jsonify,json
from flask_login import UserMixin,login_user,LoginManager,current_user,logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from forms import LoginForm, RegisterForm, RegisterNewEqp,FilterTblEqp,GetSerialEqp,Confirmform,MerchantAddForm,MerchantMangeForm,MerchantSelectform, Installterm
from forms import marca_eqp_list,model_eqp_list,status_eqp_list, country_list,state_list,city_list
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
email_user_glb=''
serial_number_glb=''
merchant_data_glb=[]

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

class country(db.Model,UserMixin):
    __tablename__ = "country"
    id_country      = db.Column(db.Integer, primary_key=True)
    desc_country    = db.Column(db.String(30), nullable=False)

class state(db.Model, UserMixin):
    __tablename__ = "states"
    id_country    = db.Column(db.Integer, primary_key=True)
    id_state      = db.Column(db.Integer, primary_key=True)
    desc_state    = db.Column(db.String(30), nullable=False)

class city(db.Model, UserMixin):
    __tablename__ = "city"
    id_country  = db.Column(db.Integer, primary_key=True)
    id_state    = db.Column(db.Integer, primary_key=True)
    id_city     = db.Column(db.Integer, primary_key=True)
    desc_city   = db.Column(db.String(30), nullable=False)

class Merchant(db.Model, UserMixin):
    __tablename__ = "merchant_tbl"
    id_merchant      = db.Column(db.String(10), primary_key=True)
    merchant_name    = db.Column(db.String(60), nullable=False)
    merchant_address = db.Column(db.String(80), nullable=False)
    id_country       = db.Column(db.Integer, primary_key=False)
    id_state         = db.Column(db.Integer, primary_key=False)
    id_city          = db.Column(db.Integer, primary_key=False)

# Funciones generales del aplicativo
def fn_install_eqp_merchant(p_serial_number,p_id_merchant):
    if fn_chk_merchant_exist(p_id_merchant=p_id_merchant, p_merchant_name=None):
        update_inveqp =InventoryEqp.query.get(p_serial_number)
        if update_inveqp :
            update_inveqp.store_id  =p_id_merchant
            update_inveqp.id_status = 1 # Equipo Instalado
            db.session.commit()
            return True
        else:
            return False
    else:
        return False

def fn_update_merchant(p_update_merchant):
    '''Function to update Merchant information'''
    global merchant_data_glb
    merchant_data_glb = Merchant.query.get(p_update_merchant.id_merchant)
    if merchant_data_glb :
       merchant_data_glb.merchant_name     =p_update_merchant.merchant_name
       merchant_data_glb.merchant_address  =p_update_merchant.merchant_address
       merchant_data_glb.id_country        =p_update_merchant.id_country
       merchant_data_glb.id_state          =p_update_merchant.id_state
       merchant_data_glb.id_city           =p_update_merchant.id_city
       db.session.commit()
       return True
    else:
        return False

def fn_delete_merchant(p_id_merchant,p_merchant_name):
    '''Function to delete merchant information'''
    global merchant_data_glb
    if fn_chk_merchant_exist(p_id_merchant=p_id_merchant,p_merchant_name=p_merchant_name):
        merchant_data_glb = Merchant.query.get(p_id_merchant)
        if merchant_data_glb :
            db.session.delete(merchant_data_glb)
            db.session.commit()
            return True
    else :
        return False

def fn_get_info_merchant(p_merchant_id):
    '''Function for getting merchant information'''
    global merchant_data_glb
    merchant_data_glb = Merchant.query.get(p_merchant_id)
    if merchant_data_glb:
        return True
    else:
        return False

def fn_add_merchant(p_add_merchant):
    '''Function to add new Merchant'''
    if not fn_chk_merchant_exist(p_id_merchant=p_add_merchant.id_merchant,p_merchant_name=p_add_merchant.merchant_name):
        db.session.add(p_add_merchant)
        db.session.commit()
        return True
    else :
        return False

def fn_chk_merchant_exist(p_id_merchant,p_merchant_name):
    '''Function to check if merchant exist'''
    if  Merchant.query.get(p_id_merchant):
        return True
    else:
        if Merchant.query.filter(Merchant.merchant_name == p_merchant_name).first():
            return True
        else:
            return False

def fn_get_countries(p_id_country):
    '''Function to get list countries'''
    country_list.clear()
    if not p_id_country:
        all_countries = country.query.all()
        for i in range(len(all_countries)):
            country_list.append((all_countries[i].id_country, all_countries[i].desc_country))
    else:
        all_countries =country.query.get(p_id_country)
        country_list.append((all_countries.id_country, all_countries.desc_country))

def fn_get_states(p_idcountry,p_idstate):
    '''Function to get list states for the country'''
    state_list.clear()
    if not p_idstate:
        all_states = state.query.filter(state.id_country == p_idcountry).all()
        for i in range(len(all_states)):
            state_list.append((all_states[i].id_state, all_states[i].desc_state))
    else :
        all_states = state.query.filter(state.id_country == p_idcountry, state.id_state==p_idstate).all()
        state_list.append((all_states[0].id_state, all_states[0].desc_state))

def fn_get_cities(p_idcountry,p_idstate,p_idcity):
    '''Function to get list city for the country/state'''
    city_list.clear()
    if not p_idcity :
        all_cities = city.query.filter(city.id_country == p_idcountry, city.id_state == p_idstate).all()
        for i in range(len(all_cities)):
            city_list.append((all_cities[i].id_city, all_cities[i].desc_city))
    else :
        all_cities = city.query.filter(city.id_country == p_idcountry, city.id_state == p_idstate, city.id_city == p_idcity).all()
        city_list.append((all_cities[0].id_city, all_cities[0].desc_city))

def fn_delete_eqpinc(p_serial_number):
    #if fn_chk_eqp_exist(p_serial_number=p_serial_number):
    eqp_to_delete = InventoryEqp.query.get(p_serial_number)
    db.session.delete(eqp_to_delete)
    db.session.commit()
    return True

def fn_get_info_eqp(p_serial_number):
    return InventoryEqp_vw.query.filter(InventoryEqp_vw.serial_number==p_serial_number).all()

def fn_get_all_inveqp(p_filter,p_filter_data,p_id_merchant):
    '''Función que retorna el listado del inventario de equipos'''
    if p_filter == 0 :
        return InventoryEqp_vw.query.all()
    elif p_filter == 1 :
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
    else : #p_filter == 2
        return InventoryEqp_vw.query.filter(InventoryEqp_vw.store_id == p_id_merchant).all()

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
    global ctl_flg_glb,email_user_glb
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
                        email_user_glb = chk_user_exist.email_user
                        if check_password_hash(pwhash=chk_user_exist.password, password=form_login.password_user.data):
                            login_user(chk_user_exist, remember=True)
                            #flask.flash("Usuario autenticado de forma correcta en la plataforma")
                            return render_template(template_name_or_list='index.html'
                                                   ,flg             =1
                                                   ,email_user      =email_user_glb
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
    global email_user_glb
    fn_get_all_marcaeqp(p_filter=0)
    fn_get_all_modeleqp(p_filter=0)
    fn_get_all_statuseqp(p_filter=0)
    form_reg_eqp = RegisterNewEqp()

    if request.method == 'GET':
        return render_template(template_name_or_list='index.html'
                               ,flg             =2
                               ,title_form      ='Registro de Nuevos Equipos'
                               ,form            =form_reg_eqp
                               ,email_user      =email_user_glb
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
                                   , email_user=email_user_glb
                                   )

@app.route('/fn_get_show_inveqp',methods=['GET','POST'])
def fn_get_show_inveqp():
    global email_user_glb
    fn_get_all_marcaeqp(p_filter=1)
    fn_get_all_modeleqp(p_filter=1)
    fn_get_all_statuseqp(p_filter=1)
    form_filter =FilterTblEqp()
    tbl_header_list =('Nro. Serial','Stored Id','Store name','Marca','Modelo','Status')
    if request.method == 'GET':
        tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0,p_filter_data=(0,0,0),p_id_merchant=None)
    else:
        filter_data =(int(form_filter.marca_eqp.data),int(form_filter.model_eqp.data),int(form_filter.status_eqp.data))
        if filter_data ==(0,0,0) :
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0, p_filter_data=filter_data,p_id_merchant=None)
        else:
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=1,p_filter_data=filter_data,p_id_merchant=None)

    return render_template(template_name_or_list   ='index.html'
                           ,flg                    =3
                           ,title_form             ='Tabla Inventario de Equipos'
                           ,tbl_header_list_web    =tbl_header_list
                           ,tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                           ,form                   =form_filter
                           ,email_user             =email_user_glb
                           )

@app.route('/fn_Del_Serialeqp',methods=['GET','POST'])
def fn_DelEqpInv():
    global email_user_glb,serial_number_glb
    form =GetSerialEqp()
    form_confirm = Confirmform()
    tbl_header_list = ('Nro. Serial', 'Stored Id', 'Store name', 'Marca', 'Modelo', 'Status')
    if request.method=='GET':
        tbl_all_inventory_eqp_list = []
        return render_template(template_name_or_list    ='index.html'
                               , flg                    =4
                               , title_form             ='Eliminar Equipo del Inventario'
                               , tbl_header_list_web    =tbl_header_list
                               , tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                               , form                   =form
                               , email_user             =email_user_glb
                               )
    else :
        if form.select.data and form.serial_number.data:
            tbl_all_inventory_eqp_list = fn_get_info_eqp(p_serial_number=form.serial_number.data)
            if tbl_all_inventory_eqp_list :
                return render_template(template_name_or_list    ='index.html'
                                       , flg                    =4
                                       , title_form             ='Eliminar Equipo del Inventario'
                                       , tbl_header_list_web    =tbl_header_list
                                       , tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                                       , form                   =form
                                       , email_user             =email_user_glb
                                       )
            else :
                flask.flash("El equipo no existe, por favor verifique")
                return redirect(location=url_for("fn_DelEqpInv"))
        elif form.select.data and not form.serial_number.data:
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0, p_filter_data=(0, 0, 0))
            return render_template(template_name_or_list    ='index.html'
                                   , flg                    =4
                                   , title_form             ='Eliminar Equipo del Inventario'
                                   , tbl_header_list_web    =tbl_header_list
                                   , tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                                   , form                   =form
                                   , email_user             =email_user_glb
                                   )
        elif form.delete.data and form.serial_number.data:
                serial_number_glb=form.serial_number.data
                return render_template(template_name_or_list='index.html'
                                       , flg                =5
                                       , title_form         ='Eliminar Equipo del Inventario'
                                       , msg                ='Seguro desea eliminar el equipo: ' + form.serial_number.data + ' del inventario Si/No?'
                                       , form               =form_confirm
                                       , email_user         =email_user_glb
                                       )
        elif form_confirm.confirmar.data :
            if fn_delete_eqpinc(p_serial_number=serial_number_glb):
                flask.flash("El equipo ha sido eliminado del inventario")
            else:
                flask.flash("El equipo no pudo ser eliminado del inventario")
            tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0, p_filter_data=(0, 0, 0))
            return render_template(template_name_or_list    ='index.html'
                                   , flg                    =4
                                   , title_form             ='Eliminar Equipo del Inventario'
                                   , tbl_header_list_web    =tbl_header_list
                                   , tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                                   , form                   =form
                                   , email_user             =email_user_glb
                                   )
        else:
                tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=0, p_filter_data=(0, 0, 0))
                return render_template(template_name_or_list    ='index.html'
                                       , flg                    =4
                                       , title_form             ='Eliminar Equipo del Inventario'
                                       , tbl_header_list_web    =tbl_header_list
                                       , tbl_inventory_eqp_list =tbl_all_inventory_eqp_list
                                       , form                   =form
                                       , email_user             =email_user_glb
                                       )
            # return redirect(location=url_for("fn_DelEqpInv"))

@app.route('/fn_RegNewMerchant',methods=['GET','POST'])
def fn_RegNewMerchant():
    fn_get_countries(p_id_country=None)
    fn_get_states(p_idcountry=1,p_idstate=None)
    fn_get_cities(p_idcountry=1,p_idstate=1,p_idcity=None)
    form = MerchantAddForm()
    if request.method == 'GET':
        return render_template(template_name_or_list='index.html'
                               ,flg                 =6
                               ,title_form          ='Register Merchants'
                               ,email_user          =email_user_glb
                               ,form                = form
                               )
    else:
        if form.validate_on_submit():
            new_merchant_add =Merchant(id_merchant        =form.id_merchant.data
                                        ,merchant_name    =form.merchant_name.data
                                        ,merchant_address =form.merchant_address.data
                                        ,id_country       =form.id_country.data
                                        ,id_state         =form.id_state.data
                                        ,id_city          =form.id_city.data
                                    )
            if fn_add_merchant(new_merchant_add):
                flask.flash('El merchant ha sido resgistrado correctamente')
            else:
                flask.flash('Error al registrar la información, el merchant ya existe')
            return redirect(url_for('fn_RegNewMerchant'))
        else :
            return render_template(template_name_or_list='index.html'
                                   , flg                =6
                                   , title_form         ='Register Merchants'
                                   , email_user         =email_user_glb
                                   , form               =form
                                   )

@app.route('/fn_ManageMerchant',methods=['GET','POST'])
def fn_ManageMerchant():
    global merchant_data_glb,country_list,state_list,city_list
    # form = MerchantAddForm(id_state=25)  # Colocar un default value form = TestForm(test_field=1)
    form = MerchantSelectform()
    if request.method == 'POST':
        if form.validate_on_submit():
            form1 = MerchantMangeForm()
            if form.submit.data :
                if fn_get_info_merchant(p_merchant_id=form.id_merchant.data):
                    form1 = MerchantMangeForm(id_country=merchant_data_glb.id_country, id_state=merchant_data_glb.id_state,id_city=merchant_data_glb.id_city)
                    form1.id_merchant.data      = merchant_data_glb.id_merchant
                    form1.merchant_name.data    = merchant_data_glb.merchant_name
                    form1.merchant_address.data = merchant_data_glb.merchant_address
                    return render_template(template_name_or_list='index.html'
                                           , flg                =6
                                           , title_form         ='Manage the Merchants'
                                           , email_user         =email_user_glb
                                           , form               =form1
                                           )
                else:
                    flask.flash('El merchant no existe , favor validar')
                    return redirect(url_for('fn_ManageMerchant'))
            elif form1.update.data:
                update_merchant_data = Merchant( id_merchant       =form1.id_merchant.data
                                                ,merchant_name     =form1.merchant_name.data
                                                ,merchant_address  =form1.merchant_address.data
                                                ,id_country        =form1.id_country.data
                                                ,id_state          =form1.id_state.data
                                                ,id_city           =form1.id_city.data
                                                )
                if fn_update_merchant(p_update_merchant=update_merchant_data):
                    flask.flash('La información del merchant fue actualizada correctamente')
                else:
                    flask.flash('La información del merchant no pudo ser actualizada')
            elif form1.delete.data:
                if fn_delete_merchant(p_id_merchant=form1.id_merchant.data, p_merchant_name=form1.merchant_name.data):
                     flask.flash('La información del merchant ha sido eliminada')
                else :
                     flask.flash('La información del merchant no pudo ser eliminada')

    return render_template(template_name_or_list='index.html'
                           , flg                =6
                           , title_form         ='Getting Merchant Information '
                           , email_user         =email_user_glb
                           , form               =form
                           )
@app.route('/fn_installterm',methods=['GET','POST'])
def fn_installterm():
    global tbl_all_inventory_eqp_list
    tbl_all_inventory_eqp_list =[]
    tbl_header_tbl_list = ['#','Id merchant','Serial number','Marca','Modelo','Status']
    form =Installterm()
    if request.method =='POST':
        if form.validate_on_submit():
            if fn_install_eqp_merchant(p_serial_number=form.serial_number.data,p_id_merchant=form.id_merchant.data):
                flask.flash('El equipo fue instalado correctamente en el Merchant')
                tbl_all_inventory_eqp_list = fn_get_all_inveqp(p_filter=2, p_filter_data=(0, 0, 0),p_id_merchant=form.id_merchant.data)
            else:
                flask.flash('El equipo no pudo ser instalado en el Merchant')

    return render_template(template_name_or_list='index.html'
                           , flg                =7
                           , title_form         ='Installing terminal at the Merchants '
                           , email_user         =email_user_glb
                           , form               =form
                           , tbl_header_tbl_list= tbl_header_tbl_list
                           , tbl_eqp_intalled   =tbl_all_inventory_eqp_list
                           )

@app.route('/state/<id_country>')
def statebycountry(id_country):
    fn_get_states(p_idcountry=id_country,p_idstate=None)
    stateArray = []
    for i in range(len(state_list)):
        stateObj = {}
        stateObj['id']      = state_list[i][0]
        stateObj['name']    = state_list[i][1]
        stateArray.append(stateObj)
    return jsonify({'statecountry' : stateArray})

@app.route('/cities/<id_data>')
def citiesbystate(id_data):
    fn_get_cities(p_idcountry =id_data.split(sep='|')[0] , p_idstate=id_data.split(sep='|')[1],p_idcity=None)
    citiesArray = []
    for i in range(len(city_list)):
        citiesObj = {}
        citiesObj['id']     = city_list[i][0]
        citiesObj['name']   = city_list[i][1]
        citiesArray.append(citiesObj)
    return jsonify({'citiesbystate' : citiesArray})

if __name__ =='__main__':
    fn_get_countries(p_id_country=None)
    fn_get_states(p_idcountry=1, p_idstate=None)
    fn_get_cities(p_idcountry=1, p_idstate=1, p_idcity=None)
    app.run(debug=True,port=5001)