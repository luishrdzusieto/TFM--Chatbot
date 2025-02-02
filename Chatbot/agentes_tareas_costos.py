from pymongo import MongoClient

# Conexión a MongoDB Atlas
mongo_uri = "mongodb+srv://lhernand:Unir2025%24@cluster0.kw5ss.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['aseguradora']
collection_clientes = db['asegurados']
collection_piezas = db['coste_reparaciones']

def verificar_cliente(nombre, apellido):
    """
    Verifica si un cliente está registrado en la base de datos MongoDB.

    Args:
        nombre (str): Nombre del cliente.
        apellido (str): Apellido del cliente.

    Returns:
        dict: Datos del cliente si está registrado, None en caso contrario.
    """
    cliente = collection_clientes.find_one({
        "nombre": {"$regex": f"^{nombre.strip()}$", "$options": "i"},
        "apellido": {"$regex": f"^{apellido.strip()}$", "$options": "i"}
    })
    return cliente  # Devuelve los datos completos si se encuentra, None si no existe

def ejecutar_flujo(entradas):
    """
    Busca información relevante en MongoDB basado en las entradas proporcionadas.

    Args:
        entradas (list of dict): Lista de diccionarios con 'Componente'.

    Returns:
        list of dict: Información detallada de los componentes encontrados.
    """
    contenido = []
    for entrada in entradas:
        pieza = collection_piezas.find_one({"Componente": entrada["Componente"]})
        if pieza:
            pieza["Coste_Total"] = int(pieza["Coste_Material"]) + int(pieza["Coste_Mano_Obra"])
            contenido.append(pieza)
    
    # Preguntar al usuario si hay algún daño adicional no detectado
    agregar_manual = input("¿Hay algún daño adicional que no se haya detectado? (si/no): ").strip().lower()
    if agregar_manual == "si":
        print("Opciones de piezas disponibles:")
        piezas_disponibles = collection_piezas.distinct("Componente")
        for i, pieza in enumerate(piezas_disponibles, 1):
            print(f"{i}. {pieza}")
        
        try:
            seleccion = int(input("Selecciona el número de la pieza dañada: "))
            if 1 <= seleccion <= len(piezas_disponibles):
                pieza_manual = collection_piezas.find_one({"Componente": piezas_disponibles[seleccion - 1]})
                if pieza_manual:
                    pieza_manual["Coste_Total"] = int(pieza_manual["Coste_Material"]) + int(pieza_manual["Coste_Mano_Obra"])
                    contenido.append(pieza_manual)
            else:
                print("Selección inválida. No se agregó ningún daño adicional.")
        except ValueError:
            print("Entrada no válida. No se agregó ningún daño adicional.")

    return contenido
