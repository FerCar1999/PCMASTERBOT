import sqlite3
import streamlit as st
from difflib import SequenceMatcher
import re
import uuid
import logging
from openai import OpenAI

from repository import *
from PoblarDatos import *

client = OpenAI(api_key="ACA PONGAN LA APK")

logging.basicConfig(level=logging.DEBUG)

#Crear categoria
def create_category(self, name, description=""):
    cursor = self.conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO categories (name, description)
            VALUES (?, ?)
        """, (name, description))
        self.conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
        return cursor.fetchone()[0]
    
    #crear un chat nuevo
def create_chat(self, name, category_id=None):
    cursor = self.conn.cursor()
    chat_uuid = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO chats (chat_uuid, name, category_id)
        VALUES (?, ?, ?)
    """, (chat_uuid, name, category_id))
    self.conn.commit()
    return chat_uuid

#crear un nuevo chat o obtener uno 
def get_or_create_chat(self, chat_uuid, name="Nuevo Chat"):
    cursor = self.conn.cursor()
    cursor.execute("SELECT id FROM chats WHERE chat_uuid = ?", (chat_uuid,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        return self.create_chat(name)

    #Extraer las palabras claves    
def extract_keywords(text):
    common_words = {'que', 'cual', 'como', 'donde', 'quien', 'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'en', 'de'}
    words = re.findall(r'\w+', text.lower())
    keywords = {word for word in words if len(word) > 3 and word not in common_words}
    return list(keywords)

#buscar una pregunta similar en la bd
def find_similar_question( question, chat_id=None, category_id=None, similarity_threshold=0.85):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    keywords = extract_keywords(question)
    if not keywords:
        return None
    
    cursor = conn.cursor()
    query_parts = []
    params = []

    # Base query
    query = """
        SELECT ch.question, ch.answer, COUNT(ck.keyword_id) as keyword_matches
        FROM chat_history ch
        JOIN chat_keywords ck ON ch.id = ck.chat_history_id
        JOIN keywords k ON ck.keyword_id = k.id
        WHERE
    """
    
    # Add parameters for keywords
    #query_parts.extend(['?'] * len(keywords))
    # Usando enumerate para obtener índice y valor
# Construir las condiciones de la consulta utilizando LIKE
    like_conditions = []
    for key in keywords:
        like_conditions.append(f"k.keyword LIKE '%{key}%'")

# Unir las condiciones con OR
    query += " OR ".join(like_conditions)

    #params.extend(keywords)

    """
    # Add chat_id filter if specified
    if chat_id:
        query += " AND ch.chat_id = ?"
        params.append(chat_id)
    """
    # Add category_id filter if specified
    if category_id:
        query += " AND ch.category_id = ?"
        params.append(category_id)

    # Complete the query
    query = query.format(','.join(['?'] * len(keywords)))
    query += " GROUP BY ch.id ORDER BY keyword_matches DESC LIMIT 5"

    cursor.execute(query, params)
    potential_matches = cursor.fetchall()

    logging.debug(potential_matches)

    for stored_question, answer, _ in potential_matches:
        similarity = SequenceMatcher(None, question.lower(), stored_question.lower()).ratio()
        if similarity >= similarity_threshold:
            return answer

    return None

#actualizar historial de chat
def update_chat_activity(self, chat_id):
    cursor = self.conn.cursor()
    cursor.execute("""
        UPDATE chats 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (chat_id,))
    self.conn.commit()
    
# Función para guardar mensajes en la base de datos
def save_chat(user_input, bot_response):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO chat_history (question, answer) VALUES (?, ?)', (user_input, bot_response))
    conn.commit()
    
    # Obtener el ID del registro recién insertado
    last_inserted_id = cursor.lastrowid
    
    conn.close()  # Asegúrate de cerrar la conexión
    return last_inserted_id

# Función para manejar palabras clave
def add_keywords_to_chat_history(chat_history_id, user_input):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    keywords = extract_keywords(None, user_input)  # Extrae las palabras clave del texto de entrada

    for keyword in keywords:
        # Verifica si la palabra clave ya existe
        cursor.execute("SELECT id FROM keywords WHERE keyword = ?", (keyword,))
        result = cursor.fetchone()
        
        if result:  # Si existe, usa el id existente
            keyword_id = result[0]
        else:  # Si no existe, inserta la nueva palabra clave
            cursor.execute("INSERT INTO keywords (keyword) VALUES (?)", (keyword,))
            keyword_id = cursor.lastrowid  # Obtiene el id de la nueva palabra clave

        # Crear la relación en chat_keywords
        cursor.execute("INSERT INTO chat_keywords (chat_history_id, keyword_id) VALUES (?, ?)", (chat_history_id, keyword_id))

    conn.commit()

# Función para agregar una nueva categoría o devolver el id de una existente
def get_or_create_category(name, description=""):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (name,))
    result = cursor.fetchone()
    
    if result:  # Si la categoría ya existe, devuelve su ID
        return result[0]
    else:  # Si no existe, inserta la nueva categoría
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        return cursor.lastrowid  # Devuelve el ID de la nueva categoría

def search_product_links(component_list):
    headers = {"User-Agent": "Mozilla/5.0"}
    product_links = ""

    for component in component_list:
        query = f"{component}"
        url = f"https://www.google.com/search?q={query}+comprar"
        product_links += f"- [{component}]({url})\n"

    return product_links

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

def principal(user_input,user_money):
     if user_input and user_money:
            # 1. Verificar si hay una pregunta similar
            existing_answer = find_similar_question(user_input)
            
            if existing_answer:
                #st.write("Respuesta anterior:", existing_answer)
                save_chat(user_input+user_money,existing_answer)
                return [existing_answer, "pala pico madera" ] #la lista aun no se como manejarla, no se si crear una tabla a parte para esot
            else:
                # 1. Obtener o crear categoría ¿?
                #category_id = get_or_create_category(user_input)

                # 2. Generar recomendaciones
                [bot_response, bot_items] = get_bot_response(user_money, user_input)

                # 3. Guardar la pregunta y respuesta en la base de datos
                id_chat = save_chat(user_input, bot_response)

                 # 4. Extraer palabras clave
                add_keywords_to_chat_history(id_chat,user_input)  # Usar el ID del historial del chat si está disponible

                # 4. Mostrar recomendaciones
                return   [bot_response, bot_items]
                #st.write("Recomendaciones:", recommendations)