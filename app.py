from openai import OpenAI

client = OpenAI(api_key="ACA PONGAN LA APK")
import sqlite3
import streamlit as st
import requests

# Configura la API de OpenAI
  # Reemplaza con tu clave de API de OpenAI

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear la tabla de historial si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    bot_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

# Función para guardar mensajes en la base de datos
def save_chat(user_input, bot_response):
    cursor.execute('INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)', (user_input, bot_response))
    conn.commit()
    
# Función para guardar mensajes en la base de datos
def find_chat(user_input, bot_response):
    cursor.execute('INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)', (user_input, bot_response))
    conn.commit()

# Función para interactuar con la API de OpenAI
def get_bot_response(money, prompt):
    # Solicitar respuesta del modelo
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Entregame una lista de los productos que necesito para una pc, mi presupuesto es de "+money+" y mi objetivo es"+ prompt }]
    )
    
    # Obtener el contenido de la respuesta
    content = response.choices[0].message.content
    
    # Crear un nuevo prompt para extraer productos en formato de lista iterable
    list_prompt = "entregame en un formato de lista iterable los productos de este texto, si el producto traer precio quitaselo : " + content
    
    # Solicitar la lista de productos
    response_items = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": list_prompt}]
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
    lines = bot_response.split('\n')
    for line in lines:
        if ". " in line:
            component = line.split('. ')[1].strip()
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
        [bot_response, bot_items] = get_bot_response(user_money, user_input)

        # Extraer componentes de la respuesta del bot
        components = extract_components(bot_items)

        # Generar enlaces para cada componente
        product_links = search_product_links(components)

        # Guardar el chat en la base de datos
        save_chat(user_input, bot_response + "\n" + product_links)

        # Mostrar respuesta y enlaces
        st.success(bot_response)
        st.markdown(product_links, unsafe_allow_html=True)
    else:
        st.warning("Por favor, ingresa un texto para enviar.")

# Mostrar historial de conversaciones
if st.button("Mostrar historial"):
    cursor.execute('SELECT * FROM chat_history')
    history = cursor.fetchall()
    st.write("Historial de chat:")
    for entry in history:
        st.write(f"👤 Usuario: {entry[1]}")
        st.write(f"🤖 Bot: {entry[2]}")
        st.write("---")
