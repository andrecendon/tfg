from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from modelo.models import User, Session
from flask_login import login_user, current_user

# Crear el Blueprint
login_bp = Blueprint("login", __name__, template_folder="templates", url_prefix='/login')

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

        if user and user.contraseña == password:
            login_user(user, remember=True)
            session['username'] = username
            session['user_id'] = user.id
            Session.commit()
            return redirect("/proyectos")
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template("login/login.html")
    else:
        return render_template("login/login.html")
