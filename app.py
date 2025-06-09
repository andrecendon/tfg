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

# from aplicacion.funciones.Fase1.chatbot import Fase1_bp
import json
import atexit


app = Flask(__name__, static_folder="aplicacion/static", template_folder="aplicacion/templates")
app.secret_key = 'your_secret_key'



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


Session = DatabaseSession()


p = Session.query(Project).all()
p2 = Session.query(FoodProject).all()

proj = Session.query(Project).filter(Project.id == 1).first()


    
estado=0
h = Session.query(User).all()

h2 = Session.query(EvaluacionAvance).all()

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

if len(Session.query(Fase).all())<1:
    fases_data = {
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

    # Crear una lista con todas las fases
    todas_las_fases = []
    for i, (nombre, estado) in enumerate(fases_data.items(), start=1):
        fase = Fase(nombre=nombre, numero_paso=i, estado=int(estado))
        todas_las_fases.append(fase)
        Session.add(fase)

    # Commit intermedio para que las fases tengan ID si fuera necesario
    Session.commit()

if len(h2)<1:
    todas_las_fases = Session.query(Fase).all()

    print("Todas las fases:", todas_las_fases)

    # Crear una evaluación nueva
    evaluacion = EvaluacionAvance(
        id=1,  
        avance=False,
        comentarios="Evaluación inicial",
        numero_fases=len(todas_las_fases),
        fases=todas_las_fases,  # Asigna todas las fases directamente
        project_id=1  # Asegúrate de que el proyecto con ID=1 exista
    )

    # Añadir y guardar
    Session.add(evaluacion)
    Session.commit()




Session.commit()




# Rutas

app.register_blueprint(agente_bp, url_prefix='/chatbot/agente')

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
    return render_template("login/login.html")

if __name__ == '__main__':
    app.run(debug=True)
