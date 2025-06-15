from flask import Flask, render_template, session, redirect
from aplicacion.funciones.funciones import funciones_bp
from aplicacion.chatbot.chatbot import chatbot_bp
from aplicacion.proyectos.proyectos import proyectos_bp
from modelo.models import User, Project, Food, Prototype, FoodProject, DatabaseSession, Fase, EvaluacionAvance, Test_Aceptacion, Test_Hedonico, Test_Sensorial, Test_Sensorial_Inicial
from sqlalchemy.orm import sessionmaker

from aplicacion.chatbot.agente import agente_bp

from aplicacion.funciones.Fase1.composicionQuimica import composicionQuimica_bp
from aplicacion.funciones.Fase1.formularios import formularios_bp
from aplicacion.funciones.Fase1.estudioMercado import estudioMercado_bp
from aplicacion.funciones.Fase1.prototipado import prototipado_bp
from aplicacion.funciones.Fase1.diseñoExperimental import diseñoExperimental_bp
from aplicacion.funciones.Fase1.matrizSustentable import matrizSustentable_bp
from aplicacion.funciones.Fase2.analisisNormativo import analisisNormativo_bp
from aplicacion.funciones.Fase2.empaque import empaque_bp
from aplicacion.funciones.Fase2.prototipoMedio import prototipoMedio_bp
from aplicacion.funciones.Fase2.simulacionCostes import simulacionCostes_bp
from aplicacion.funciones.Fase3.preciosIngredientes import preciosIngredientes_bp
from aplicacion.funciones.Fase3.prototipadoFinal import prototipoFinal_bp
from aplicacion.funciones.Fase3.analisisSensorial import analisisSensorial_bp
from aplicacion.funciones.Fase3.calculoGastos import calculoGastos_bp
from aplicacion.funciones.Fase3.empaqueFidelidad import empaqueFidelidad_bp
from aplicacion.funciones.Fase3.escalamiento import escalamiento_bp
from aplicacion.funciones.Fase3.simulacionProduccion import simulacionProduccion_bp
from aplicacion.funciones.Fase3.validacionNutricional import validacionNutricional_bp
from aplicacion.funciones.Fase4.chequeo import chequeo_bp
from aplicacion.funciones.Fase4.vidaUtil import vidaUtil_bp
from aplicacion.funciones.Fase4.parametrosSustentables import parametrosSustentables_bp
from aplicacion.funciones.Fase4.analisisSensorial2 import analisisSensorial2_bp
from aplicacion.funciones.Fase4.validacionEmpaque import validacionEmpaque_bp
from aplicacion.funciones.EvaluacionAvance.evaluacionAvance import evaluacionAvance_bp
from aplicacion.funciones.resumen import resumen_bp
from aplicacion.login.login import login_bp
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import timedelta
from flask_bcrypt import Bcrypt
import json
import atexit
from datetime import datetime
from flask import flash, url_for, request


MAX_SEGUNDOS_INACTIVO = 30 * 60 # 30 minutos de inactividad se cierra sesión y el usuario debe volver a iniciar.
app = Flask(__name__, static_folder="aplicacion/static", template_folder="aplicacion/templates")
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=MAX_SEGUNDOS_INACTIVO)  #cierra cookies en 30min
bcrypt = Bcrypt(app)  # Inicializa Bcrypt con tu app Flask



  
SEGUNDOS_INACTIVOS = 0
FECHA_ULTIMA_ACTIVIDAD = None

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.log'
app.secret_key = "my_secret_key"
app.config['SECRET_KEY'] = "my_secret_key"

@login_manager.user_loader
def load_user(user_id):
    user = Session.query(User).filter_by(id=user_id).first()
    return user  

import pytz

Session = DatabaseSession()

#Comprueba si se cerraron las cookies en ese caso se hace logout
@app.before_request
def check_session_expiration():
    if request.endpoint == 'login.log':
        return
    if not session:
                logout_user()
                session.clear() # Para que no acceda a otro proyecto, prototipo sin querer. 
                Session.commit()
                return redirect(url_for('login.log'))

       
            

# Rutas

app.register_blueprint(agente_bp, url_prefix='/chatbot/agente')

app.register_blueprint(funciones_bp, url_prefix='/funciones')
app.register_blueprint(resumen_bp, url_prefix='/funciones/resumen')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(proyectos_bp, url_prefix='/proyectos')
app.register_blueprint(formularios_bp, url_prefix='/funciones/Fase1/formularios')

app.register_blueprint(evaluacionAvance_bp, url_prefix='/funciones/evaluacionAvance')

app.register_blueprint(composicionQuimica_bp, url_prefix='/funciones/Fase1/composicionQuimica')
app.register_blueprint(estudioMercado_bp, url_prefix='/funciones/Fase1/estudioMercado')
app.register_blueprint(prototipado_bp, url_prefix='/funciones/Fase1/prototipado')
app.register_blueprint(diseñoExperimental_bp, url_prefix='/funciones/Fase1/diseñoExperimental')
app.register_blueprint(matrizSustentable_bp, url_prefix='/funciones/Fase1/matrizSustentable')


app.register_blueprint(empaque_bp, url_prefix='/funciones/Fase2/empaque')
app.register_blueprint(prototipoMedio_bp, url_prefix='/funciones/Fase2/prototipoMedio')
app.register_blueprint(simulacionCostes_bp, url_prefix='/funciones/Fase2/simulacionCostes')
app.register_blueprint(analisisNormativo_bp, url_prefix='/funciones/Fase2/analisisNormativo')


app.register_blueprint(preciosIngredientes_bp, url_prefix='/funciones/Fase3/preciosIngredientes')
app.register_blueprint(prototipoFinal_bp, url_prefix='/funciones/Fase3/prototipoFinal')
app.register_blueprint(analisisSensorial_bp, url_prefix='/funciones/Fase3/analisisSensorial')
app.register_blueprint(empaqueFidelidad_bp, url_prefix='/funciones/Fase3/empaqueFidelidad')
app.register_blueprint(simulacionProduccion_bp, url_prefix='/funciones/Fase3/simulacionProduccion')
app.register_blueprint(calculoGastos_bp, url_prefix='/funciones/Fase3/calculoGastos')
app.register_blueprint(escalamiento_bp, url_prefix='/funciones/Fase3/escalamiento')
app.register_blueprint(validacionNutricional_bp, url_prefix='/funciones/Fase3/validacionNutricional')


app.register_blueprint(chequeo_bp, url_prefix='/funciones/Fase4/chequeo')
app.register_blueprint(vidaUtil_bp, url_prefix='/funciones/Fase4/vidaUtil')
app.register_blueprint(parametrosSustentables_bp, url_prefix='/funciones/Fase4/parametrosSustentables')
app.register_blueprint(analisisSensorial2_bp, url_prefix='/funciones/Fase4/analisisSensorial2')
app.register_blueprint(validacionEmpaque_bp, url_prefix='/funciones/Fase4/validacionEmpaque')

app.register_blueprint(login_bp, url_prefix='/login')




# Base de datos
@app.route("/")
def home():
    #todas las cookies 
    print("Cookies:", request.cookies)
    print("USUARIO LOGEADO? ", current_user.is_authenticated)
    
    return render_template("login/login.html")

if __name__ == '__main__':
    app.run(debug=True)
