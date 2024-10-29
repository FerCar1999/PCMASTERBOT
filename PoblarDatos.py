
import sqlite3
import streamlit as st

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def poblar():
    """Pobla la base de datos con datos de ejemplo."""
    cursor = conn.cursor()
    
    # Listas de categorías
    categorias = [
        ('Ofimática', 'Optimizado para tareas básicas de oficina'),
        ('Diseño Gráfico', 'Optimizado para diseño gráfico y multimedia'),
        ('Edición de Video', 'Optimizado para edición de video y procesamiento de medios'),
        ('Programación', 'Optimizado para entornos de desarrollo y compilación de código')
    ]
    
    # Insertar categorías
    cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categorias)
    
    # Listas de historial de chat (preguntas y respuestas)
    historial_chats = [
        ('¿Qué PC puedo armar para gaming con bajo presupuesto?', 'Para gaming económico, te recomiendo una configuración con un procesador Ryzen 5, 16GB de RAM y una GTX 1650.'),
        ('¿Qué PC necesito para trabajos de oficina?', 'Para ofimática, te recomiendo un procesador i3 o Ryzen 3, 8GB de RAM, y un SSD de 256GB.'),
        ('¿Qué componentes necesito para diseño gráfico?', 'Para diseño gráfico, idealmente busca un procesador Ryzen 7, 32GB de RAM y una tarjeta RTX 3060.'),
        ('¿Qué PC es adecuada para edición de video?', 'Para edición de video, un procesador Intel i7, 32GB de RAM y una tarjeta gráfica RTX 3070 será óptimo.'),
        ('¿Qué PC armar para programación?', 'Para programación, un procesador i5 o Ryzen 5 con 16GB de RAM es adecuado.')
    ]
    
    # Insertar historial de chat
    cursor.executemany("INSERT INTO chat_history (question, answer) VALUES (?, ?)", historial_chats)
    
    # Lista de palabras clave
    palabras_clave = [
        ('gaming',),
        ('ofimática',),
        ('diseño gráfico',),
        ('edición de video',),
        ('programación',),
        ('presupuesto bajo',),
        ('presupuesto alto',),
        ('económico',)
    ]
    
    # Insertar palabras clave
    cursor.executemany("INSERT INTO keywords (keyword) VALUES (?)", palabras_clave)
    
    # Relacionar preguntas con palabras clave en la tabla chat_keywords
    relaciones = [
        (2, 2),  # chat_history_id = 2, keyword_id = 2
        (3, 3),  # chat_history_id = 3, keyword_id = 3
        (4, 4),  # chat_history_id = 4, keyword_id = 4
        (5, 5),  # chat_history_id = 5, keyword_id = 5
        (1, 6),  # chat_history_id = 1, keyword_id = 6
        (1, 7),  # chat_history_id = 1, keyword_id = 7
        (1, 8)   # chat_history_id = 1, keyword_id = 8
    ]
    
    # Insertar relaciones
    cursor.executemany("INSERT INTO chat_keywords (chat_history_id, keyword_id) VALUES (?, ?)", relaciones)

    # Guardar los cambios y cerrar la conexión
    conn.commit()