from flask import Flask, render_template, session, redirect
from app.login.login import login_bp, logout_user
from app.chatbot.chatbot import chatbot_bp
from app.proyectos.proyectos import proyectos_bp
from app.models import User, Project, Food, Prototype, FoodProject, DatabaseSession, Test_Aceptacion, Test_Hedonico, Test_Sensorial_Inicial
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import timedelta
import json
import atexit

app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'

# Base de datos
Session = DatabaseSession()

p = Session.query(Project).all()
p2 = Session.query(FoodProject).all()

proj = Session.query(Project).filter(Project.id == 1).first()

estado = 0
h = Session.query(User).all()

h3 = Session.query(Test_Hedonico).all()

for u in h:
    if u.name == "Andre2":
        estado = 1
        andre = u
        break

if estado == 0:
    andre = User(name="Andre2", contraseña="1234")
    Session.add(andre)

if len(p) < 1:
    jo = Project(name="Ejemplo", user=andre)
    Session.add_all([jo])

Session.commit()

if len(h3) < 1:
    test = Test_Aceptacion(project_id=1)
    Session.add(test)
    test2 = Test_Hedonico(project_id=1)
    Session.add(test2)
    test3 = Test_Sensorial_Inicial(project_id=1)
    Session.add(test3)
    Session.commit()

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.log'
app.secret_key = "my_secret_key"
app.config['SECRET_KEY'] = "my_secret_key"

@login_manager.user_loader
def load_user(user_id):
    user = Session.query(User).filter_by(id=user_id).first()
    return user

# Rutas
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(proyectos_bp, url_prefix='/proyectos')
app.register_blueprint(login_bp, url_prefix='/login')

@app.route("/")
def home():
    return redirect('/login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

atexit.register(logout)

if __name__ == '__main__':
    app.run()
