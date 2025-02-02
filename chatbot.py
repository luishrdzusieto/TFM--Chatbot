import streamlit as st

# Título del chatbot
st.title("Chatbot para detección de daños en coches 🚗")

# Paso 1: Pedir la marca del coche
marca = st.text_input("Introduce la marca de tu coche", placeholder="Ejemplo: Toyota")

# Validar entrada
if marca:
    st.write(f"¡Genial! Marca seleccionada: {marca}")

    # Paso 2: Subir la imagen del coche
    uploaded_file = st.file_uploader("Sube una imagen del coche")

    if uploaded_file:
        # Mostrar la imagen subida
        st.image(uploaded_file, caption="Imagen subida", use_column_width=True)
        
        # Simular una respuesta del chatbot
        st.success("¡Gracias! Estamos procesando la imagen...")
        st.write("👉 En esta versión inicial, aún no procesamos imágenes. Pronto te daremos un diagnóstico y un presupuesto.")
