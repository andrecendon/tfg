
from flask import Blueprint, request, redirect, url_for, render_template, session
from sqlalchemy.orm import sessionmaker
from modelo.models import Food,  Prototype, Project, User, FoodPrototype, DatabaseSession, ParametrosSustentables
from collections import defaultdict
from flask_login import login_required
from aplicacion.chatbot.chatbot import ModeloIA

# Crear el Blueprint
parametrosSustentables_bp = Blueprint("parametrosSustentables", __name__, template_folder="templates")


Session = DatabaseSession()

#### PANTALLA principal ####
@parametrosSustentables_bp.route('/', methods=["POST", "GET"])
@login_required
def inicio():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")
        if project.parametros_sustentables is None: 
            # Si no existe, creamos una nueva instancia
            chequeo = ParametrosSustentables(project=project)
            Session.add(chequeo)
            Session.commit()
        if project.parametros_sustentables.chequeo is None: 
            print("Creando nuevo")
            project.parametros_sustentables.chequeo = [
                                { "texto": "¿Usamos agua de forma eficiente y controlada en la producción?", "check": False },
                                { "texto": "¿Tenemos prácticas activas para conservar el suelo o prevenir erosión?", "check": False },
                                { "texto": "¿Realizamos separación y gestión de residuos orgánicos e inorgánicos?", "check": False },
                                { "texto": "¿Hacemos compostaje o tratamiento de residuos sólidos?", "check": False },
                                { "texto": "¿Contamos con algún sistema de tratamiento de aguas residuales?", "check": False },
                                { "texto": "¿Registramos o medimos el consumo energético en el proceso?", "check": False },
                                { "texto": "¿Implementamos estrategias para reducir el consumo de energía?", "check": False },
                                { "texto": "¿Utilizamos materiales de empaque reciclables o biodegradables?", "check": False },
                                { "texto": "¿Protegemos o integramos fuentes de biodiversidad en el entorno de la planta?", "check": False },
                                { "texto": "¿Hemos evaluado nuestra huella hídrica o de carbono?", "check": False },
                                { "texto": "¿Registramos los costos de producción con regularidad?", "check": False },
                                { "texto": "¿Diversificamos nuestros productos o fuentes de ingreso?", "check": False },
                                { "texto": "¿Tenemos planificada una estrategia de mejora continua o inversión?", "check": False },
                                { "texto": "¿Realizamos control de inventarios y mermas productivas?", "check": False },
                                { "texto": "¿Conocemos el margen de ganancia de cada producto?", "check": False },
                                { "texto": "¿Hemos evaluado la rentabilidad económica de nuestro sistema productivo?", "check": False },
                                { "texto": "¿Ofrecemos algún valor agregado (procesamiento, diseño, presentación)?", "check": False },
                                { "texto": "¿Realizamos alianzas o compras con proveedores locales?", "check": False },
                                { "texto": "¿Contamos con una política clara de precios justos?", "check": False },
                                { "texto": "¿Tenemos indicadores financieros mínimos definidos (flujo, retorno)?", "check": False },
                                { "texto": "¿La empresa ofrece condiciones laborales seguras y dignas?", "check": False },
                                { "texto": "¿Incluimos a mujeres, jóvenes o adultos mayores en el equipo?", "check": False },
                                { "texto": "¿El equipo participa en decisiones operativas importantes?", "check": False },
                                { "texto": "¿Hemos capacitado a nuestro personal en sostenibilidad o buenas prácticas?", "check": False },
                                { "texto": "¿Hemos consultado o recibido retroalimentación de nuestros consumidores?", "check": False },
                                { "texto": "¿Producimos alimentos accesibles y relevantes para la comunidad donde operamos?", "check": False },
                                { "texto": "¿Contribuimos con alimentos saludables o culturalmente aceptados?", "check": False },
                                { "texto": "¿Hemos creado materiales educativos o de sensibilización ambiental?", "check": False },
                                { "texto": "¿Participamos en ferias, redes o actividades comunitarias?", "check": False },
                                { "texto": "¿Hemos mejorado prácticas tras la observación directa de nuestros usuarios finales?", "check": False }
                                ]
            

            Session.commit()
    
    for p in project.prototypes:
        p.actualizar_peso()
    
    return render_template("funciones/Fase4/parametrosSustentables.html", project=project)



@parametrosSustentables_bp.route('/guardar', methods=["POST", "GET"])
@login_required
def guardar():
    
    if 'project_id' in session:
        project_id = session.get('project_id')
        project = Session.query(Project).filter(Project.id == project_id).first()
        if not project:
            return redirect("/proyectos")


    
    if request.method == "POST":

       
        

        try:
        # Obtener datos del formulario
            data = request.form
            
            # Crear o actualizar registro
            
           
            parametros = project.parametros_sustentables
            if parametros is not None:

                # --- Campos numéricos ---
                # Consumo de agua
                if 'agua' in data and data['agua'].strip():
                    parametros.consumo_agua = float(data['agua'])

                # Consumo de electricidad
                if 'electricidad' in data and data['electricidad'].strip():
                    parametros.consumo_electricidad = float(data['electricidad'])

                # Consumo de gas licuado
                if 'gas' in data and data['gas'].strip():
                    parametros.consumo_gas_licuado = float(data['gas'])

                # Materia prima usada
                if 'materia_prima' in data and data['materia_prima'].strip():
                    parametros.materia_prima_usada = float(data['materia_prima'])

                # Uso de empaques
                if 'empaques' in data and data['empaques'].strip():
                    parametros.uso_empaques = float(data['empaques'])

                # Residuos sólidos generados
                if 'residuos_solidos' in data and data['residuos_solidos'].strip():
                    parametros.residuos_solidos_generados = float(data['residuos_solidos'])

                # Residuos líquidos
                if 'residuos_liquidos' in data and data['residuos_liquidos'].strip():
                    parametros.residuos_liquidos = float(data['residuos_liquidos'])

                # Emisiones directas CO2
                if 'co2_directo' in data and data['co2_directo'].strip():
                    parametros.emisiones_directas_co2 = float(data['co2_directo'])

                # Emisiones indirectas electricidad
                if 'co2_indirecto' in data and data['co2_indirecto'].strip():
                    parametros.emisiones_indirectas_electricidad = float(data['co2_indirecto'])

                # Subproductos valorizados
                if 'subproductos' in data and data['subproductos'].strip():
                    parametros.subproductos_valorizados = float(data['subproductos'])

                # Km recorridos insumos
                if 'km_recorridos' in data and data['km_recorridos'].strip():
                    parametros.km_recorridos_insumos = float(data['km_recorridos'])

                # Carga total transportada
                if 'carga_transportada' in data and data['carga_transportada'].strip():
                    parametros.carga_total_transportada = float(data['carga_transportada'])

                # Producción mensual batido
                if 'produccion_mensual' in data and data['produccion_mensual'].strip():
                    parametros.produccion_mensual_batido = float(data['produccion_mensual'])

                # Mermas de proceso
                if 'mermas' in data and data['mermas'].strip():
                    parametros.mermas_proceso = float(data['mermas'])

                # Uso productos limpieza
                if 'productos_limpieza' in data and data['productos_limpieza'].strip():
                    parametros.uso_productos_limpieza = float(data['productos_limpieza'])

                # Consumo energía renovable
                if 'energia_renovable' in data and data['energia_renovable'].strip():
                    parametros.consumo_energia_renovable = float(data['energia_renovable'])

                # --- Campos de texto ---
                # Tipo transporte principal
                if 'tipo_transporte' in data:
                    parametros.tipo_transporte_principal = data['tipo_transporte'].strip()

                # Ubicación proveedores
                if 'ubicacion_proveedores' in data:
                    parametros.ubicacion_proveedores = data['ubicacion_proveedores'].strip()

                # --- Porcentajes local/importado ---
                # Origen local
                if 'origen_local' in data and data['origen_local'].strip():
                    parametros.origen_insumos_local = float(data['origen_local'])

                # Origen importado
                if 'origen_importado' in data and data['origen_importado'].strip():
                    parametros.origen_insumos_importado = float(data['origen_importado'])

                
            else: 
                print("M cago en tal")
        except Exception as e:
            return "Error 404"
          
    Session.commit()     
    if request.form.get('action') == 'guardar':
        return redirect('/funciones/Fase4/parametrosSustentables/')
        
    elif request.form.get('action') == 'back':
        return redirect('/funciones/')
              
    return redirect('/funciones/Fase4/chequeo/')
