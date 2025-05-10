from flask import Flask, render_template, session, redirect
from aplicacion.funciones.funciones import funciones_bp
from aplicacion.chatbot.chatbot import chatbot_bp
from aplicacion.proyectos.proyectos import proyectos_bp
from modelo.models import User, Project, Food, Prototype, FoodProject, DatabaseSession, Fase, EvaluacionAvance, Test_Aceptacion, Test_Hedonico, Test_Sensorial, Test_Sensorial_Inicial
from sqlalchemy.orm import sessionmaker
from aplicacion.funciones.Fase1.composicionQuimica import composicionQuimica_bp
from aplicacion.funciones.Fase1.formularios import formularios_bp
from aplicacion.funciones.Fase1.estudioMercado import estudioMercado_bp
from aplicacion.funciones.Fase1.prototipado import prototipado_bp
from aplicacion.funciones.Fase1.diseñoExperimental import diseñoExperimental_bp
from aplicacion.funciones.Fase1.matrizSustentable import matrizSustentable_bp
from aplicacion.funciones.EvaluacionAvance.evaluacionAvance import evaluacionAvance_bp
from aplicacion.funciones.resumen import resumen_bp
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import timedelta
# from aplicacion.funciones.Fase1.chatbot import Fase1_bp
import json
import atexit


app = Flask(__name__, static_folder="funciones/static", template_folder="funciones/templates")
app.secret_key = 'your_secret_key'


Session = DatabaseSession()

# Base de datos
@app.route("/")
def home():
    return render_template("login/login.html")

if __name__ == '__main__':
    app.run()
