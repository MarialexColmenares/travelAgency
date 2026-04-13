from sqlmodel import SQLModel, Field

class Cliente(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    pasaporte: str
    teléfono: str
    correo: str
    
class PaqueteTurístico(SQLModel, table=True):
    id:int | None = Field(default=None, primary_key=True)
    nombre: str
    descripción: str
    duración: int
    precio: float
    cupo: int
    estado: str   
    
class Destino(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    Ciudad: str
    país: str
    descripción: str
    clima: str 
    observaciones: str 

class Reserva(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha: str
    cantidad_personas: int
    estado: str
    monto: float
    comentarios: str
    
class Pago(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha: str
    monto: float
    método_pago: str
    estado: str
    
class PersonaGuia(SQLModel,table=True):
    id:int | None = Field(default=None, primary_key=True)
    nombre: str
    idiomas: str
    experiencia: str
    disponibilidad: str 
    
class Transporte(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tipo: str
    empresa: str 
    capacidad: str 

class Hotel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    categoria: str
    direccion: str 
    contacto: str
    