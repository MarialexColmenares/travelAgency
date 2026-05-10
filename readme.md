# ✈️ Sistema de Gestión - Agencia de Viajes

Este proyecto es una **API** robusta desarrollada con **FastAPI** para la gestión integral de una agencia de viajes. El sistema permite administrar catálogos de servicios (hoteles, guías, transportes), diseñar paquetes turísticos dinámicos y gestionar el ciclo de vida completo de reservas y pagos de forma relacional.

---

## ✨ Características Principales

Además de las operaciones CRUD básicas, el sistema incluye lógica de negocio avanzada:

- **Gestión de Relaciones Complejas:** Implementación de relaciones _Muchos a Muchos_ (Paquetes y Destinos) y _Uno a Muchos_ (Reservas y Pagos).
- **CRUD Funcional Ampliado:**
  - Búsqueda inteligente de clientes por número de documento.
  - Cálculo automático de **Saldo Pendiente** en reservas según los pagos realizados.
  - Verificación de **Disponibilidad de Cupos** en paquetes turísticos en tiempo real.
- **Eliminación Lógica:** Los clientes no se borran físicamente, se gestionan mediante estados de actividad (`is_active`).
- **Validación Estricta:** Uso de Pydantic para asegurar la integridad de los datos de entrada (ej. validación de correos con `EmailStr`).

---

## 📂 Estructura del Proyecto

Basado en una arquitectura modular para facilitar la escalabilidad:

```

/TRAVELAGENCY
├── env/                # Entorno virtual
├── database/           # Configuración de la conexión y motor de BD
├── esquemas/           # Modelos de validación (Pydantic Schemas)
├── modelos/            # Definición de tablas y entidades (SQLModel)
├── routers/            # Módulos de rutas segmentados por entidad
├── main.py             # Punto de entrada y registro de routers
├── requirements.txt    # Dependencias del proyecto
└── readme.md           # Documentación

```

## 🛠️ Stack Tecnológico

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) (Combinación de SQLAlchemy y Pydantic)
- **Base de Datos:** PostgreSQL
- **Servidor ASGI:** Uvicorn
- **Validación de Datos:** Pydantic v2

# 🗺️ Modelo de Negocio (Lógica de Datos)

El sistema se divide en cuatro capas lógicas según los modelos implementados:

- Catálogos de Servicio: Gestión de Destinos, Guías, Transportes y Hoteles.

- Producto (Paquetes): El PaqueteTuristico actúa como núcleo, vinculando servicios y múltiples destinos mediante una tabla intermedia (PaqueteDestinoLink).

- Clientes: Registro y control de usuarios activos.

- Transacciones: Flujo de Reservas vinculadas a clientes y paquetes, con seguimiento detallado de Pagos.

# 🚀 Instalación y Uso

- Clonar el repositorio y entrar al directorio:

```
Bash
git clone (https://github.com/MarialexColmenares/travelAgency)
cd TRAVELAGENCY
```

- Configurar el entorno virtual:

```
Bash
python -m venv env
# En Windows:
env\Scripts\activate
# En Linux/Mac:
source env/bin/activate
```

- Instalar dependencias:

```
Bash
pip install -r ../requirements.txt
```

- Configurar la Base de Datos

```
Python
dbUrl = "postgresql://usuario:password@localhost:5432/nombre_db"
```

- Ejecutar la aplicación:

```
Bash
uvicorn main:app --reload
```

- 📖 Documentación Interactiva

Una vez iniciado el servidor, puedes acceder a la documentación automática en:

- Swagger UI: http://127.0.0.1:8000/docs

- ReDoc: http://127.0.0.1:8000/redoc

# 👤 Autor

Marialex Colemenares - LinkedIn: https://www.linkedin.com/in/marialex-colmenares-480171388/
