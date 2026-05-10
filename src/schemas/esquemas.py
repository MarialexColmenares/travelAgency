from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr

#  --- DESTINOS ---
class CreateDestino(BaseModel):
    ciudad: str
    pais: str
    descripcion: str
    clima: str
    observaciones: Optional[str] = None
    estado: bool 
class UpdateDestino(CreateDestino):
    pass   
class UpdateDestinoParcial(BaseModel):
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    descripcion: Optional[str] = None
    clima: Optional[str] = None
    observaciones: Optional[str] = None
class DestinoSimple(BaseModel):
    ciudad: str
    pais: str
    
# --- GUIAS ---
class GuiaCreate(BaseModel):
    nombre: str
    idiomas: str
    experiencia: int
    telefono: str  
class GuiaUpdate(GuiaCreate):
    pass
class GuiaUpdateParcial(BaseModel):
    nombre: Optional[str] = None
    idiomas: Optional[str] = None
    experiencia: Optional[int] = None
    telefono: Optional[str] = None
    estado: Optional[str] = None

# --- TRANSPORTE ---
class TransporteCreate(BaseModel):
    tipo: str
    empresa: str
    capacidad: int  
class TransporteUpdate(TransporteCreate):
    pass
class TransporteUpdateParcial(BaseModel):
    tipo: Optional[str] = None
    empresa: Optional[str] = None
    capacidad: Optional[int] = None
    estado: Optional[str] = None

# --- CLIENTE ---
class ClienteBase(BaseModel):
    nombre: str
    documento: str
    telefono: str
    correo: EmailStr
class ClienteCreate(ClienteBase):
    pass 
class ClienteRead(ClienteBase):
    id: int
class clienteUpdate(BaseModel):
    nombre: Optional[str] = None
    documento: Optional[str] = None
    telefono: Optional[str] = None
    correo:  Optional[EmailStr] = None

# --- HOTELES ---
class HotelCreate(BaseModel):
    nombre: str
    categoria: int
    direccion: str
    contacto: str
    destino_id: Optional[int] = None
class HotelUpdate(HotelCreate):
    pass
class HotelUpdateParcial(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[int] = None
    direccion: Optional[str] = None
    contacto: Optional[str] = None

# --- PAQUETE TURÍSTICO ---
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
class paqueteConTransportes(BaseModel):
    
    nombre: str
    transporte: Optional[TransporteCreate] = None
    class Config:
        from_attributes = True

class PaqueteInfoCliente(BaseModel):
    nombre: str
    descripcion: str
    duracion: str
    precio: float
    cupo: int
    estado: str
    
    nombre_guia: Optional[str] = None
    transporte_empresa: Optional[str] = None
    destinos: List[DestinoSimple] = []

    class Config:
        from_attributes = True

# --- RESERVA ---
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


# --- PAGO ---
class PagoBase(BaseModel):
    monto: float
    fecha_pago: date
    tipo_pago: str
    reserva_id: int
class PagoCreate(PagoBase):
    pass
class PagoUpdateParcial(BaseModel):
    monto: Optional[float] = None
    fecha_pago: Optional[date] = None
    tipo_pago: Optional[str] = None

class PagoUpdate(PagoBase):
    pass