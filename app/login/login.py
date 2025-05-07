from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from sqlalchemy.orm import sessionmaker
from models import User,  Session
from flask_login import login_user, current_user, logout_user, login_required

# Crear el Blueprint
login_bp = Blueprint("login", __name__, template_folder="templates", url_prefix='/login') # Añade url_prefix

# Session = sessionmaker(bind=engine)  # No crees la sesión aquí, créala dentro de las vistas
# Session = Session()                 # Tampoco crees la instancia aquí

#Index
@login_bp.route('/') #  ruta base es ahora /login/
def log():
    return render_template("login/login.html")


# Ruta para mostrar el formulario de login
@login_bp.route('/auth', methods=['GET', 'POST'])  # Cambia el nombre para evitar conflictos
def auth():
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.form.get('username')
        password = request.form.get('password')
        

        # Verificar si el usuario y contraseña son correctos
        user = Session.query(User).filter_by(name=username).first() #busca por usuario primero

        if user and user.contraseña == password: #verifica la contraseña solo si el usuario existe
            login_user(user, remember=True)
            print("USARIO LOGEADO: ", current_user.is_authenticated)
            session['username'] = username
            session['user_id'] = user.id 
            
            Session.commit()
            return redirect("/proyectos")

        else:
            flash('Usuario o contraseña incorrectos', 'danger')  # Mensaje flash para errores
            return render_template("login/login.html") #Recarga la pagina con los mensajes flash
       
    else:
        return render_template("login/login.html")