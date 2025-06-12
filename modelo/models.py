import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, inspect, Inspector, MetaData
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column, scoped_session
from sqlalchemy import ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from typing import List
from flask_login import UserMixin
from sqlalchemy import Table, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict
# Ensure the directory exists

Base = declarative_base()

class DatabaseSession:
    _instance = None
    engine = None

    def __new__(cls):
        if cls._instance is None:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            parent_directory = os.path.dirname(current_directory)
            db_directory = os.path.join(parent_directory, "database")
            dbr_url = f"sqlite:///{db_directory}/database.db"

            cls.engine = create_engine(dbr_url)
            cls._instance = scoped_session(sessionmaker(bind=cls.engine))
        return cls._instance
    
    @classmethod
    def clear_all_data(cls):
        """Elimina todos los datos de todas las tablas, manteniendo las estructuras."""
        if cls.engine is not None:
            # Obtener metadata y reflejar las tablas existentes
            metadata = MetaData()
            metadata.reflect(bind=cls.engine)
            
            # Iniciar una nueva sesión
            session = cls()
            
            try:
                # Desactivar las restricciones de clave foránea (especialmente importante para SQLite)
                if cls.engine.url.drivername == 'sqlite':
                    session.execute("PRAGMA foreign_keys = OFF")
                
                # Eliminar datos de todas las tablas en orden inverso para evitar problemas con claves foráneas
                for table in reversed(metadata.sorted_tables):
                    session.execute(table.delete())
                
                session.commit()
                
                # Reactivar las restricciones de clave foránea
                if cls.engine.url.drivername == 'sqlite':
                    session.execute("PRAGMA foreign_keys = ON")
                
                print("Todos los datos han sido eliminados de las tablas.")
            except Exception as e:
                session.rollback()
                print(f"Error al eliminar datos: {e}")
                raise
            
    

# Para borrar todos los datos:
#DatabaseSession.clear_all_data()

Session = DatabaseSession()

# Clase que nos permite hacer funciones/atbos globales a todos. EN este caso no se usa, pero se deja por si acaso
class BaseModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True



class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contraseña = Column(String, nullable=False)
    email = Column(String)
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)

    def get_id(self):
        return str(self.id)
    def __repr__(self):
        return f"User(name={self.name}, age={self.age})"
    
    #constructor para q no de error si ya hay usuario con ese nombre
    
        
        
    @classmethod
    def add_user_if_not_exists(cls, session, user):
        existing_user = session.query(cls).filter_by(id=user.name).first()
        if existing_user is None:
            session.add(user)
            return True
        return False
    



class FoodProject(BaseModel):
    __tablename__ = 'food_projects'
    id = Column(Integer, primary_key=True)
    food_id = Column('food_id', Integer, ForeignKey('foods.id', ondelete="CASCADE"), nullable=False)
    project_id = Column('project_id', Integer, ForeignKey('projects.id', ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint('food_id', 'project_id', name='uq_food_project'),)
    
    #Imprimir
    def __repr__(self):
        return f"FoodProject(food_id={self.food_id}, project_id={self.project_id})"
    

class Test_Sensorial(BaseModel):
    __tablename__ = 'tests_sensoriales'
    
    id = Column(Integer, primary_key=True)
    nombre_evaluador = Column(String)

    atributo = Column(String)
    fecha = Column(Date, nullable=True)
    resultados = Column(MutableDict.as_mutable(JSON)) 
    comentarios = Column(String)
    type = Column(String)
    numero_muestras = Column(Integer, nullable=True)  # Número de muestras evaluadas
    
    # Relación con proyectos
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tests_sensoriales")
    
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'sensorial'
    }

    def __repr__(self):
        return f"Test_Sensorial(id={self.id}, nombre_evaluador={self.nombre_evaluador}, atributo={self.atributo}, fecha={self.fecha}, resultados={self.resultados}, comentarios={self.comentarios}, numero_muestras={self.numero_muestras}, type={self.type})"

class Test_Sensorial_Inicial(Test_Sensorial): 
    __tablename__ = 'tests_sensoriales_iniciales'
    __mapper_args__ = {'polymorphic_identity': 'inicial'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)
    muestras = Column(JSON)  

class Test_Hedonico(Test_Sensorial): 
    __tablename__ = 'tests_hedonicos'
    __mapper_args__ = {'polymorphic_identity': 'hedonico'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)

    #Codigo de la muestra, en hedonico solo se usa una por fila
    muestra = Column(String)  
    puntuacion = Column(Integer)  # Cambiado a Integer para puntuación


    def __repr__(self):
        return f"Test_Hedonico(id={self.id}, nombre_evaluador={self.nombre_evaluador}, atributo={self.atributo}, fecha={self.fecha}, resultados={self.resultados}, comentarios={self.comentarios}, numero_muestras={self.numero_muestras}, type={self.type}, muestra={self.muestra})"

class Test_Aceptacion(Test_Sensorial): 
    __tablename__ = 'tests_aceptacion'
    __mapper_args__ = {'polymorphic_identity': 'aceptacion'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)
    muestra = Column(String)
    agrado = Column(String)  # Cambiado a String
    sabor = Column(String)
    textura = Column(String)
    apariencia = Column(String)
    compra = Column(String)  # Mejor como booleano para intención de compra
     
class Costos(BaseModel):
    __tablename__ = 'costos'
    id = Column(Integer, primary_key=True)
    empaque = Column(MutableDict.as_mutable(JSON), default={"empaque":{"descripcion": "envase primario", "cantidad":1, "costo": 1}, "etiqueta":{"descripcion": "envase primario", "cantidad":1, "costo": 1}, "otros":{"descripcion": "envase primario", "cantidad":1, "costo": 1, "precio_total": 1}})  # Precio del empaque en dolares #Guardar en json: lista de materiales etiqueta:{"descripcion": "envase primario", "cantidad":1, "precio": 0.5, "precio_total": 0.5}
    ingredientes = Column(MutableDict.as_mutable(JSON))  # Precio total de los ingredientes en dolares. tomate:{"descripcion": "primario", "cantidad":1, "precio": 0.5}
    mano_obra = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio de la mano de obra en JSON
    electricidad = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio de la electricidad en JSON
    agua = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio del agua en JSON
    depreciacion_equipos = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio de la depreciación de equipos en JSON
    transporte = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio del transporte en JSON
    mermas = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 1, "costo": 1})  # Precio de las mermas en JSON
    adicionales = Column(MutableDict.as_mutable(JSON), default={"descripcion": " ", "cantidad": 0, "costo": 0})
    
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="costos")

    def asignar_ingredientes(self):
        for p in self.project.prototypes:
            if p.is_favourite:
                for food in p.food_prototypes:
                    
                    if food.food.precio >= 0:
                            if self.ingredientes is None:
                                self.ingredientes = {}
                            self.ingredientes[food.food_description] = {
                                "descripcion": " ",
                                "cantidad": food.cantidad,
                                "costo": food.food.precio,
                                
                            }
                            print("Alimentos asignados a costos: ", self.ingredientes)
                    else:
                        print(f"Alimento {food.food_description} no encontrado en la base de datos.")
            Session.commit()
    #Constructor 
    def __init__(self, project):
        self.project = project
        self.project_id = project.id
        self.ingredientes = {}
        self.empaque = {"empaque":{"descripcion": "envase primario", "cantidad":1, "costo": 1}, "etiqueta":{"descripcion": "envase primario", "cantidad":1, "costo": 1}, "otros":{"descripcion": "envase primario", "cantidad":1, "costo": 1, "precio_total": 1}}
        self.mano_obra = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.electricidad = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.agua = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.depreciacion_equipos = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.transporte = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.mermas = {"descripcion": " ", "cantidad": 1, "costo": 1}
        self.adicionales = {"descripcion": " ", "cantidad": 0, "costo": 0}

        self.asignar_ingredientes()
    def __repr__(self):
        return f"Costos(id={self.id}, empaque={self.empaque}, ingredientes={self.ingredientes}, mano_obra={self.mano_obra}, electricidad={self.electricidad}, agua={self.agua}, depreciacion_equipos={self.depreciacion_equipos}"

class Ideacion(BaseModel):
    __tablename__ = 'ideaciones'
    id = Column(Integer, primary_key=True)

    nombre = Column(String)
    factibilidad = Column(Integer)
    impacto = Column(Integer)

    #Relación 1:N con projec, mejor mapeada
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="ideas")




class Project(BaseModel):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)

    idea_inicial = Column(String)
    requisitos_iniciales = Column(String)
    claves_iniciales = Column(String)

    empatizar1 = Column(String, default="")  # Entrevistas 10 usuarios
    empatizar2 = Column(String, default="")  # Visitar 10 lugares

    name = Column(String)
    description = Column(String)
    responsable = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)
    user_name = Column(Integer, ForeignKey('users.name'))
    user = relationship("User", back_populates="projects")
    

    # Relación 1:1 con simulacion_produccion
    simulacion_produccion = relationship("SimulacionProduccion", back_populates="project",  cascade="all, delete-orphan", uselist=False)
    parametros_sustentables = relationship("ParametrosSustentables", back_populates="project",  cascade="all, delete-orphan", uselist=False)
    costos = relationship("Costos", back_populates="project",  cascade="all, delete-orphan", uselist=False)

    #Relación 1:N con prototypes, mejor mapeada
    prototypes: Mapped[List["Prototype"]] = relationship(back_populates="project", cascade="all, delete-orphan", passive_deletes=True)
    empaques: Mapped[List["Empaque"]] = relationship(back_populates="project", cascade="all, delete-orphan", passive_deletes=True) 

    #En este caso solo tiene 1. Podriamos llegar a aumentarlo a varios
    evaluaciones_avances: Mapped[List["EvaluacionAvance"]] = relationship(back_populates="project", cascade="all, delete-orphan", passive_deletes=True)
    ideas: Mapped[List["Ideacion"]] = relationship(back_populates="project", cascade="all, delete-orphan", passive_deletes=True)

    tests_sensoriales: Mapped[List["Test_Sensorial"]] = relationship(back_populates="project", cascade="all, delete-orphan", passive_deletes=True)

    foods = relationship("Food", secondary="food_projects", back_populates="projects",cascade="save-update, merge",  passive_deletes=True ) #No queremos que elimine las comidas

    #constuctor que no crea prototypes ni foods
    def __init__(self, name, user, responsable=None, idea_inicial=None, requisitos_iniciales=None, claves_iniciales=None):
        self.user = user
        self.name = name
        self.user_name = user.name
        foods = []
        prototypes  = []
        
    #Además debemos modificar los Prototipos ya que tienen asociados por otro lado los alimentos
    def añadirAlimento(self, food_id, Session):
        
        food = Session.query(Food).filter(Food.id == food_id).first()
        
        if food:
            try: 
                self.foods.append(food)
                Session.commit()
                for prototitpo in self.prototypes:
                    food_prototype = Session.query(FoodPrototype).filter_by(food_id=food.id, prototype_id=prototitpo.id).first()
                    print("Buscando food_prototype ", food_prototype)
                    if not food_prototype:
                        food_prototype = FoodPrototype(food_id=food.id, prototype_id=prototitpo.id, cantidad=0, food_description=food.food_description)
                        prototitpo.food_prototypes.append(food_prototype)
                        Session.add(food_prototype)
                        Session.commit()
            except:
                print("Este proyecto ya tiene el alimento asignado\n")
                Session.rollback()
        else:
            print("No se encontró el alimento")
        
       
        

    def quitarAlimento(self, food, Session):
        
        for f in self.foods:
            if f.id == food.id:
                self.foods.remove(f)
                Session.commit()
                break
        for prototipo in self.prototypes:
            food_prototype = Session.query(FoodPrototype).filter_by(food_id=food.id, prototype_id=prototipo.id).first()
            if food_prototype:
                print("Eliminando de food_protype: ", food_prototype)
                prototipo.food_prototypes.remove(food_prototype)
                Session.delete(food_prototype)
                Session.commit()
        
        


    def add_food(self, food):
        self.foods.append(food)
    def add_prototypes(self, prototype):
        self.prototypes.append(prototype)
    def __repr__(self):
        return f"Project(name={self.name}, food_description={[food.food_description for food in self.foods]}) \
            prototipos={[p.name for p in self.prototypes]}"

   

    def update_status(self, status):
        self.status = status


class Empaque(BaseModel):
    __tablename__ = 'empaques'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    caracteristicas = Column(String)
    precio = Column(Float, default=0.0)  # Precio en dolares
    is_favourite = Column(Boolean, default=False) 
    proveedor = Column(String)
    web = Column(String)
    imagen1 = Column(String) #cada empaque un maximo de 3 imagenes
    imagen2 = Column(String)
    imagen3 = Column(String)
    notas = Column(String)

    chequeo = Column(JSON) #formulario, por orden se guarda booleano de la pregunta


    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="empaques")

    def __repr__(self):
        return f"id {self.id}, nombre: {self.nombre}, precio: {self.precio}, notas: {self.notas}"




    


class FoodPrototype(BaseModel):
    __tablename__ = 'food_prototypes'
    id = Column(Integer, primary_key=True)
    food_id = Column('food_id', Integer, ForeignKey('foods.id', ondelete="CASCADE"))
    prototype_id = Column('prototype_id', Integer, ForeignKey('prototypes.id', ondelete="CASCADE"))
    cantidad = Column(Float, nullable=False, default=0)
    food_description = Column(String)
    

    prototype = relationship('Prototype', back_populates='food_prototypes')
    food = relationship("Food")




    def __init__(self, food_id, prototype_id, food_description=None, cantidad=0):
        self.food_id = food_id
        self.food_description=food_description
        self.prototype_id = prototype_id
        self.cantidad = cantidad
        
        if food_description is None:
            food = Session.query(Food).filter(Food.id == food_id).first()
            if food:
                self.food_description = food.food_description
            else:
                self.food_description = None
        
        
fase_evaluacion_avance = Table(
    "fase_evaluacion_avance",
    Base.metadata,
    Column("fase_id", ForeignKey("fases.id"), primary_key=True),
    Column("evaluacion_id", ForeignKey("evaluacion_avance.id"), primary_key=True)
    
)

class Fase(BaseModel):
    __tablename__ = 'fases'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    numero_paso = Column(Integer, nullable=False, default=0)
    estado = Column(Integer, nullable=False, default=0)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    evaluaciones: Mapped[List["EvaluacionAvance"]] = relationship(
        "EvaluacionAvance",
        secondary=fase_evaluacion_avance,
        back_populates="fases"
    )


class EvaluacionAvance(BaseModel):
    __tablename__ = 'evaluacion_avance'
    id = Column(Integer, primary_key=True)
    avance = Column(Boolean, default=False) 
    avance2 = Column(Boolean, default=False) 
    avance3 = Column(Boolean, default=False) 
    finalizacion = Column(Boolean, default=False)
    comentarios = Column(String)
    numero_fases = Column(Integer, nullable=False, default=0)
    conclusiones = Column(String)

    #A partir de la sgunda evaluacion se usan
    cualidades = Column(String)
    debilidades = Column(String)
    mejoras = Column(String)

    # Relación muchos a muchos con Fase, no se eliminan las fases al eliminar la evaluación
    fases: Mapped[List["Fase"]] = relationship(
        "Fase",
        secondary=fase_evaluacion_avance,
        back_populates="evaluaciones"
    )

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="evaluaciones_avances")

    def __repr__(self):
        return f"EvaluacionAvance(id={self.id}, avance={self.avance}, comentarios={self.comentarios}, numero_fases={self.numero_fases}, cualidades={self.cualidades}, debilidades={self.debilidades}, mejoras={self.mejoras}, finalizacion={self.finalizacion})"



class ParametrosSustentables(BaseModel):
    __tablename__ = 'parametros_sustentables'
    id = Column(Integer, primary_key=True)
    comentarios = Column(String)
    chequeo = Column(JSON) #formulario, por orden se guarda booleano de la pregunta

    consumo_agua = Column(Float)  # m³/mes
    consumo_electricidad = Column(Float)  # kWh/mes
    consumo_gas_licuado = Column(Float)  # L/mes
    materia_prima_usada = Column(Float)  # kg/mes
    uso_empaques = Column(Float)  # kg/mes
    residuos_solidos_generados = Column(Float)  # kg/mes
    residuos_liquidos = Column(Float)  # L/mes
    emisiones_directas_co2 = Column(Float)  # kg CO2/mes
    emisiones_indirectas_electricidad = Column(Float)  # kg CO2/mes
    subproductos_valorizados = Column(Float)  # kg/mes
    km_recorridos_insumos = Column(Float)  # km/mes
    tipo_transporte_principal = Column(String)  # e.g., "Camión refrigerado"
    carga_total_transportada = Column(Float)  # kg/mes
    produccion_mensual_batido = Column(Float)  # kg de batido/mes
    mermas_proceso = Column(Float)  # porcentaje
    uso_productos_limpieza = Column(Float)  # L/mes
    ubicacion_proveedores = Column(String)  # texto libre
    origen_insumos_local= Column(Float)  
    origen_insumos_importado= Column(Float) 
    consumo_energia_renovable = Column(Float)  # kWh/mes

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="parametros_sustentables")



class EtapaProduccion(BaseModel):
    __tablename__ = 'etapas_produccion'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    descripcion = Column(String)
    equipos_requeridos = Column(String)  # Lista de equipos requeridos en formato JSON
    proveedor = Column(String)  # Proveedor del equipo
    web_proveedor = Column(String)  # Web del proveedor del equipo
    costo_estimado = Column(String)  # Costo estimado del equipo
    numero_etapa = Column(Integer, nullable=False, default=0)  

    # Relación con proyectos
    simulacion_id: Mapped[int] = mapped_column(ForeignKey("simulacion_produccion.id"))
    simulacion: Mapped["SimulacionProduccion"] = relationship(back_populates="etapas")


class EquipoProduccion(BaseModel):
    __tablename__ = 'equipos_produccion'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    esta_en_planta = Column(Boolean, default=False)  # Indica si el equipo está en la planta

    ubicacion = Column(String)  # Ubicación del equipo en la planta
    especificaciones = Column(String)  # Especificaciones del equipo
    dimensiones = Column(String) 
    proveedor = Column(String)
    web_proveedor = Column(String)
    costo = Column(Float, default=0.0)  
    imagen = Column(String)  # Imagen del equipo
    requisitos_uso = Column(String)  # Requisitos de uso del equipo
    requisitos_instalacion = Column(String)  # Requisitos de instalación del equipo
    observaciones = Column(String)  # Observaciones sobre el equipo

    # Relación con proyectos
    simulacion_id: Mapped[int] = mapped_column(ForeignKey("simulacion_produccion.id"))
    simulacion: Mapped["SimulacionProduccion"] = relationship(back_populates="equipos_produccion")



class SimulacionProduccion(BaseModel):
    __tablename__ = 'simulacion_produccion'
    id = Column(Integer, primary_key=True)
    tabla = Column(JSON)  #En principio no se usa
    diagrama_flujo = Column(String)
    imagen = Column(String) #Pueden llegar a subir una imagen de la línea de producción

    # Relación con etapas de producción, se borran si se elimina la simulación
    etapas: Mapped[List["EtapaProduccion"]] = relationship(back_populates="simulacion", cascade="all, delete-orphan", passive_deletes=True)
    equipos_produccion: Mapped[List["EquipoProduccion"]] = relationship(back_populates="simulacion", cascade="all, delete-orphan", passive_deletes=True)

    # Relación con proyectos
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="simulacion_produccion")

    def __repr__(self):
        return f"SimulacionProduccion(id={self.id}, diagrama_flujo={self.diagrama_flujo}, imagen={self.imagen}, etapas_produccion={[etapa.nombre for etapa in self.etapas]})"
    

class ValoresNutricionales(BaseModel):
    __tablename__ = 'valores_nutricionales'
    id = Column(Integer, primary_key=True)
    energia_kcal = Column(Float, nullable=False, default=0.0)  # Energía en kilocalorías
    proteinas = Column(Float, nullable=False, default=0.0)  # Proteínas en gramos
    grasas_totales = Column(Float, nullable=False, default=0.0)  # Grasas totales en gramos
    grasas_saturadas = Column(Float, nullable=False, default=0.0)  # Grasas saturadas en gramos
    grasas_trans = Column(Float, nullable=False, default=0.0)  # Grasas trans en gramos

    carbohidratos = Column(Float, nullable=False, default=0.0)  # Carbohidratos en gramos
    fibra = Column(Float, nullable=False, default=0.0)  # Fibra en gramos
    azucares = Column(Float, nullable=False, default=0.0)  # Azúcares en gramos

    sodio = Column(Float, nullable=False, default=0.0)  # Sodio en gramos
    sal = Column(Float, nullable=False, default=0.0)  # Sal en gramos

    prototype_id: Mapped[int] = mapped_column(ForeignKey("prototypes.id"))
    prototype: Mapped["Prototype"] = relationship(back_populates="valores_nutricionales")

    def calcular_valores_nutricionales(self):
        energia_kcal_parcial = 0.0
        proteinas_parcial = 0.0
        grasas_totales_parcial = 0.0
        grasas_saturadas_parcial = 0.0
        grasas_trans = 0.0
        sal = 0.0
        sodio = 0.0
        fibra = 0.0
        azucares = 0.0
        carbohidratos = 0.0

        for food_prototype in self.prototype.food_prototypes:
            food = food_prototype.food
            cantidad = food_prototype.cantidad

            print(f"Calculando valores nutricionales para {food.food_description} con cantidad {cantidad}g")
            
            # Calcular valores parciales para cada alimento
            energia_kcal_parcial += (food.energy_kcal * cantidad) / 100
            proteinas_parcial += (food.protein * cantidad) / 100
            grasas_totales_parcial += (food.total_fat * cantidad) / 100
            grasas_saturadas_parcial += (food.saturated_fat * cantidad) / 100
            grasas_trans += (food.trans_fat * cantidad) / 100
            sodio += (food.sodium * cantidad) / 100
            fibra += (food.fiber * cantidad) / 100
            azucares += (food.sugars * cantidad) / 100
            carbohidratos += (food.carbohydrates * cantidad) / 100

        self.energia_kcal = round(energia_kcal_parcial, 3)
        self.proteinas = round(proteinas_parcial, 3)
        self.grasas_totales = round(grasas_totales_parcial, 3)
        self.grasas_saturadas = round(grasas_saturadas_parcial, 3)
        self.grasas_trans = round(grasas_trans, 3)
        self.sal = round(sal, 3)
        self.sodio = round(sodio, 3)
        self.fibra = round(fibra, 3)
        self.azucares = round(azucares, 3)
        self.carbohidratos = round(carbohidratos, 3)
        Session.commit()

        print(f"Valores nutricionales actualizados {self}:")



    def __init(self, protoype):
        self.prototype = protoype
        self.prototype_id = protoype.id
        self.calcular_valores_nutricionales()

    def __repr__(self):
        return (f"ValoresNutricionales(energia_kcal={self.energia_kcal}, proteinas={self.proteinas}, "
                f"grasas_totales={self.grasas_totales}, grasas_saturadas={self.grasas_saturadas}, carbohidratos={self.carbohidratos}, "
                f"fibra={self.fibra}, azucares={self.azucares}, sodio={self.sodio}, sal={self.sal})")
        




class Prototype(BaseModel):
    __tablename__ = 'prototypes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    complexity = Column(String)
    composition = Column(String)
    cost = Column(Float)
    validation = Column(String)

    peso_inicial = Column(Float, nullable=False, default=0.0)  # Precio en dolares
    peso_final = Column(Float, nullable=False, default=0.0)  # Precio en dolares

    comentarios = Column(String)


    is_favourite = Column(Boolean, default=False)

    # Relación 1:1 con valores nutricionales
    valores_nutricionales = relationship("ValoresNutricionales", back_populates="prototype",  cascade="all, delete-orphan", uselist=False)



    #Relación 1:N con prototypes, mejor mapeada
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="prototypes")
    

     

    #Nos da acceso a la tabla intermedia food_prototypes, para acceder a los gramos
    food_prototypes = relationship('FoodPrototype', back_populates='prototype', cascade='all, delete-orphan')

    def __init__(self, foods=None, project_id=None, name=None, version=None, complexity=None, composition=None, cost=None, validation=None, project=None):
        self.project_id = project_id if project_id else (project.id if project else None)
        self.name = name
        self.version = version
        self.complexity = complexity
        self.composition = composition
        self.cost = cost
        self.validation = validation
        self.project = project

        Session.add(self)
        Session.commit()  # Ahora `self.id` ya existe

        if project and project.foods:
            for f in project.foods:
                existing_fp = Session.query(FoodPrototype).filter_by(food_id=f.id, prototype_id=self.id).first()
                if existing_fp:
                    print(f"Ya existe FoodPrototype para food_id={f.id} y prototype_id={self.id}")
                else:
                    print(f"Creando FoodPrototype para food_id={f.id} y prototype_id={self.id}")
                    food_prototype = FoodPrototype(food_id=f.id, prototype_id=self.id, cantidad=0, food_description=f.food_description)
                    Session.add(food_prototype)

        Session.commit()
       
    def es_favorito(self):
        for p in self.project.prototypes:
            p.is_favourite = False
        self.is_favourite = True
    
    def actualizar_peso(self):
        self.peso_inicial=0
        for f in self.food_prototypes:
            self.peso_inicial+=f.cantidad
       
        Session.commit()


    def asignar_cantidad(self, food_id, cantidad):
        
        food_id = int(food_id)
        cantidad = float(cantidad)
        i=0
        for food_prototype in self.food_prototypes:
            #Aseguramos que es un int para la comparación
            food_prototype.food_id = int(food_prototype.food_id)
            if food_prototype.food_id == food_id:
                food_prototype.cantidad = cantidad
                Session.commit()
                print(f"Asignado cantidad: {food_prototype.food_description}= {food_prototype.cantidad}")
                i=1
                print(self)
                break
        #Hay que crear el food_prototype si no existe
        if i==0:
            food = Session.query(Food).filter(Food.id == food_id).first()
            if food:
                food_prototype = FoodPrototype(food_id=food_id, prototype_id=self.id, cantidad=cantidad, food_description=food.food_description)
                Session.add(food_prototype)
                Session.commit()
                print(f"Creado FoodPrototype para food_id={food_id} y prototype_id={self.id} con cantidad {cantidad}")
            else:
                print(f"No se encontró el alimento con id {food_id}")


            

    def devolver_cantidad(self, food_id):
       
        food_prototype = Session.query(FoodPrototype).filter_by(food_id=food_id, prototype_id=self.id).first()
        if food_prototype:
            return food_prototype.cantidad
            
        else:
            print("El alimento no está asociado a este prototipo.")
        Session.commit()
       

    def verificar_alimentos(self):
        if self.foods != self.project.foods:
            for f in self.project.foods:
                if f not in self.foods:
                    self.foods.append(f)
           
    def mostrar_cantidades(self):
        
        food_prototypes = Session.query(FoodPrototype).filter_by( prototype_id=self.id)
        for f in food_prototypes:
            print(f"Producto {f.food_description} con cantidad {f.cantidad}")
            
        else:
            print("El alimento no está asociado a este prototipo.")
        Session.commit()
        


    def __repr__(self):
        food_descriptions = ""
        for f in self.food_prototypes:
            food_descriptions += f"{f.food_description} ({f.cantidad}g), "
        
        return f"Prototype(name={self.name}, version={self.version}, food_prototypes={food_descriptions})"      
        

            
    def add_food(self, food):
        self.foods.append(food)

    def eliminar_alimento(self, food_id):
        food = self.foods.filter_by(id=food_id).first()
        self.foods.remove(food)

    def validate_prototype(self):
        self.validation = "Aprobado"

    def update_version(self, version):
        self.version = version

# Association table for the many-to-many relationship


class Food(BaseModel):
    __tablename__ = 'foods'
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, nullable=False, default=-1)  # Número identificador del alimento
    food_description = Column(String)
    grams = Column(Float, nullable=False, default=0.0)
    precio = Column(Float, nullable=False, default=0.0)  # Precio en dolares
    energy_kcal = Column(Float, nullable=False, default=0.0)  # Energía en kilocalorías


    projects = relationship("Project", secondary="food_projects", back_populates="foods")
    # Nutrientes basicos
    protein = Column(Float, nullable=False, default=0.0)  # Proteína en gramos
    carbohydrates = Column(Float, nullable=False, default=0.0)  # Carbohidratos en gramos
    sugars = Column(Float, nullable=False, default=0.0)  # Azúcares totales en gramos
    fiber = Column(Float, nullable=False, default=0.0)  # Fibra dietética total en gramos
    total_fat = Column(Float, nullable=False, default=0.0)  # Grasa total en gramos
    saturated_fat = Column(Float, nullable=False, default=0.0)  # Ácidos grasos saturados en gramos
    monounsaturated_fat = Column(Float, nullable=False, default=0.0)  # Ácidos grasos monoinsaturados en gramos
    polyunsaturated_fat = Column(Float, nullable=False, default=0.0)  # Ácidos grasos poliinsaturados en gramos
    trans_fat = Column(Float, nullable=False, default=0.0)  # Grasas trans
    cholesterol = Column(Float, nullable=False, default=0.0)  # Colesterol en miligramos
    sodium = Column(Float, nullable=False, default=0.0)  # Sodio en miligramos
    water = Column(Float, nullable=False, default=0.0)  # Agua en gramos
    potassium = Column(Float, nullable=False, default=0.0)  # Potasio en miligramos
    calcium = Column(Float, nullable=False, default=0.0)  # Calcio en miligramos
    iron = Column(Float, nullable=False, default=0.0)  # Calcio en miligramos
    #Sodio es sal


    #Constructor de la clase solo con food_description
    def __init__(self, food_description):
        self.food_description = food_description
        


    @classmethod
    def buscar_alimentos(cls, termino, limite=10):
       
       
            resultados = (
                Session.query(cls)
                .filter(cls.food_description.ilike(f"%{termino}%"))
                .limit(limite)
                .all()
            )
            return resultados  # Devuelve una lista de objetos Food
    
    #Setter para verificar que es positivo el valor del precio. Se va asignando y guardando en la BD
    def setPrecio(self, precio):
        if(precio>0):
            self.precio = precio
            Session.commit()
        else: 
            print("No se pudo asignar el precio")


    def __repr__(self):
        return (
            f"Food Description: {self.food_description}\n"
            f"Grams: {self.grams}\n"
            f"Energy (kcal): {self.energy_kcal}\n"
            f"\tProtein: {self.protein}\n"
            f"\tCarbohydrates: {self.carbohydrates}\n"
            f"\tSugars: {self.sugars}\n"
            f"\tFiber: {self.fiber}\n"
            f"\tTotal Fat: {self.total_fat}\n"
            f"\tSaturated Fat: {self.saturated_fat}\n"
            f"\tMonounsaturated Fat: {self.monounsaturated_fat}\n"
            f"\tPolyunsaturated Fat: {self.polyunsaturated_fat}\n"
            f"\tCholesterol: {self.cholesterol}\n"
            f"\tSodium: {self.sodium}\n"
            f"\tWater: {self.water}\n"
            f"\tPotassium: {self.potassium}\n"
            f"\tCalcium: {self.calcium}\n"
        )


#Base.metadata.drop_all(DatabaseSession.engine)
Base.metadata.create_all(DatabaseSession.engine)