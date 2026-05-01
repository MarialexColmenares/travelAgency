from typing import List, Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

# 1. TABLAS DE APOYO (RELACIONES MUCHOS A MUCHOS)
class PaqueteDestinoLink(SQLModel, table=True):
    """ Tabla intermedia para conectar paquetes con múltiples destinos """
    paquete_id: Optional[int] = Field(default=None, foreign_key="paqueteturistico.id", primary_key=True)
    destino_id: Optional[int] = Field(default=None, foreign_key="destino.id", primary_key=True)
    
# 2. ENTIDADES DE SERVICIOS (CATÁLOGOS)
class Destino(SQLModel, table=True):
    """ Lugares disponibles para visitar """
    id: Optional[int] = Field(default=None, primary_key=True)
    ciudad: str
    pais: str
    descripcion: str
    clima: str
    observaciones: Optional[str] = None
    
    hoteles: List["Hotel"] = Relationship(back_populates="destino")
    paquetes: List["PaqueteTuristico"] = Relationship(back_populates="destinos", link_model=PaqueteDestinoLink)

class Guia(SQLModel, table=True):
    """ Personal que lidera los tours """
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    idiomas: str
    experiencia: int
    telefono: str
    estado: str = Field(default="Disponible")  # Ejemplo: "Disponible", "En viaje", "Inactivo"

    paquetes: List["PaqueteTuristico"] = Relationship(back_populates="guia")
    
class Transporte(SQLModel, table=True):
    """ Medios de transporte utilizados """
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str  # Bus, Avión, etc.
    empresa: str
    capacidad: int
    estado: str = Field(default="Activo") # Ejemplo: "Fuera de Servicio", "Inactivo"
    
    paquetes: List["PaqueteTuristico"] = Relationship(back_populates="transporte")
    
class Hotel(SQLModel, table=True):
    """ Alojamientos vinculados a los viajes """
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    categoria: int  # Estrellas (1-5)
    direccion: str
    ciudad: str
    contacto: str
    destino_id: Optional[int] = Field(default=None, foreign_key="destino.id")
    # Permite acceder a la lista de todos los paquetes asignados a este transporte
    paquetes: List["PaqueteTuristico"] = Relationship(back_populates="hotel")
    destino: Optional["Destino"] = Relationship(back_populates="hoteles")

# 3. NÚCLEO DEL NEGOCIO (PAQUETES Y CLIENTES)
class PaqueteTuristico(SQLModel, table=True):
    """ El producto principal que vende la agencia """
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str
    duracion: str
    precio: float
    cupo: int
    estado: str = Field(default="Disponible")   # agotado, disponible, inactivo

    # Claves Foráneas (Conexión con servicios)
    guia_id: Optional[int] = Field(default=None, foreign_key="guia.id")
    transporte_id: Optional[int] = Field(default=None, foreign_key="transporte.id")
    hotel_id: Optional[int] = Field(default=None, foreign_key="hotel.id")

    # Relaciones para acceder a los datos fácilmente
    destinos: List[Destino] = Relationship(back_populates="paquetes", link_model=PaqueteDestinoLink)
    reservas: List["Reserva"] = Relationship(back_populates="paquete")
    guia: Optional[Guia] = Relationship(back_populates="paquetes")
    # Esta línea estaba mal (decía back_populates="transporte")
    transporte: Optional[Transporte] = Relationship(back_populates="paquetes")
    # Esta línea también estaba mal (decía back_populates="hotel")
    hotel: Optional[Hotel] = Relationship(back_populates="paquetes")

class Cliente(SQLModel, table=True):
    """ Información de las personas que compran viajes """
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    documento: str = Field(index=True, unique=True)
    telefono: str
    correo: str
    is_active: bool = True

    reservas: List["Reserva"] = Relationship(back_populates="cliente")

# 4. TRANSACCIONES (RESERVAS Y PAGOS)
class Reserva(SQLModel, table=True):
    """ Registro de venta de un paquete a un cliente """
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: date
    cantidad_personas: int
    estado: str  # "Pendiente", "Confirmada", "Cancelada"
    monto_total: float
    comentarios: Optional[str] = None

    # Claves foráneas
    cliente_id: int = Field(foreign_key="cliente.id")
    paquete_id: int = Field(foreign_key="paqueteturistico.id")

    # Relaciones
    cliente: Cliente = Relationship(back_populates="reservas")
    paquete: PaqueteTuristico = Relationship(back_populates="reservas")
    pagos: List["Pago"] = Relationship(back_populates="reserva")

class Pago(SQLModel, table=True):
    """ Control de dinero recibido por reserva """
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    fecha_pago: date
    tipo_pago: str  # "Abono" o "Total"

    reserva_id: int = Field(foreign_key="reserva.id")
    reserva: Reserva = Relationship(back_populates="pagos")
