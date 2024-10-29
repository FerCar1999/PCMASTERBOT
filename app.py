from openai import OpenAI

from repository import *
from PoblarDatos import *

client = OpenAI(api_key="ACA PONGAN LA APK")
import sqlite3
import streamlit as st
import requests
from difflib import SequenceMatcher
import re
import uuid


# Configura la API de OpenAI
# Reemplaza con tu clave de API de OpenAI

# Conectar a la base de datos SQLite
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crear la tabla de historial si no existe
"""
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    bot_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
"""

# Tabla de categorías
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# Tabla de chats (N/A)
"""
cursor.execute(
    
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_uuid TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    )
)"""

# Tabla principal de historial de chat  #chat_id INTEGER NOT NULL,
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""
)

# Tabla de palabras clave
#Se tiene pensado agregar categoria a las palabras
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL UNIQUE
    )
"""
)

# Tabla de relación entre chat_history y keywords
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS chat_keywords (
        chat_history_id INTEGER,
        keyword_id INTEGER,
        FOREIGN KEY (chat_history_id) REFERENCES chat_history (id),
        FOREIGN KEY (keyword_id) REFERENCES keywords (id),
        PRIMARY KEY (chat_history_id, keyword_id)
    )
"""
)

print("Base de datos y tablas creadas exitosamente.")
conn.commit()
conn.close()

#=============== para poblar datos ================
#poblar() #comentar luego del primer uso
#=========================================?========

# Función para interactuar con la API de OpenAI
def get_bot_response(money, prompt):
    # Solicitar respuesta del modelo
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Entregame una lista de los productos que necesito para una pc, mi presupuesto es de "
                + money
                + " y mi objetivo es"
                + prompt,
            }
        ],
    )

    # Obtener el contenido de la respuesta
    content = response.choices[0].message.content

    # Crear un nuevo prompt para extraer productos en formato de lista iterable
    list_prompt = (
        "entregame en un formato de lista iterable los productos de este texto, si el producto traer precio quitaselo : "
        + content
    )

    # Solicitar la lista de productos
    response_items = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": list_prompt}]
    )

    # Devolver ambos contenidos: la respuesta original y la lista de productos
    return [content, response_items.choices[0].message.content]


# Buscar enlaces de productos específicos usando Google
def search_product_links(component_list):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = ""

    for component in component_list:
        query = f"{component}"
        url = f"https://www.google.com/search?q={query}+comprar"
        product_links += f"- [{component}]({url})\n"

    return product_links


# Extraer los componentes de la respuesta del bot (simplemente separados por comas en este ejemplo)
def extract_components(bot_response):
    components = []
    lines = bot_response.split("\n")
    for line in lines:
        if ". " in line:
            component = line.split(". ")[1].strip()
            if component != "":
                component = component.replace(" ", "+")
                components.append(component)
    return components


# Interfaz con Streamlit
st.title("PCMasterBot 🖥️ - Tu asistente para armar o mejorar tu PC")

# Recoger entrada del usuario
user_money = st.text_input("¿Cuál es tu presupuesto?")

# Recoger entrada del usuario
user_input = st.text_input("¿Cuál es tu objetivo?")

if st.button("Enviar"):
    if user_input and user_money:
        
        #[bot_response, bot_items] = get_bot_response(user_money, user_input)
        
        # Guardar el chat en la base de datos
        #save_chat(user_input, bot_response + "\n" + product_links)
        [bot_response, bot_items]  = principal(user_input,user_money)
        
        # Extraer componentes de la respuesta del bot
        components = extract_components(bot_items)

        # Generar enlaces para cada componente
        product_links = search_product_links(components)
        
        # Mostrar respuesta y enlaces
        st.success(bot_response)
        st.markdown(product_links, unsafe_allow_html=True)
    else:
        st.warning("Por favor, ingresa un texto para enviar.")

# Mostrar historial de conversaciones
if st.button("Mostrar historial"):
    cursor.execute("SELECT * FROM chat_history")
    history = cursor.fetchall()
    st.write("Historial de chat:")
    for entry in history:
        st.write(f"👤 Usuario: {entry[2]}")
        st.write(f"🤖 Bot: {entry[3]}")
        st.write("---")
