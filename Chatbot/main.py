import os
import streamlit as st
import pandas as pd
import datetime
import uuid
import logging
from pymongo import MongoClient
from agentes_tareas_costos import verificar_cliente
from utils import generar_pdf
from predict import detectar_componentes

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chatbot - Detección de Daños", page_icon="🚗", layout="centered")

# Configuración del registro de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Cargar estilos desde el archivo CSS
with open("styles.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Conexión a MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://lhernand:Unir2025%24@cluster0.kw5ss.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(mongo_uri)
db = client['aseguradora']
collection_costes = db['coste_reparaciones']

# Crear carpeta 'Historico fotos' si no existe
if not os.path.exists("Historico fotos"):
    os.makedirs("Historico fotos")

# Ruta del CSV donde se almacenarán los siniestros
csv_path = "aseguradora.accidentes.csv"

# Mapa entre los componentes detectados por YOLO y los nombres en la base de datos
mapa_clases = {
    'damaged door': 'Puerta',
    'damaged headlight': 'Faro',
    'damaged wind shield': 'Parabrisas',
    'damaged hood': 'Capó',
    'damaged bumper': 'Parachoques',
    'damaged window': 'Ventana',
    'damaged mirror': 'Espejo',
    'dent': 'Abolladura'
}

# Título del chatbot
st.title("Chatbot para Detección de Daños en Coches 🚗")

# Paso 0: Verificación de cliente
nombre = st.text_input("Introduce tu nombre:")
apellido = st.text_input("Introduce tu apellido:")

if nombre and apellido:
    cliente = verificar_cliente(nombre, apellido)
    if cliente:
        st.success(f"¡Bienvenido {nombre} {apellido}!")

        marca_cliente = cliente.get("marca_vehiculo", "")
        modelo_cliente = cliente.get("modelo_vehiculo", "")
        
        if marca_cliente and modelo_cliente:
            st.write(f"Marca detectada: {marca_cliente}")
            st.write(f"Modelo detectado: {modelo_cliente}")

            # Paso 1: Subir imágenes del coche
            uploaded_files = st.file_uploader("Sube imágenes del coche:", accept_multiple_files=True)

            if uploaded_files:
                all_detected_components = []
                resultado_modelo = {}
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    temp_file_name = f"imagen_temp_{idx}.jpg"
                    with open(temp_file_name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.image(temp_file_name, caption=f"Imagen subida {idx+1}", use_column_width=True)

                    # Detectar componentes dañados
                    st.info(f"Procesando la imagen {idx+1} para detectar daños...")
                    componentes_detectados = detectar_componentes(temp_file_name)
                    
                    if componentes_detectados:
                        componentes_confirmados = []
                        
                        for componente in componentes_detectados:
                            # Traducir el componente al nombre en la base de datos
                            nombre_componente = mapa_clases.get(componente, componente)
                            confirmacion = st.radio(
                                f"¿Se ha detectado correctamente el daño en {nombre_componente}?",
                                ('Sí', 'No'),
                                key=f"confirm_{componente}_{idx}"
                            )
                            if confirmacion == 'Sí':
                                componentes_confirmados.append(nombre_componente)
                                resultado_modelo[componente] = 'Acierto'
                            else:
                                resultado_modelo[componente] = 'Fallido'
                        
                        all_detected_components.extend(componentes_confirmados)
                
                # Paso 2: Agregar daños manualmente
                piezas_disponibles = collection_costes.distinct("componente")
                piezas_seleccionadas = st.multiselect("Selecciona piezas adicionales dañadas:", piezas_disponibles)

                if piezas_seleccionadas:
                    all_detected_components.extend(piezas_seleccionadas)

                # Paso 3: Calcular costos
                if all_detected_components:
                    with st.spinner("Calculando costos relacionados con los daños..."):
                        costos = []
                        coste_total_siniestro = 0
                        
                        for componente in all_detected_components:
                            try:
                                logger.info(f"Buscando información para el componente: {componente}")
                                costo = collection_costes.find_one({
                                    "marca_vehiculo": marca_cliente,
                                    "modelo_vehiculo": modelo_cliente,
                                    "componente": componente
                                })
                                if costo:
                                    logger.info(f"Información encontrada para {componente}: {costo}")
                                    costos.append(costo)
                                    coste_total_siniestro += round(costo.get('coste_material', 0) + costo.get('coste_mano_obra', 0), 2)
                                else:
                                    logger.warning(f"No se encontró información para el componente: {componente}")
                            except Exception as e:
                                logger.error(f"Error al procesar el componente {componente}: {e}")
                        
                        if costos:
                            logger.info(f"Costos calculados: {costos}")
                            st.write("Costos calculados:", costos)
                            st.write(f"Coste Total Siniestro: {coste_total_siniestro} EUR")

                            # Generar y descargar informe
                            if st.button("Generar Informe en PDF"):
                                generar_pdf(cliente, costos, "imagen_temp_0.jpg", "informe_daños.pdf", coste_total_siniestro)
                                with open("informe_daños.pdf", "rb") as pdf_file:
                                    st.download_button(
                                        label="Descargar Informe PDF",
                                        data=pdf_file,
                                        file_name="informe_daños.pdf",
                                        mime="application/pdf",
                                    )

                                # Actualizar el archivo CSV después de generar el PDF
                                try:
                                    fecha_consulta = datetime.datetime.now().strftime("%d/%m/%Y")
                                    df = pd.read_csv(csv_path, sep=',', encoding='utf-8')
                                    last_id_chatbot = df['id_chatbot'].dropna().astype(int).max() if not df.empty else 0
                                    id_chatbot = last_id_chatbot + 1
                                    registros = []
                                    for costo in costos:
                                        nuevo_registro = {
                                            "_id": str(uuid.uuid4()),
                                            "id_chatbot": id_chatbot,
                                            "fecha_consulta": fecha_consulta,
                                            "nombre": nombre,
                                            "apellido": apellido,
                                            "marca_vehiculo": marca_cliente,
                                            "modelo_vehiculo": modelo_cliente,
                                            "componente": costo["componente"],
                                            "coste_material": costo["coste_material"],
                                            "coste_mano_obra": costo["coste_mano_obra"],
                                            "coste_total": costo["coste_material"] + costo["coste_mano_obra"]
                                        }
                                        registros.append(nuevo_registro)
                                    df = pd.concat([df, pd.DataFrame(registros)], ignore_index=True)
                                    temp_csv_path = "aseguradora_temp.csv"
                                    df.to_csv(temp_csv_path, sep=',', encoding='utf-8', index=False)
                                    os.replace(temp_csv_path, csv_path)
                                    st.success("Archivo CSV actualizado correctamente después de generar el PDF.")
                                except Exception as e:
                                    st.error(f"Error al actualizar el archivo CSV: {e}")