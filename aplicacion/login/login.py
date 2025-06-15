from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from modelo.models import User, Session
from flask_login import login_user, current_user, login_required, logout_user
from flask_bcrypt import Bcrypt

# Crear el Blueprint
login_bp = Blueprint("login", __name__, template_folder="aplicacion/templates", url_prefix='/login')

# Página de inicio de sesión
@login_bp.route('/')
def log():
    return render_template("login/login.html")

# Ruta para autenticación
@login_bp.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Session.query(User).filter_by(name=username).first()

        #Desencriptamos con Bcrypt
        bcrypt = Bcrypt()
        if not user  or not bcrypt.check_password_hash(user.contraseña, password):
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template("login/login.html")
        
        login_user(user, remember=True)
        session['username'] = username
        session['user_id'] = user.id
        Session.commit()
        return redirect("/proyectos")
        
    else:
        return render_template("login/login.html")


# Ruta para cerrar sesión
@login_bp.route('/logout')
@login_required
def logout():
    print("Cerrando sesión de usuario:", current_user.name)
    if current_user.is_authenticated:
        print("Cerrando sesión de usuario:", current_user.name)
        session.clear() # Limpiamos la sesión
        logout_user()
        flash('Has cerrado sesión correctamente', 'success')
    else:
        flash('No estás autenticado', 'warning')
    return redirect(url_for('login.log'))


#Registro de usuario
@login_bp.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        email = request.form.get('email')

        if not username or not password:
            flash('Por favor, completa todos los campos', 'warning')
            return render_template("login/register.html")

        existing_user = Session.query(User).filter_by(name=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template("login/register.html")
        
        #Encriptamos con Bcrypt
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(name=username, contraseña=hashed_password, email=email)
        Session.add(new_user)
        Session.commit()

        flash('Usuario registrado correctamente', 'success')
        return redirect(url_for('login.log'))

    return render_template("login/registro.html")


@login_bp.route('/editarUsuario', methods=['GET', 'POST'])
@login_required
def editar():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        email = request.form.get('email')
        user_id = request.form.get('user_id')

        existing_user = Session.query(User).filter_by(id = user_id).first()

        if username!=existing_user.name:
            existing_user2 = Session.query(User).filter_by(name=username).first()
            if existing_user:
                flash('El nombre de usuario ya está en uso', 'danger')
                return render_template("proyectos/editarUsuario.html", user=current_user)
        
        


        if not username or not password:
            flash('Por favor, completa todos los campos', 'warning')
            return render_template("proyectos/editarUsuario.html", user = current_user)
        
        #Encriptamos con Bcrypt
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        existing_user.contraseña = hashed_password
        existing_user.name = username
        existing_user.email = email
        
        Session.commit()

        flash('Usuario registrado correctamente', 'success')
        return redirect("/proyectos")
    
    if 'user_id' in session:
        user_id = session['user_id']
        current_user = Session.query(User).filter_by(id=user_id).first()

    return render_template("proyectos/editarUsuario.html", user=current_user)