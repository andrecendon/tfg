import json
from modelo.models import Food, DatabaseSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from time import sleep

session = DatabaseSession()

pr = session.query(Food).all()
for project in pr:
    print(project.food_description)
#eliminamos todos los alimentos de la base de datos
session.query(Food).delete()
session.commit()

#Añadimos todos los alimentos a partir del json
#Diccionario para asignar al json el nombre de los atributos
dic_nutrientes = {
    "Iron, Fe": "iron",
    "Energy": "energy_kcal",
    "Magnesium, Mg": "magnesium",
    "Phosphorus, P": "phosphorus",
    "Potassium, K": "potassium",
    "Sodium, Na": "sodium",
    "Zinc, Zn": "zinc",
    "Nitrogen": "nitrogen",
    "Copper, Cu": "copper",
    "Total lipid (fat)": "total_fat",
    "Manganese, Mn": "manganese",
    "Ash": "ash",
    "Selenium, Se": "selenium",
    "Fiber, total dietary": "fiber",
    "Fiber, insoluble": "fiber",
    "Fatty acids, total saturated": "saturated_fat",
    "Fatty acids, total monounsaturated": "monounsaturated_fat",
    "Fatty acids, total polyunsaturated": "polyunsaturated_fat",
    "Cholesterol": "cholesterol",
    "Sugars, Total": "sugars",
    "Water": "water",
    "Calcium, Ca": "calcium",
    "Protein": "protein",
    "Carbohydrate, by difference": "carbohydrates",
    #""Carbohydrate, by summation": "carbohydrates","
}

# Load JSON data
with open("foundationDownload.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Function to print attribute names
def asignar_nutrientes(food_data, f):
    for key in food_data.keys():
        if key == "foodNutrients":
            for n in food_data[key]:
                n2 = n.get('nutrient', None)
                
                if  n2 is not None:
                    mediana = n.get('median', None)
                    if mediana is None: 
                        mediana = n.get('amount', None)
                    nombre_nutriente = n2['name']
                    #print("NUTRIENT : ", nombre_nutriente)
                    
                    if(nombre_nutriente in dic_nutrientes):
                        nombre_nutriente_final = dic_nutrientes[nombre_nutriente]                     
                        setattr(f, nombre_nutriente_final, mediana)
                        #sleep(1)
                        #print("\t Asignando: ", nombre_nutriente_final, nombre_nutriente, mediana)

                        
    
    
                
        

for food_data in data["FoundationFoods"]:
    nombre = food_data.get('description', 'No description')
    if nombre!= 'No description': 
        food = Food(food_description=nombre)
        asignar_nutrientes(food_data, food)
        #metemos en la base de datos
        #print("Metemos comida: ", food)
        session.add(food)
        
      

session.commit()
session.close()