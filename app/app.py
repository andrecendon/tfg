from flask import Flask, render_template, session, redirect
from funciones.funciones import funciones_bp
from login.login import login_bp, logout_user
from chatbot.chatbot import chatbot_bp
from proyectos.proyectos import proyectos_bp
from models import User,  Project, Food, Prototype, FoodProject,  DatabaseSession, Fase, EvaluacionAvance, Test_Aceptacion, Test_Hedonico, Test_Sensorial, Test_Sensorial_Inicial
from sqlalchemy.orm import sessionmaker
from funciones.Fase1.composicionQuimica import composicionQuimica_bp
from funciones.Fase1.formularios import formularios_bp
from funciones.Fase1.estudioMercado import estudioMercado_bp
from funciones.Fase1.prototipado import prototipado_bp
from funciones.Fase1.diseñoExperimental import diseñoExperimental_bp
from funciones.Fase1.matrizSustentable import matrizSustentable_bp
from funciones.Fase2.prototipoMedio import prototipoMedio_bp
from funciones.Fase3.preciosIngredientes import preciosIngredientes_bp
from funciones.Fase3.prototipadoFinal import prototipoFinal_bp
from funciones.Fase3.analisisSensorial import analisisSensorial_bp
from funciones.Fase3.calculoGastos import calculoGastos_bp
from funciones.Fase2.analisisNormativo import analisisNormativo_bp
from funciones.EvaluacionAvance.evaluacionAvance import evaluacionAvance_bp
from funciones.Fase3.empaqueFidelidad import empaqueFidelidad_bp
from funciones.Fase3.simulacionProduccion import simulacionProduccion_bp
from funciones.resumen import resumen_bp
from funciones.Fase2.empaque import empaque_bp
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from datetime import timedelta
from funciones.Fase2.simulacionCostes import simulacionCostes_bp
#from funciones.Fase1.chatbot import Fase1_bp
import json
import atexit

app = Flask(__name__, static_folder="static")
app.secret_key = 'your_secret_key'
#Cargamos base de datos, se ejecuta cada vez que cambiamos algo en el codigo


Session = DatabaseSession()


p = Session.query(Project).all()
p2 = Session.query(FoodProject).all()

proj = Session.query(Project).filter(Project.id == 1).first()


    
estado=0
h = Session.query(User).all()

h2 = Session.query(Fase).all()

h3 = Session.query(Test_Sensorial).all()


for u in h:
    if u.name == "Andre2":
        estado = 1
        andre = u
        break

if estado==0: 
    andre = User(name="Andre2", contraseña="1234")
    Session.add(andre)


if len(p)<1:
    jo = Project(name="Ejemplo", user=andre)
    Session.add_all([jo])

##Projecto 
if len(h2)<1:
     #Evalucacion 
     ev = EvaluacionAvance(project_id=1)
     Session.add(ev)
     fases_data={
        "1. Idea inicial de proyecto": "0",
        "2. Empatizar con los usuarios": "0",
        "3. Base de datos composición química de alimentos": "0",
        "4. Estudio de mercado": "0",
        "5. Ingredientes sustentables (matriz)": "0",
        "6. Ideación": "0",
        "7. Diseño experimental": "0",
        "8. Prototipo 1 – Baja complejidad (diseño experimental)": "0",
        "9. Evaluación de avance": "0",
        "10. Prototipo de mediana complejidad (formulación y simulación nutricional)": "0",
        "11. Simulación de costos": "0",
        "12. Análisis de viabilidad normativa": "0",
        "13. Prototipo empírico": "0",
        "14. Evaluación de avance": "0",
        "15. Prototipado según diseño": "0",
        "16. Simulación de producción": "0",
        "17. Actualización de precios de ingredientes": "0",
        "18. Análisis sensorial 1": "0",
        "19. Validación de composición nutricional": "0",
        "20. Escalamiento": "0",
        "21. Validación de costos": "0",
        "22. Prototipo de empaque 3 – Alta fidelidad": "0"
        }
     for nombre in fases_data.keys():
            nueva_fase = Fase(nombre=nombre, evaluacion=ev)
            Session.add(nueva_fase)
        
        # 4. Hacer commit para guardar en la base de datos
     Session.commit()


Session.commit()


if (len(h3)<1):
    #Test_Aceptacion
    test = Test_Aceptacion(project_id=1)
    Session.add(test)
    #Test_Hedonico
    test2 = Test_Hedonico(project_id=1)
    Session.add(test2)
    #Test_Sensorial_Inicial
    test3 = Test_Sensorial_Inicial(project_id=1)
    Session.add(test3)
    Session.commit()

#Seguridad


# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.log'
app.secret_key="my_secret_key"


app.config['SECRET_KEY'] ="my_secret_key"

@login_manager.user_loader
def load_user(user_id):
    user = Session.query(User).filter_by(id=user_id).first()
    return user  



# Rutas
app.register_blueprint(funciones_bp, url_prefix='/funciones')
app.register_blueprint(resumen_bp, url_prefix='/funciones/resumen')
app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
app.register_blueprint(proyectos_bp, url_prefix='/proyectos')
app.register_blueprint(formularios_bp, url_prefix='/funciones/formularios')

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
    app.run(debug=True)

