import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, inspect, Inspector, MetaData
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column, scoped_session
from sqlalchemy import ForeignKey, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from typing import List
from flask_login import UserMixin
from sqlalchemy import Table, UniqueConstraint
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

# Clase que nos permite hacer funciones/atbos globales a todos
class BaseModel(Base):
    __abstract__ = True
    __allow_unmapped__ = True



class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    contraseña = Column(String, nullable=False)
    email = Column(String)
    projects = relationship("Project", back_populates="user")

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
    resultados = Column(JSON) 
    comentarios = Column(String)
    type = Column(String)  # Columna discriminadora
    
    # Relación con proyectos
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tests_sensoriales")
    
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'sensorial'
    }

class Test_Sensorial_Inicial(Test_Sensorial): 
    __tablename__ = 'tests_sensoriales_iniciales'
    __mapper_args__ = {'polymorphic_identity': 'inicial'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)
    muestras = Column(JSON)  

class Test_Hedonico(Test_Sensorial): 
    __tablename__ = 'tests_hedonicos'
    __mapper_args__ = {'polymorphic_identity': 'hedonico'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)
    muestras = Column(JSON)  # Formato: {"muestra1": {"puntuacion": 5, "comentarios": ""}}

class Test_Aceptacion(Test_Sensorial): 
    __tablename__ = 'tests_aceptacion'
    __mapper_args__ = {'polymorphic_identity': 'aceptacion'}
    
    id = Column(Integer, ForeignKey('tests_sensoriales.id'), primary_key=True)
    muestra = Column(String)
    agrado = Column(String)  # Cambiado a Integer para puntuación
    sabor = Column(String)
    textura = Column(String)
    apariencia = Column(String)
    compra = Column(String)  # Mejor como booleano para intención de compra
     
    

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
    phases = relationship("Phase", back_populates="project")

    # Relación 1:1 con simulacion_produccion
    simulacion_produccion = relationship("SimulacionProduccion", back_populates="project",  cascade="all, delete-orphan", uselist=False)

    #Relación 1:N con prototypes, mejor mapeada
    prototypes: Mapped[List["Prototype"]] = relationship(back_populates="project")
    empaques: Mapped[List["Empaque"]] = relationship(back_populates="project")
    evaluaciones_avances: Mapped[List["EvaluacionAvance"]] = relationship(back_populates="project")

    tests_sensoriales: Mapped[List["Test_Sensorial"]] = relationship(back_populates="project")

    foods = relationship("Food", secondary="food_projects", back_populates="projects",cascade="all, delete")

    #constuctor que no crea prototypes ni foods
    def __init__(self, name, user, responsable=None, idea_inicial=None, requisitos_iniciales=None, claves_iniciales=None):
        self.user = user
        self.name = name
        self.user_name = user.name
        foods = []
        prototypes  = []
        
    def añadirAlimento(self, food_id, Session):
        
        food = Session.query(Food).filter(Food.id == food_id).first()
        
        if food:
            try: 
                self.foods.append(food)
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
        
        


    def add_food(self, food):
        self.foods.append(food)
    def add_prototypes(self, prototype):
        self.prototypes.append(prototype)
    def __repr__(self):
        return f"Project(name={self.name}, food_description={[food.food_description for food in self.foods]}) \
            prototipos={[p.name for p in self.prototypes]}"

    def add_phase(self, phase):
        self.phases.append(phase)

    def update_status(self, status):
        self.status = status


class Empaque(BaseModel):
    __tablename__ = 'empaques'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    caracteristicas = Column(String)
    precio = Column(String)
    proveedor = Column(String)
    web = Column(String)
    imagen = Column(String)
    notas = Column(String)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="empaques")

    def __repr__(self):
        return f"id {self.id}, nombre: {self.nombre}, precio: {self.precio}, notas: {self.notas}"



class Phase(BaseModel):
    __tablename__ = 'phases'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship("Project", back_populates="phases")

    def __repr__(self):
        return f"Phase(name={self.name})"
    


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
        
        
class Fase(BaseModel):
    __tablename__ = 'fases'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    estado = Column(Integer, nullable=False, default=0)  
    #porcentaje de avance
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    evaluacion_id: Mapped[int] = mapped_column(ForeignKey("evaluacion_avance.id"))
    evaluacion: Mapped["EvaluacionAvance"] = relationship(back_populates="fases")

class EvaluacionAvance(BaseModel):
    __tablename__ = 'evaluacion_avance'
    id = Column(Integer, primary_key=True)
    avance = Column(String)
    comentarios = Column(String)
    numero_fases = Column(Integer, nullable=False, default=0)

    #lista de fases
    fases: Mapped[List["Fase"]] = relationship(back_populates="evaluacion")


    # Relación 1:N con proyectos, mejor mapeada
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="evaluaciones_avances")


    def __repr__(self):
        return f"EvaluacionAvance(avance={self.avance})"


class SimulacionProduccion(BaseModel):
    __tablename__ = 'simulacion_produccion'
    id = Column(Integer, primary_key=True)
    tabla = Column(JSON)  #Luego hay que convertir a formato tabla con simulacion_produccion_IA
    diagrama_flujo = Column(String)  
    imagen = Column(String)

    # Relación con proyectos
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="simulacion_produccion")
    
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


    is_favourite = Column(Boolean, default=False)



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
                    Session.add(food_prototype)  # ✅ Solo agregamos aquí

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
        for food_prototype in self.food_prototypes:
            #Aseguramos que es un int para la comparación
            food_prototype.food_id = int(food_prototype.food_id)
            if food_prototype.food_id == food_id:
                food_prototype.cantidad = cantidad
                print(f"Asignado cantidad: {food_prototype.food_description}= {food_prototype.cantidad}")
                Session.commit()

                print(self)
                break
        print("No se pudo asignar cantidad")

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

    #prototypes = relationship("Prototype", secondary="food_prototypes", back_populates="foods") 

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
    cholesterol = Column(Float, nullable=False, default=0.0)  # Colesterol en miligramos
    sodium = Column(Float, nullable=False, default=0.0)  # Sodio en miligramos
    water = Column(Float, nullable=False, default=0.0)  # Agua en gramos
    potassium = Column(Float, nullable=False, default=0.0)  # Potasio en miligramos
    calcium = Column(Float, nullable=False, default=0.0)  # Calcio en miligramos
    iron = Column(Float, nullable=False, default=0.0)  # Calcio en miligramos


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