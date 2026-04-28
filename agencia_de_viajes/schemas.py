from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr

# --- SCHEMAS PARA CLIENTE ---
class ClienteBase(BaseModel):
    nombre: str
    documento: str
    telefono: str
    correo: EmailStr

class ClienteCreate(ClienteBase):
    pass  # Lo que el usuario envía al crear

class ClienteRead(ClienteBase):
    id: int  # Lo que devolvemos (incluye el ID)

class clienteUpdate(BaseModel):
    nombre: Optional[str] = None
    documento: Optional[str] = None
    telefono: Optional[str] = None
    correo:  Optional[EmailStr] = None

# --- SCHEMAS PARA PAQUETE TURÍSTICO ---
class PaqueteBase(BaseModel):
    nombre: str
    descripcion: str
    duracion: str
    precio: float
    cupo: int
    estado: str
    guia_id: Optional[int] = None
    transporte_id: Optional[int] = None
    hotel_id: Optional[int] = None
class PaqueteCreate(PaqueteBase):
    destinos_ids: list[int] = []

class PaqueteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    duracion: Optional[str] = None
    precio: Optional[float] = None
    cupo: Optional[int] = None
    estado: Optional[str] = None
    guia_id: Optional[int] = None
    transporte_id: Optional[int] = None
    hotel_id: Optional[int] = None

# --- SCHEMAS PARA RESERVA ---
class ReservaBase(BaseModel):
    fecha: date
    cantidad_personas: int
    estado: str
    monto_total: float
    comentarios: Optional[str] = None
    cliente_id: int
    paquete_id: int

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    fecha: Optional[date] = None
    cantidad_personas: Optional[int] = None
    estado: Optional[str] = None
    monto_total: Optional[float] = None
    comentarios: Optional[str] = None
    cliente_id: Optional[int] = None
    paquete_id: Optional[int] = None


# --- SCHEMAS PARA PAGO ---
class PagoBase(BaseModel):
    monto: float
    fecha_pago: date
    tipo_pago: str
    reserva_id: int

class PagoCreate(PagoBase):
    pass

class PagoUpdate(BaseModel):
    monto: Optional[float] = None
    fecha_pago: Optional[date] = None
    tipo_pago: Optional[str] = None

class GuiaCreate(BaseModel):
    nombre: str
    idiomas: str
    experiencia: int
    telefono: str
    estado: str

class GuiaUpdate(BaseModel):
    nombre: Optional[str] = None
    idiomas: Optional[str] = None
    experiencia: Optional[int] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None

# --- SCHEMAS PARA TRANSPORTE ---
class TransporteCreate(BaseModel):
    tipo: str
    empresa: str
    capacidad: int
    estado: str

class TransporteUpdate(BaseModel):
    tipo: Optional[str] = None
    empresa: Optional[str] = None
    capacidad: Optional[int] = None
    estado: Optional[str] = None


class HotelCreate(BaseModel):
    nombre: str
    categoria: int
    direccion: str
    ciudad: str
    contacto: str

class HotelUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[int] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    contacto: Optional[str] = None

class CreateDestino(BaseModel):
    ciudad: str
    pais: str
    descripcion: str
    clima: str
    observaciones: Optional[str] = None

class UpdateDestino(BaseModel):
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    descripcion: Optional[str] = None
    clima: Optional[str] = None
    observaciones: Optional[str] = None