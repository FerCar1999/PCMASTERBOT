# PCMasterBot

PCMasterBot es un asistente conversacional creado con Python que utiliza **OpenAI**, **SQLite** y **Streamlit**. Este bot sugiere componentes para armar PCs basados en el presupuesto ingresado por el usuario y proporciona enlaces de búsqueda directa en Google para comparar precios.

---

## 🚀 **Requisitos previos**

Asegúrate de tener los siguientes programas instalados:

- **Python 3.8 o superior**:  
  Verifica la versión con:
  ```bash
  python --version
  ```
- **Virtualenv (opcional pero recomendado)**:
  Si no tienes virtualenv, puedes instalarlo con:
  ```bash
  pip install virtualenv
  ```

---

## 📥 **Instalación**


Clona este repositorio:
```bash
git clone <URL-del-repositorio>
cd PCMasterBot
```
Crea y activa un entorno virtual:

Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```
---
## 🏃 **Ejecución del proyecto**
Ejecuta el bot con Streamlit:

```bash
streamlit run app.py
```

Abre tu navegador y ve a la dirección que aparece en la terminal.