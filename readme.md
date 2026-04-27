# ✈️ Sistema de Gestión - Agencia de Viajes

Este proyecto es una **API** desarrollada con **FastAPI** para la gestión integral de una agencia de viajes. Permite administrar catálogos de servicios (hoteles, guías, transportes), diseñar paquetes turísticos dinámicos y gestionar el ciclo de vida de reservas y pagos.

---

## 📂 Estructura del Proyecto

Basado en una arquitectura modular para facilitar la escalabilidad:

```
/TRAVELAGENCY
├── agencia_de_viajes/     # Directorio principal del código
│   ├── env/               # Entorno virtual
│   ├── routers/           # Módulos de rutas (Clientes, Reservas, etc.)
│   ├── conexion.py        # Configuración de base de datos (Engine/Session)
│   ├── main.py            # Punto de entrada y registro de routers
│   ├── models.py          # Definición de entidades (SQLModel)
│   └── schemas.py         # Modelos de validación (Pydantic)
├── requirements.txt       # Dependencias del proyecto
└── readme.md              # Documentación
```

# 🛠️ Stack Tecnológico

- Framework: FastAPI

- ORM: SQLModel (basado en SQLAlchemy y Pydantic)

- Base de Datos: PostgreSQL

- Servidor ASGI: Uvicorn

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

cd TRAVELAGENCY/agencia_de_viajes
```

- Configurar el entorno virtual:

```
Bash
python -m venv env
source env/Scripts/activate  # En Windows: env\Scripts\activate
```

- Instalar dependencias:

```
Bash
pip install -r ../requirements.txt
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
