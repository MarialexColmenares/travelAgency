# ✈️ Sistema de Agencia de Viajes (CRUD I)

Implementación de endpoints fundamentales y configuración inicial del proyecto utilizando **FastAPI** y **SQLModel / SQLAlchemy**. Este sistema permite la gestión de servicios turísticos mediante la creación y consulta de datos.

## 🎯 Objetivos

- Implementar endpoints **GET** y **POST** funcionales.
- Configurar la conexión base a una base de datos Postgres (Engine y Session).
- Estructurar el desarrollo de un miniproyecto escalable y organizado.

---

## 📂 Estructura del Proyecto

Jerarquía de archivos dentro del directorio `/mini_proyecto`:

```text
/mini_proyecto
├── database.py        # Punto de entrada de la aplicación y rutas
├── main.py            # Configuración de la conexión (Engine y Session)
├── models.py          # Modelos de la base de datos (SQLModel)
├── requirements.txt   # Listado de librerías necesarias
└── env/               # Entorno virtual
```

# 🛠️ Configuración del Entorno

1. Creación del entorno virtual

```
python -m venv env

```

2. Instalación de librerías

```
pip install -r requirements.txt
```

# 🏗️ Modelado de Datos (Entidades)

El sistema integra las siguientes entidades para el funcionamiento de la agencia:

- 👤 Cliente: Datos personales, pasaporte o documento, teléfono y correo.

>> ¿ se puedes agregar entidades que crea necesarias ? 

aqui agregaria: nombre

- 📦 Paquete Turístico: Nombre, descripción, duración, precio, cupo y estado.

>> tengo dudas sobre los tipos de datos en duracion, cupo y estado

- 📍 Destino: Ciudad, país, descripción, clima y observaciones.

- 📅 Reserva: Fecha, cantidad de personas, estado, monto y comentarios.

- 💳 Pago: Registro de liquidación del paquete o abonos.

- 🚩 Guía: Nombre, idiomas, experiencia y disponibilidad.

- 🚌 Transporte: Tipo de transporte, empresa y capacidad.

- 🏨 Hotel: Nombre, categoría, dirección y contacto. 
