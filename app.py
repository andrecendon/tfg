from flask import Flask, render_template, session, redirect
from funciones.login.login import login_bp
from datetime import timedelta
from modelo.models import User, Project, Food, Prototype, FoodProject, DatabaseSession, Fase, EvaluacionAvance, Test_Aceptacion, Test_Hedonico, Test_Sensorial, Test_Sensorial_Inicial
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
